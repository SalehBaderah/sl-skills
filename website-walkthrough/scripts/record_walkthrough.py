#!/usr/bin/env python3
"""Record an authorized, single-tab browser walkthrough and a matching edit plan."""
import argparse
import asyncio
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

import cv2
from playwright.async_api import async_playwright

from sound_effects import EFFECTS

# A temporary, two-color slate lets us trim browser startup and align event times
# to the saved video. It never appears in the trimmed source or final export.
MARKER = """() => {
  const el = document.createElement('div'); el.id = '__walkthrough_sync';
  el.style.cssText = 'position:fixed;inset:0;z-index:2147483647;pointer-events:none;background:linear-gradient(to right,#e71df2 50%,#17e6bc 50%)';
  document.documentElement.append(el);
}"""
REMOVE_MARKER = """() => {
  document.getElementById('__walkthrough_sync').remove();
  return performance.timeOrigin + performance.now();
}"""
TRACK = """(() => {
  const send = (kind, e) => {
    if (!e.isTrusted) return;
    window.__walkthroughEvent({kind, time: performance.timeOrigin + performance.now(),
      x: e.clientX / innerWidth, y: e.clientY / innerHeight}).catch(() => {});
  };
  addEventListener('pointermove', e => send('move', e), true);
  addEventListener('pointerdown', e => send('down', e), true);
})();"""


def finite(value, low, high, label):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"{label} must be a number in {low}..{high}")
    return value


def web_url(value):
    url = urlsplit(value)
    if url.scheme not in ("http", "https") or not url.hostname or url.username or url.password:
        raise ValueError("Use an http(s) URL without embedded credentials")
    return value


def locator(page, target):
    if not isinstance(target, dict):
        raise ValueError("A target must specify role/name, text, test_id, or css")
    kinds = [k for k in ("role", "text", "test_id", "css") if k in target]
    if len(kinds) != 1:
        raise ValueError("Specify exactly one target selector kind")
    kind = kinds[0]
    if kind == "role":
        if "name" not in target:
            raise ValueError("A role target needs an exact accessible name")
        return page.get_by_role(target["role"], name=target["name"], exact=True)
    if kind == "text": return page.get_by_text(target["text"], exact=True)
    if kind == "test_id": return page.get_by_test_id(target["test_id"])
    return page.locator(target["css"])


async def move_pointer(page, x, y, current):
    old_x, old_y = current
    for i in range(1, 19):
        f = i / 18
        eased = f*f*(3-2*f)
        await page.mouse.move(old_x+(x-old_x)*eased, old_y+(y-old_y)*eased)
        await asyncio.sleep(.025)
    return x, y


async def run_actions(page, config, state):
    size = config.get("viewport", {"width": 1440, "height": 900})
    current = (size["width"]*.5, size["height"]*.5)
    for step in config["steps"]:
        action = step["action"]
        state["sound"] = step.get("sound", "click")
        if action in ("click", "tap", "hover", "fill", "press", "wait_for"):
            target = locator(page, step["target"])
            await target.wait_for(state="visible")
            if await target.count() != 1:
                raise ValueError("Target is ambiguous; inspect the page and refine the selector")
            if action == "wait_for": continue
            await target.scroll_into_view_if_needed()
            box = await target.bounding_box()
            if not box: raise RuntimeError("Target has no visible bounds")
            current = await move_pointer(page, box["x"]+box["width"]/2, box["y"]+box["height"]/2, current)
            if action == "click": await target.click()
            elif action == "tap": await target.tap()
            elif action == "hover": await target.hover()
            elif action == "press": await target.press(step["key"])
            else:
                if "value_env" in step:
                    value = os.environ.get(step["value_env"])
                    if value is None: raise ValueError("A required fill environment variable is unset")
                else: value = step["value"]
                await target.fill(value)
        elif action == "scroll":
            duration = step.get("duration", 1.6)
            ticks = max(16, round(duration*30))
            previous = 0
            for i in range(1, ticks+1):
                t = i/ticks
                eased = t*t*(3-2*t)
                delta = eased-previous
                await page.mouse.wheel(step.get("dx", 0)*delta, step.get("dy", 500)*delta)
                previous = eased
                await asyncio.sleep(duration/ticks)
        elif action == "goto":
            await page.goto(step["url"], wait_until="domcontentloaded")
        elif action == "wait":
            await asyncio.sleep(step.get("seconds", 1))
            continue
        await asyncio.sleep(step.get("pause", 2.5))


def trim_start(raw):
    """Find the first non-slate frame after a stable sync slate (VP8 tolerant)."""
    cap = cv2.VideoCapture(str(raw))
    fps = cap.get(cv2.CAP_PROP_FPS)
    index, stable = 0, 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok: break
            h, w = frame.shape[:2]
            expected = ((242, 29, 231), (188, 230, 23))  # BGR
            marker = all(
                max(abs(int(a)-b) for a, b in zip(frame[int(h*y), int(w*x)], color)) < 40
                for x, color in ((.25, expected[0]), (.75, expected[1])) for y in (.25, .75)
            )
            if marker: stable += 1
            elif stable >= 3:
                if not 1 <= fps <= 120: raise RuntimeError("Unexpected recording frame rate")
                return index/fps, fps
            else: stable = 0
            index += 1
    finally: cap.release()
    raise RuntimeError("Cannot locate the sync slate; do not use unaligned interaction data")


def validate(config):
    if not isinstance(config, dict): raise ValueError("Capture script must be an object")
    web_url(config.get("url", ""))
    viewport = config.get("viewport", {"width": 1440, "height": 900})
    for key in ("width", "height"):
        value = viewport[key]
        if type(value) is not int or not 240 <= value <= 3840 or value % 2:
            raise ValueError("Viewport dimensions must be even integers in 240..3840")
    if not isinstance(config.get("steps"), list): raise ValueError("steps must be a list")
    finite(config.get("settle", 1), 0, 60, "settle")
    finite(config.get("initial_hold", 2.5), 0, 60, "initial_hold")
    finite(config.get("end_hold", 3), 0, 60, "end_hold")
    for step in config["steps"]:
        if not isinstance(step, dict) or step.get("action") not in {"click", "tap", "hover", "fill", "press", "wait_for", "scroll", "wait", "goto"}:
            raise ValueError("Unsupported capture action")
        if step.get("sound", "click") not in EFFECTS | {"none"}: raise ValueError("Unsupported step sound")
        finite(step.get("pause", 2.5), 0, 60, "pause")
        if step["action"] == "wait": finite(step.get("seconds", 1), 0, 60, "wait seconds")
        if step["action"] == "scroll":
            finite(step.get("duration", 1.6), .2, 30, "scroll duration")
            finite(step.get("dx", 0), -10000, 10000, "scroll dx")
            finite(step.get("dy", 500), -10000, 10000, "scroll dy")
        if step["action"] == "goto": web_url(step["url"])
        if step["action"] == "fill":
            if ("value" in step) == ("value_env" in step): raise ValueError("fill needs either value or value_env")
            if "value_env" in step and not os.environ.get(step["value_env"]):
                raise ValueError("A required fill environment variable is unset")


async def record(args, config):
    args.output_dir.mkdir(parents=True, exist_ok=False)
    raw_dir = args.output_dir/"raw"
    size = config.get("viewport", {"width": 1440, "height": 900})
    events, cursor = [], []
    state = {"origin": None, "sound": "click"}

    def receive(source, data):
        if state["origin"] is None or source["frame"] != source["page"].main_frame: return
        t = (data["time"]-state["origin"])/1000
        if t < 0: return
        x, y = (min(1, max(0, float(data[k]))) for k in ("x", "y"))
        if not cursor or t > cursor[-1][0]: cursor.append([t, x, y])
        if data["kind"] == "down":
            events.append({"time": t, "x": x, "y": y, "zoom": 1.4, "sound": state["sound"]})

    async with async_playwright() as pw:
        options = {"headless": not args.headed}
        if args.browser_path: options["executable_path"] = str(args.browser_path)
        browser = await pw.chromium.launch(**options)
        context = None
        try:
            context = await browser.new_context(
                viewport=size, record_video_dir=str(raw_dir), record_video_size=size,
                device_scale_factor=1, has_touch=any(s["action"] == "tap" for s in config["steps"]),
                storage_state=str(args.storage_state) if args.storage_state else None,
            )
            await context.expose_binding("__walkthroughEvent", receive)
            await context.add_init_script(TRACK)
            page = await context.new_page()
            page.set_default_timeout(15000)
            await page.goto(config["url"], wait_until="domcontentloaded")
            await asyncio.sleep(config.get("settle", 1))
            await page.evaluate(MARKER)
            await asyncio.sleep(.6)
            state["origin"] = await page.evaluate(REMOVE_MARKER)
            cursor.append([0, .5, .5])
            await asyncio.sleep(config.get("initial_hold", 2.5))
            await run_actions(page, config, state)
            await asyncio.sleep(config.get("end_hold", 3))
            video = page.video
            await context.close()
            context = None
            raw = await video.path()
        finally:
            if context: await context.close()
            await browser.close()

    cut, fps = trim_start(raw)
    # Keep the preparation step lossless. The final renderer performs the H.264
    # delivery encode; another H.264 generation here would soften text twice.
    recording = args.output_dir/"source.mkv"
    subprocess.run(["ffmpeg", "-v", "error", "-n", "-ss", str(cut), "-i", str(raw),
                    "-an", "-c:v", "ffv1", "-level", "3", str(recording)], check=True)
    info = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_format", "-of", "json", str(recording)]))
    duration = float(info["format"]["duration"])
    plan = {"frame": True, "audio": "preserve", "crf": 14, "click_highlights": True,
            "camera": [[0, 1, .5, .5], [duration, 1, .5, .5]],
            "sound_effects": {"enabled": True, "volume": .35},
            "source_cursor_visible": bool(config.get("site_draws_cursor", False)),
            "events": [e for e in events if e["time"] <= duration]}
    if not plan["source_cursor_visible"]:
        plan["cursor"] = [p for p in cursor if p[0] <= duration]
    (args.output_dir/"plan.json").write_text(json.dumps(plan, indent=2)+"\n")
    (args.output_dir/"capture-info.json").write_text(json.dumps({
        "duration": duration, "fps": fps, "trim_seconds": cut,
        "pointer_events": len(events), "audio": "not captured",
        "timing": "Browser event timestamps aligned by a visual slate; verify against saved frames. Expect a few frames of capture latency.",
    }, indent=2)+"\n")
    print(f"Recorded {recording}; review plan.json and render the final edit. Browser audio was not captured.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--script", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path, help="New directory; never overwritten")
    ap.add_argument("--browser-path", type=Path, help="Optional installed Chromium executable")
    ap.add_argument("--storage-state", type=Path, help="Sensitive, authorized Playwright session state; never package it")
    ap.add_argument("--headed", action="store_true")
    args = ap.parse_args()
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool): raise RuntimeError(f"{tool} must be on PATH")
    config = json.loads(args.script.read_text())
    validate(config)
    asyncio.run(record(args, config))


if __name__ == "__main__":
    try: main()
    except Exception as exc:
        # Browser/locator errors can include input values or URL query strings.
        # Avoid echoing those into chat/logs; inspect the local script and page.
        print(f"Capture failed ({type(exc).__name__}). Check browser setup, script selectors, and access. Partial files are not a completed walkthrough.", file=sys.stderr)
        sys.exit(1)
