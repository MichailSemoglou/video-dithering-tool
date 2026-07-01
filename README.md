# Video Dithering Tool

A Python tool that applies dithering effects to video files, frame by frame. It implements five algorithms, Floyd-Steinberg (Floyd & Steinberg, 1976), Atkinson, Jarvis-Judice-Ninke (Jarvis, Judice & Ninke, 1976), ordered (Bayer) dithering (Bayer, 1973), and random threshold dithering, then hands the frames to FFmpeg or exports them directly as an animated GIF.

v1.0.0 · released October 2025 · MIT

## What is Dithering?

Dithering is a technique that creates the illusion of color depth in images with a limited color palette. It is commonly used to create:

- **Retro/vintage aesthetics** (like old computer graphics)
- **Artistic effects** with reduced color palettes
- **Print-style graphics** with dot patterns
- **Low-fi video effects** for social media

## Features

### Five Dithering Algorithms

- **Floyd-Steinberg** – Error diffusion with smooth gradients
- **Atkinson** – Softer transitions, developed for early Macintosh computers
- **Jarvis-Judice-Ninke** – Distributed error diffusion for smoother results
- **Ordered (Bayer)** – Regular dot patterns in 2x2, 4x4, or 8x8 grids
- **Random** – Pseudo-random threshold noise for a film-grain look

### Processing Options

- **Color and grayscale** processing
- **Custom output dimensions** for different social media formats
- **Frame limiting** for quick previews
- **Adjustable effect intensity**
- **Direct animated GIF export**, with frames mapped exactly onto the dithering palette (no extra lossy re-quantization)

## Installation

### Step 1: Install Python

Download Python 3.7 or higher from [python.org](https://www.python.org/downloads/)

### Step 2: Install FFmpeg

**Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html)  
**Mac:** Install via Homebrew: `brew install ffmpeg`  
**Linux:** `sudo apt install ffmpeg`

### Step 3: Download and Setup

```bash
# Download the project
git clone https://github.com/MichailSemoglou/video-dithering-tool.git
cd video-dithering-tool

# Install dependencies
pip install -r requirements.txt
```

## Quick Start Guide

### Basic Usage (Copy and paste these commands)

```bash
# Apply Floyd-Steinberg dithering to your video
python video_dithering.py your_video.mp4

# For stronger dithering effect, use color mode
python video_dithering.py your_video.mp4 --color

# Try different algorithms
python video_dithering.py your_video.mp4 -m atkinson --color
python video_dithering.py your_video.mp4 -m ordered
python video_dithering.py your_video.mp4 -m random
```

### Understanding the Output

The tool creates a folder called `frames/` containing PNG images of each processed frame. Use FFmpeg to turn these frames back into a video.

## Creating a Prominent Dithering Effect

To make the dithering pattern more visible and dramatic:

1. **Process at a low resolution** (e.g., 135x240)
2. **Scale up the frames** using FFmpeg with nearest-neighbor interpolation

### Step 1: Extract low-res dithered frames

```bash
python video_dithering.py input.mp4 -w 135 --height 240 -d 1.0
```

### Step 2: Reassemble and scale up with FFmpeg

```bash
ffmpeg -r 30 -i frames/frame_%04d.png -vf scale=540:960:flags=neighbor -c:v libx264 -pix_fmt yuv420p output_dithered.mp4
```

**Why this works:**

- `flags=neighbor` ensures sharp, pixelated scaling (no smoothing)
- Low resolution makes dithering patterns more visible
- Scaling up preserves the chunky, retro aesthetic
- You can adjust the scale to any desired output size

## Social Media Formats

### Instagram/TikTok Stories (9:16)

```bash
# Standard resolution
python video_dithering.py input.mp4 -w 540 --height 960 -m floyd_steinberg --color

# High resolution for better quality
python video_dithering.py input.mp4 -w 1080 --height 1920 -m atkinson --color
```

### Instagram Posts (1:1)

```bash
python video_dithering.py input.mp4 -w 1080 --height 1080 -m ordered --matrix-size 4
```

### YouTube/Landscape (16:9)

```bash
python video_dithering.py input.mp4 -w 1920 --height 1080 -m jarvis_judice_ninke --color
```

### Twitter/X (16:9)

```bash
python video_dithering.py input.mp4 -w 1280 --height 720 -m random --threshold-variance 60
```

## Command Reference

### Required

- `input_video` – Path to your video file (MP4, AVI, MOV, etc.)

### Common Options

| Option         | What it does                                 | Example         |
| -------------- | -------------------------------------------- | --------------- |
| `-m, --method` | Choose dithering style                       | `-m atkinson`   |
| `-c, --color`  | Keep colors (vs black & white)               | `--color`       |
| `-w, --width`  | Video width in pixels                        | `-w 1080`       |
| `--height`     | Video height in pixels                       | `--height 1920` |
| `-f, --frames` | Limit frames (for testing)                   | `-f 120`        |
| `-o, --output` | Output folder/file name                      | `-o my_frames`  |
| `--gif`        | Export an animated GIF instead of PNG frames | `--gif`         |

### Advanced Options

| Option                  | What it does                            | Default | Example                   |
| ----------------------- | --------------------------------------- | ------- | ------------------------- |
| `-d, --dither-strength` | Effect intensity (0.0–1.0)              | 1.0     | `-d 0.5`                  |
| `--matrix-size`         | Dot pattern size (2, 4, 8)              | 4       | `--matrix-size 8`         |
| `--threshold-variance`  | Random noise amount                     | 50      | `--threshold-variance 75` |
| `--fps`                 | Output video framerate / GIF frame rate | 30      | `--fps 24`                |
| `--gif-loop`            | GIF loop count, 0 = infinite            | 0       | `--gif-loop 1`            |

## Dithering Methods Explained

### Floyd-Steinberg (`floyd_steinberg`)

Implements the error-diffusion algorithm of Floyd & Steinberg (1976).

**Best for:** General use, smooth gradients  
**Look:** Classic dithering with flowing patterns

```bash
python video_dithering.py input.mp4 -m floyd_steinberg --color
```

### Atkinson (`atkinson`)

Implements Bill Atkinson’s dithering algorithm, developed for early Macintosh graphics.

**Best for:** Retro computer aesthetic, softer look  
**Look:** Less aggressive than Floyd-Steinberg, reminiscent of early Mac graphics

```bash
python video_dithering.py input.mp4 -m atkinson --color
```

### Jarvis-Judice-Ninke (`jarvis_judice_ninke`)

Implements the error-diffusion algorithm of Jarvis, Judice & Ninke (1976).

**Best for:** Smoother results, less visible patterns  
**Look:** Most subtle dithering, good for maintaining detail

```bash
python video_dithering.py input.mp4 -m jarvis_judice_ninke --color
```

### Ordered/Bayer (`ordered`)

Implements the ordered dither matrix of Bayer (1973).

**Best for:** Regular patterns, newspaper/comic book effects  
**Look:** Visible dot grids, very graphic and geometric

```bash
python video_dithering.py input.mp4 -m ordered --matrix-size 4
python video_dithering.py input.mp4 -m ordered --matrix-size 8  # Bigger dots
```

### Random (`random`)

Applies pseudo-random threshold noise per pixel.

**Best for:** Film grain, organic textures  
**Look:** Noisy, film-like quality

```bash
python video_dithering.py input.mp4 -m random --threshold-variance 60
```

## Direct GIF Export

Instead of exporting PNG frames and stitching them together yourself, you can export an animated GIF directly:

```bash
# Export straight to an animated GIF
python video_dithering.py input.mp4 --gif -m ordered --matrix-size 4

# Choose your own output filename and loop once instead of looping forever
python video_dithering.py input.mp4 --gif -o my_animation --gif-loop 1 --color
```

The GIF’s palette is built from the exact colors used during dithering (the default 8-color palette, or black/white in grayscale mode), so each pixel is mapped onto its palette color directly rather than being re-quantized by a generic GIF encoder. This avoids the double-dithering and color-shift artifacts that FFmpeg’s `palettegen`/`paletteuse` filters otherwise produce.

If `-o/--output` is left at its default, the GIF is written to `output.gif`; otherwise `.gif` is appended automatically when the filename does not include it.

## Creating Your Final Video

If you would rather assemble an MP4, or want more control than the `--gif` flag gives, you will have a folder full of PNG frames. Use these FFmpeg commands to create your final video:

### Standard Quality

```bash
ffmpeg -r 30 -i frames/frame_%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4
```

### High Quality (Recommended)

```bash
ffmpeg -r 30 -i frames/frame_%04d.png -c:v libx264 -crf 18 -pix_fmt yuv420p output_hq.mp4
```

### For Social Media (Smaller file size)

```bash
ffmpeg -r 30 -i frames/frame_%04d.png -c:v libx264 -crf 28 -preset fast output_social.mp4
```

### Create an Animated GIF

```bash
# Generate color palette
ffmpeg -r 15 -i frames/frame_%04d.png -vf "palettegen" palette.png

# Create GIF with palette
ffmpeg -r 15 -i frames/frame_%04d.png -i palette.png -lavfi "paletteuse" output.gif
```

## Workflow Tips for Designers

### 1. Start Small and Fast

Always test with a short clip first:

```bash
python video_dithering.py input.mp4 -f 60 -m floyd_steinberg
```

This processes only 60 frames (~2 seconds) so you can see the effect quickly.

### 2. Resolution Strategy

- **Low-res + upscale** = More visible, chunky dithering
- **High-res direct** = Subtle, professional dithering
- **Medium-res** = Balanced approach

### 3. Color vs Grayscale

- **Grayscale** (default): Faster processing, classic look
- **Color** (`--color` flag): More vibrant, modern retro feel

### 4. Performance Tips

- **Ordered dithering** is fastest
- **Random dithering** is fast
- **Error diffusion** methods (Floyd-Steinberg, Atkinson, JJN) are slower but higher quality
- **Grayscale processing** is ~3x faster than color

## Troubleshooting

### "Cannot open video file"

- Check your file path is correct
- Make sure the video format is supported (MP4, AVI, MOV, MKV, WMV, FLV)
- Try a different video file to test

### "FFmpeg not found"

- Make sure FFmpeg is installed and in your system PATH
- Try using the full path: `/usr/local/bin/ffmpeg` instead of just `ffmpeg`

### "Out of memory" errors

- Reduce resolution: `-w 270 --height 480`
- Process fewer frames: `-f 300`
- Close other applications

### Processing is too slow

- Use ordered dithering: `-m ordered`
- Lower resolution for testing
- Skip color processing (remove `--color`)

### Effect is too subtle

- Use low resolution and scale up (see “Creating a Prominent Dithering Effect”)
- Try ordered dithering with larger matrices: `--matrix-size 8`
- Increase random variance: `--threshold-variance 100`

## Project Examples

### Retro Gaming Aesthetic

```bash
python video_dithering.py gameplay.mp4 -m ordered --matrix-size 4 -w 320 --height 240
ffmpeg -r 30 -i frames/frame_%04d.png -vf scale=1280:960:flags=neighbor -c:v libx264 output.mp4
```

### Vintage Computer Look

```bash
python video_dithering.py input.mp4 -m atkinson --color -w 512 --height 384
ffmpeg -r 30 -i frames/frame_%04d.png -vf scale=1024:768:flags=neighbor -c:v libx264 output.mp4
```

### Artistic Black & White

```bash
python video_dithering.py input.mp4 -m jarvis_judice_ninke -d 0.8 -w 540 --height 960
```

### Film Grain Effect

```bash
python video_dithering.py input.mp4 -m random --threshold-variance 30 --color
```

## Supported Formats

**Input:** MP4, AVI, MOV, MKV, WMV, FLV  
**Output:** PNG frames → MP4/GIF via FFmpeg

## Contributing

Report bugs or suggest features by [opening an issue](https://github.com/MichailSemoglou/video-dithering-tool/issues) on GitHub.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Credits

- **Floyd-Steinberg algorithm** – Floyd & Steinberg (1976)
- **Atkinson dithering** – Bill Atkinson, Apple Computer
- **Jarvis-Judice-Ninke** – Jarvis, Judice & Ninke (1976)
- **Ordered (Bayer) dithering** – Bayer (1973)
- Built with **OpenCV**, **NumPy**, and **FFmpeg**

---

For further help, [open an issue](https://github.com/MichailSemoglou/video-dithering-tool/issues) or see the troubleshooting section above.
