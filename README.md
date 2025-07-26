# Video Dithering Tool

A powerful Python tool for applying various dithering effects to video files, supporting both grayscale and color processing with multiple popular algorithms.

## Features

- **Five Popular Dithering Algorithms:**
  - Floyd-Steinberg dithering (error diffusion)
  - Atkinson dithering (reduced error bleeding)
  - Jarvis-Judice-Ninke dithering (distributed error diffusion)
  - Ordered dithering (Bayer matrices: 2x2, 4x4, 8x8)
  - Random dithering (organic noise patterns)

- **Flexible Processing:**
  - Grayscale and color mode support
  - Customizable output dimensions
  - Frame count limiting
  - Adjustable algorithm parameters

- **Professional Output:**
  - High-quality PNG frame export
  - FFmpeg integration for video creation
  - Progress tracking with tqdm
  - Comprehensive error handling

## Installation

### Prerequisites

- Python 3.7 or higher
- FFmpeg (for video reconstruction)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Development Installation

```bash
git clone https://github.com/yourusername/video-dithering-tool.git
cd video-dithering-tool
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```bash
# Apply Floyd-Steinberg dithering to a video
python video_dithering.py input.mp4

# Use Atkinson dithering with color processing
python video_dithering.py input.mp4 -m atkinson -c

# Apply ordered dithering with custom output directory
python video_dithering.py input.mp4 -m ordered -o my_frames
```

### Advanced Examples

```bash
# High-resolution color processing with custom settings
python video_dithering.py input.mp4 \
  --method jarvis_judice_ninke \
  --color \
  --width 1080 \
  --height 1920 \
  --frames 1440 \
  --dither-strength 0.8

# Ordered dithering with 8x8 Bayer matrix
python video_dithering.py input.mp4 \
  --method ordered \
  --matrix-size 8 \
  --width 720 \
  --height 1280

# Random dithering with high variance
python video_dithering.py input.mp4 \
  --method random \
  --threshold-variance 75 \
  --color
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `input_video` | Path to input video file | Required |
| `-o, --output` | Output directory for frames | `frames` |
| `-m, --method` | Dithering method | `floyd_steinberg` |
| `-w, --width` | Target width for frames | `540` |
| `--height` | Target height for frames | `960` |
| `-f, --frames` | Maximum frames to process | `720` |
| `-c, --color` | Process as color image | `False` |
| `-d, --dither-strength` | Error diffusion strength (0.0-1.0) | `1.0` |
| `--matrix-size` | Bayer matrix size (2, 4, 8) | `4` |
| `--threshold-variance` | Random dithering variance | `50` |
| `--fps` | Output video frame rate | `30` |

## Dithering Methods

### Floyd-Steinberg
Classic error diffusion algorithm that distributes quantization error to neighboring pixels.
```bash
python video_dithering.py input.mp4 -m floyd_steinberg -d 0.8
```

### Atkinson
Bill Atkinson's algorithm with reduced error bleeding, creating softer transitions.
```bash
python video_dithering.py input.mp4 -m atkinson -c
```

### Jarvis-Judice-Ninke
More distributed error diffusion pattern for smoother gradients.
```bash
python video_dithering.py input.mp4 -m jarvis_judice_ninke
```

### Ordered
Uses Bayer matrices for predictable, repeating patterns.
```bash
python video_dithering.py input.mp4 -m ordered --matrix-size 4
```

### Random
Adds random noise for organic, film-grain-like textures.
```bash
python video_dithering.py input.mp4 -m random --threshold-variance 60
```

## Creating Videos from Frames

After processing, use FFmpeg to create a video:

```bash
# Standard conversion
ffmpeg -r 30 -i frames/frame_%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4

# High quality with custom bitrate
ffmpeg -r 30 -i frames/frame_%04d.png -c:v libx264 -crf 18 -pix_fmt yuv420p output_hq.mp4

# GIF creation
ffmpeg -r 15 -i frames/frame_%04d.png -vf "palettegen" palette.png
ffmpeg -r 15 -i frames/frame_%04d.png -i palette.png -lavfi "paletteuse" output.gif
```

## Examples Gallery

### Portrait Video (9:16)
```bash
python video_dithering.py portrait.mp4 -m floyd_steinberg -w 540 --height 960
```

### Landscape Video (16:9)
```bash
python video_dithering.py landscape.mp4 -m atkinson -w 1920 --height 1080 -c
```

### Square Social Media (1:1)
```bash
python video_dithering.py square.mp4 -m ordered -w 1080 --height 1080
```

## Performance Tips

- **Frame Limiting:** Use `-f` to limit frames for testing
- **Resolution:** Lower resolution for faster processing
- **Method Selection:** Ordered dithering is fastest, error diffusion methods are slower
- **Color vs Grayscale:** Grayscale processing is ~3x faster

## Troubleshooting

### Common Issues

**"Cannot open video file"**
- Verify file path and format
- Ensure OpenCV supports the codec

**"Out of memory"**
- Reduce resolution or frame count
- Process in smaller batches

**"FFmpeg not found"**
- Install FFmpeg and add to PATH
- Use full path to FFmpeg executable

### Supported Formats

**Input:** MP4, AVI, MOV, MKV, WMV, FLV
**Output:** PNG frames, MP4 video (via FFmpeg)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Floyd-Steinberg algorithm creators
- Bill Atkinson for the Atkinson dithering method
- Jarvis, Judice, and Ninke for their error diffusion work
- OpenCV and NumPy communities
- FFmpeg project for video processing capabilities
