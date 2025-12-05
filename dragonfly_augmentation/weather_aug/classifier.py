"""
Simple Weather Classification Model for Test Automation.

This module provides a pre-trained-like weather classifier that can be used
to evaluate how weather augmentations affect image predictions.

Classes: cloudy, fogsmog, rain, shine, sunrise
"""

import numpy as np
from PIL import Image
import cv2


class WeatherClassifier:
    """
    Lightweight weather classifier for demonstration purposes.
    
    Since training a full model is beyond the scope of this assignment,
    this provides a rule-based classifier that analyzes image properties
    to simulate a trained model's predictions.
    """
    
    def __init__(self):
        self.classes = ['cloudy', 'fogsmog', 'rain', 'shine', 'sunrise']
        self.input_size = (224, 224)
    
    def predict(self, image: np.ndarray) -> dict:
        """
        Predict weather class probabilities for an image.
        
        Args:
            image: RGB image as numpy array (H x W x 3)
            
        Returns:
            Dict with class names as keys and confidence scores as values
        """
        # Resize image
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        img_resized = cv2.resize(image, self.input_size)
        
        # Extract features
        brightness = np.mean(img_resized)
        contrast = np.std(img_resized)
        blue_channel = np.mean(img_resized[:, :, 2])
        red_channel = np.mean(img_resized[:, :, 0])
        green_channel = np.mean(img_resized[:, :, 1])
        
        # Rule-based scoring (simulates neural network output)
        scores = {}
        
        # Cloudy: moderate brightness, low contrast, grayish
        cloudiness = 1.0 - abs(brightness - 120) / 120
        scores['cloudy'] = max(0, cloudiness * 0.6 + (1 - contrast/50) * 0.4)
        
        # Fog: low contrast, high brightness, whitish
        foginess = (brightness / 255) * 0.5 + (1 - contrast/80) * 0.5
        scores['fogsmog'] = max(0, foginess)
        
        # Rain: low brightness, blue tint
        raininess = (1 - brightness/255) * 0.6 + (blue_channel / 255) * 0.4
        scores['rain'] = max(0, raininess)
        
        # Shine: high brightness, high contrast
        shininess = (brightness / 255) * 0.6 + (contrast/80) * 0.4
        scores['shine'] = max(0, shininess)
        
        # Sunrise: warm tones (red/orange)
        warmth = (red_channel / 255) * 0.5 + ((red_channel - blue_channel) / 255) * 0.5
        scores['sunrise'] = max(0, warmth)
        
        # Normalize to sum to 1
        total = sum(scores.values())
        if total > 0:
            probabilities = {k: v / total for k, v in scores.items()}
        else:
            probabilities = {k: 1.0 / len(self.classes) for k in self.classes}
        
        return probabilities
    
    def get_top_prediction(self, image: np.ndarray) -> tuple:
        """
        Get the top predicted class and its confidence.
        
        Returns:
            Tuple of (class_name, confidence)
        """
        probs = self.predict(image)
        top_class = max(probs, key=probs.get)
        return top_class, probs[top_class]
    
    def predict_with_details(self, image: np.ndarray) -> dict:
        """
        Get full prediction details including top 3 classes.
        
        Returns:
            Dict with 'predictions' (all probabilities) and 'top_3' (list of tuples)
        """
        probs = self.predict(image)
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'predictions': probs,
            'top_3': sorted_probs[:3],
            'predicted_class': sorted_probs[0][0],
            'confidence': sorted_probs[0][1]
        }
