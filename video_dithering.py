#!/usr/bin/env python3
"""
Video Dithering Tool

A powerful Python tool for applying various dithering effects to video files,
supporting both grayscale and color processing with multiple popular algorithms.

Author: Michail Semoglou
License: MIT
"""

import cv2
import numpy as np
import os
import argparse
from tqdm import tqdm
import random

def floyd_steinberg_dither(image, dither_strength=1.0, is_color=False, palette=None):
    """Apply Floyd-Steinberg dithering to image"""
    if is_color and palette is None:
        palette = [
            (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0),
            (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)
        ]
    
    img = image.astype(np.float32)
    
    if is_color:
        h, w, c = img.shape
        for y in range(h):
            for x in range(w):
                old_pixel = img[y, x].copy()
                distances = [np.linalg.norm(old_pixel - np.array(color)) for color in palette]
                new_pixel = np.array(palette[np.argmin(distances)], dtype=np.float32)
                img[y, x] = new_pixel
                error = (old_pixel - new_pixel) * dither_strength
                
                if x + 1 < w:
                    img[y, x + 1] += error * 7/16
                if y + 1 < h:
                    if x > 0:
                        img[y + 1, x - 1] += error * 3/16
                    img[y + 1, x] += error * 5/16
                    if x + 1 < w:
                        img[y + 1, x + 1] += error * 1/16
    else:
        h, w = img.shape
        for y in range(h):
            for x in range(w):
                old_pixel = img[y, x]
                new_pixel = 255 if old_pixel > 128 else 0
                img[y, x] = new_pixel
                error = (old_pixel - new_pixel) * dither_strength
                
                if x + 1 < w:
                    img[y, x + 1] += error * 7/16
                if y + 1 < h:
                    if x > 0:
                        img[y + 1, x - 1] += error * 3/16
                    img[y + 1, x] += error * 5/16
                    if x + 1 < w:
                        img[y + 1, x + 1] += error * 1/16
    
    return np.clip(img, 0, 255).astype(np.uint8)

def atkinson_dither(image, dither_strength=1.0, is_color=False, palette=None):
    """Apply Atkinson dithering to image"""
    if is_color and palette is None:
        palette = [
            (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0),
            (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)
        ]
    
    img = image.astype(np.float32)
    
    if is_color:
        h, w, c = img.shape
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
                new_pixel = 255 if old_pixel > 128 else 0
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
    
    return np.clip(img, 0, 255).astype(np.uint8)

def jarvis_judice_ninke_dither(image, dither_strength=1.0, is_color=False, palette=None):
    """Apply Jarvis-Judice-Ninke dithering to image"""
    if is_color and palette is None:
        palette = [
            (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0),
            (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)
        ]
    
    img = image.astype(np.float32)
    
    if is_color:
        h, w, c = img.shape
        for y in range(h):
            for x in range(w):
                old_pixel = img[y, x].copy()
                distances = [np.linalg.norm(old_pixel - np.array(color)) for color in palette]
                new_pixel = np.array(palette[np.argmin(distances)], dtype=np.float32)
                img[y, x] = new_pixel
                error = (old_pixel - new_pixel) * dither_strength
                
                if x + 1 < w:
                    img[y, x + 1] += error * 7/48
                if x + 2 < w:
                    img[y, x + 2] += error * 5/48
                if y + 1 < h:
                    if x > 1:
                        img[y + 1, x - 2] += error * 3/48
                    if x > 0:
                        img[y + 1, x - 1] += error * 5/48
                    img[y + 1, x] += error * 7/48
                    if x + 1 < w:
                        img[y + 1, x + 1] += error * 5/48
                    if x + 2 < w:
                        img[y + 1, x + 2] += error * 3/48
                if y + 2 < h:
                    if x > 1:
                        img[y + 2, x - 2] += error * 1/48
                    if x > 0:
                        img[y + 2, x - 1] += error * 3/48
                    img[y + 2, x] += error * 5/48
                    if x + 1 < w:
                        img[y + 2, x + 1] += error * 3/48
                    if x + 2 < w:
                        img[y + 2, x + 2] += error * 1/48
    else:
        h, w = img.shape
        for y in range(h):
            for x in range(w):
                old_pixel = img[y, x]
                new_pixel = 255 if old_pixel > 128 else 0
                img[y, x] = new_pixel
                error = (old_pixel - new_pixel) * dither_strength
                
                if x + 1 < w:
                    img[y, x + 1] += error * 7/48
                if x + 2 < w:
                    img[y, x + 2] += error * 5/48
                if y + 1 < h:
                    if x > 1:
                        img[y + 1, x - 2] += error * 3/48
                    if x > 0:
                        img[y + 1, x - 1] += error * 5/48
                    img[y + 1, x] += error * 7/48
                    if x + 1 < w:
                        img[y + 1, x + 1] += error * 5/48
                    if x + 2 < w:
                        img[y + 1, x + 2] += error * 3/48
                if y + 2 < h:
                    if x > 1:
                        img[y + 2, x - 2] += error * 1/48
                    if x > 0:
                        img[y + 2, x - 1] += error * 3/48
                    img[y + 2, x] += error * 5/48
                    if x + 1 < w:
                        img[y + 2, x + 1] += error * 3/48
                    if x + 2 < w:
                        img[y + 2, x + 2] += error * 1/48
    
    return np.clip(img, 0, 255).astype(np.uint8)

def ordered_dither(image, matrix_size=4, is_color=False, palette=None):
    """Apply ordered dithering using Bayer matrix"""
    if is_color and palette is None:
        palette = [
            (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0),
            (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)
        ]
    
    if matrix_size == 2:
        bayer_matrix = np.array([[0, 2], [3, 1]]) / 4
    elif matrix_size == 4:
        bayer_matrix = np.array([
            [0, 8, 2, 10],
            [12, 4, 14, 6],
            [3, 11, 1, 9],
            [15, 7, 13, 5]
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
            [63, 31, 55, 23, 61, 29, 53, 21]
        ]) / 64
    
    img = image.astype(np.float32)
    
    if is_color:
        h, w, c = img.shape
        for y in range(h):
            for x in range(w):
                threshold = bayer_matrix[y % matrix_size, x % matrix_size] * 255
                old_pixel = img[y, x].copy()
                
                if len(palette) == 2:
                    gray_val = np.mean(old_pixel)
                    new_pixel = np.array(palette[1] if gray_val > threshold else palette[0], dtype=np.float32)
                else:
                    distances = [np.linalg.norm(old_pixel - np.array(color)) for color in palette]
                    new_pixel = np.array(palette[np.argmin(distances)], dtype=np.float32)
                
                img[y, x] = new_pixel
    else:
        h, w = img.shape
        for y in range(h):
            for x in range(w):
                threshold = bayer_matrix[y % matrix_size, x % matrix_size] * 255
                img[y, x] = 255 if img[y, x] > threshold else 0
    
    return np.clip(img, 0, 255).astype(np.uint8)

def random_dither(image, threshold_variance=50, is_color=False, palette=None):
    """Apply random dithering"""
    if is_color and palette is None:
        palette = [
            (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0),
            (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)
        ]
    
    img = image.astype(np.float32)
    
    if is_color:
        h, w, c = img.shape
        for y in range(h):
            for x in range(w):
                old_pixel = img[y, x].copy()
                noise = np.random.uniform(-threshold_variance, threshold_variance, 3)
                noisy_pixel = np.clip(old_pixel + noise, 0, 255)
                distances = [np.linalg.norm(noisy_pixel - np.array(color)) for color in palette]
                new_pixel = np.array(palette[np.argmin(distances)], dtype=np.float32)
                img[y, x] = new_pixel
    else:
        h, w = img.shape
        for y in range(h):
            for x in range(w):
                threshold = 128 + random.uniform(-threshold_variance, threshold_variance)
                img[y, x] = 255 if img[y, x] > threshold else 0
    
    return np.clip(img, 0, 255).astype(np.uint8)

def apply_dithering(image, method, is_color=False, **kwargs):
    """Apply specified dithering method to image"""
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

def process_video(input_path, output_dir, method='floyd_steinberg', target_width=540, 
                 target_height=960, max_frames=720, is_color=False, **dither_params):
    """Process video with specified dithering method and export frames"""
    os.makedirs(output_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video file {input_path}")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video: {fps} fps, {total_frames} total frames")
    print(f"Processing up to {max_frames} frames using {method} dithering...")
    
    frame_count = 0
    
    with tqdm(total=min(max_frames, total_frames), desc="Processing frames") as pbar:
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.resize(frame, (target_width, target_height))
            
            if not is_color:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            dithered = apply_dithering(frame, method, is_color, **dither_params)
            
            filename = f"frame_{frame_count:04d}.png"
            cv2.imwrite(os.path.join(output_dir, filename), dithered)
            
            frame_count += 1
            pbar.update(1)
    
    cap.release()
    print(f"Exported {frame_count} frames to {output_dir}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Apply various dithering effects to video frames')
    
    parser.add_argument('input_video', help='Path to input video file')
    
    parser.add_argument('-o', '--output', default='frames',
                       help='Output directory for frames (default: frames)')
    
    parser.add_argument('-m', '--method', 
                       choices=['floyd_steinberg', 'atkinson', 'jarvis_judice_ninke', 'ordered', 'random'],
                       default='floyd_steinberg',
                       help='Dithering method (default: floyd_steinberg)')
    
    parser.add_argument('-w', '--width', type=int, default=540,
                       help='Target width for frames (default: 540)')
    
    parser.add_argument('--height', type=int, default=960,
                       help='Target height for frames (default: 960)')
    
    parser.add_argument('-f', '--frames', type=int, default=720,
                       help='Maximum number of frames to process (default: 720)')
    
    parser.add_argument('-c', '--color', action='store_true',
                       help='Process as color image (default: grayscale)')
    
    parser.add_argument('-d', '--dither-strength', type=float, default=1.0,
                       help='Dithering strength for error diffusion methods (0.0-1.0, default: 1.0)')
    
    parser.add_argument('--matrix-size', type=int, choices=[2, 4, 8], default=4,
                       help='Matrix size for ordered dithering (default: 4)')
    
    parser.add_argument('--threshold-variance', type=int, default=50,
                       help='Threshold variance for random dithering (default: 50)')
    
    parser.add_argument('--fps', type=int, default=30,
                       help='Frame rate for output video (default: 30)')
    
    return parser.parse_args()

def main():
    """Main entry point for the application"""
    args = parse_arguments()
    
    if hasattr(args, 'dither_strength') and not 0.0 <= args.dither_strength <= 1.0:
        print("Error: Dithering strength must be between 0.0 and 1.0")
        exit(1)
    
    print(f"Processing video: {args.input_video}")
    print(f"Output directory: {args.output}")
    print(f"Dithering method: {args.method}")
    print(f"Target dimensions: {args.width}x{args.height}")
    print(f"Max frames: {args.frames}")
    print(f"Color mode: {'Color' if args.color else 'Grayscale'}")
    print()
    
    dither_params = {}
    if args.method in ['floyd_steinberg', 'atkinson', 'jarvis_judice_ninke']:
        dither_params['dither_strength'] = args.dither_strength
    elif args.method == 'ordered':
        dither_params['matrix_size'] = args.matrix_size
    elif args.method == 'random':
        dither_params['threshold_variance'] = args.threshold_variance
    
    process_video(args.input_video, args.output, args.method, args.width, 
                 args.height, args.frames, args.color, **dither_params)
    
    print("\nDone! You can now create a video from frames using:")
    suffix = f"_{args.method}_{'color' if args.color else 'bw'}"
    print(f"ffmpeg -r {args.fps} -i {args.output}/frame_%04d.png -c:v libx264 -pix_fmt yuv420p output_dithered{suffix}.mp4")

if __name__ == "__main__":
    main()
