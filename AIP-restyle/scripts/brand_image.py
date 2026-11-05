#!/usr/bin/env python3
"""Place the exact AIP emblem on a visually inspected raster design.

Requires Pillow. Does not restyle/recolor the source or detect empty space.
Only PNG output is supported, preserving alpha. Never overwrites a file.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageColor, ImageOps


ROOT = Path(__file__).resolve().parents[1]
LOGOS = ROOT / "assets/logos"
FILLS = {"purple": (74, 59, 104), "white": (255, 255, 255),
         "dark-purple": (47, 36, 71), "navy": (2, 6, 36)}
MIN_WIDTH = 32  # Application minimum, not an official brand requirement.


def rectangle(values, size):
    x, y, width, height = map(int, values)
    if min(x, y) < 0 or min(width, height) <= 0 or x+width > size[0] or y+height > size[1]:
        raise ValueError("Region must be positive and entirely inside the canvas")
    return x, y, width, height


def intersects(a, b):
    return a[0] < b[0]+b[2] and b[0] < a[0]+a[2] and a[1] < b[1]+b[3] and b[1] < a[1]+a[3]


def luminance(rgb):
    channels = [v/255 for v in rgb]
    linear = [v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4 for v in channels]
    return sum(a*b for a, b in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast_score(patch, logo, fill, intended_background):
    if patch.getchannel("A").getextrema()[0] < 255:
        if intended_background is None:
            raise ValueError("Logo region is transparent: supply --background for contrast checking; alpha stays intact")
        base = Image.new("RGBA", patch.size, ImageColor.getrgb(intended_background)+(255,))
        patch = Image.alpha_composite(base, patch)
    level = luminance(fill)
    scores = []
    rgb = patch.convert("RGB")
    mask = logo.getchannel("A")
    rgb_data = rgb.get_flattened_data() if hasattr(rgb, "get_flattened_data") else rgb.getdata()
    mask_data = mask.get_flattened_data() if hasattr(mask, "get_flattened_data") else mask.getdata()
    for pixel, alpha in zip(rgb_data, mask_data):
        if alpha >= 245:  # Exclude intentionally antialiased edge coverage.
            other = luminance(pixel)
            scores.append((max(level, other)+0.05)/(min(level, other)+0.05))
    if not scores:
        raise ValueError("Logo has no opaque interior at this size")
    scores.sort()
    return scores[int((len(scores)-1)*0.05)]


def brand_image(input_path, output_path, *, region=None, mode="overlay", variant="auto",
                logo_width=None, clear_space=None, min_contrast=3.0, background=None,
                footer_color="#F6F9FC", avoid=()):
    input_path, output_path = Path(input_path), Path(output_path)
    if output_path.suffix.lower() != ".png":
        raise ValueError("Output must be PNG to preserve alpha")
    if input_path.resolve() == output_path.resolve() or output_path.exists():
        raise ValueError("Refusing to overwrite the original or an existing output")
    if mode not in {"overlay", "surface", "footer"} or variant not in {"auto", *FILLS}:
        raise ValueError("Invalid placement mode or logo variant")
    if clear_space is None:
        clear_space = 0.5 if mode == "surface" else 0.65
    if not math.isfinite(clear_space) or clear_space < 0.5:
        raise ValueError("Clear-space factor must be at least 0.5; consult the guideline for final placement")
    if not math.isfinite(min_contrast) or not 1 <= min_contrast <= 21:
        raise ValueError("Minimum contrast must be between 1 and 21")
    with Image.open(input_path) as source:
        if getattr(source, "n_frames", 1) != 1:
            raise ValueError("Animated input needs a frame-aware workflow; refusing to flatten")
        if source.mode == "CMYK":
            raise ValueError("Convert CMYK to a color-managed sRGB preview before using this helper")
        canvas = ImageOps.exif_transpose(source).convert("RGBA")
    original_size = canvas.size
    protected = [rectangle(box, original_size) for box in avoid]
    logos = {}
    for name in FILLS:
        with Image.open(LOGOS / f"aip-emblem-{name}.png") as image:
            logos[name] = image.convert("RGBA")
    alpha = logos["purple"].getchannel("A").tobytes()
    if any(logo.getchannel("A").tobytes() != alpha for logo in logos.values()):
        raise ValueError("Bundled logo variant geometry differs")
    source_logo = logos["purple"]
    ratio = source_logo.height/source_logo.width
    requested_width = logo_width
    if mode == "surface" and region is not None:
        rectangle(region, canvas.size)
        default_width = round(region[2]*0.55)
    else:
        default_width = max(48, round(min(canvas.size)*0.08))
    width = int(logo_width) if logo_width is not None else default_width
    if width < MIN_WIDTH:
        raise ValueError(f"Logo width must be at least {MIN_WIDTH}px to remain legible")

    def metrics(w):
        h = max(1, round(w*ratio))
        pad = math.ceil(h*clear_space)
        return h, pad, w+2*pad, h+2*pad

    if mode in {"overlay", "surface"}:
        if region is None:
            raise ValueError("Placement requires --region X Y W H, selected after visual inspection")
        rx, ry, rw, rh = rectangle(region, canvas.size)
        while width >= MIN_WIDTH:
            height, padding, footprint_w, footprint_h = metrics(width)
            if footprint_w <= rw and footprint_h <= rh:
                break
            if requested_width is not None:
                raise ValueError("Requested logo and clear space do not fit the inspected region")
            width -= 1
        else:
            raise ValueError("Region too small for a legible emblem and clear space")
        fx, fy = rx+(rw-footprint_w)//2, ry+(rh-footprint_h)//2
    else:
        if region is not None:
            raise ValueError("Footer mode selects a new area; do not pass --region")
        height, padding, footprint_w, footprint_h = metrics(width)
        if footprint_w > canvas.width:
            raise ValueError("Logo and clear space exceed canvas width")
        fill = (0, 0, 0, 0) if footer_color == "transparent" else ImageColor.getrgb(footer_color)+(255,)
        extended = Image.new("RGBA", (canvas.width, canvas.height+footprint_h), fill)
        extended.paste(canvas, (0, 0))  # Copy source alpha exactly, including transparent pixels.
        canvas = extended
        fx, fy = canvas.width-footprint_w, original_size[1]
    footprint = (fx, fy, footprint_w, footprint_h)
    if any(intersects(footprint, box) for box in protected):
        raise ValueError("Logo or its clear space overlaps a protected region")
    x, y = fx+padding, fy+padding
    resized = {name: logo.resize((width, height), Image.Resampling.LANCZOS)
               for name, logo in logos.items()}
    patch = canvas.crop((x, y, x+width, y+height))
    choices = list(FILLS) if variant == "auto" else [variant]
    scores = {name: contrast_score(patch, resized[name], FILLS[name], background) for name in choices}
    chosen = max(scores, key=scores.get)
    if scores[chosen] < min_contrast:
        raise ValueError("Insufficient logo contrast: choose another empty area/theme; no background badge is added")
    canvas.alpha_composite(resized[chosen], (x, y))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("xb") as output:
        canvas.save(output, format="PNG")
    return {
        "output": str(output_path), "mode": mode, "variant": chosen,
        "placement": "integrated surface print" if mode == "surface" else "layout overlay" if mode == "overlay" else "explicit footer",
        "region_xywh": list(region) if region is not None else None,
        "logo_fraction_of_region_width": round(width/region[2], 3) if region is not None else None,
        "original_size": list(original_size), "output_size": list(canvas.size),
        "logo_bounds_xywh": [x, y, width, height],
        "clear_space_bounds_xywh": list(footprint),
        "contrast_5th_percentile": round(scores[chosen], 3),
        "clear_space_note": "Application setting; inspect against guideline page 7, not an official numeric rule",
        "source_untouched_outside_logo": mode in {"overlay", "surface"},
        "display_verified": False,
        "delivery_note": "This report verifies a saved file, not that a host displayed it; inspect and display this output path explicitly.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--mode", choices=["surface", "overlay", "footer"], default="surface")
    parser.add_argument("--region", type=int, nargs=4, metavar=("X", "Y", "W", "H"))
    parser.add_argument("--avoid", type=int, nargs=4, action="append", default=[], metavar=("X", "Y", "W", "H"))
    parser.add_argument("--variant", choices=["auto", *FILLS], default="auto")
    parser.add_argument("--logo-width", type=int)
    parser.add_argument("--clear-space", type=float, help="Application spacing factor: 0.5 for surface, 0.65 for layout; not an official numeric rule")
    parser.add_argument("--min-contrast", type=float, default=3.0)
    parser.add_argument("--background", help="Intended viewing background for transparent logo regions; does not fill alpha")
    parser.add_argument("--footer-color", default="#F6F9FC", help="Only used by footer mode; hex or transparent")
    args = parser.parse_args()
    try:
        result = brand_image(args.input, args.output, region=args.region, mode=args.mode,
                             variant=args.variant, logo_width=args.logo_width,
                             clear_space=args.clear_space, min_contrast=args.min_contrast,
                             background=args.background, footer_color=args.footer_color, avoid=args.avoid)
    except (ValueError, OSError) as error:
        parser.exit(2, f"Cannot place logo: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
