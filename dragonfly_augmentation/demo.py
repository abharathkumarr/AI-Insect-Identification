import os
from datetime import datetime

import numpy as np
from PIL import Image
import streamlit as st

from weather_aug.augmentor import WeatherAugmentor
from weather_aug.classifier import WeatherClassifier

SAMPLES_ORIGINAL_DIR = os.path.join("samples", "original")
SAMPLES_AUGMENTED_DIR = os.path.join("samples", "augmented")


def ensure_dirs():
    os.makedirs(SAMPLES_ORIGINAL_DIR, exist_ok=True)
    os.makedirs(SAMPLES_AUGMENTED_DIR, exist_ok=True)


def pil_to_np(img: Image.Image) -> np.ndarray:
    return np.array(img.convert("RGB"))


def np_to_pil(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(arr.astype(np.uint8))


def save_image(img: Image.Image, prefix: str, effect: str | None = None) -> str:
    """Save image under samples/augmented/ with timestamped filename."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    if effect:
        name = f"{prefix}_{effect}_{ts}.png"
    else:
        name = f"{prefix}_{ts}.png"
    path = os.path.join(SAMPLES_AUGMENTED_DIR, name)
    img.save(path)
    return path


def main():
    st.set_page_config(page_title="Dragonfly Weather Augmentation Demo", layout="wide")
    st.title("Dragonfly Weather-Based Image Augmentation")

    st.markdown(
        """Upload an insect image (e.g., a dragonfly), then apply weather effects
        like **Rain**, **Snow**, **Fog**, **Night**, or **Sunny**. The original image
        (Old) is shown on the left, and the augmented image (New) on the right,
        matching the professor's diagram."""
    )

    ensure_dirs()

    # Sidebar controls
    st.sidebar.header("Controls")
    intensity = st.sidebar.selectbox("Intensity", ["low", "medium", "high"], index=1)
    auto_save = st.sidebar.checkbox("Automatically save augmented images", value=True)
    enable_classifier = st.sidebar.checkbox("Enable Weather Prediction (ML Model)", value=True)

    # Initialize classifier if enabled
    classifier = WeatherClassifier() if enable_classifier else None

    uploaded_file = st.file_uploader("Upload an insect image", type=["png", "jpg", "jpeg"])

    col_old, col_new = st.columns(2)

    original_img = None
    original_predictions = None
    
    if uploaded_file is not None:
        original_img = Image.open(uploaded_file)
        with col_old:
            st.subheader("Old (Original)")
            st.image(original_img, use_column_width=True)
            
            # Show prediction for original image
            if classifier:
                orig_np = pil_to_np(original_img)
                original_predictions = classifier.predict_with_details(orig_np)
                st.caption("**Weather Prediction:**")
                st.write(f"🔍 {original_predictions['predicted_class'].capitalize()}: {original_predictions['confidence']*100:.1f}%")
                with st.expander("See all predictions"):
                    for cls, prob in original_predictions['top_3']:
                        st.write(f"- {cls.capitalize()}: {prob*100:.1f}%")
    else:
        with col_old:
            st.info("Upload an image to get started.")

    effect_clicked = None
    st.markdown("### Apply Weather Effect")

    # Row 1: Original effects
    btn_cols = st.columns(5)
    if btn_cols[0].button("Rain"):
        effect_clicked = "rain"
    if btn_cols[1].button("Snow"):
        effect_clicked = "snow"
    if btn_cols[2].button("Fog"):
        effect_clicked = "fog"
    if btn_cols[3].button("Night"):
        effect_clicked = "night"
    if btn_cols[4].button("Sunny"):
        effect_clicked = "sunny"

    # Row 2: New effects
    btn_cols_2 = st.columns(5)
    if btn_cols_2[0].button("Autumn"):
        effect_clicked = "autumn"
    if btn_cols_2[1].button("Motion Blur"):
        effect_clicked = "motion_blur"

    # Multi-select for combined effects
    st.markdown("### Combine Effects")
    multi_effects = st.multiselect(
        "Choose multiple effects to apply in order:",
        ["rain", "snow", "fog", "night", "sunny", "autumn", "motion_blur"]
    )
    if st.button("Apply Selected Effects"):
        effect_clicked = "multi"

    if st.sidebar.button("Reset"):
        effect_clicked = None
        st.experimental_rerun()

    if effect_clicked and original_img is not None:
        try:
            augmentor = WeatherAugmentor(intensity=intensity)
            np_img = pil_to_np(original_img)
            
            if effect_clicked == "multi":
                # Apply multiple effects sequentially
                np_aug = np_img
                applied_effects = []
                for eff in multi_effects:
                    np_aug = augmentor.apply_effect(np_aug, eff)
                    applied_effects.append(eff)
                effect_name = "+".join(applied_effects) if applied_effects else "none"
            else:
                np_aug = augmentor.apply_effect(np_img, effect_clicked)
                effect_name = effect_clicked

            aug_img = np_to_pil(np_aug)

            with col_new:
                st.subheader("New (Augmented)")
                st.image(aug_img, use_column_width=True)
                st.caption(f"Effect: {effect_name.capitalize()}, Intensity: {intensity}")

                # Show prediction for augmented image
                if classifier:
                    aug_predictions = classifier.predict_with_details(np_aug)
                    st.caption("**Weather Prediction:**")
                    st.write(f"🔍 {aug_predictions['predicted_class'].capitalize()}: {aug_predictions['confidence']*100:.1f}%")
                    
                    # Show prediction change
                    if original_predictions:
                        orig_class = original_predictions['predicted_class']
                        aug_class = aug_predictions['predicted_class']
                        if orig_class != aug_class:
                            st.warning(f"⚠️ Prediction changed: {orig_class.capitalize()} → {aug_class.capitalize()}")
                        else:
                            orig_conf = original_predictions['confidence']
                            aug_conf = aug_predictions['confidence']
                            conf_change = (aug_conf - orig_conf) * 100
                            if abs(conf_change) > 5:
                                st.info(f"Confidence changed by {conf_change:+.1f}%")
                    
                    with st.expander("See all predictions"):
                        for cls, prob in aug_predictions['top_3']:
                            st.write(f"- {cls.capitalize()}: {prob*100:.1f}%")

                # Convert PIL image to bytes for download button
                from io import BytesIO
                buf = BytesIO()
                aug_img.save(buf, format="PNG")
                byte_im = buf.getvalue()

                st.download_button(
                    label="Download Image",
                    data=byte_im,
                    file_name=f"augmented_{effect_name}.png",
                    mime="image/png"
                )

            # Logging
            log_augmentation(effect_name, uploaded_file.name)

            if auto_save:
                base_prefix = os.path.splitext(os.path.basename(uploaded_file.name))[0]
                path = save_image(aug_img, prefix=base_prefix, effect=effect_name)
                st.success(f"Augmented image saved to: {path}")
        except Exception as e:
            st.error(f"Failed to apply effect: {e}")
    elif effect_clicked and original_img is None:
        st.warning("Please upload an image before applying an effect.")


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
