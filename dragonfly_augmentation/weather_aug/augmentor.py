import numpy as np

try:
    import albumentations as A
except ImportError as e:
    A = None

class WeatherAugmentor:
    """Weather-based image augmentation wrapper around Albumentations.

    Usage:
        augmentor = WeatherAugmentor(intensity="medium")
        rainy = augmentor.apply_rain(image_np)
    """

    def __init__(self, intensity: str = "medium", seed: int | None = None):
        if A is None:
            raise ImportError(
                "albumentations is required but not installed. "
                "Install it with `pip install albumentations`."
            )
        intensity = intensity.lower()
        if intensity not in {"low", "medium", "high"}:
            raise ValueError("intensity must be one of: low, medium, high")
        self.intensity = intensity
        self.rng = np.random.RandomState(seed) if seed is not None else None

    # ---------- public API ----------

    def apply_effect(self, image: np.ndarray, effect: str) -> np.ndarray:
        """Apply an effect by name: rain, snow, fog, night, sunny, autumn, motion_blur."""
        effect = effect.lower()
        if effect == "rain":
            return self.apply_rain(image)
        if effect == "snow":
            return self.apply_snow(image)
        if effect == "fog":
            return self.apply_fog(image)
        if effect == "night":
            return self.apply_night(image)
        if effect == "sunny":
            return self.apply_sunny(image)
        if effect == "autumn":
            return self.apply_autumn(image)
        if effect == "motion_blur":
            return self.apply_motion_blur(image)
        raise ValueError(f"Unknown effect: {effect}")

    def apply_rain(self, image: np.ndarray) -> np.ndarray:
        transform = self._build_rain()
        return self._apply(transform, image)

    def apply_snow(self, image: np.ndarray) -> np.ndarray:
        transform = self._build_snow()
        return self._apply(transform, image)

    def apply_fog(self, image: np.ndarray) -> np.ndarray:
        transform = self._build_fog()
        return self._apply(transform, image)

    def apply_night(self, image: np.ndarray) -> np.ndarray:
        transform = self._build_night()
        return self._apply(transform, image)

    def apply_sunny(self, image: np.ndarray) -> np.ndarray:
        transform = self._build_sunny()
        return self._apply(transform, image)

    # ---------- internal helpers ----------

    def _apply(self, transform, image: np.ndarray) -> np.ndarray:
        if image is None:
            raise ValueError("image is None")
        if image.dtype != np.uint8:
            # Albumentations expects uint8 images
            image = image.astype(np.uint8)
        if self.rng is not None:
            # Albumentations supports setting a random seed via NumPy
            state = np.random.get_state()
            np.random.set_state(self.rng.get_state())
            try:
                augmented = transform(image=image)["image"]
            finally:
                np.random.set_state(state)
        else:
            augmented = transform(image=image)["image"]
        return augmented

    # --- individual effect builders ---

    def _build_rain(self):
        if self.intensity == "low":
            drop_length = 10
            blur_value = 3
            brightness = 0.8
        elif self.intensity == "medium":
            drop_length = 15
            blur_value = 5
            brightness = 0.7
        else:  # high
            drop_length = 20
            blur_value = 7
            brightness = 0.6

        return A.Compose([
            A.RandomRain(
                slant_lower=-10,
                slant_upper=10,
                drop_length=drop_length,
                drop_width=1,
                drop_color=(200, 200, 200),
                blur_value=blur_value,
                brightness_coefficient=brightness,
                p=1.0,
            ),
        ])

    def _build_snow(self):
        if self.intensity == "low":
            brightness = (0.1, 0.2)
            density = 0.05
        elif self.intensity == "medium":
            brightness = (0.2, 0.3)
            density = 0.1
        else:  # high
            brightness = (0.3, 0.4)
            density = 0.2

        return A.Compose([
            A.RandomSnow(
                snow_point_lower=0.1,
                snow_point_upper=density,
                brightness_coeff=np.mean(brightness),
                p=1.0,
            ),
        ])

    def _build_fog(self):
        if self.intensity == "low":
            fog_coef = 0.2
            alpha_coef = 0.1
        elif self.intensity == "medium":
            fog_coef = 0.35
            alpha_coef = 0.15
        else:  # high
            fog_coef = 0.5
            alpha_coef = 0.2

        return A.Compose([
            A.RandomFog(
                fog_coef_lower=fog_coef * 0.8,
                fog_coef_upper=fog_coef,
                alpha_coef=alpha_coef,
                p=1.0,
            ),
        ])

    def _build_night(self):
        # Night effect: darken + slight blue/cyan shift
        if self.intensity == "low":
            brightness = (-0.1, -0.2)
            contrast = (0.0, 0.1)
        elif self.intensity == "medium":
            brightness = (-0.2, -0.3)
            contrast = (0.0, 0.15)
        else:  # high
            brightness = (-0.3, -0.4)
            contrast = (0.0, 0.2)

        return A.Compose([
            A.RandomBrightnessContrast(
                brightness_limit=brightness,
                contrast_limit=contrast,
                p=1.0,
            ),
            A.HueSaturationValue(
                hue_shift_limit=5,
                sat_shift_limit=-10,
                val_shift_limit=-10,
                p=1.0,
            ),
        ])

    def _build_sunny(self):
        # Sunny effect: brighten image + optional sun flare
        if self.intensity == "low":
            brightness = (0.1, 0.2)
            contrast = (0.0, 0.1)
        elif self.intensity == "medium":
            brightness = (0.2, 0.3)
            contrast = (0.05, 0.15)
        else:  # high
            brightness = (0.3, 0.4)
            contrast = (0.1, 0.2)

        transforms = [
            A.RandomBrightnessContrast(
                brightness_limit=brightness,
                contrast_limit=contrast,
                p=1.0,
            ),
        ]
        # Optional flare is applied probabilistically
        transforms.append(
            A.RandomSunFlare(
                flare_roi=(0.0, 0.0, 1.0, 0.5),
                angle_lower=0.0,
                angle_upper=1.0,
                num_flare_circles_lower=3,
                num_flare_circles_upper=6,
                src_radius=50,
                src_color=(255, 255, 255),
                p=0.5,
            )
        )
        return A.Compose(transforms)

    def apply_autumn(self, image: np.ndarray) -> np.ndarray:
        transform = self._build_autumn()
        return self._apply(transform, image)

    def apply_motion_blur(self, image: np.ndarray) -> np.ndarray:
        transform = self._build_motion_blur()
        return self._apply(transform, image)

    def _build_autumn(self):
        # Autumn: Shift colors towards red/orange (warm tones)
        if self.intensity == "low":
            r_shift = (10, 20)
            g_shift = (0, 10)
            b_shift = (-10, 0)
        elif self.intensity == "medium":
            r_shift = (20, 30)
            g_shift = (5, 15)
            b_shift = (-20, -10)
        else:  # high
            r_shift = (30, 50)
            g_shift = (10, 20)
            b_shift = (-30, -10)

        return A.Compose([
            A.RGBShift(
                r_shift_limit=r_shift,
                g_shift_limit=g_shift,
                b_shift_limit=b_shift,
                p=1.0
            ),
            A.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.2, hue=0.05, p=0.5)
        ])

    def _build_motion_blur(self):
        # Motion blur: Simulate movement
        if self.intensity == "low":
            blur_limit = 5
        elif self.intensity == "medium":
            blur_limit = 15
        else:  # high
            blur_limit = 30

        return A.Compose([
            A.MotionBlur(blur_limit=blur_limit, p=1.0)
        ])
