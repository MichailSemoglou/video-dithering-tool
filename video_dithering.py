#!/usr/bin/env python3
"""Video Dithering Tool.

A command-line tool for applying dithering effects to video files, supporting
both grayscale and color processing with five dithering algorithms:
Floyd-Steinberg (Floyd & Steinberg, 1976), Atkinson, Jarvis-Judice-Ninke
(Jarvis, Judice & Ninke, 1976), ordered (Bayer, 1973), and random dithering.
Output is either a sequence of PNG frames or a single animated GIF.

Author: Michail Semoglou
License: MIT
"""

import argparse
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm

Color = Tuple[int, int, int]

DEFAULT_COLOR_PALETTE: List[Color] = [
    (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0),
    (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255),
]


def floyd_steinberg_dither(
    image: np.ndarray,
    dither_strength: float = 1.0,
    is_color: bool = False,
    palette: Optional[List[Color]] = None,
) -> np.ndarray:
    """Apply Floyd-Steinberg error-diffusion dithering (Floyd & Steinberg, 1976).

    Error diffusion propagates each pixel's quantization error to its
    unvisited neighbors, so pixels are processed in raster order; this
    sequential dependency is why the loop below is not vectorized.

    Args:
        image: Grayscale (height, width) or color BGR (height, width, 3)
            array of dtype uint8.
        dither_strength: Fraction of the quantization error diffused to
            neighboring pixels, in the range 0.0 to 1.0.
        is_color: Whether `image` is a color (BGR) image rather than
            grayscale.
        palette: Candidate BGR colors to quantize to when `is_color` is
            True. Defaults to `DEFAULT_COLOR_PALETTE` when not provided.

    Returns:
        The dithered image as a uint8 array with the same shape as `image`.
    """
    if palette is None:
        palette = DEFAULT_COLOR_PALETTE

    img = image.astype(np.float32)

    if is_color:
        h, w, _ = img.shape
        for y in range(h):
            for x in range(w):
                old_pixel = img[y, x].copy()
                distances = [np.linalg.norm(old_pixel - np.array(color)) for color in palette]
                new_pixel = np.array(palette[np.argmin(distances)], dtype=np.float32)
                img[y, x] = new_pixel
                error = (old_pixel - new_pixel) * dither_strength

                if x + 1 < w:
                    img[y, x + 1] += error * 7 / 16
                if y + 1 < h:
                    if x > 0:
                        img[y + 1, x - 1] += error * 3 / 16
                    img[y + 1, x] += error * 5 / 16
                    if x + 1 < w:
                        img[y + 1, x + 1] += error * 1 / 16
    else:
        h, w = img.shape
        for y in range(h):
            for x in range(w):
                old_pixel = img[y, x]
                new_value = 255 if old_pixel > 128 else 0
                img[y, x] = new_value
                error = (old_pixel - new_value) * dither_strength

                if x + 1 < w:
                    img[y, x + 1] += error * 7 / 16
                if y + 1 < h:
                    if x > 0:
                        img[y + 1, x - 1] += error * 3 / 16
                    img[y + 1, x] += error * 5 / 16
                    if x + 1 < w:
                        img[y + 1, x + 1] += error * 1 / 16

    return np.clip(img, 0, 255).astype(np.uint8)


def atkinson_dither(
    image: np.ndarray,
    dither_strength: float = 1.0,
    is_color: bool = False,
    palette: Optional[List[Color]] = None,
) -> np.ndarray:
    """Apply Atkinson error-diffusion dithering.

    Like Floyd-Steinberg, this diffuses only a fraction (6/8) of each
    pixel's error to a fixed neighborhood, which produces less smearing at
    the cost of more contrast loss. The sequential error propagation is why
    the loop below is not vectorized.

    Args:
        image: Grayscale (height, width) or color BGR (height, width, 3)
            array of dtype uint8.
        dither_strength: Fraction of the quantization error diffused to
            neighboring pixels, in the range 0.0 to 1.0.
        is_color: Whether `image` is a color (BGR) image rather than
            grayscale.
        palette: Candidate BGR colors to quantize to when `is_color` is
            True. Defaults to `DEFAULT_COLOR_PALETTE` when not provided.

    Returns:
        The dithered image as a uint8 array with the same shape as `image`.
    """
    if palette is None:
        palette = DEFAULT_COLOR_PALETTE

    img = image.astype(np.float32)

    if is_color:
        h, w, _ = img.shape
        for y in range(h):
            for x in range(w):
                old_pixel = img[y, x].copy()
                distances = [np.linalg.norm(old_pixel - np.array(color)) for color in palette]
                new_pixel = np.array(palette[np.argmin(distances)], dtype=np.float32)
                img[y, x] = new_pixel
                error = (old_pixel - new_pixel) * dither_strength / 8

                if x + 1 < w:
                    img[y, x + 1] += error
                if x + 2 < w:
                    img[y, x + 2] += error
                if y + 1 < h:
                    if x > 0:
                        img[y + 1, x - 1] += error
                    img[y + 1, x] += error
                    if x + 1 < w:
                        img[y + 1, x + 1] += error
                if y + 2 < h:
                    img[y + 2, x] += error
    else:
        h, w = img.shape
        for y in range(h):
            for x in range(w):
                old_pixel = img[y, x]
                new_value = 255 if old_pixel > 128 else 0
                img[y, x] = new_value
                error = (old_pixel - new_value) * dither_strength / 8

                if x + 1 < w:
                    img[y, x + 1] += error
                if x + 2 < w:
                    img[y, x + 2] += error
                if y + 1 < h:
                    if x > 0:
                        img[y + 1, x - 1] += error
                    img[y + 1, x] += error
                    if x + 1 < w:
                        img[y + 1, x + 1] += error
                if y + 2 < h:
                    img[y + 2, x] += error

    return np.clip(img, 0, 255).astype(np.uint8)


def jarvis_judice_ninke_dither(
    image: np.ndarray,
    dither_strength: float = 1.0,
    is_color: bool = False,
    palette: Optional[List[Color]] = None,
) -> np.ndarray:
    """Apply Jarvis-Judice-Ninke error-diffusion dithering (Jarvis, Judice & Ninke, 1976).

    Diffuses error across a wider 5x3 neighborhood than Floyd-Steinberg,
    producing smoother gradients at a higher computational cost. The
    sequential error propagation is why the loop below is not vectorized.

    Args:
        image: Grayscale (height, width) or color BGR (height, width, 3)
            array of dtype uint8.
        dither_strength: Fraction of the quantization error diffused to
            neighboring pixels, in the range 0.0 to 1.0.
        is_color: Whether `image` is a color (BGR) image rather than
            grayscale.
        palette: Candidate BGR colors to quantize to when `is_color` is
            True. Defaults to `DEFAULT_COLOR_PALETTE` when not provided.

    Returns:
        The dithered image as a uint8 array with the same shape as `image`.
    """
    if palette is None:
        palette = DEFAULT_COLOR_PALETTE

    img = image.astype(np.float32)

    if is_color:
        h, w, _ = img.shape
        for y in range(h):
            for x in range(w):
                old_pixel = img[y, x].copy()
                distances = [np.linalg.norm(old_pixel - np.array(color)) for color in palette]
                new_pixel = np.array(palette[np.argmin(distances)], dtype=np.float32)
                img[y, x] = new_pixel
                error = (old_pixel - new_pixel) * dither_strength

                if x + 1 < w:
                    img[y, x + 1] += error * 7 / 48
                if x + 2 < w:
                    img[y, x + 2] += error * 5 / 48
                if y + 1 < h:
                    if x > 1:
                        img[y + 1, x - 2] += error * 3 / 48
                    if x > 0:
                        img[y + 1, x - 1] += error * 5 / 48
                    img[y + 1, x] += error * 7 / 48
                    if x + 1 < w:
                        img[y + 1, x + 1] += error * 5 / 48
                    if x + 2 < w:
                        img[y + 1, x + 2] += error * 3 / 48
                if y + 2 < h:
                    if x > 1:
                        img[y + 2, x - 2] += error * 1 / 48
                    if x > 0:
                        img[y + 2, x - 1] += error * 3 / 48
                    img[y + 2, x] += error * 5 / 48
                    if x + 1 < w:
                        img[y + 2, x + 1] += error * 3 / 48
                    if x + 2 < w:
                        img[y + 2, x + 2] += error * 1 / 48
    else:
        h, w = img.shape
        for y in range(h):
            for x in range(w):
                old_pixel = img[y, x]
                new_value = 255 if old_pixel > 128 else 0
                img[y, x] = new_value
                error = (old_pixel - new_value) * dither_strength

                if x + 1 < w:
                    img[y, x + 1] += error * 7 / 48
                if x + 2 < w:
                    img[y, x + 2] += error * 5 / 48
                if y + 1 < h:
                    if x > 1:
                        img[y + 1, x - 2] += error * 3 / 48
                    if x > 0:
                        img[y + 1, x - 1] += error * 5 / 48
                    img[y + 1, x] += error * 7 / 48
                    if x + 1 < w:
                        img[y + 1, x + 1] += error * 5 / 48
                    if x + 2 < w:
                        img[y + 1, x + 2] += error * 3 / 48
                if y + 2 < h:
                    if x > 1:
                        img[y + 2, x - 2] += error * 1 / 48
                    if x > 0:
                        img[y + 2, x - 1] += error * 3 / 48
                    img[y + 2, x] += error * 5 / 48
                    if x + 1 < w:
                        img[y + 2, x + 1] += error * 3 / 48
                    if x + 2 < w:
                        img[y + 2, x + 2] += error * 1 / 48

    return np.clip(img, 0, 255).astype(np.uint8)


def ordered_dither(
    image: np.ndarray,
    matrix_size: int = 4,
    is_color: bool = False,
    palette: Optional[List[Color]] = None,
) -> np.ndarray:
    """Apply ordered dithering with a Bayer threshold matrix (Bayer, 1973).

    Each pixel is quantized against a per-position threshold from a tiled
    Bayer matrix. For a 2-color palette, the threshold splits pixels
    directly into the light or dark color; for larger palettes, each pixel
    is perturbed by a Bayer-derived offset before nearest-color matching,
    generalizing ordered dithering to an arbitrary palette (Ulichney,
    1987). There is no error propagation between pixels, so this function
    is vectorized.

    Args:
        image: Grayscale (height, width) or color BGR (height, width, 3)
            array of dtype uint8.
        matrix_size: Bayer matrix dimension: 2, 4, or 8. Any other value
            falls back to the 8x8 matrix.
        is_color: Whether `image` is a color (BGR) image rather than
            grayscale.
        palette: Candidate BGR colors to quantize to when `is_color` is
            True. Defaults to `DEFAULT_COLOR_PALETTE` when not provided.

    Returns:
        The dithered image as a uint8 array with the same shape as `image`.
    """
    if palette is None:
        palette = DEFAULT_COLOR_PALETTE

    if matrix_size == 2:
        bayer_matrix = np.array([[0, 2], [3, 1]]) / 4
    elif matrix_size == 4:
        bayer_matrix = np.array([
            [0, 8, 2, 10],
            [12, 4, 14, 6],
            [3, 11, 1, 9],
            [15, 7, 13, 5],
        ]) / 16
    else:
        bayer_matrix = np.array([
            [0, 32, 8, 40, 2, 34, 10, 42],
            [48, 16, 56, 24, 50, 18, 58, 26],
            [12, 44, 4, 36, 14, 46, 6, 38],
            [60, 28, 52, 20, 62, 30, 54, 22],
            [3, 35, 11, 43, 1, 33, 9, 41],
            [51, 19, 59, 27, 49, 17, 57, 25],
            [15, 47, 7, 39, 13, 45, 5, 37],
            [63, 31, 55, 23, 61, 29, 53, 21],
        ]) / 64

    img = image.astype(np.float32)

    matrix_h, matrix_w = bayer_matrix.shape

    if is_color:
        h, w, _ = img.shape
        thresholds = np.tile(
            bayer_matrix, (h // matrix_h + 1, w // matrix_w + 1)
        )[:h, :w] * 255

        if len(palette) == 2:
            gray = img.mean(axis=2)
            mask = gray > thresholds
            img[mask] = palette[1]
            img[~mask] = palette[0]
        else:
            # Generalized ordered dithering to an arbitrary palette
            # (Ulichney, 1987): perturb each pixel by a Bayer-derived
            # offset, scaled to the average spacing between quantization
            # levels, before nearest-color matching. This is what makes the
            # Bayer pattern visible in the output; without the offset, the
            # result would be plain nearest-color quantization with no
            # dithering texture.
            level_step = 255.0 / max(len(palette) - 1, 1)
            offset = (thresholds / 255 - 0.5) * level_step
            perturbed = np.clip(img + offset[:, :, None], 0, 255)

            palette_arr = np.array(palette, dtype=np.float32)
            diffs = perturbed[:, :, None, :] - palette_arr[None, None, :, :]
            distances = np.linalg.norm(diffs, axis=-1)
            nearest = np.argmin(distances, axis=-1)
            img = palette_arr[nearest]
    else:
        h, w = img.shape
        thresholds = np.tile(
            bayer_matrix, (h // matrix_h + 1, w // matrix_w + 1)
        )[:h, :w] * 255
        img = np.where(img > thresholds, 255, 0)

    return np.clip(img, 0, 255).astype(np.uint8)


def random_dither(
    image: np.ndarray,
    threshold_variance: int = 50,
    is_color: bool = False,
    palette: Optional[List[Color]] = None,
) -> np.ndarray:
    """Apply random threshold dithering.

    Each pixel is quantized against an independently randomized threshold
    (or, for color images, against random per-channel noise), with no
    dependency between pixels, so this function is vectorized.

    Args:
        image: Grayscale (height, width) or color BGR (height, width, 3)
            array of dtype uint8.
        threshold_variance: Maximum absolute deviation of the per-pixel
            random threshold (grayscale) or noise (color) from its base
            value.
        is_color: Whether `image` is a color (BGR) image rather than
            grayscale.
        palette: Candidate BGR colors to quantize to when `is_color` is
            True. Defaults to `DEFAULT_COLOR_PALETTE` when not provided.

    Returns:
        The dithered image as a uint8 array with the same shape as `image`.
    """
    if palette is None:
        palette = DEFAULT_COLOR_PALETTE

    img = image.astype(np.float32)

    if is_color:
        h, w, _ = img.shape
        noise = np.random.uniform(-threshold_variance, threshold_variance, (h, w, 3))
        noisy = np.clip(img + noise, 0, 255).astype(np.float32)
        palette_arr = np.array(palette, dtype=np.float32)
        diffs = noisy[:, :, None, :] - palette_arr[None, None, :, :]
        distances = np.linalg.norm(diffs, axis=-1)
        nearest = np.argmin(distances, axis=-1)
        img = palette_arr[nearest]
    else:
        h, w = img.shape
        thresholds = 128 + np.random.uniform(-threshold_variance, threshold_variance, (h, w))
        img = np.where(img > thresholds, 255, 0)

    return np.clip(img, 0, 255).astype(np.uint8)


def apply_dithering(
    image: np.ndarray,
    method: str,
    is_color: bool = False,
    **kwargs: Any,
) -> np.ndarray:
    """Dispatch to the dithering function named by `method`.

    Args:
        image: Grayscale (height, width) or color BGR (height, width, 3)
            array of dtype uint8.
        method: One of 'floyd_steinberg', 'atkinson', 'jarvis_judice_ninke',
            'ordered', or 'random'.
        is_color: Whether `image` is a color (BGR) image rather than
            grayscale.
        **kwargs: Extra arguments forwarded to the chosen dithering
            function (for example `dither_strength`, `matrix_size`,
            `threshold_variance`, or `palette`).

    Returns:
        The dithered image as a uint8 array with the same shape as `image`.

    Raises:
        ValueError: If `method` does not name a supported algorithm.
    """
    if method == 'floyd_steinberg':
        return floyd_steinberg_dither(image, is_color=is_color, **kwargs)
    elif method == 'atkinson':
        return atkinson_dither(image, is_color=is_color, **kwargs)
    elif method == 'jarvis_judice_ninke':
        return jarvis_judice_ninke_dither(image, is_color=is_color, **kwargs)
    elif method == 'ordered':
        return ordered_dither(image, is_color=is_color, **kwargs)
    elif method == 'random':
        return random_dither(image, is_color=is_color, **kwargs)
    else:
        raise ValueError(f"Unknown dithering method: {method}")


def frame_to_gif_image(
    dithered_frame: np.ndarray,
    is_color: bool,
    palette: Optional[List[Color]] = None,
) -> Image.Image:
    """Convert a dithered frame to a palette-mode PIL image for GIF export.

    Since every pixel in `dithered_frame` already matches one of the palette
    colors used during dithering, quantizing against that same palette (with
    dithering disabled) maps each pixel to its exact color instead of
    re-quantizing it with a lossy, auto-generated palette the way a generic
    GIF encoder normally would.

    Args:
        dithered_frame: A frame already produced by one of the dithering
            functions: grayscale (height, width) or color BGR
            (height, width, 3), dtype uint8.
        is_color: Whether `dithered_frame` is a color (BGR) frame rather
            than grayscale.
        palette: The BGR palette the frame was dithered against. Defaults
            to `DEFAULT_COLOR_PALETTE` when not provided and `is_color` is
            True; ignored for grayscale frames, which always map to
            black and white.

    Returns:
        A Pillow image in mode 'P' quantized onto the exact palette colors.
    """
    if is_color:
        colors = palette if palette is not None else DEFAULT_COLOR_PALETTE
        # Dithering operates on OpenCV's BGR channel order; convert to RGB for Pillow.
        colors_rgb = [tuple(reversed(color)) for color in colors]
        rgb_frame = cv2.cvtColor(dithered_frame, cv2.COLOR_BGR2RGB)
        pil_frame = Image.fromarray(rgb_frame, mode='RGB')
    else:
        colors_rgb = [(0, 0, 0), (255, 255, 255)]
        pil_frame = Image.fromarray(dithered_frame, mode='L').convert('RGB')

    palette_image = Image.new('P', (1, 1))
    flat_palette = [channel for color in colors_rgb for channel in color]
    flat_palette += [0] * (768 - len(flat_palette))
    palette_image.putpalette(flat_palette)

    return pil_frame.quantize(palette=palette_image, dither=Image.Dither.NONE)


def process_video(
    input_path: str,
    output_path: str,
    method: str = 'floyd_steinberg',
    target_width: int = 540,
    target_height: int = 960,
    max_frames: int = 720,
    is_color: bool = False,
    export_gif: bool = False,
    fps: int = 30,
    gif_loop: int = 0,
    **dither_params: Any,
) -> None:
    """Dither a video's frames and export them as PNG frames or an animated GIF.

    Args:
        input_path: Path to the source video file.
        output_path: Destination directory for PNG frames, or destination
            file path when `export_gif` is True.
        method: Dithering method name; see `apply_dithering`.
        target_width: Width, in pixels, each frame is resized to.
        target_height: Height, in pixels, each frame is resized to.
        max_frames: Maximum number of frames to read and process.
        is_color: Whether to dither in color (BGR) rather than grayscale.
        export_gif: If True, export a single animated GIF at `output_path`
            instead of a directory of PNG frames.
        fps: Frame rate used to compute the GIF's per-frame duration. Falls
            back to the source video's frame rate, then to 30, if not
            positive.
        gif_loop: Number of times the GIF should loop; 0 means loop
            indefinitely.
        **dither_params: Extra arguments forwarded to `apply_dithering`
            (for example `dither_strength`, `matrix_size`,
            `threshold_variance`, or `palette`).

    Notes:
        When `export_gif` is True, every dithered frame is kept in memory
        (as a palette-mode PIL image) until all frames are processed, since
        Pillow's animated GIF writer needs the full frame sequence at
        `save()` time. Memory use scales with
        `target_width * target_height * max_frames`; lower `max_frames` or
        the target resolution for long clips if memory is constrained.
    """
    if export_gif:
        parent_dir = os.path.dirname(output_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
    else:
        os.makedirs(output_path, exist_ok=True)

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video file {input_path}")
        return

    frame_count = 0
    gif_frames: List[Image.Image] = []

    try:
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Video: {video_fps} fps, {total_frames} total frames")
        print(f"Processing up to {max_frames} frames using {method} dithering...")

        with tqdm(total=min(max_frames, total_frames), desc="Processing frames") as pbar:
            while frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.resize(frame, (target_width, target_height))

                if not is_color:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                dithered = apply_dithering(frame, method, is_color, **dither_params)

                if export_gif:
                    gif_frames.append(frame_to_gif_image(dithered, is_color, dither_params.get('palette')))
                else:
                    filename = f"frame_{frame_count:04d}.png"
                    cv2.imwrite(os.path.join(output_path, filename), dithered)

                frame_count += 1
                pbar.update(1)
    finally:
        cap.release()

    if export_gif:
        if not gif_frames:
            print("Error: No frames were processed, GIF was not created")
            return

        if fps > 0:
            duration_ms = int(1000 / fps)
        elif video_fps > 0:
            duration_ms = int(1000 / video_fps)
        else:
            duration_ms = int(1000 / 30)
        gif_frames[0].save(
            output_path,
            save_all=True,
            append_images=gif_frames[1:],
            duration=duration_ms,
            loop=gif_loop,
            optimize=False,
            disposal=2,
        )
        print(f"Exported {frame_count} frames as an animated GIF to {output_path}")
    else:
        print(f"Exported {frame_count} frames to {output_path}")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for the video dithering tool.

    Returns:
        The parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(description='Apply various dithering effects to video frames')

    parser.add_argument('input_video', help='Path to input video file')

    parser.add_argument(
        '-o', '--output', default='frames',
        help='Output directory for frames (default: frames)',
    )

    parser.add_argument(
        '-m', '--method',
        choices=['floyd_steinberg', 'atkinson', 'jarvis_judice_ninke', 'ordered', 'random'],
        default='floyd_steinberg',
        help='Dithering method (default: floyd_steinberg)',
    )

    parser.add_argument(
        '-w', '--width', type=int, default=540,
        help='Target width for frames (default: 540)',
    )

    parser.add_argument(
        '--height', type=int, default=960,
        help='Target height for frames (default: 960)',
    )

    parser.add_argument(
        '-f', '--frames', type=int, default=720,
        help='Maximum number of frames to process (default: 720)',
    )

    parser.add_argument(
        '-c', '--color', action='store_true',
        help='Process as color image (default: grayscale)',
    )

    parser.add_argument(
        '-d', '--dither-strength', type=float, default=1.0,
        help='Dithering strength for error diffusion methods (0.0-1.0, default: 1.0)',
    )

    parser.add_argument(
        '--matrix-size', type=int, choices=[2, 4, 8], default=4,
        help='Matrix size for ordered dithering (default: 4)',
    )

    parser.add_argument(
        '--threshold-variance', type=int, default=50,
        help='Threshold variance for random dithering (default: 50)',
    )

    parser.add_argument(
        '--fps', type=int, default=30,
        help='Frame rate for output video (default: 30)',
    )

    parser.add_argument(
        '--gif', action='store_true',
        help='Export directly as an animated GIF instead of PNG frames '
             '(holds all frames in memory until saved, so lower --frames '
             'or resolution for long clips on constrained systems)',
    )

    parser.add_argument(
        '--gif-loop', type=int, default=0,
        help='Number of times the GIF should loop, 0 = infinite (default: 0)',
    )

    return parser.parse_args()


def main() -> None:
    """Parse arguments, validate them, and run the dithering pipeline."""
    args = parse_arguments()

    if not 0.0 <= args.dither_strength <= 1.0:
        print("Error: Dithering strength must be between 0.0 and 1.0")
        sys.exit(1)

    if args.width <= 0 or args.height <= 0:
        print("Error: --width and --height must be positive")
        sys.exit(1)

    if args.frames <= 0:
        print("Error: --frames must be positive")
        sys.exit(1)

    output_path = args.output
    if args.gif:
        if output_path == 'frames':
            output_path = 'output.gif'
        elif not output_path.lower().endswith('.gif'):
            output_path = f"{output_path}.gif"

    print(f"Processing video: {args.input_video}")
    print(f"Output {'GIF file' if args.gif else 'directory'}: {output_path}")
    print(f"Dithering method: {args.method}")
    print(f"Target dimensions: {args.width}x{args.height}")
    print(f"Max frames: {args.frames}")
    print(f"Color mode: {'Color' if args.color else 'Grayscale'}")
    print()

    dither_params: Dict[str, Any] = {}
    if args.method in ['floyd_steinberg', 'atkinson', 'jarvis_judice_ninke']:
        dither_params['dither_strength'] = args.dither_strength
    elif args.method == 'ordered':
        dither_params['matrix_size'] = args.matrix_size
    elif args.method == 'random':
        dither_params['threshold_variance'] = args.threshold_variance

    process_video(
        args.input_video, output_path, args.method, args.width,
        args.height, args.frames, args.color, export_gif=args.gif,
        fps=args.fps, gif_loop=args.gif_loop, **dither_params,
    )

    if args.gif:
        print(f"\nDone! Your animated GIF is ready: {output_path}")
    else:
        print("\nDone! You can now create a video from frames using:")
        suffix = f"_{args.method}_{'color' if args.color else 'bw'}"
        output_mp4 = f"output_dithered{suffix}.mp4"
        print(
            f"ffmpeg -r {args.fps} -i {output_path}/frame_%04d.png "
            f"-c:v libx264 -pix_fmt yuv420p {output_mp4}"
        )


if __name__ == "__main__":
    main()
