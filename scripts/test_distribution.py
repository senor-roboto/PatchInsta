import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from bundle import digest, validate_mpp, verify_checksums, version_tuple
from publish import metadata, verify_public, find_release
from io import BytesIO
import hashlib


class DistributionTests(unittest.TestCase):
    def test_existing_draft_lookup_tolerates_delayed_collection_without_recreating(self):
        release={'id':123,'tag_name':'v4.1.1','draft':True};replies=[[],[],[release]];waits=[];calls=[]
        def request(path):
            calls.append(path);return replies.pop(0)
        self.assertEqual(find_release('repos/example/repo','v4.1.1',request,waits.append),release)
        self.assertEqual(waits,[2,4]);self.assertEqual(len(calls),3)
        self.assertTrue(all(p.endswith('/releases?per_page=100') for p in calls))

    def test_missing_known_draft_fails_without_unbounded_wait_or_mutation(self):
        waits=[]
        with self.assertRaisesRegex(ValueError,'Known release'):
            find_release('repos/example/repo','v4.1.1',lambda p:[],waits.append)
        self.assertEqual(len(waits),5)

    def test_stable_url_retries_old_cached_feed_then_verifies_new_bytes(self):
        feed={'version':'4.1.1','download_url':'https://example.test/new.mpp'}
        replies=[json.dumps({'version':'4.1.0'}).encode(), json.dumps(feed).encode(), b'new bundle']
        urls=[]; waits=[]
        def open_response(url, **kwargs):
            urls.append(url); return BytesIO(replies.pop(0))
        verify_public('https://example.test/patches-bundle.json',feed,hashlib.sha256(b'new bundle').hexdigest(),open_response,waits.append)
        self.assertEqual(urls[:2],['https://example.test/patches-bundle.json']*2)
        self.assertEqual(urls[-1],feed['download_url']); self.assertEqual(waits,[5])

    def test_anonymous_corruption_is_not_hidden_by_retries(self):
        feed={'version':'4.1.1','download_url':'https://example.test/new.mpp'}
        replies=[json.dumps(feed).encode(),b'wrong']; waits=[]
        with self.assertRaisesRegex(ValueError,'checksum'):
            verify_public('https://example.test/feed',feed,hashlib.sha256(b'right').hexdigest(),lambda *a,**k:BytesIO(replies.pop(0)),waits.append)
        self.assertEqual(waits,[])

    def test_permanently_stale_feed_has_a_bounded_failure(self):
        waits=[]
        with self.assertRaisesRegex(ValueError,'bounded'):
            verify_public('https://example.test/feed',{'version':'4.1.1'},'unused',lambda *a,**k:BytesIO(b'{}'),waits.append)
        self.assertEqual(len(waits),6)

    def test_bundle_rejects_a_jar_without_android_dex(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'test.mpp'
            with zipfile.ZipFile(path,'w') as z:
                z.writestr('META-INF/MANIFEST.MF','Name: PatchInsta\nVersion: 4.1.0\n')
                z.writestr('extensions/instagram.rve',b'extension fixture')
            with self.assertRaisesRegex(ValueError,'DEX'):
                validate_mpp(path,'4.1.0','PatchInsta')

    def test_bundle_rejects_wrong_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'test.mpp'
            with zipfile.ZipFile(path,'w') as z:
                z.writestr('META-INF/MANIFEST.MF','Name: Old bundle\nVersion: 3.9.0\n')
            with self.assertRaisesRegex(ValueError,'identity'):
                validate_mpp(path,'4.1.0','PatchInsta')

    def test_checksum_detects_a_changed_download(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); file=root/'bundle.mpp'; file.write_bytes(b'original')
            (root/'SHA256SUMS.txt').write_text(digest(file)+'  bundle.mpp\n')
            self.assertIn('bundle.mpp',verify_checksums(root))
            file.write_bytes(b'corrupted')
            with self.assertRaisesRegex(ValueError,'mismatch'):
                verify_checksums(root)

    def test_checksum_rejects_paths_outside_kit(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); (root/'SHA256SUMS.txt').write_text('0'*64+'  ../outside\n')
            with self.assertRaisesRegex(ValueError,'entry'):
                verify_checksums(root)

    def test_versions_compare_numerically_and_require_stable_semver(self):
        self.assertGreater(version_tuple('4.10.0'),version_tuple('4.9.99'))
        for value in ('v4.1.0','4.1','4.1.0-dev.1','not-a-version'):
            with self.assertRaises(ValueError): version_tuple(value)

    def test_morphe_dto_uses_local_datetime_and_durable_versioned_asset(self):
        result=metadata({'version':'4.1.0','repository':'senor-roboto/PatchInsta'},
                        {'published_at':'2026-09-08T10:00:00Z','html_url':'https://github.com/senor-roboto/PatchInsta/releases/tag/v4.1.0'})
        self.assertEqual(set(result),{'version','created_at','description','download_url','signature_download_url','page_url'})
        self.assertEqual(result['created_at'],'2026-09-08T10:00:00')
        self.assertEqual(result['download_url'],'https://github.com/senor-roboto/PatchInsta/releases/download/v4.1.0/PatchInsta-4.1.0.mpp')
        self.assertIsNone(result['signature_download_url'])
        self.assertEqual(json.loads(json.dumps(result)),result)


if __name__=='__main__': unittest.main()
