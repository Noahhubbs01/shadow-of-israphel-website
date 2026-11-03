import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image

SITE = Path(__file__).resolve().parents[1]
def module(name):
 spec=importlib.util.spec_from_file_location(name,SITE/'scripts'/f'{name}.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
announce=module('announce');build=module('build')

class AnnouncementTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name);self.root=self.base/'site';self.root.mkdir()
  for folder in ('templates','content'):shutil.copytree(SITE/folder,self.root/folder)
  shutil.copy(SITE/'media.js',self.root/'media.js')
  needed=['assets/media/03-yogcave.webp','assets/media/shadow-of-israphel-trailer.mp4','assets/media/previews/01-mistral-overlook-1280.webp']
  for manifest in (self.root/'content/screenshots').glob('*.json'):
   for shot in json.loads(manifest.read_text()):needed.extend([shot['src'],shot['preview']])
  for name in needed:
   path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.touch()
  self.images=[]
  for n,size in enumerate([(1600,900),(720,1000)]):
   source=self.base/f'capture-{n}.png';Image.new('RGB',size,(50,80,20)).save(source);self.images.append(source)
  self.payload={'update_id':'build-test','date':'2026-11-03','title':'A verified test','summary':'A test fixture only.','body':'A **completed** change.','evidence':['private report path'], 'screenshots':[{'source':str(p),'alt':f'Capture {i}','caption':f'Caption {i}'} for i,p in enumerate(self.images)]}
 def tearDown(self):self.temp.cleanup()
 def test_multiple_images_preserve_originals_and_aspect_ratio(self):
  before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in self.images]
  result=announce.import_update(self.payload,self.root,ready=True)
  self.assertEqual(result['screenshots'],2)
  manifest=json.loads(next((self.root/'content/screenshots').glob('*build-test.json')).read_text())
  for i,shot in enumerate(manifest):
   self.assertEqual(hashlib.sha256((self.root/shot['src']).read_bytes()).hexdigest(),before[i])
   self.assertEqual(hashlib.sha256(self.images[i].read_bytes()).hexdigest(),before[i])
   with Image.open(self.root/shot['preview']) as image:self.assertLessEqual(max(image.size),1280)
  self.assertEqual((manifest[1]['width'],manifest[1]['height']),(720,1000))
  with patch.object(build,'ROOT',self.root):out=build.outputs()
  page=out['blog/2026-11-03-build-test/index.html']
  self.assertEqual(page.count('class="screenshot-link"'),2)
  self.assertIn('Capture 1',page);self.assertIn('Full-size image',page)
  self.assertNotIn('private report path',''.join(out.values()))
 def test_retry_does_not_duplicate_or_replace(self):
  first=announce.import_update(self.payload,self.root,ready=True);text=Path(first['post']).read_text()
  self.payload['body']='Changed retry'
  second=announce.import_update(self.payload,self.root,ready=True)
  self.assertEqual(second['status'],'already_exists');self.assertEqual(Path(first['post']).read_text(),text)
 def test_bad_second_image_leaves_no_new_public_files(self):
  self.payload['screenshots'][1]['source']=str(self.base/'missing.png')
  with self.assertRaises(ValueError):announce.import_update(self.payload,self.root,ready=True)
  self.assertFalse((self.root/'content/posts/2026-11-03-build-test.md').exists())
  self.assertFalse((self.root/'assets/updates/2026-11-03-build-test').exists())
 def test_draft_not_listed_until_explicitly_marked_ready(self):
  result=announce.import_update(self.payload,self.root)
  with patch.object(build,'ROOT',self.root):out=build.outputs()
  self.assertNotIn('blog/2026-11-03-build-test/index.html',out)
  path=Path(result['post']);path.write_text(path.read_text().replace('draft: true\n',''))
  with patch.object(build,'ROOT',self.root):out=build.outputs()
  self.assertIn('blog/2026-11-03-build-test/index.html',out)
 def test_duplicate_ids_across_sessions_rejected_by_build(self):
  result=announce.import_update(self.payload,self.root,ready=True)
  source=Path(result['post']).read_text()
  (self.root/'content/posts/2026-11-03-second-task.md').write_text(source)
  with patch.object(build,'ROOT',self.root),self.assertRaisesRegex(ValueError,'duplicate update_id'):build.read_posts()
 def test_empty_evidence_or_missing_alt_is_rejected(self):
  self.payload['evidence']=[]
  with self.assertRaisesRegex(ValueError,'evidence'):announce.import_update(self.payload,self.root)
  self.payload['evidence']=['report'];self.payload['screenshots'][0]['alt']=''
  with self.assertRaisesRegex(ValueError,'alt'):announce.import_update(self.payload,self.root)
 def test_text_only_update(self):
  self.payload['screenshots']=[]
  result=announce.import_update(self.payload,self.root,ready=True)
  self.assertEqual(result['screenshots'],0)
  self.assertFalse((self.root/'assets/updates/2026-11-03-build-test').exists())

if __name__=='__main__':unittest.main()
