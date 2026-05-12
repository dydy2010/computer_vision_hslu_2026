#!/usr/bin/env python3
"""Reusable video downsizing utility using OpenCV.

Example:
    python other_document/downsize_video.py \
        --input videos-dashcam.mp4 \
        --output videos-dashcam-downsized.mp4 \
        --width 960
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import cv2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Downsize a video while preserving aspect ratio.",
    )
    parser.add_argument(
        "--input",
        default="videos-dashcam.mp4",
        help="Input video path (default: videos-dashcam.mp4)",
    )
    parser.add_argument(
        "--output",
        default="videos-dashcam-downsized.mp4",
        help="Output video path (default: videos-dashcam-downsized.mp4)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=960,
        help="Target width in pixels (default: 960)",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=None,
        help="Optional output fps (default: keep source fps)",
    )
    parser.add_argument(
        "--codec",
        default="mp4v",
        help="FourCC codec (default: mp4v)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output if it already exists.",
    )
    return parser.parse_args()


def ensure_parent_dir(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)


def calc_output_size(src_w: int, src_h: int, target_w: int) -> tuple[int, int]:
    if target_w <= 0:
        raise ValueError("--width must be > 0")
    if src_w <= 0 or src_h <= 0:
        raise ValueError("Source video has invalid dimensions")

    scale = target_w / float(src_w)
    target_h = max(2, int(round(src_h * scale)))

    # Ensure even dimensions for broad codec compatibility.
    if target_w % 2 != 0:
        target_w += 1
    if target_h % 2 != 0:
        target_h += 1

    return target_w, target_h


def main() -> int:
    args = parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    if not input_path.is_file():
        raise FileNotFoundError(f"Input video not found: {input_path}")

    if output_path.exists() and not args.overwrite:
        raise FileExistsError(
            f"Output already exists: {output_path}. Use --overwrite to replace it."
        )

    ensure_parent_dir(output_path)

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open input video: {input_path}")

    src_fps = cap.get(cv2.CAP_PROP_FPS)
    src_fps = src_fps if src_fps and src_fps > 0 else 30.0
    out_fps = args.fps if args.fps and args.fps > 0 else src_fps

    src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    dst_w, dst_h = calc_output_size(src_w, src_h, args.width)

    print("=== Downsize Video ===")
    print(f"Input : {input_path}")
    print(f"Output: {output_path}")
    print(f"Source: {src_w}x{src_h} @ {src_fps:.2f} fps")
    print(f"Target: {dst_w}x{dst_h} @ {out_fps:.2f} fps")
    if total_frames > 0:
        print(f"Frames: {total_frames}")

    fourcc = cv2.VideoWriter_fourcc(*args.codec)
    writer = cv2.VideoWriter(str(output_path), fourcc, out_fps, (dst_w, dst_h))
    if not writer.isOpened():
        cap.release()
        raise RuntimeError(
            f"Failed to create output writer with codec '{args.codec}'. "
            "Try --codec avc1 or --codec XVID."
        )

    processed = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            resized = cv2.resize(frame, (dst_w, dst_h), interpolation=cv2.INTER_AREA)
            writer.write(resized)
            processed += 1

            if processed % 300 == 0:
                print(f"Processed {processed} frames...")
    finally:
        cap.release()
        writer.release()

    print("=== Done ===")
    print(f"Processed frames: {processed}")
    print(f"Saved to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
