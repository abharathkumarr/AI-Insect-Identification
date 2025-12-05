"""
Generate test cases CSV from images in the original folder
Automatically determines expected_species based on image name
"""

import csv
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from config import TEST_DATA_DIR, TEST_CASES_CSV, ORIGINAL_IMAGES_DIR

def determine_expected_species(image_name):
    """Determine expected species from image name"""
    name_lower = image_name.lower()
    
    if "darner" in name_lower:
        return "darner"
    elif "skimmer" in name_lower:
        return "skimmer"
    else:
        return "dragonfly"  # Generic fallback

def generate_test_cases():
    """Generate test cases CSV from images"""
    original_dir = Path(ORIGINAL_IMAGES_DIR)
    test_data_dir = Path(TEST_DATA_DIR)
    test_data_dir.mkdir(exist_ok=True)
    
    test_cases_file = Path(TEST_CASES_CSV)
    
    # Find all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    images = []
    
    for ext in image_extensions:
        images.extend(list(original_dir.glob(f"*{ext}")))
        images.extend(list(original_dir.glob(f"*{ext.upper()}")))
    
    # Sort images
    images.sort()
    
    print(f"Found {len(images)} images in {original_dir}")
    
    # Generate test cases
    test_cases = []
    test_id_counter = 1
    
    for image_path in images:
        image_name = image_path.name
        expected_species = determine_expected_species(image_name)
        
        test_case = {
            "test_id": f"TC{test_id_counter:03d}",
            "image_name": image_name,
            "expected_species": expected_species,
            "image_type": "original",
            "augmentation": "none",
        }
        
        test_cases.append(test_case)
        test_id_counter += 1
    
    # Write to CSV
    if test_cases:
        with open(test_cases_file, 'w', newline='') as f:
            fieldnames = ['test_id', 'image_name', 'expected_species', 'image_type', 'augmentation']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(test_cases)
        
        print(f"\nGenerated {len(test_cases)} test cases:")
        print(f"  - Darner: {sum(1 for tc in test_cases if tc['expected_species'] == 'darner')}")
        print(f"  - Skimmer: {sum(1 for tc in test_cases if tc['expected_species'] == 'skimmer')}")
        print(f"  - Generic: {sum(1 for tc in test_cases if tc['expected_species'] == 'dragonfly')}")
        print(f"\nTest cases saved to: {test_cases_file}")
        
        # Print first few test cases as preview
        print("\nPreview of test cases:")
        for tc in test_cases[:5]:
            print(f"  {tc['test_id']}: {tc['image_name']} -> {tc['expected_species']}")
        if len(test_cases) > 5:
            print(f"  ... and {len(test_cases) - 5} more")
    else:
        print("No images found to generate test cases!")

if __name__ == "__main__":
    generate_test_cases()




