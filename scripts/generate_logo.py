#!/usr/bin/env python3
"""Generate a simple text-based logo PNG for bambuuzle."""

import os

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 640, 200
BG_COLOR = (30, 30, 30)
TEXT_COLOR = (0, 200, 120)
ACCENT_COLOR = (255, 180, 0)


def generate_logo(output_path: str = "logo.png") -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Try to use a nice monospace font, fall back to default
    font_size = 72
    small_size = 24
    try:
        font = ImageFont.truetype("DejaVuSansMono-Bold.ttf", font_size)
        small_font = ImageFont.truetype("DejaVuSansMono.ttf", small_size)
    except OSError:
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", font_size
            )
            small_font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", small_size
            )
        except OSError:
            try:
                # macOS
                font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", font_size)
                small_font = ImageFont.truetype(
                    "/System/Library/Fonts/Menlo.ttc", small_size
                )
            except OSError:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()

    # Main title
    title = "bambuuzle"
    bbox = draw.textbbox((0, 0), title, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (WIDTH - tw) // 2
    y = (HEIGHT - th) // 2 - 20
    draw.text((x, y), title, fill=TEXT_COLOR, font=font)

    # Subtitle
    subtitle = "gcode.3mf extraction & reinsertion"
    bbox2 = draw.textbbox((0, 0), subtitle, font=small_font)
    sw = bbox2[2] - bbox2[0]
    sx = (WIDTH - sw) // 2
    sy = y + th + 20
    draw.text((sx, sy), subtitle, fill=ACCENT_COLOR, font=small_font)

    # Top/bottom accent lines
    draw.rectangle([(0, 0), (WIDTH, 4)], fill=TEXT_COLOR)
    draw.rectangle([(0, HEIGHT - 4), (WIDTH, HEIGHT)], fill=TEXT_COLOR)

    img.save(output_path)
    print(f"Logo saved to {output_path} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    output = os.path.join(project_dir, "logo.png")
    generate_logo(output)
