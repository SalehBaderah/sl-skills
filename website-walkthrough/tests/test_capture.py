import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

import cv2

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args): pass


@unittest.skipUnless(os.environ.get("RUN_BROWSER_TESTS") == "1", "Set RUN_BROWSER_TESTS=1 with browser dependencies installed")
class CaptureTests(unittest.TestCase):
    def test_capture_visible_actions_metadata_and_final_render(self):
        with tempfile.TemporaryDirectory() as folder:
            work = Path(folder)
            (work/"index.html").write_text('''<!doctype html><html><head><style>
body{margin:0;height:1000px;background:#f5f5f5;font:20px sans-serif}nav{padding:20px;display:flex;gap:20px}
button{font:20px sans-serif;padding:10px}#panel{position:absolute;left:20px;top:110px;width:400px;height:150px;background:#cc3355;color:white}
</style></head><body><nav>
<button onclick="document.querySelector('#panel').hidden=false">Menu</button>
<button onclick="document.body.style.background='#223344'">Theme</button>
</nav><div id="panel" hidden>Features</div>
<div style="position:absolute;top:650px;left:20px;width:400px;height:100px;background:#3366dd">More features</div>
<a href="project.html" style="position:absolute;top:760px;left:20px">Open featured project</a>
<footer id="contact" style="position:absolute;top:800px;left:20px;width:400px;height:180px;background:#d9b354">
<h2>Demo Studio</h2><p>Let's get in touch</p><a href="mailto:demo@example.com">Email</a></footer>
</body></html>''')
            (work/"project.html").write_text('''<!doctype html><html><body style="margin:0;background:#22aa66;font:20px sans-serif">
<a href="index.html#contact">Back to contact</a><h1>Featured project</h1>
<section style="height:200px"><h2>Observed result</h2><p>A complete project outcome.</p></section>
</body></html>''')
            server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=folder))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                script = work/"capture.json"
                script.write_text(json.dumps({"url": f"http://127.0.0.1:{server.server_port}", "viewport": {"width": 480, "height": 320},
                    "steps": [{"action": "click", "target": {"role": "button", "name": "Menu"}, "sound": "open"},
                              {"action": "click", "target": {"role": "button", "name": "Theme"}, "sound": "toggle"},
                              {"action": "scroll", "dy": 500, "duration": 1.2, "pause": .5},
                              {"action": "wait", "seconds": 4},
                              {"action": "click", "target": {"role": "link", "name": "Open featured project"}, "sound": "open"},
                              {"action": "click", "target": {"role": "link", "name": "Back to contact"}}]}))
                capture = work/"capture"
                command = [sys.executable, str(ROOT/"scripts/record_walkthrough.py"), "--script", str(script), "--output-dir", str(capture)]
                if os.environ.get("TEST_CHROMIUM_EXECUTABLE"):
                    command += ["--browser-path", os.environ["TEST_CHROMIUM_EXECUTABLE"]]
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                plan = json.loads((capture/"plan.json").read_text())
                self.assertEqual(len(plan["events"]), 4)
                self.assertEqual([e["sound"] for e in plan["events"]], ["open", "toggle", "open", "click"])
                self.assertGreater(len(plan["cursor"]), 10)
                source = capture/"source.mkv"
                info = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(source)]))
                self.assertEqual(info["streams"][0]["codec_name"], "ffv1")
                cap = cv2.VideoCapture(str(source))
                try:
                    cap.set(cv2.CAP_PROP_POS_MSEC, 200)
                    ok, before = cap.read()
                    self.assertTrue(ok)
                    self.assertGreater(min(before[200, 100]), 230)  # empty light page
                    cap.set(cv2.CAP_PROP_POS_MSEC, (plan["events"][0]["time"]+.35)*1000)
                    ok, after = cap.read()
                    self.assertTrue(ok)
                    self.assertGreater(int(after[200, 100, 2]), 180)  # real red panel
                    self.assertLess(int(after[200, 100, 1]), 90)
                    cap.set(cv2.CAP_PROP_POS_MSEC, (plan["events"][1]["time"]+.35)*1000)
                    ok, dark = cap.read()
                    self.assertTrue(ok)
                    self.assertLess(max(dark[300, 450]), 100)  # real theme change
                    cap.set(cv2.CAP_PROP_POS_MSEC, (plan["events"][2]["time"]-3)*1000)
                    ok, scrolled = cap.read()
                    self.assertTrue(ok)
                    self.assertGreater(int(scrolled[200, 100, 0]), 180)  # blue content revealed by scrolling
                    self.assertLess(int(scrolled[200, 100, 2]), 90)
                    cap.set(cv2.CAP_PROP_POS_MSEC, (plan["events"][2]["time"]+.35)*1000)
                    ok, detail = cap.read()
                    self.assertTrue(ok)
                    self.assertGreater(int(detail[250, 100, 1]), 140)  # real navigation to the green project page
                    self.assertLess(int(detail[250, 100, 2]), 70)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_FRAME_COUNT)-10)
                    ok, closing = cap.read()
                    self.assertTrue(ok)
                    self.assertGreater(int(closing[280, 100, 2]), 180)  # gold contact section is the closing composition
                    self.assertGreater(int(closing[280, 100, 1]), 140)
                    self.assertLess(int(closing[280, 100, 0]), 130)
                finally: cap.release()
                output = work/"final.mp4"
                subprocess.run([sys.executable, str(ROOT/"scripts/render_walkthrough.py"), str(source), "--plan", str(capture/"plan.json"), "--output", str(output)], check=True, capture_output=True)
                subprocess.run(["ffmpeg", "-v", "error", "-i", str(output), "-f", "null", "-"], check=True, capture_output=True)
                self.assertGreater(output.stat().st_size, 5000)
                # Existing output directories are protected, never overwritten.
                second = subprocess.run(command, capture_output=True)
                self.assertNotEqual(second.returncode, 0)
            finally:
                server.shutdown()
                server.server_close()
                thread.join()


if __name__ == "__main__": unittest.main()
