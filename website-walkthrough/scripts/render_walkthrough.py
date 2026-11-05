#!/usr/bin/env python3
"""Render camera moves from a recording-specific JSON plan; requires FFmpeg and requirements.txt."""
import argparse, json, math, subprocess, sys, tempfile
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from sound_effects import cues, write_effects


def probe(path):
    data = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))
    v = next(s for s in data['streams'] if s['codec_type'] == 'video')
    if any(abs(float(d.get('rotation',0))) > .01 for d in v.get('side_data_list',[])) or abs(float(v.get('tags',{}).get('rotate',0))) > .01:
        raise ValueError('Normalize source rotation before rendering')
    if v.get('color_transfer') in ('smpte2084','arib-std-b67'):
        raise ValueError('Tone-map HDR source to SDR before rendering')
    rate = v.get('r_frame_rate', '30/1')
    n, d = map(float, rate.split('/')); fps = n / d if d else 30
    if not 1 <= fps <= 120: fps = 30
    return int(v['width']), int(v['height']), fps, float(data['format']['duration']), any(s['codec_type'] == 'audio' for s in data['streams'])


def smooth(x):
    x = np.clip(x, 0, 1)
    return x*x*x*(x*(x*6-15)+10)


def interpolate(keys, t):
    if t <= keys[0][0]: return np.array(keys[0][1:], float)
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            f = smooth((t-a[0])/(b[0]-a[0]))
            return np.array(a[1:])*(1-f)+np.array(b[1:])*f
    return np.array(keys[-1][1:], float)


def validate(plan, duration):
    if not isinstance(plan, dict): raise ValueError('Plan must be an object')
    if plan.get('audio', 'preserve') not in ('preserve', 'mute'): raise ValueError('audio must be preserve or mute')
    if not isinstance(plan.get('events', []), list): raise ValueError('events must be a list')
    for group, length in [('camera', 4), ('cursor', 3)]:
        keys = plan.get(group, [])
        previous = -1
        for row in keys:
            if len(row) != length or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in row):
                raise ValueError(f'{group}: invalid keyframe')
            if not 0 <= row[0] <= duration+.1 or row[0] <= previous: raise ValueError(f'{group}: times must increase within the recording')
            previous = row[0]
            coords = row[2:] if group == 'camera' else row[1:]
            if not all(0 <= x <= 1 for x in coords): raise ValueError(f'{group}: coordinates must be normalized 0..1')
            if group == 'camera' and not 1 <= row[1] <= 3: raise ValueError('Zoom must be between 1 and 3')
    for e in plan.get('events', []):
        if not isinstance(e, dict): raise ValueError('Invalid event')
        if not all(isinstance(e.get(k), (int, float)) and math.isfinite(e[k]) for k in ['time', 'x', 'y']): raise ValueError('Invalid event')
        if not 0 <= e['time'] <= duration or not all(0 <= e[k] <= 1 for k in ['x', 'y']): raise ValueError('Event outside source bounds')
        if not 1 <= e.get('zoom', 1.5) <= 3: raise ValueError('Invalid event zoom')
    if plan.get('cursor') and plan.get('source_cursor_visible', True):
        raise ValueError('Cursor overlay requires source_cursor_visible=false after verified cursor removal or a cursor-free source')
    cues(plan, duration)


def camera(plan, t):
    if plan.get('camera'): return interpolate(plan['camera'], t)
    weights, centers, zooms = [], [], []
    for e in plan.get('events', []):
        age = t-e['time']
        weight = float(smooth((age+.55)/.55)) * (1-float(smooth((age-.60)/.80)))
        if weight > 0:
            weights.append(weight); centers.append([e['x'], e['y']]); zooms.append(e.get('zoom', 1.5))
    total = sum(weights)
    if not total: return np.array([1, .5, .5])
    strength = min(1, total)
    center = np.average(centers, axis=0, weights=weights)*strength + np.array([.5, .5])*(1-strength)
    zoom = 1 + (np.average(zooms, weights=weights)-1)*strength
    return np.array([zoom, *center])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path); ap.add_argument('--plan', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True); ap.add_argument('--fps', type=float)
    ap.add_argument('--preview-times', nargs='+', type=float, help='Save stills only, to --output directory')
    args = ap.parse_args(); plan = json.loads(args.plan.read_text())
    if args.input.resolve() == args.output.resolve(): raise ValueError('Never overwrite the input')
    if not args.preview_times and args.output.exists(): raise ValueError('Output exists; choose a new filename')
    w, h, source_fps, duration, has_audio = probe(args.input); validate(plan, duration)
    fps = args.fps or source_fps
    if not 1 <= fps <= 120: raise ValueError('FPS must be 1..120')
    ow, oh = w-w%2, h-h%2
    framed = plan.get('frame', True); margin = .035 if framed else 0
    sw, sh = int(ow*(1-2*margin)), int(oh*(1-2*margin)); sx, sy = (ow-sw)//2, (oh-sh)//2
    cv2.setNumThreads(2)
    yy, xx = np.mgrid[0:oh, 0:ow]
    glow = np.exp(-(((xx/ow-.15)/.7)**2+((yy/oh-.1)/.9)**2)*2)
    rgb = np.array([19, 22, 32]) + glow[..., None]*np.array([29, 23, 40])
    back = Image.fromarray(rgb.astype(np.uint8)).convert('RGBA')
    radius = max(2, int(min(sw, sh)*.022)) if framed else 0
    if framed:
        shadow = Image.new('RGBA', back.size)
        ImageDraw.Draw(shadow).rounded_rectangle((sx, sy+8, sx+sw, sy+sh+8), radius=radius, fill=(0,0,0,145))
        back = Image.alpha_composite(back, shadow.filter(ImageFilter.GaussianBlur(max(2, ow*.012))))
    background = np.array(back.convert('RGB'))[:, :, ::-1].copy()
    mask = Image.new('L', (sw, sh)); ImageDraw.Draw(mask).rounded_rectangle((0,0,sw-1,sh-1), radius=radius, fill=255)
    alpha = np.array(mask, dtype=np.float32)[..., None]/255
    corners = [(0,0), (sw-radius,0), (0,sh-radius), (sw-radius,sh-radius)]

    def compose(frame, t):
        z, x, y = camera(plan,t); vw, vh = w/z, h/z
        left = float(np.clip(x*w-vw/2,0,w-vw)); top = float(np.clip(y*h-vh/2,0,h-vh))
        ax, ay = sw/vw, sh/vh
        m = np.array([[ax,0,-left*ax],[0,ay,-top*ay]],np.float32)
        screen = cv2.warpAffine(frame,m,(sw,sh),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_REPLICATE)
        if plan.get('click_highlights', True):
            for e in plan.get('events', []):
                if not e.get('highlight', True): continue
                age = t-e['time']
                if 0 <= age < .45:
                    pos = (int((e['x']*w-left)*ax),int((e['y']*h-top)*ay))
                    overlay = screen.copy(); r = max(4,int((8+24*smooth(age/.45))*ow/1920))
                    cv2.circle(overlay,pos,r,(255,222,180),max(1,ow//960),cv2.LINE_AA)
                    a = .65*(1-age/.45)**1.5; screen = cv2.addWeighted(overlay,a,screen,1-a,0)
        if plan.get('cursor'):
            x,y = interpolate(plan['cursor'],t); px,py = (x*w-left)*ax,(y*h-top)*ay
            scale = max(.6,ow/1920)
            points = np.array([[0,0],[0,29],[8,22],[14,35],[20,32],[14,19],[25,19]],float)*scale+[px,py]
            points = points.astype(np.int32)
            cv2.fillPoly(screen,[points],(255,255,255),cv2.LINE_AA);cv2.polylines(screen,[points],True,(25,23,20),max(1,int(2*scale)),cv2.LINE_AA)
        out = background.copy(); region = out[sy:sy+sh,sx:sx+sw]; region[:] = screen
        if framed:
            for cx,cy in corners:
                a = alpha[cy:cy+radius,cx:cx+radius]
                region[cy:cy+radius,cx:cx+radius] = (screen[cy:cy+radius,cx:cx+radius]*a + background[sy+cy:sy+cy+radius,sx+cx:sx+cx+radius]*(1-a)).astype(np.uint8)
        return out

    if args.preview_times:
        args.output.mkdir(parents=True,exist_ok=True); cap=cv2.VideoCapture(str(args.input))
        try:
            for t in args.preview_times:
                if not 0 <= t < duration: raise ValueError('Preview timestamp outside source')
                cap.set(cv2.CAP_PROP_POS_MSEC,t*1000); ok,frame=cap.read()
                if not ok: raise RuntimeError(f'Cannot read preview at {t}')
                if not cv2.imwrite(str(args.output/f'{t:09.3f}.png'),compose(frame,t)): raise RuntimeError('Cannot save preview')
        finally: cap.release()
        return
    args.output.parent.mkdir(parents=True,exist_ok=True)
    crf=plan.get('crf',16)
    if not isinstance(crf,int) or not 0 <= crf <= 28: raise ValueError('CRF must be integer 0..28')
    audio=plan.get('audio','preserve')
    if audio not in ('preserve','mute'): raise ValueError('audio must be preserve or mute')
    sound_cues = cues(plan, duration)
    temp = tempfile.TemporaryDirectory(prefix='walkthrough-audio-')
    effects_path = Path(temp.name)/'effects.wav'
    if sound_cues: write_effects(effects_path, sound_cues, duration)
    dec=subprocess.Popen(['ffmpeg','-v','error','-noautorotate','-i',str(args.input),'-vf',f'fps={fps:.8f}','-f','rawvideo','-pix_fmt','bgr24','-'],stdout=subprocess.PIPE)
    command=['ffmpeg','-hide_banner','-loglevel','warning','-n','-f','rawvideo','-pix_fmt','bgr24','-s',f'{ow}x{oh}','-r',f'{fps:.8f}','-i','-','-i',str(args.input)]
    if sound_cues:
        command += ['-i',str(effects_path),'-map','0:v:0']
        if has_audio and audio == 'preserve':
            # Keep original speech; only limit peaks where the mix could clip.
            command += ['-filter_complex','[1:a:0]aresample=48000,asetpts=PTS-STARTPTS[original];[original][2:a:0]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95:level=false:latency=true[mix]','-map','[mix]']
        else: command += ['-map','2:a:0']
        command += ['-c:a','aac','-b:a','192k']
    elif audio == 'preserve': command += ['-map','0:v:0','-map','1:a:0?','-c:a','aac','-b:a','192k']
    else: command += ['-map','0:v:0','-an']
    command+=['-c:v','libx264','-preset','slow','-crf',str(crf),'-pix_fmt','yuv420p','-movflags','+faststart','-map_metadata','-1','-t',str(duration),str(args.output)]
    enc=None; success=False
    try:
        enc=subprocess.Popen(command,stdin=subprocess.PIPE);i=0
        while True:
            raw=dec.stdout.read(w*h*3)
            if not raw: break
            if len(raw)!=w*h*3: raise RuntimeError('Truncated decoder frame')
            frame=np.frombuffer(raw,np.uint8).reshape(h,w,3)
            enc.stdin.write(compose(frame,i/fps).tobytes());i+=1
            if i%120==0: print(f'{i} frames rendered',flush=True)
        enc.stdin.close()
        if enc.wait()!=0 or dec.wait()!=0 or i==0: raise RuntimeError('FFmpeg failed')
        success=True; print(f'Saved {args.output} ({i} frames)',flush=True)
    finally:
        for proc in (dec,enc):
            if proc and proc.poll() is None:
                proc.terminate()
                try: proc.wait(timeout=5)
                except subprocess.TimeoutExpired: proc.kill();proc.wait()
        temp.cleanup()
        if not success: print('Render incomplete. Do not deliver the partial output.',file=sys.stderr)

if __name__=='__main__':
    try: main()
    except (ValueError, RuntimeError, subprocess.CalledProcessError) as e:
        print(str(e),file=sys.stderr);sys.exit(1)
