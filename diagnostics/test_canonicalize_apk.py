import tempfile, unittest, zipfile
from pathlib import Path
from unittest.mock import patch
from canonicalize_apk import canonicalize

class CanonicalApkTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.original=self.root/'original.apk';self.rebuilt=self.root/'rebuilt.apk';self.dex=self.root/'dex';self.dex.mkdir();self.output=self.root/'output.apk'
        self.write(self.original,{'classes.dex':b'dex\nold','classes2.dex':b'dex\nstale','lib/arm64-v8a/native.so':b'native'})
        self.entries={'classes.dex':b'dex\nnew','classes2.dex':b'dex\nstale','lib/arm64-v8a/native.so':b'native','assets/keep.dex':b'asset'}
        (self.dex/'classes.dex').write_bytes(b'dex\nnew');self.write(self.rebuilt,self.entries)
    @staticmethod
    def write(path,entries):
        with zipfile.ZipFile(path,'w') as z:
            for name,data in entries.items():z.writestr(name,data)
    def run_gate(self):
        return canonicalize(self.original,self.rebuilt,self.dex,self.output,'zipalign')
    def test_only_stale_root_dex_is_removed_and_all_other_entries_survive(self):
        # Archive filtering unit test only; actual SDK alignment is exercised separately on the real APK.
        def alignment(args,check):
            if '-c' not in args:Path(args[-1]).write_bytes(Path(args[-2]).read_bytes())
        with patch('canonicalize_apk.subprocess.run',side_effect=alignment) as calls:result=self.run_gate()
        self.assertEqual(['classes2.dex'],result['removed_stale_original_dex']);self.assertEqual(2,calls.call_count)
        with zipfile.ZipFile(self.output) as z:
            self.assertEqual(set(self.entries)-{'classes2.dex'},set(z.namelist()))
            for name in z.namelist():self.assertEqual(self.entries[name],z.read(name))
    def test_unrecognized_extra_dex_is_not_deleted(self):
        self.entries['classes2.dex']=b'dex\nother';self.write(self.rebuilt,self.entries)
        with self.assertRaisesRegex(AssertionError,'Unexpected extra DEX'):self.run_gate()
        self.assertFalse(self.output.exists())
    def test_missing_generated_dex_is_rejected(self):
        (self.dex/'classes2.dex').write_bytes(b'dex\nnew2');self.entries.pop('classes2.dex');self.write(self.rebuilt,self.entries)
        with self.assertRaisesRegex(AssertionError,'Generated DEX absent'):self.run_gate()
    def test_changed_native_library_is_rejected(self):
        self.entries['lib/arm64-v8a/native.so']=b'changed';self.write(self.rebuilt,self.entries)
        with self.assertRaisesRegex(AssertionError,'Native library differs'):self.run_gate()

if __name__=='__main__':unittest.main()
