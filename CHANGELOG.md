# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-07-01

### Fixed

- Fixed `ordered_dither` ignoring the Bayer threshold for palettes with more
  than two colors. The threshold is now applied as a Bayer-derived offset
  before nearest-color matching, following the generalized ordered dithering
  method in Ulichney (1987).
- Fixed `ordered_dither` computing tile-repeat counts from the requested
  `matrix_size` instead of the actual Bayer matrix dimensions. Any
  `matrix_size` outside `{2, 4}` falls back to an 8x8 matrix, and using the
  requested size to size the tiling produced thresholds smaller than the
  image, breaking the `img > thresholds` broadcast.

### Changed

- Added type hints and Google-style docstrings throughout `video_dithering.py`.
- Vectorized `ordered_dither` and `random_dither` for performance.
- Wrapped video capture release in a `try`/`finally` block for resource safety.
- Added input validation for width, height, and frame count in `main`.

## [1.0.0] - 2025-10-20

### Added

- Initial release: a command-line tool implementing five dithering
  algorithms (Floyd-Steinberg, Atkinson, Jarvis-Judice-Ninke, ordered,
  random) with PNG-frame and GIF video export.
