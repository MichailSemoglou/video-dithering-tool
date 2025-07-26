import unittest
import numpy as np
import cv2
import tempfile
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from video_dithering import (
    floyd_steinberg_dither,
    atkinson_dither,
    jarvis_judice_ninke_dither,
    ordered_dither,
    random_dither,
    apply_dithering
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

if __name__ == '__main__':
    unittest.main()
