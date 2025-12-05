"""
Script to rename images to consistent format
darner_1.jpg, darner_2.jpg, skimmer_1.jpg, skimmer_2.jpg, etc.
"""

import os
from pathlib import Path

def rename_images():
    """Rename images to consistent format"""
    current_dir = Path(__file__).parent
    
    # Organize images by type
    darner_images = []
    skimmer_images = []
    generic_images = []
    
    for f in os.listdir(current_dir):
        if f.lower().endswith(('.jpg', '.jpeg', '.png')) and f != 'rename_images.py':
            f_lower = f.lower()
            if 'darner' in f_lower:
                darner_images.append(f)
            elif 'skimmer' in f_lower:
                skimmer_images.append(f)
            else:
                generic_images.append(f)
    
    # Sort for consistent ordering
    darner_images.sort()
    skimmer_images.sort()
    generic_images.sort()
    
    print(f"Found {len(darner_images)} darner images")
    print(f"Found {len(skimmer_images)} skimmer images")
    print(f"Found {len(generic_images)} generic images")
    
    # Rename darner images
    for i, old_name in enumerate(darner_images, 1):
        ext = Path(old_name).suffix
        new_name = f"darner_{i}{ext}"
        old_path = current_dir / old_name
        new_path = current_dir / new_name
        
        if old_path.exists() and old_path != new_path:
            # Check if new name already exists
            if new_path.exists():
                print(f"Warning: {new_name} already exists, skipping {old_name}")
            else:
                old_path.rename(new_path)
                print(f"Renamed: {old_name} -> {new_name}")
    
    # Rename skimmer images
    for i, old_name in enumerate(skimmer_images, 1):
        ext = Path(old_name).suffix
        new_name = f"skimmer_{i}{ext}"
        old_path = current_dir / old_name
        new_path = current_dir / new_name
        
        if old_path.exists() and old_path != new_path:
            if new_path.exists():
                print(f"Warning: {new_name} already exists, skipping {old_name}")
            else:
                old_path.rename(new_path)
                print(f"Renamed: {old_name} -> {new_name}")
    
    # Rename generic dragonfly images
    for i, old_name in enumerate(generic_images, 1):
        ext = Path(old_name).suffix
        new_name = f"dragonfly_{i}{ext}"
        old_path = current_dir / old_name
        new_path = current_dir / new_name
        
        if old_path.exists() and old_path != new_path:
            if new_path.exists():
                print(f"Warning: {new_name} already exists, skipping {old_name}")
            else:
                old_path.rename(new_path)
                print(f"Renamed: {old_name} -> {new_name}")
    
    print("\nRenaming complete!")

if __name__ == "__main__":
    rename_images()




