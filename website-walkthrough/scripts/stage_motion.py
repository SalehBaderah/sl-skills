"""Aspect-correct viewport layout and restrained motion of a video plane."""
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def _number(value, low, high, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'{label} must be a finite number in {low}..{high}')
    return value


def validate_composition(plan, duration):
    crop = plan.get('crop', [0, 0, 1, 1])
    if not isinstance(crop, list) or len(crop) != 4:
        raise ValueError('crop must be [left, top, right, bottom]')
    for value in crop: _number(value, 0, 1, 'crop bound')
    if crop[0] >= crop[2] or crop[1] >= crop[3]:
        raise ValueError('crop must have positive width and height')
    canvas = plan.get('canvas')
    if 'canvas' in plan and (not isinstance(canvas, list) or len(canvas) != 2 or any(type(n) is not int or n < 2 or n > 7680 or n % 2 for n in canvas)):
        raise ValueError('canvas must contain two even integers in 2..7680')
    config = plan.get('motion', {})
    if not isinstance(config, dict) or not isinstance(config.get('enabled', False), bool):
        raise ValueError('motion must be an object with a boolean enabled field')
    if config.get('enabled', False) and not plan.get('frame', True):
        raise ValueError('motion requires frame=true for room around the viewport')
    keys = config.get('keyframes', [])
    if not isinstance(keys, list): raise ValueError('motion.keyframes must be a list')
    previous = -1
    for row in keys:
        if not isinstance(row, list) or len(row) != 6:
            raise ValueError('motion keyframe must be [time, dx, dy, pitch, yaw, roll]')
        for value, low, high, label in zip(row, [0, -.02, -.02, -3, -3, -1], [duration, .02, .02, 3, 3, 1], ['time', 'dx', 'dy', 'pitch', 'yaw', 'roll']):
            _number(value, low, high, 'motion '+label)
        if row[0] <= previous: raise ValueError('motion keyframe times must strictly increase')
        previous = row[0]
    intervals = config.get('settle', [])
    if not isinstance(intervals, list): raise ValueError('motion.settle must be a list')
    for interval in intervals:
        if not isinstance(interval, list) or len(interval) != 2:
            raise ValueError('motion settle interval must be [start, end]')
        a, b = interval
        _number(a, 0, duration, 'settle start'); _number(b, 0, duration, 'settle end')
        if a > b: raise ValueError('settle start must be before its end')


def layout(plan, width, height):
    """Return canvas size, source crop in pixels, and fitted screen bounds."""
    ow, oh = plan.get('canvas', [width-width % 2, height-height % 2])
    crop = plan.get('crop', [0, 0, 1, 1])
    left, top, right, bottom = [round(v*n) for v, n in zip(crop, [width, height, width, height])]
    cw, ch = right-left, bottom-top
    if min(cw, ch, ow, oh) < 2: raise ValueError('Crop and canvas must be at least two pixels in each dimension')
    margin = .035 if plan.get('frame', True) else 0
    fit = min(ow/cw, oh/ch)*(1-2*margin)
    sw, sh = max(1, int(cw*fit)), max(1, int(ch*fit))
    return (ow, oh), (left, top, right, bottom), ((ow-sw)//2, (oh-sh)//2, sw, sh)


def _ease(t):
    t = float(np.clip(t, 0, 1))
    return t*t*t*(t*(t*6-15)+10)


def pose(plan, t, duration):
    config = plan.get('motion', {})
    if not config.get('enabled', False): return np.zeros(5)
    keys = config.get('keyframes', [])
    if keys:
        values = np.array(keys[-1][1:], float)
        if t <= keys[0][0]: values = np.array(keys[0][1:], float)
        else:
            for a, b in zip(keys, keys[1:]):
                if t <= b[0]:
                    f = _ease((t-a[0])/(b[0]-a[0]))
                    values = np.array(a[1:])*(1-f)+np.array(b[1:])*f
                    break
    else:
        phase = 2*math.pi*float(np.clip(t/max(duration, .001), 0, 1))
        s = math.sin(phase)
        values = np.array([.004*s, .003*(math.cos(phase)-1), .6*s, 1.2*s, .2*s])
    intervals = config.get('settle')
    if intervals is None:
        intervals = [(max(0, e['time']-.45), min(duration, e['time']+.75)) for e in plan.get('events', [])]
    weight = 1.0
    for start, end in intervals:
        distance = max(start-t, t-end, 0)
        weight = min(weight, _ease(distance/.3))
    return values*weight


def homography(plan, t, duration, canvas, bounds):
    ow, oh = canvas
    sx, sy, sw, sh = bounds
    dx, dy, pitch, yaw, roll = pose(plan, t, duration)
    p, y, r = np.deg2rad([pitch, yaw, roll])
    rx = np.array([[1, 0, 0], [0, np.cos(p), -np.sin(p)], [0, np.sin(p), np.cos(p)]])
    ry = np.array([[np.cos(y), 0, np.sin(y)], [0, 1, 0], [-np.sin(y), 0, np.cos(y)]])
    rz = np.array([[np.cos(r), -np.sin(r), 0], [np.sin(r), np.cos(r), 0], [0, 0, 1]])
    original = np.array([[0, 0], [ow, 0], [ow, oh], [0, oh]], np.float32)
    plane = np.column_stack((original-[ow/2, oh/2], np.zeros(4)))
    rotated = plane @ (rz @ ry @ rx).T
    focal = 1.35*max(ow, oh)
    projected = rotated[:, :2]*focal/(focal+rotated[:, 2:3])+[ow/2+dx*ow, oh/2+dy*oh]
    transform = cv2.getPerspectiveTransform(original, projected.astype(np.float32))
    # Keep the complete viewport visible even on tall/narrow output canvases.
    viewport = np.array([[[sx, sy], [sx+sw, sy], [sx+sw, sy+sh], [sx, sy+sh]]], np.float32)
    corners = cv2.perspectiveTransform(viewport, transform)[0]
    extent = np.max(np.abs(corners-[ow/2, oh/2]), axis=0)
    scale = min(1, (ow/2-1)/max(extent[0], .001), (oh/2-1)/max(extent[1], .001))
    fit = np.array([[scale, 0, (1-scale)*ow/2], [0, scale, (1-scale)*oh/2], [0, 0, 1]])
    return fit @ transform


class MotionStage:
    """Composite a premultiplied video plane and shadow over a fixed backdrop."""
    def __init__(self, background, front_alpha, bounds, radius, plan, duration):
        self.background = background
        self.oh, self.ow = background.shape[:2]
        self.bounds, self.plan, self.duration = bounds, plan, duration
        self.front_alpha = front_alpha
        sx, sy, sw, sh = bounds
        shadow = Image.new('L', (self.ow, self.oh))
        ImageDraw.Draw(shadow).rounded_rectangle((sx, sy+8, sx+sw, sy+sh+8), radius=radius, fill=145)
        shadow_alpha = np.array(shadow.filter(ImageFilter.GaussianBlur(max(2, self.ow*.012))), np.float32)/255
        front = np.zeros((self.oh, self.ow), np.float32)
        front[sy:sy+sh, sx:sx+sw] = front_alpha[:, :, 0]
        self.alpha = front+shadow_alpha*(1-front)
        self.layer = np.zeros((self.oh, self.ow, 3), np.float32)

    def render(self, screen, t):
        sx, sy, sw, sh = self.bounds
        self.layer[sy:sy+sh, sx:sx+sw] = screen*self.front_alpha
        transform = homography(self.plan, t, self.duration, (self.ow, self.oh), self.bounds)
        # Positive, matching interpolation weights keep premultiplied RGB and
        # opacity consistent and avoid dark fringes on light viewport edges.
        foreground = cv2.warpPerspective(self.layer, transform, (self.ow, self.oh), flags=cv2.INTER_LINEAR)
        matte = np.clip(cv2.warpPerspective(self.alpha, transform, (self.ow, self.oh), flags=cv2.INTER_LINEAR), 0, 1)[..., None]
        return np.clip(foreground+self.background*(1-matte), 0, 255).astype(np.uint8)
