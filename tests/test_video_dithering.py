import unittest
import numpy as np
import cv2
import tempfile
import os
import sys
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from video_dithering import (
    floyd_steinberg_dither,
    atkinson_dither,
    jarvis_judice_ninke_dither,
    ordered_dither,
    random_dither,
    apply_dithering,
    frame_to_gif_image,
    DEFAULT_COLOR_PALETTE
)

class TestDitheringMethods(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures with sample images"""
        self.grayscale_image = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        self.color_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        
    def test_floyd_steinberg_grayscale(self):
        """Test Floyd-Steinberg dithering on grayscale image"""
        result = floyd_steinberg_dither(self.grayscale_image, dither_strength=1.0)
        
        self.assertEqual(result.shape, self.grayscale_image.shape)
        self.assertEqual(result.dtype, np.uint8)
        self.assertTrue(np.all((result == 0) | (result == 255)))
        
    def test_floyd_steinberg_color(self):
        """Test Floyd-Steinberg dithering on color image"""
        palette = [(0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0)]
        result = floyd_steinberg_dither(self.color_image, dither_strength=1.0, 
                                      is_color=True, palette=palette)
        
        self.assertEqual(result.shape, self.color_image.shape)
        self.assertEqual(result.dtype, np.uint8)
        
    def test_atkinson_dither(self):
        """Test Atkinson dithering"""
        result = atkinson_dither(self.grayscale_image, dither_strength=1.0)
        
        self.assertEqual(result.shape, self.grayscale_image.shape)
        self.assertEqual(result.dtype, np.uint8)
        self.assertTrue(np.all((result == 0) | (result == 255)))
        
    def test_jarvis_judice_ninke_dither(self):
        """Test Jarvis-Judice-Ninke dithering"""
        result = jarvis_judice_ninke_dither(self.grayscale_image, dither_strength=1.0)
        
        self.assertEqual(result.shape, self.grayscale_image.shape)
        self.assertEqual(result.dtype, np.uint8)
        self.assertTrue(np.all((result == 0) | (result == 255)))
        
    def test_ordered_dither(self):
        """Test ordered dithering with different matrix sizes"""
        for matrix_size in [2, 4, 8]:
            result = ordered_dither(self.grayscale_image, matrix_size=matrix_size)
            
            self.assertEqual(result.shape, self.grayscale_image.shape)
            self.assertEqual(result.dtype, np.uint8)
            self.assertTrue(np.all((result == 0) | (result == 255)))

    def test_ordered_dither_color_multi_color_palette_uses_threshold(self):
        """Ordered dithering with a >2-color palette should vary by pixel position.

        A uniform-gray input is equidistant from no single palette color, so its
        nearest color is fixed for every pixel unless the Bayer threshold actually
        perturbs the pixel before quantizing. If the threshold were ignored (as it
        was before the fix), every pixel would quantize to the same single color.
        """
        palette = [(0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0)]
        uniform_image = np.full((8, 8, 3), 128, dtype=np.uint8)

        result = ordered_dither(uniform_image, matrix_size=4, is_color=True, palette=palette)

        unique_colors = np.unique(result.reshape(-1, 3), axis=0)
        self.assertGreater(len(unique_colors), 1)
        for color in unique_colors:
            self.assertTrue(any(np.array_equal(color, p) for p in palette))

    def test_random_dither(self):
        """Test random dithering"""
        result = random_dither(self.grayscale_image, threshold_variance=50)
        
        self.assertEqual(result.shape, self.grayscale_image.shape)
        self.assertEqual(result.dtype, np.uint8)
        self.assertTrue(np.all((result == 0) | (result == 255)))
        
    def test_apply_dithering_method_selection(self):
        """Test apply_dithering function with different methods"""
        methods = ['floyd_steinberg', 'atkinson', 'jarvis_judice_ninke', 'ordered', 'random']
        
        for method in methods:
            result = apply_dithering(self.grayscale_image, method)
            
            self.assertEqual(result.shape, self.grayscale_image.shape)
            self.assertEqual(result.dtype, np.uint8)
            
    def test_invalid_method(self):
        """Test apply_dithering with invalid method"""
        with self.assertRaises(ValueError):
            apply_dithering(self.grayscale_image, 'invalid_method')
            
    def test_dither_strength_boundaries(self):
        """Test dithering with boundary strength values"""
        result_zero = floyd_steinberg_dither(self.grayscale_image, dither_strength=0.0)
        result_full = floyd_steinberg_dither(self.grayscale_image, dither_strength=1.0)
        
        self.assertEqual(result_zero.shape, self.grayscale_image.shape)
        self.assertEqual(result_full.shape, self.grayscale_image.shape)
        
    def test_color_palette_consistency(self):
        """Test that color dithering uses only palette colors"""
        palette = [(0, 0, 0), (255, 255, 255)]
        result = floyd_steinberg_dither(self.color_image, is_color=True, palette=palette)
        
        unique_colors = np.unique(result.reshape(-1, 3), axis=0)
        
        for color in unique_colors:
            self.assertTrue(any(np.array_equal(color, p) for p in palette))

class TestImageProperties(unittest.TestCase):
    
    def test_small_image(self):
        """Test dithering on very small image"""
        small_image = np.array([[100, 150], [200, 50]], dtype=np.uint8)
        result = floyd_steinberg_dither(small_image)
        
        self.assertEqual(result.shape, small_image.shape)
        self.assertTrue(np.all((result == 0) | (result == 255)))
        
    def test_single_pixel(self):
        """Test dithering on single pixel"""
        single_pixel = np.array([[128]], dtype=np.uint8)
        result = floyd_steinberg_dither(single_pixel)
        
        self.assertEqual(result.shape, single_pixel.shape)
        self.assertTrue(result[0, 0] in [0, 255])
        
    def test_uniform_image(self):
        """Test dithering on uniform gray image"""
        uniform_image = np.full((50, 50), 128, dtype=np.uint8)
        result = floyd_steinberg_dither(uniform_image)
        
        self.assertEqual(result.shape, uniform_image.shape)
        self.assertTrue(np.all((result == 0) | (result == 255)))

class TestParameterValidation(unittest.TestCase):
    
    def setUp(self):
        self.test_image = np.random.randint(0, 256, (50, 50), dtype=np.uint8)
        
    def test_matrix_size_validation(self):
        """Test ordered dithering with valid matrix sizes"""
        valid_sizes = [2, 4, 8]
        
        for size in valid_sizes:
            result = ordered_dither(self.test_image, matrix_size=size)
            self.assertEqual(result.shape, self.test_image.shape)
            
    def test_threshold_variance_range(self):
        """Test random dithering with different variance values"""
        variance_values = [0, 25, 50, 100]
        
        for variance in variance_values:
            result = random_dither(self.test_image, threshold_variance=variance)
            self.assertEqual(result.shape, self.test_image.shape)

class TestGifExport(unittest.TestCase):

    def setUp(self):
        self.grayscale_image = np.random.randint(0, 256, (20, 20), dtype=np.uint8)
        self.color_image = np.random.randint(0, 256, (20, 20, 3), dtype=np.uint8)

    def test_frame_to_gif_image_grayscale(self):
        """Grayscale dithered frames should convert to a 2-color palette image"""
        dithered = floyd_steinberg_dither(self.grayscale_image)
        gif_image = frame_to_gif_image(dithered, is_color=False)

        self.assertIsInstance(gif_image, Image.Image)
        self.assertEqual(gif_image.mode, 'P')
        self.assertEqual(gif_image.size, (20, 20))

    def test_frame_to_gif_image_color_exact_palette(self):
        """Color dithered frames should map exactly onto the dithering palette"""
        # Palette is in OpenCV's BGR channel order, matching frame_to_gif_image's input.
        # The intended *visible* RGB colors are written out literally below (not derived
        # by reproducing the function's own BGR-to-RGB conversion) so this test fails if
        # that conversion is missing or wrong: black, white, blue, green.
        bgr_palette = [(0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0)]
        expected_rgb_colors = {(0, 0, 0), (255, 255, 255), (0, 0, 255), (0, 255, 0)}

        # Build the frame directly from the palette (rather than running actual
        # dithering on random data) so every palette entry is guaranteed to appear;
        # dithering's nearest-color selection isn't guaranteed to hit every entry.
        rows = [bgr_palette[x % len(bgr_palette)] for x in range(20)]
        dithered = np.array([rows for _ in range(20)], dtype=np.uint8)

        gif_image = frame_to_gif_image(dithered, is_color=True, palette=bgr_palette)

        self.assertIsInstance(gif_image, Image.Image)
        self.assertEqual(gif_image.mode, 'P')

        rgb_image = gif_image.convert('RGB')
        result_colors = {tuple(int(v) for v in color)
                          for color in np.array(rgb_image).reshape(-1, 3)}

        self.assertEqual(result_colors, expected_rgb_colors)

    def test_frame_to_gif_image_default_palette(self):
        """When no palette is supplied, the default color palette should be used"""
        dithered = floyd_steinberg_dither(self.color_image, is_color=True)
        gif_image = frame_to_gif_image(dithered, is_color=True, palette=None)

        self.assertIsInstance(gif_image, Image.Image)
        self.assertLessEqual(len(gif_image.getcolors(maxcolors=256)), len(DEFAULT_COLOR_PALETTE))

if __name__ == '__main__':
    unittest.main()
