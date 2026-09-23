import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from bundle import digest, validate_mpp, verify_checksums, version_tuple
from publish import metadata, verify_public, find_release, select_release, upload_assets, load_device_evidence, verify_candidate
from io import BytesIO
import hashlib
from unittest.mock import patch


class DistributionTests(unittest.TestCase):
    def physical_evidence(self):
        return {
            'schema':'patchinsta-device-validation/v1', 'version':'4.1.9',
            'candidate_run_id':'12345', 'source_commit':'a'*40, 'mpp_sha256':'b'*64,
            'attested_by':'tester', 'tested_at':'2026-09-23T15:00:00+02:00',
            'device':{'model':'Galaxy Z Fold','android_version':'Android 16','one_ui_version':'One UI 8'},
            'instagram':{'version':'439.0.0.37.89'},
            'scenarios':{'cold_starts':10,'swipes':30,'fold_cycles':5},
            'checks':{
                'external_screen_visual_pass':True, 'internal_screen_native_pass':True,
                'no_media_border':True, 'gradient_full_width_bottom':True,
                'author_and_caption_readable':True, 'comments_work':True,
                'scrubber_seeks_correctly':True, 'no_crashes':True},
            'screenshot_sha256':['a'*64]}

    def test_physical_gate_accepts_complete_attestation_for_exact_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            evidence=Path(directory)/'evidence.json'
            evidence.write_text(json.dumps(self.physical_evidence()))
            result=load_device_evidence(evidence,{'version':'4.1.9'},'12345','a'*40,'b'*64)
            self.assertEqual(result['mpp_sha256'],'b'*64)

    def test_physical_gate_rejects_digest_run_or_source_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            evidence=Path(directory)/'evidence.json'
            evidence.write_text(json.dumps(self.physical_evidence()))
            for run, commit, digest in [('999','a'*40,'b'*64), ('12345','c'*40,'b'*64), ('12345','a'*40,'c'*64)]:
                with self.subTest(run=run, commit=commit, digest=digest), self.assertRaisesRegex(ValueError,'does not match'):
                    load_device_evidence(evidence,{'version':'4.1.9'},run,commit,digest)

    def test_physical_gate_rejects_failed_or_incomplete_device_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            evidence=Path(directory)/'evidence.json'
            data=self.physical_evidence(); data['checks']['no_media_border']=False
            evidence.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'required passing check'):
                load_device_evidence(evidence,{'version':'4.1.9'},'12345','a'*40,'b'*64)
            data=self.physical_evidence(); data['scenarios']['swipes']=29
            evidence.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'scenario counts'):
                load_device_evidence(evidence,{'version':'4.1.9'},'12345','a'*40,'b'*64)

    def test_promotion_uses_only_the_mpp_with_the_user_supplied_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); output=root/'output'; output.mkdir()
            evidence=root/'validation-evidence.json'; evidence.write_text(json.dumps(self.physical_evidence()))
            (output/'build-info.json').write_text(json.dumps({
                'source_commit':'a'*40, 'run_url':'https://github.com/example/PatchInsta/actions/runs/12345',
                'mpp_sha256':'b'*64}))
            config={'version':'4.1.9','repository':'example/PatchInsta'}
            with patch('publish.verify_kit', return_value={'PatchInsta-4.1.9.mpp':'b'*64}):
                verified, source = verify_candidate(root,config,'12345','b'*64,evidence)
                self.assertEqual(verified['PatchInsta-4.1.9.mpp'],'b'*64)
                self.assertEqual(source,'a'*40)
                with self.assertRaisesRegex(ValueError,'explicitly approved digest'):
                    verify_candidate(root,config,'12345','c'*64,evidence)

    def test_promotion_is_separate_from_push_candidate_build(self):
        root=Path(__file__).resolve().parents[1]
        build=(root/'.github/workflows/build-fold-reels.yml').read_text()
        promote=(root/'.github/workflows/promote-fold-reels.yml').read_text()
        self.assertIn('Upload candidate kit for device validation',build)
        self.assertNotIn('scripts/publish.py',build)
        self.assertNotIn('release:',build)
        self.assertIn('workflow_dispatch:',promote)
        self.assertIn('EXPECTED_MPP_SHA256',promote)
        self.assertIn('--promote --evidence',promote)

    def test_recovers_only_our_empty_untagged_draft(self):
        draft={'id':1,'tag_name':'untagged-123','draft':True,'assets':[],
               'name':'PatchInsta 4.1.1','author':{'login':'github-actions[bot]'}}
        self.assertEqual(select_release([draft],'v4.1.1','PatchInsta 4.1.1'),draft)
        for changed in ({'draft':False},{'assets':[{'name':'keep.mpp'}]},{'name':'Different release'},{'author':{'login':'owner'}}):
            self.assertIsNone(select_release([{**draft,**changed}],'v4.1.1','PatchInsta 4.1.1'))

    def test_published_assets_cannot_be_replaced_by_upload_helper(self):
        with self.assertRaisesRegex(ValueError,'immutable'):
            upload_assets('repos/owner/repo',{'draft':False},Path('unused'))

    def test_ambiguous_drafts_require_resolution_instead_of_guessing(self):
        draft={'id':1,'tag_name':'untagged-1','draft':True,'assets':[],
               'name':'PatchInsta 4.1.1','author':{'login':'github-actions[bot]'}}
        with self.assertRaisesRegex(ValueError,'Ambiguous'):
            select_release([draft,{**draft,'id':2,'tag_name':'untagged-2'}],'v4.1.1','PatchInsta 4.1.1')

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

