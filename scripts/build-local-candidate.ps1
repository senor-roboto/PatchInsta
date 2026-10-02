[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)][string]$Apkm,
    [Parameter(Mandatory = $true)][string]$Mpp,
    [Parameter(Mandatory = $true)][string]$OutputApk,
    [string]$PythonExe
)

# Builds a local, test-signed candidate APK. This script deliberately has no
# ADB/install path and never copies the private APKM into the workspace.
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$java = Join-Path $root '.work/jdk21/jdk-21.0.12.1+1/bin/java.exe'
$keytool = Join-Path $root '.work/jdk21/jdk-21.0.12.1+1/bin/keytool.exe'
$morphe = Join-Path $root '.work/morphe-1.14.0-dev.1.jar'
$buildTools = Join-Path $root '.work/android-sdk/build-tools/35.0.0'
$zipalign = Join-Path $buildTools 'zipalign.exe'
$aapt = Join-Path $buildTools 'aapt.exe'
$apksigner = Join-Path $buildTools 'lib/apksigner.jar'
$canonicalizer = Join-Path $root 'diagnostics/canonicalize_apk.py'
$verifyClass = Join-Path $root '.work/VerifyFoldDex.class'
$verifyJar = Join-Path $root '.work/morphe-verify.jar'

foreach ($tool in @($java, $keytool, $morphe, $zipalign, $aapt, $apksigner, $canonicalizer, $verifyClass, $verifyJar)) {
    if (!(Test-Path -LiteralPath $tool -PathType Leaf)) { throw "Required local tool/file missing: $tool" }
}
$apkmPath = (Resolve-Path -LiteralPath $Apkm -ErrorAction Stop).Path
$mppPath = (Resolve-Path -LiteralPath $Mpp -ErrorAction Stop).Path
$outputPath = [IO.Path]::GetFullPath($OutputApk)
if ([IO.Path]::GetExtension($outputPath) -ne '.apk') { throw 'OutputApk must end in .apk' }
if (Test-Path -LiteralPath $outputPath) { throw "Refusing to overwrite output: $outputPath" }
$outputDir = Split-Path -Parent $outputPath
if (!(Test-Path -LiteralPath $outputDir -PathType Container)) { throw "Output directory must already exist: $outputDir" }
if ($apkmPath -eq $outputPath -or $mppPath -eq $outputPath) { throw 'Output must differ from every input.' }
if ($PSCmdlet.ShouldProcess($outputPath, 'Build and sign local test APK')) { } else { return }
if (!$PythonExe) {
    $pythonCommand = Get-Command python, python3 -ErrorAction SilentlyContinue | Select-Object -First 1
    if (!$pythonCommand) { throw 'Python 3 is required for the canonical APK check; pass -PythonExe with a Python 3.8+ executable.' }
    $PythonExe = $pythonCommand.Source
}
if (!(Test-Path -LiteralPath $PythonExe -PathType Leaf)) { throw "Python executable not found: $PythonExe" }

$runId = [Guid]::NewGuid().ToString('N')
$work = Join-Path $root ".work/local-candidate-$runId"
New-Item -ItemType Directory -Path $work | Out-Null
$optionsPath = Join-Path $work 'options.json'
$rawApk = Join-Path $work 'patched-raw.apk'
$canonicalApk = Join-Path $work 'patched-canonical-unsigned.apk'
$resultPath = Join-Path $work 'morphe-result.json'
$patchLog = Join-Path $work 'morphe.log'
$keyStore = Join-Path $root '.work/lab-signing/test-only.jks'
$reportPath = Join-Path $work 'canonicalize-report.json'

function Invoke-Checked([string]$File, [string[]]$Arguments, [string]$Label) {
    $lines = & $File @Arguments 2>&1
    $code = $LASTEXITCODE
    if ($code -ne 0) { throw "$Label failed (exit $code): $($lines -join [Environment]::NewLine)" }
    return ,$lines
}

# Create a template from the supplied candidate MPP; then explicitly enable
# precisely its 60 Instagram patches and set Clone's package identity.
Invoke-Checked $java @('-jar', $morphe, 'options-create', '-p', $mppPath, '-f', 'com.instagram.android', '-o', $optionsPath) 'Morphe options-create' | Out-Null
$options = Get-Content -LiteralPath $optionsPath -Raw | ConvertFrom-Json
if ($options.Count -ne 1) { throw 'Expected exactly one options bundle for the candidate MPP.' }
$patchMap = $options[0].patches
if (@($patchMap.PSObject.Properties).Count -ne 60) { throw "Expected 60 patches in candidate MPP; found $(@($patchMap.PSObject.Properties).Count)." }
foreach ($name in @('Adaptive Fold Reels', 'Clone')) {
    if (!$patchMap.PSObject.Properties[$name]) { throw "Required patch absent from candidate MPP: $name" }
}
foreach ($name in $patchMap.PSObject.Properties.Name) { $patchMap.$name.enabled = $true }
$patchMap.Clone.options.packageName = 'com.instagram.android.patchinstalab'
$patchMap.Clone.options.appName = 'PatchInsta Lab'
ConvertTo-Json -InputObject @($options) -Depth 30 | Set-Content -LiteralPath $optionsPath -Encoding utf8

# Do not pass -i/--install. Morphe merges the local APKM and produces a local APK.
$morpheArgs = @('-jar', $morphe, 'patch', $apkmPath, '-p', $mppPath,
    '--options-file', $optionsPath, '--unsigned', '--disable-purge', '-o', $rawApk,
    '-r', $resultPath, '-t', (Join-Path $work 'morphe-temp'))
$patchOutput = & $java @morpheArgs 2>&1
$patchExit = $LASTEXITCODE
$patchOutput | Set-Content -LiteralPath $patchLog -Encoding utf8
if ($patchExit -ne 0) { throw "Morphe patch failed (exit $patchExit); see $patchLog" }
if (!(Test-Path -LiteralPath $rawApk -PathType Leaf) -or !(Test-Path -LiteralPath $resultPath -PathType Leaf)) {
    throw "Morphe did not produce both raw APK and result report; see $patchLog"
}

$result = Get-Content -LiteralPath $resultPath -Raw | ConvertFrom-Json
$applied = @($result.appliedPatches)
if ($applied.Count -ne 60 -or @($result.failedPatches).Count -ne 0) { throw 'Morphe result did not report 60 successful patches with no failures.' }
$appliedNames = @($applied | ForEach-Object { $_.name })
if ($appliedNames -notcontains 'Adaptive Fold Reels' -or $appliedNames -notcontains 'Clone') { throw 'Required patches were not applied.' }
$clone = $applied | Where-Object name -eq 'Clone' | Select-Object -First 1
if (($clone.options | Where-Object key -eq 'packageName' | Select-Object -ExpandProperty value -First 1) -ne 'com.instagram.android.patchinstalab') {
    throw 'Clone packageName did not match the required isolated package.'
}

# APKM's base.apk is the immutable original for DEX and native-library comparisons.
# Reject code or native libraries in split APKs, since those would make base.apk
# an incomplete source for this strict check.
Add-Type -AssemblyName System.IO.Compression.FileSystem
$mergedApk = Join-Path $work 'source-base.apk'
$archive = [IO.Compression.ZipFile]::OpenRead($apkmPath)
try {
    $baseEntry = $archive.Entries | Where-Object FullName -CEQ 'base.apk' | Select-Object -First 1
    if (!$baseEntry) { throw 'APKM has no base.apk entry.' }
    $splitIndex = 0
    foreach ($split in @($archive.Entries | Where-Object { $_.FullName -match '\.apk$' -and $_.FullName -cne 'base.apk' })) {
        $splitIndex++
        $splitPath = Join-Path $work "split-check-$splitIndex.apk"
        [IO.Compression.ZipFileExtensions]::ExtractToFile($split, $splitPath)
        $splitZip = [IO.Compression.ZipFile]::OpenRead($splitPath)
        try {
            $codeOrLibrary = $splitZip.Entries | Where-Object { $_.FullName -match '^classes(?:[2-9]|[1-9][0-9]+)?\.dex$|^lib/.+\.so$' } | Select-Object -First 1
            if ($codeOrLibrary) { throw "APKM split contains code or native library: $($split.FullName) / $($codeOrLibrary.FullName)" }
        } finally { $splitZip.Dispose() }
    }
    [IO.Compression.ZipFileExtensions]::ExtractToFile($baseEntry, $mergedApk)
}
finally { $archive.Dispose() }
$badging = Invoke-Checked $aapt @('dump', 'badging', $rawApk) 'aapt badging'
if (($badging -join "`n") -notmatch "package: name='com\.instagram\.android\.patchinstalab'") {
    throw 'Patched APK manifest package is not the isolated lab package.'
}

# Compare against Morphe's actual generated DEX, never a copy extracted from the APK.
$generatedDirs = @(Get-ChildItem (Join-Path $work 'morphe-temp') -Directory -Recurse | Where-Object { $_.FullName -match '[\\/]patched[\\/]dex$' })
if ($generatedDirs.Count -ne 1) { throw 'Expected one authoritative generated DEX directory.' }
$dexDir = $generatedDirs[0].FullName

Invoke-Checked $PythonExe @($canonicalizer, $mergedApk, $rawApk, $dexDir, $canonicalApk, $zipalign, $reportPath) 'APK canonicalization' | Out-Null
Invoke-Checked $java @('-cp', "$verifyJar;$root/.work", 'VerifyFoldDex', $mergedApk, $canonicalApk) 'Fold DEX static verification' | Out-Null

# Reuse the local lab certificate so future test APKs can update this isolated clone.
if (!(Test-Path -LiteralPath $keyStore)) {
New-Item -ItemType Directory -Force -Path (Split-Path $keyStore -Parent) | Out-Null
Invoke-Checked $keytool @('-genkeypair', '-noprompt', '-keystore', $keyStore, '-storetype', 'JKS',
    '-storepass', 'changeit', '-keypass', 'changeit', '-alias', 'patchinsta-test',
    '-keyalg', 'RSA', '-keysize', '2048', '-validity', '3650', '-dname', 'CN=PatchInsta Local Test') 'Test-key generation' | Out-Null
}
Invoke-Checked $java @('-jar', $apksigner, 'sign', '--ks', $keyStore, '--ks-key-alias', 'patchinsta-test',
    '--ks-pass', 'pass:changeit', '--key-pass', 'pass:changeit', '--v1-signing-enabled', 'true',
    '--v2-signing-enabled', 'true', '--v3-signing-enabled', 'true', '--v4-signing-enabled', 'false',
    '--out', $outputPath, $canonicalApk) 'APK signing' | Out-Null
Invoke-Checked $java @('-jar', $apksigner, 'verify', '--verbose', $outputPath) 'APK signature verification' | Out-Null
Invoke-Checked $zipalign @('-c', '-P', '16', '4', $outputPath) 'Final APK alignment verification' | Out-Null
$finalBadging = Invoke-Checked $aapt @('dump', 'badging', $outputPath) 'Final aapt badging'
if (($finalBadging -join "`n") -notmatch "package: name='com\.instagram\.android\.patchinstalab'") { throw 'Final APK package identity changed after signing.' }

$sha = (Get-FileHash -LiteralPath $outputPath -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Output "Built local test APK: $outputPath"
Write-Output "SHA-256: $sha"
Write-Output "Build evidence: $work; persistent local lab signing key: $keyStore"
Write-Output 'No device installation was performed. The APK is signed with a locally generated test key.'
