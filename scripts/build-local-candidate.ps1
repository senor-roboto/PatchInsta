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
$apksigner = Join-Path $buildTools 'apksigner.bat'
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
$dexDir = Join-Path $work 'generated-dex'
$keyStore = Join-Path $work 'local-test-only.jks'
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
if ($patchMap.Count -ne 60) { throw "Expected 60 patches in candidate MPP; found $($patchMap.Count)." }
foreach ($name in @('Adaptive Fold Reels', 'Clone')) {
    if (!$patchMap.PSObject.Properties[$name]) { throw "Required patch absent from candidate MPP: $name" }
}
foreach ($name in $patchMap.PSObject.Properties.Name) { $patchMap.$name.enabled = $true }
$patchMap.Clone.options.packageName = 'com.instagram.android.patchinstalab'
$patchMap.Clone.options.appName = 'PatchInsta Lab'
$options | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $optionsPath -Encoding utf8

# Do not pass -i/--install. Morphe merges the local APKM and produces a local APK.
$morpheArgs = @('-jar', $morphe, 'patch', $apkmPath, '-p', $mppPath,
    '--options-file', $optionsPath, '--unsigned', '-o', $rawApk,
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

# The CLI reports its merged source APK in the local output. Use that merged
# artifact for canonical DEX/native comparisons; never reconstruct from guessed splits.
$mergedApk = $null
foreach ($line in $patchOutput) {
    if ([string]$line -match 'Saved to:\s*(.+-merged\.apk)\s*$') { $mergedApk = $Matches[1].Trim() }
}
if (!$mergedApk) { throw "Could not identify Morphe's merged local APK from its output; see $patchLog" }
if (!(Test-Path -LiteralPath $mergedApk -PathType Leaf)) { throw "Morphe merged APK is unavailable: $mergedApk" }

$badging = Invoke-Checked $aapt @('dump', 'badging', $rawApk) 'aapt badging'
if (($badging -join "`n") -notmatch "package: name='com\.instagram\.android\.patchinstalab'") {
    throw 'Patched APK manifest package is not the isolated lab package.'
}

New-Item -ItemType Directory -Path $dexDir | Out-Null
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [IO.Compression.ZipFile]::OpenRead($rawApk)
try {
    $dexEntries = @($zip.Entries | Where-Object { $_.FullName -match '^classes(?:[2-9]|[1-9][0-9]+)?\.dex$' })
    if ($dexEntries.Count -lt 1) { throw 'Patched APK has no DEX entries.' }
    foreach ($entry in $dexEntries) {
        $dest = Join-Path $dexDir $entry.Name
        [IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $dest)
    }
}
finally { $zip.Dispose() }

Invoke-Checked $PythonExe @($canonicalizer, $mergedApk, $rawApk, $dexDir, $canonicalApk, $zipalign, $reportPath) 'APK canonicalization' | Out-Null
Invoke-Checked $java @('-cp', "$verifyJar;$root/.work", 'VerifyFoldDex', $mergedApk, $canonicalApk) 'Fold DEX static verification' | Out-Null

# A fresh, local test-only certificate is generated inside this ignored work dir.
Invoke-Checked $keytool @('-genkeypair', '-noprompt', '-keystore', $keyStore, '-storetype', 'JKS',
    '-storepass', 'changeit', '-keypass', 'changeit', '-alias', 'patchinsta-test',
    '-keyalg', 'RSA', '-keysize', '2048', '-validity', '3650', '-dname', 'CN=PatchInsta Local Test') 'Test-key generation' | Out-Null
Invoke-Checked $apksigner @('sign', '--ks', $keyStore, '--ks-key-alias', 'patchinsta-test',
    '--ks-pass', 'pass:changeit', '--key-pass', 'pass:changeit', '--v1-signing-enabled', 'true',
    '--v2-signing-enabled', 'true', '--v3-signing-enabled', 'true', '--v4-signing-enabled', 'false',
    '--out', $outputPath, $canonicalApk) 'APK signing' | Out-Null
Invoke-Checked $apksigner @('verify', '--verbose', $outputPath) 'APK signature verification' | Out-Null
Invoke-Checked $zipalign @('-c', '-P', '16', '4', $outputPath) 'Final APK alignment verification' | Out-Null
$finalBadging = Invoke-Checked $aapt @('dump', 'badging', $outputPath) 'Final aapt badging'
if (($finalBadging -join "`n") -notmatch "package: name='com\.instagram\.android\.patchinstalab'") { throw 'Final APK package identity changed after signing.' }

$sha = (Get-FileHash -LiteralPath $outputPath -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Output "Built local test APK: $outputPath"
Write-Output "SHA-256: $sha"
Write-Output "Build evidence and local test-only signing key: $work"
Write-Output 'No device installation was performed. The APK is signed with a locally generated test key.'

