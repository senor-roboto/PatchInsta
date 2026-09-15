"""Use the authoritative generated DEX set; preserve every other rebuilt ZIP entry."""
import argparse, hashlib, json, re, subprocess, zipfile
from pathlib import Path

def sha(data): return hashlib.sha256(data).hexdigest()

def canonicalize(original, rebuilt, dex_dir, output, zipalign):
    original, rebuilt, dex_dir, output = map(Path, (original, rebuilt, dex_dir, output))
    assert not output.exists(), 'Refusing to overwrite output'
    temporary = output.with_suffix('.unaligned.zip')
    assert not temporary.exists(), 'Refusing to overwrite intermediate'
    generated = {p.name: p.read_bytes() for p in dex_dir.glob('classes*.dex')}
    expected = {'classes.dex'} | {f'classes{i}.dex' for i in range(2, len(generated)+1)}
    assert generated and set(generated) == expected, 'Noncanonical generated DEX set'
    assert all(data.startswith(b'dex\n') for data in generated.values()), 'Invalid DEX magic'
    with zipfile.ZipFile(original) as src, zipfile.ZipFile(rebuilt) as candidate:
        assert candidate.testzip() is None, 'Corrupt rebuilt APK'
        names = candidate.namelist()
        assert len(names) == len(set(names)), 'Duplicate ZIP entries'
        dex_names = {n for n in names if re.fullmatch(r'classes(?:[2-9]|[1-9][0-9]+)?\.dex', n)}
        assert set(generated) <= dex_names, 'Generated DEX absent from APK'
        for name, data in generated.items():
            assert candidate.read(name) == data, f'Rebuilt/generated DEX differs: {name}'
        stale = dex_names - set(generated)
        for name in stale:
            assert name in src.namelist() and candidate.read(name) == src.read(name), f'Unexpected extra DEX: {name}'
        libraries = {n: sha(src.read(n)) for n in src.namelist() if n.startswith('lib/') and n.endswith('.so')}
        for name, digest in libraries.items():
            assert sha(candidate.read(name)) == digest, f'Native library differs: {name}'
        with zipfile.ZipFile(temporary, 'w') as dst:
            for entry in candidate.infolist():
                if entry.filename not in stale: dst.writestr(entry, candidate.read(entry.filename))
    subprocess.run([str(zipalign), '-P', '16', '4', str(temporary), str(output)], check=True)
    subprocess.run([str(zipalign), '-c', '-P', '16', '4', str(output)], check=True)
    with zipfile.ZipFile(rebuilt) as before, zipfile.ZipFile(output) as after:
        assert after.testzip() is None
        assert set(after.namelist()) == set(before.namelist()) - stale
        assert all(after.read(n) == before.read(n) for n in after.namelist()), 'Entry content changed'
    temporary.unlink()
    return {'removed_stale_original_dex': sorted(stale), 'generated_dex_count': len(generated),
            'native_libraries_preserved': len(libraries), 'native_library_sha256': libraries,
            'all_retained_entries_byte_identical': True, 'zip_integrity': True,
            'zipalign_16k': True, 'unsigned_apk_sha256': sha(output.read_bytes()),
            'art_device_validation': False}

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('original'); p.add_argument('rebuilt'); p.add_argument('dex_dir');p.add_argument('output');p.add_argument('zipalign');p.add_argument('report')
    a=p.parse_args();r=canonicalize(a.original,a.rebuilt,a.dex_dir,a.output,a.zipalign)
    Path(a.report).write_text(json.dumps(r,indent=2)+'\n'); print(json.dumps(r,indent=2))
