#!/usr/bin/env python3

from __future__ import annotations

import math
import os
import struct
import zlib
from pathlib import Path


Color = tuple[int, int, int, int]


def blend(dst: Color, src: Color) -> Color:
    src_a = src[3] / 255.0
    dst_a = dst[3] / 255.0
    out_a = src_a + dst_a * (1.0 - src_a)
    if out_a <= 0:
        return (0, 0, 0, 0)

    def channel(index: int) -> int:
        value = (
            src[index] * src_a + dst[index] * dst_a * (1.0 - src_a)
        ) / out_a
        return max(0, min(255, round(value)))

    return (channel(0), channel(1), channel(2), max(0, min(255, round(out_a * 255))))


class Canvas:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.pixels = [[(0, 0, 0, 0) for _ in range(width)] for _ in range(height)]

    def put(self, x: int, y: int, color: Color) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = blend(self.pixels[y][x], color)

    def set_pixel(self, x: int, y: int, color: Color) -> None:
        """Set pixel directly without alpha blending."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color

    def write_png(self, path: Path) -> None:
        raw = bytearray()
        for row in self.pixels:
            raw.append(0)
            for r, g, b, a in row:
                raw.extend((r, g, b, a))

        def chunk(kind: bytes, data: bytes) -> bytes:
            return (
                struct.pack(">I", len(data))
                + kind
                + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            )

        png = bytearray(b"\x89PNG\r\n\x1a\n")
        png.extend(
            chunk(
                b"IHDR",
                struct.pack(">IIBBBBB", self.width, self.height, 8, 6, 0, 0, 0),
            )
        )
        png.extend(chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
        png.extend(chunk(b"IEND", b""))
        path.write_bytes(png)


def draw_circle(canvas: Canvas, cx: float, cy: float, radius: float, color: Color) -> None:
    min_x = max(0, math.floor(cx - radius - 1))
    max_x = min(canvas.width - 1, math.ceil(cx + radius + 1))
    min_y = max(0, math.floor(cy - radius - 1))
    max_y = min(canvas.height - 1, math.ceil(cy + radius + 1))

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            dx = x + 0.5 - cx
            dy = y + 0.5 - cy
            if dx * dx + dy * dy <= radius * radius:
                canvas.put(x, y, color)


def distance_to_segment(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    abx = bx - ax
    aby = by - ay
    apx = px - ax
    apy = py - ay
    length_squared = abx * abx + aby * aby
    if length_squared == 0:
        return math.hypot(apx, apy)

    t = max(0.0, min(1.0, (apx * abx + apy * aby) / length_squared))
    closest_x = ax + abx * t
    closest_y = ay + aby * t
    return math.hypot(px - closest_x, py - closest_y)


def draw_line(
    canvas: Canvas, ax: float, ay: float, bx: float, by: float, thickness: float, color: Color
) -> None:
    half = thickness / 2.0
    min_x = max(0, math.floor(min(ax, bx) - half - 1))
    max_x = min(canvas.width - 1, math.ceil(max(ax, bx) + half + 1))
    min_y = max(0, math.floor(min(ay, by) - half - 1))
    max_y = min(canvas.height - 1, math.ceil(max(ay, by) + half + 1))

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if distance_to_segment(x + 0.5, y + 0.5, ax, ay, bx, by) <= half:
                canvas.put(x, y, color)


def point_in_polygon(px: float, py: float, points: list[tuple[float, float]]) -> bool:
    inside = False
    count = len(points)
    for i in range(count):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % count]
        intersects = ((y1 > py) != (y2 > py)) and (
            px < (x2 - x1) * (py - y1) / ((y2 - y1) or 1e-9) + x1
        )
        if intersects:
            inside = not inside
    return inside


def draw_polygon(canvas: Canvas, points: list[tuple[float, float]], color: Color) -> None:
    xs = [x for x, _ in points]
    ys = [y for _, y in points]
    min_x = max(0, math.floor(min(xs)))
    max_x = min(canvas.width - 1, math.ceil(max(xs)))
    min_y = max(0, math.floor(min(ys)))
    max_y = min(canvas.height - 1, math.ceil(max(ys)))

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if point_in_polygon(x + 0.5, y + 0.5, points):
                canvas.put(x, y, color)


def draw_rounded_rect(
    canvas: Canvas, x: float, y: float, width: float, height: float, radius: float, color: Color, overwrite: bool = False
) -> None:
    min_x = max(0, math.floor(x))
    max_x = min(canvas.width - 1, math.ceil(x + width))
    min_y = max(0, math.floor(y))
    max_y = min(canvas.height - 1, math.ceil(y + height))

    for py in range(min_y, max_y + 1):
        for px in range(min_x, max_x + 1):
            sample_x = px + 0.5
            sample_y = py + 0.5
            dx = max(abs(sample_x - (x + width / 2.0)) - (width / 2.0 - radius), 0.0)
            dy = max(abs(sample_y - (y + height / 2.0)) - (height / 2.0 - radius), 0.0)
            if dx * dx + dy * dy <= radius * radius:
                if overwrite:
                    canvas.set_pixel(px, py, color)
                else:
                    canvas.put(px, py, color)


def _in_rounded_rect(
    px: float, py: float, x: float, y: float, width: float, height: float, radius: float
) -> bool:
    dx = max(abs(px - (x + width / 2.0)) - (width / 2.0 - radius), 0.0)
    dy = max(abs(py - (y + height / 2.0)) - (height / 2.0 - radius), 0.0)
    return dx * dx + dy * dy <= radius * radius


def draw_bubble_outline(
    canvas: Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    radius: float,
    thickness: float,
    color: Color,
) -> None:
    inner_x = x + thickness
    inner_y = y + thickness
    inner_w = width - thickness * 2
    inner_h = height - thickness * 2
    inner_r = max(0.0, radius - thickness)

    min_x = max(0, math.floor(x))
    max_x = min(canvas.width - 1, math.ceil(x + width))
    min_y = max(0, math.floor(y))
    max_y = min(canvas.height - 1, math.ceil(y + height))

    for py in range(min_y, max_y + 1):
        for px in range(min_x, max_x + 1):
            sx = px + 0.5
            sy = py + 0.5
            if _in_rounded_rect(sx, sy, x, y, width, height, radius) and not _in_rounded_rect(
                sx, sy, inner_x, inner_y, inner_w, inner_h, inner_r
            ):
                canvas.put(px, py, color)

    tail = [
        (x + width * 0.38, y + height),
        (x + width * 0.53, y + height),
        (x + width * 0.43, y + height + thickness * 1.8),
    ]
    draw_polygon(canvas, tail, color)


def draw_background(canvas: Canvas, size: int) -> None:
    outer = 0.5
    draw_rounded_rect(canvas, outer, outer, size - 1.0, size - 1.0, size * 0.24, (11, 18, 32, 255))
    draw_rounded_rect(canvas, size * 0.08, size * 0.08, size * 0.84, size * 0.84, size * 0.18, (15, 23, 42, 255))

    left_panel = [
        (size * 0.11, size * 0.11),
        (size * 0.58, size * 0.11),
        (size * 0.46, size * 0.89),
        (size * 0.11, size * 0.89),
    ]
    right_panel = [
        (size * 0.54, size * 0.11),
        (size * 0.89, size * 0.11),
        (size * 0.89, size * 0.89),
        (size * 0.42, size * 0.89),
    ]
    stripe = [
        (size * 0.47, size * 0.08),
        (size * 0.60, size * 0.08),
        (size * 0.53, size * 0.92),
        (size * 0.40, size * 0.92),
    ]

    draw_polygon(canvas, left_panel, (17, 24, 39, 210))
    draw_polygon(canvas, right_panel, (8, 145, 178, 96))
    draw_polygon(canvas, stripe, (34, 211, 238, 224))


def draw_pull_request_symbol(canvas: Canvas, size: int) -> None:
    stroke = max(1.5, size * 0.08)
    node = size * 0.072
    color = (248, 250, 252, 255)

    x_left = size * 0.27
    x_right = size * 0.44
    y_top = size * 0.28
    y_mid = size * 0.50
    y_bottom = size * 0.72

    draw_line(canvas, x_left, y_top, x_left, y_bottom, stroke, color)
    draw_line(canvas, x_left, y_mid, x_right, y_mid, stroke, color)
    draw_circle(canvas, x_left, y_top, node, color)
    draw_circle(canvas, x_right, y_mid, node, color)
    draw_circle(canvas, x_left, y_bottom, node, color)


def draw_review_symbol(canvas: Canvas, size: int) -> None:
    color = (236, 254, 255, 255)
    outline = max(1.8, size * 0.07)
    draw_bubble_outline(
        canvas,
        size * 0.58,
        size * 0.28,
        size * 0.21,
        size * 0.21,
        size * 0.055,
        outline,
        color,
    )

    check_color = (34, 197, 94, 255)
    draw_line(canvas, size * 0.63, size * 0.40, size * 0.67, size * 0.44, outline * 0.82, check_color)
    draw_line(canvas, size * 0.67, size * 0.44, size * 0.75, size * 0.34, outline * 0.82, check_color)


def render_icon(size: int, path: Path) -> None:
    canvas = Canvas(size, size)
    draw_background(canvas, size)
    draw_pull_request_symbol(canvas, size)
    draw_review_symbol(canvas, size)
    canvas.write_png(path)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    icons_dir = root / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)

    for size in (16, 32, 48, 128):
        render_icon(size, icons_dir / f"icon-{size}.png")


if __name__ == "__main__":
    main()