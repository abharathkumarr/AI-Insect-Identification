"""
Test Data Management for Dragonfly Test Cases
Handles CSV/Excel test data and image paths
"""

import csv
import os
import logging
from pathlib import Path
from typing import List, Dict

from config import (
    TEST_DATA_DIR,
    TEST_CASES_CSV,
    ORIGINAL_IMAGES_DIR,
    AUGMENTED_IMAGES_DIR,
)

logger = logging.getLogger(__name__)


class TestDataManager:
    """Manages test data and test cases"""
    
    def __init__(self):
        self.test_data_dir = Path(TEST_DATA_DIR)
        self.test_data_dir.mkdir(exist_ok=True)
        self.test_cases_file = Path(TEST_CASES_CSV)
        self.original_images_dir = Path(ORIGINAL_IMAGES_DIR)
        self.augmented_images_dir = Path(AUGMENTED_IMAGES_DIR)
    
    def create_default_test_cases(self):
        """Create default test cases CSV if it doesn't exist"""
        if self.test_cases_file.exists():
            logger.info(f"Test cases file already exists: {self.test_cases_file}")
            return
        
        logger.info("Creating default test cases file...")
        
        # Default test cases for dragonfly images
        default_cases = [
            {
                "test_id": "TC001",
                "image_name": "dragonfly_closeup_1.jpg",
                "expected_species": "dragonfly",
                "image_type": "original",
                "augmentation": "none",
            },
            {
                "test_id": "TC002",
                "image_name": "dragonfly_in_flight_3.jpg",
                "expected_species": "dragonfly",
                "image_type": "original",
                "augmentation": "none",
            },
            {
                "test_id": "TC003",
                "image_name": "dragonfly_perched_on_leaf_2.jpg",
                "expected_species": "dragonfly",
                "image_type": "original",
                "augmentation": "none",
            },
        ]
        
        self.save_test_cases(default_cases)
        logger.info(f"Created default test cases file: {self.test_cases_file}")
    
    def save_test_cases(self, test_cases: List[Dict]):
        """Save test cases to CSV file"""
        try:
            with open(self.test_cases_file, 'w', newline='') as f:
                if not test_cases:
                    return
                
                fieldnames = test_cases[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(test_cases)
            
            logger.info(f"Saved {len(test_cases)} test cases to {self.test_cases_file}")
            
        except Exception as e:
            logger.error(f"Error saving test cases: {str(e)}")
            raise
    
    def load_test_cases(self) -> List[Dict]:
        """Load test cases from CSV file"""
        try:
            if not self.test_cases_file.exists():
                logger.warning("Test cases file not found, creating default...")
                self.create_default_test_cases()
            
            test_cases = []
            with open(self.test_cases_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    test_cases.append(row)
            
            logger.info(f"Loaded {len(test_cases)} test cases from {self.test_cases_file}")
            return test_cases
            
        except Exception as e:
            logger.error(f"Error loading test cases: {str(e)}")
            return []
    
    def get_image_path(self, image_name: str, image_type: str = "original") -> Path:
        """
        Get full path to test image
        
        Args:
            image_name: Name of the image file
            image_type: 'original' or 'augmented'
            
        Returns:
            Path object to the image file
        """
        if image_type == "original":
            image_path = self.original_images_dir / image_name
        else:
            image_path = self.augmented_images_dir / image_name
        
        if not image_path.exists():
            logger.warning(f"Image not found: {image_path}")
            # Try alternative locations
            alt_paths = [
                Path("samples/original") / image_name,
                Path("samples/augmented") / image_name,
                Path("../dragonfly_augmentation/samples/original") / image_name,
                Path("../dragonfly_augmentation/samples/augmented") / image_name,
            ]
            
            for alt_path in alt_paths:
                if alt_path.exists():
                    logger.info(f"Found image at alternative location: {alt_path}")
                    return alt_path
        
        return image_path
    
    def add_augmented_test_cases(self, original_image: str, augmentation_effects: List[str]):
        """
        Add test cases for augmented images
        
        Args:
            original_image: Name of original image
            augmentation_effects: List of augmentation effect names
        """
        existing_cases = self.load_test_cases()
        
        # Find base test ID
        base_test_id = None
        for case in existing_cases:
            if case.get("image_name") == original_image:
                base_test_id = case.get("test_id", "TC000")
                break
        
        if not base_test_id:
            base_test_id = f"TC{len(existing_cases) + 1:03d}"
        
        # Add augmented test cases
        new_cases = []
        for i, effect in enumerate(augmentation_effects):
            augmented_name = f"{Path(original_image).stem}_{effect}.png"
            test_id = f"{base_test_id}_AUG{i+1:02d}"
            
            new_cases.append({
                "test_id": test_id,
                "image_name": augmented_name,
                "expected_species": "dragonfly",
                "image_type": "augmented",
                "augmentation": effect,
            })
        
        # Add to existing cases
        existing_cases.extend(new_cases)
        self.save_test_cases(existing_cases)
        
        logger.info(f"Added {len(new_cases)} augmented test cases")
    
    def list_available_images(self, image_type: str = "original") -> List[str]:
        """List all available test images"""
        if image_type == "original":
            image_dir = self.original_images_dir
        else:
            image_dir = self.augmented_images_dir
        
        if not image_dir.exists():
            logger.warning(f"Image directory not found: {image_dir}")
            return []
        
        # Supported image extensions
        extensions = ['.jpg', '.jpeg', '.png', '.webp']
        
        images = []
        for ext in extensions:
            images.extend(list(image_dir.glob(f"*{ext}")))
            images.extend(list(image_dir.glob(f"*{ext.upper()}")))
        
        return [img.name for img in images]




