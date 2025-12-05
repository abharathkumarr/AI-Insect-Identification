"""Batch-generate augmented samples from images in samples/original.

Usage:
    1. Place one or more images into samples/original/.
    2. Run: python generate_samples.py
    3. Augmented images will be written into samples/augmented/.
"""

import os
from glob import glob
from datetime import datetime

import cv2
import numpy as np

from weather_aug.augmentor import WeatherAugmentor

SAMPLES_ORIGINAL_DIR = os.path.join("samples", "original")
SAMPLES_AUGMENTED_DIR = os.path.join("samples", "augmented")


def ensure_dirs():
    os.makedirs(SAMPLES_ORIGINAL_DIR, exist_ok=True)
    os.makedirs(SAMPLES_AUGMENTED_DIR, exist_ok=True)


def save_np_image(arr: np.ndarray, base_name: str, effect: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{base_name}_{effect}_{ts}.png"
    path = os.path.join(SAMPLES_AUGMENTED_DIR, fname)
    # OpenCV expects BGR
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    cv2.imwrite(path, bgr)
    return path


def main():
    ensure_dirs()
    image_paths = glob(os.path.join(SAMPLES_ORIGINAL_DIR, "*"))

    if not image_paths:
        print(f"No images found in {SAMPLES_ORIGINAL_DIR}. Please add images and try again.")
        return

    effects = ["rain", "snow", "fog", "night", "sunny", "autumn", "motion_blur"]
    augmentor = WeatherAugmentor(intensity="medium")

    for img_path in image_paths:
        base = os.path.splitext(os.path.basename(img_path))[0]
        bgr = cv2.imread(img_path)
        if bgr is None:
            print(f"Skipping unreadable image: {img_path}")
            continue
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

        for effect in effects:
            try:
                aug = augmentor.apply_effect(rgb, effect)
                out_path = save_np_image(aug, base_name=base, effect=effect)
                log_augmentation(effect, os.path.basename(img_path))
                print(f"Saved {effect} image to {out_path}")
            except Exception as e:
                print(f"Failed to apply {effect} to {img_path}: {e}")


def log_augmentation(effect: str, filename: str):
    """Log augmentation details to logs/augmentations.log"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "augmentations.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"{timestamp} | Effect: {effect} | File: {filename}\n")


if __name__ == "__main__":
    main()
