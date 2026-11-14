import importlib.util
from pathlib import Path
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch

SITE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('site_build', SITE/'scripts/build.py')
build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build)

class AuthoringTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  for folder in ['templates','content']:
   shutil.copytree(SITE/folder,self.root/folder)
  shutil.copy(SITE/'media.js',self.root/'media.js')
  (self.root/'assets/media').mkdir(parents=True)
  for name in ['07-mistral-market.webp','03-yogcave.webp']:
   (self.root/'assets/media'/name).touch()
  (self.root/'assets/media/shadow-of-israphel-trailer.mp4').touch()
  (self.root/'assets/media/previews').mkdir()
  (self.root/'assets/media/previews/01-mistral-overlook-1280.webp').touch()
  for manifest in (self.root/'content/screenshots').glob('*.json'):
   for shot in json.loads(manifest.read_text()):
    for key in ('src','preview'):
     (self.root/shot[key]).parent.mkdir(parents=True,exist_ok=True)
     (self.root/shot[key]).touch()
  self.mock=patch.object(build,'ROOT',self.root);self.mock.start()
 def tearDown(self):
  self.mock.stop();self.temp.cleanup()
 def post(self,text):
  (self.root/'content/posts/2026-11-04-a-new-update.md').write_text(text)
 def test_drafts_are_not_exposed(self):
  published_count=len(build.read_posts())
  self.post('---\ntitle: Secret draft\ndate: 2026-11-04\nsummary: Not ready\ndraft: true\n---\nPrivate draft body')
  self.assertEqual(len(build.read_posts()),published_count)
  self.assertNotIn('Private draft body',''.join(build.outputs().values()))
 def test_sixth_post_creates_pagination_and_feed(self):
  self.post('---\ntitle: A new update\ndate: 2026-11-04\nsummary: New work\n---\nA **real** update.')
  out=build.outputs()
  self.assertIn('blog/page/2/index.html',out)
  self.assertIn('/blog/page/2/',out['blog/index.html'])
  self.assertIn('A <strong>real</strong> update.',out['blog/2026-11-04-a-new-update/index.html'])
  self.assertIn('/blog/2026-11-04-a-new-update/',out['feed.xml'])
  self.assertIn('/blog/2026-11-04-a-new-update/',out['sitemap.xml'])
 def test_post_can_pin_its_original_video(self):
  (self.root/'assets/media/new.mp4').touch()
  self.post('---\ntitle: Update\ndate: 2026-11-04\nsummary: Work\nvideo: true\nvideo_src: assets/media/new.mp4\nvideo_url: https://youtu.be/example\n---\nContent')
  out=build.outputs()
  self.assertIn('/assets/media/new.mp4',out['blog/2026-11-04-a-new-update/index.html'])
  self.assertIn('/assets/media/shadow-of-israphel-trailer.mp4',out['blog/2026-11-01-first-gameplay-trailer/index.html'])
 def test_missing_summary_is_rejected(self):
  self.post('---\ntitle: Update\ndate: 2026-11-04\n---\nContent')
  with self.assertRaisesRegex(ValueError,'missing summary'):build.read_posts()
 def test_direct_playthrough_is_above_original_trailer_with_youtube_link(self):
  out=build.outputs()
  home=out['index.html']
  self.assertEqual(home.count('<video '),2)
  self.assertNotIn('<iframe',home)
  self.assertLess(home.index('shadow-of-israphel-playthrough-1080p60.mp4'),home.index('/assets/media/shadow-of-israphel-trailer.mp4'))
  self.assertIn('https://youtu.be/x04XBUYBdSk',home)
  self.assertIn('Watch on YouTube',home)
 def test_direct_https_video_preserves_source_and_accessible_name(self):
  url='https://example.com/playthrough.mp4'
  self.post('---\ntitle: New showcase\ndate: 2026-11-04\nsummary: Work\nvideo: true\nvideo_src: '+url+'\nvideo_title: No-commentary playthrough\n---\nContent')
  post=build.outputs()['blog/2026-11-04-a-new-update/index.html']
  self.assertIn('src="'+url+'"',post)
  self.assertIn('aria-label="No-commentary playthrough"',post)
  self.assertIn('preload="none"',post)
  self.assertNotIn('autoplay',post)
 def test_insecure_remote_video_is_rejected(self):
  self.post('---\ntitle: Bad video\ndate: 2026-11-04\nsummary: Work\nvideo: true\nvideo_src: http://example.com/video.mp4\n---\nContent')
  with self.assertRaisesRegex(ValueError,'video_src'):build.read_posts()
 def test_youtube_showcase_does_not_replace_historical_trailer(self):
  self.post('---\ntitle: New showcase\ndate: 2026-11-04\nsummary: No commentary\nyoutube_id: AbCdEf123_-\nvideo_caption: 18 minutes\n---\nContent')
  out=build.outputs()
  post=out['blog/2026-11-04-a-new-update/index.html']
  self.assertIn('https://www.youtube-nocookie.com/embed/AbCdEf123_-?rel=0',post)
  self.assertNotIn('autoplay=1',post)
  self.assertNotIn('<video ',post)
  self.assertIn('/assets/media/shadow-of-israphel-trailer.mp4',out['blog/2026-11-01-first-gameplay-trailer/index.html'])
 def test_invalid_youtube_id_is_rejected(self):
  self.post('---\ntitle: Bad embed\ndate: 2026-11-04\nsummary: Work\nyoutube_id: https://example.com/video\n---\nContent')
  with self.assertRaisesRegex(ValueError,'youtube_id'):build.read_posts()
 def test_image_requires_caption_and_alt(self):
  self.post('---\ntitle: Update\ndate: 2026-11-04\nsummary: Work\nimage: assets/media/03-yogcave.webp\n---\nContent')
  with self.assertRaisesRegex(ValueError,'image needs'):build.read_posts()
 def test_invalid_retrospective_date_is_rejected(self):
  self.post('---\ntitle: Update\ndate: 2026-11-04\nwritten: 2026-11-03\nsummary: Work\n---\nContent')
  with self.assertRaisesRegex(ValueError,'cannot precede'):build.read_posts()
 def test_retrospective_uses_writing_date_for_metadata(self):
  out=build.outputs()['blog/2026-10-26-research-archive/index.html']
  self.assertIn('"datePublished": "2026-11-03"',out)
  self.assertIn('Looking back at work recorded on 26 October 2026',out)
 def test_same_day_updates_follow_creation_time_across_timezones(self):
  # Keep both fixtures on the homepage regardless of future published posts.
  for post in (self.root/'content/posts').glob('*.md'):
   post.unlink()
  self.post('---\ntitle: Earlier\ndate: 2026-11-04\ncreated_at: 2026-11-04T10:00:00-06:00\nsummary: Work\n---\nEarlier update')
  (self.root/'content/posts/2026-11-04-a-later-update.md').write_text('---\ntitle: Later\ndate: 2026-11-04\ncreated_at: 2026-11-04T17:00:00+00:00\nsummary: Work\n---\nLater update')
  self.assertEqual([p['title'] for p in build.read_posts() if p['date']=='2026-11-04'],['Later','Earlier'])
  out=build.outputs()
  for name in ['index.html','blog/index.html','feed.xml']:
   self.assertLess(out[name].index('Later'),out[name].index('Earlier'))

if __name__=='__main__':unittest.main()
