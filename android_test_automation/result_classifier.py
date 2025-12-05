"""
Result Classification for Dragonfly Identification Tests
Classifies app results as: correct_species, incorrect_species, no_identification, uncertain
"""

import logging
from config import (
    EXPECTED_DRAGONFLY_SPECIES,
    UNCERTAIN_KEYWORDS,
    NO_IDENTIFICATION_KEYWORDS,
)

logger = logging.getLogger(__name__)


class ResultClassifier:
    """Classifies test results into categories"""
    
    def __init__(self, expected_species_list=None):
        """
        Initialize classifier
        
        Args:
            expected_species_list: List of expected species names (defaults to dragonfly species)
        """
        self.expected_species = expected_species_list or EXPECTED_DRAGONFLY_SPECIES
        self.uncertain_keywords = UNCERTAIN_KEYWORDS
        self.no_id_keywords = NO_IDENTIFICATION_KEYWORDS
    
    def classify_result(self, app_result, expected_species=None):
        """
        Classify the app's identification result
        Combines app result ("Dragonfly") with expected species to create output:
        - dragonfly_darner if app shows "Dragonfly" and expected is "darner"
        - dragonfly_skimmer if app shows "Dragonfly" and expected is "skimmer"
        - dragonfly if app shows "Dragonfly" and expected is "dragonfly"
        - uncertain if no output from app
        
        Args:
            app_result: Dict with keys: species, confidence, full_text, status
            expected_species: Expected species name (darner, skimmer, or dragonfly)
            
        Returns:
            Dict with classification: {
                'category': 'correct_species' | 'incorrect_species' | 'no_identification' | 'uncertain',
                'reason': str,
                'app_species': str,  # Combined output: dragonfly_darner, dragonfly_skimmer, dragonfly, or uncertain
                'expected_species': str,
                'confidence': float
            }
        """
        if expected_species is None:
            # Default to checking if it's any dragonfly species
            expected_species = "dragonfly"
        
        species = app_result.get("species", "")
        full_text = app_result.get("full_text", "").lower() if app_result.get("full_text") else ""
        confidence = app_result.get("confidence")
        
        # Check if app identified as "Dragonfly"
        app_shows_dragonfly = False
        if species:
            species_lower = species.lower()
            if "dragonfly" in species_lower or "dragon fly" in species_lower:
                app_shows_dragonfly = True
        elif full_text:
            if "dragonfly" in full_text or "dragon fly" in full_text:
                app_shows_dragonfly = True
        
        # Check for "No insect" cases first - combine with uncertain (same category)
        if not species or species.lower() in ["none", "no insect", "no insect visible", "no insect detected"]:
            if "no insect" in full_text or "couldn't detect" in full_text:
                return {
                    "category": "no_identification",
                    "reason": "App detected no insect in the image",
                    "app_species": "no_insect_visible",
                    "expected_species": expected_species,
                    "confidence": confidence,
                }
        
        # If app shows "Dragonfly", combine with expected species
        if app_shows_dragonfly:
            expected_lower = expected_species.lower()
            
            # Create combined output based on expected species
            if expected_lower == "darner":
                combined_output = "dragonfly_darner"
                category = "correct_species"
                reason = f"App correctly identified as Dragonfly (expected: {expected_species})"
            elif expected_lower == "skimmer":
                combined_output = "dragonfly_skimmer"
                category = "correct_species"
                reason = f"App correctly identified as Dragonfly (expected: {expected_species})"
            elif expected_lower == "dragonfly":
                combined_output = "dragonfly"
                category = "correct_species"
                reason = f"App correctly identified as Dragonfly"
            else:
                # Expected species is not darner/skimmer/dragonfly
                combined_output = "dragonfly"
                category = "correct_species"
                reason = f"App identified as Dragonfly (expected: {expected_species})"
            
            return {
                "category": category,
                "reason": reason,
                "app_species": combined_output,
                "expected_species": expected_species,
                "confidence": confidence,
            }
        
        # If app didn't show "Dragonfly", it's either incorrect species or no identification
        species_lower = species.lower() if species else ""
        all_text = f"{species_lower} {full_text}".lower()
        
        # Check for no identification (combine with uncertain - same thing)
        if self._is_no_identification(all_text, species_lower):
            return {
                "category": "no_identification",
                "reason": "App did not provide identification or returned error",
                "app_species": "no_insect_visible",
                "expected_species": expected_species,
                "confidence": confidence,
            }
        
        # If we have a species but it's not Dragonfly, it's incorrect species
        if species and len(species) > 2:
            # If it's not dragonfly, it's incorrect (we're testing dragonfly images)
            if "dragonfly" not in species_lower and "dragon fly" not in species_lower:
                return {
                    "category": "incorrect_species",
                    "reason": f"App identified as '{species}' but expected dragonfly species (got: {expected_species})",
                    "app_species": species,
                    "expected_species": expected_species,
                    "confidence": confidence,
                }
            # If it is dragonfly but doesn't match expected, still check
            elif self._is_correct_species(species_lower, all_text, expected_species):
                return {
                    "category": "correct_species",
                    "reason": f"App correctly identified as {species}",
                    "app_species": species,
                    "expected_species": expected_species,
                    "confidence": confidence,
                }
            else:
                return {
                    "category": "incorrect_species",
                    "reason": f"App identified as '{species}' but expected '{expected_species}'",
                    "app_species": species,
                    "expected_species": expected_species,
                    "confidence": confidence,
                }
        
        # Default to no_identification if we can't determine (combine with uncertain)
        return {
            "category": "no_identification",
            "reason": "Could not extract valid identification from app",
            "app_species": "no_insect_visible",
            "expected_species": expected_species,
            "confidence": confidence,
        }
    
    def _is_no_identification(self, text, species):
        """Check if result indicates no identification"""
        # Check for no identification keywords
        for keyword in self.no_id_keywords:
            if keyword.lower() in text:
                return True
        
        # Check if species is empty or too short
        if not species or len(species.strip()) < 2:
            return True
        
        # Check for error messages
        error_keywords = ["error", "failed", "try again", "invalid"]
        for keyword in error_keywords:
            if keyword in text:
                return True
        
        return False
    
    def _is_uncertain(self, text, confidence):
        """Check if result indicates uncertain identification"""
        # Check for uncertain keywords
        for keyword in self.uncertain_keywords:
            if keyword.lower() in text:
                return True
        
        # Check confidence level (if available)
        if confidence is not None:
            if confidence < 50:  # Low confidence threshold
                return True
        
        return False
    
    def _is_correct_species(self, species, full_text, expected_species):
        """Check if identified species matches expected"""
        expected_lower = expected_species.lower()
        species_lower = species.lower()
        
        # Direct match
        if expected_lower in species_lower or species_lower in expected_lower:
            return True
        
        # Check for darner specifically
        if expected_species.lower() == "darner":
            darner_keywords = ["darner", "aeshnidae", "aeshna", "hawker"]
            for keyword in darner_keywords:
                if keyword in species_lower or keyword in full_text:
                    return True
        
        # Check for skimmer specifically
        if expected_species.lower() == "skimmer":
            skimmer_keywords = ["skimmer", "libellulidae", "libellula", "percher"]
            for keyword in skimmer_keywords:
                if keyword in species_lower or keyword in full_text:
                    return True
        
        # Check if any expected dragonfly species is mentioned
        for exp_species in self.expected_species:
            if exp_species.lower() in species_lower or exp_species.lower() in full_text:
                return True
        
        # Check if "dragonfly" or "dragon fly" is in the text (fallback for generic dragonfly)
        if expected_species.lower() == "dragonfly":
            dragonfly_variants = ["dragonfly", "dragon fly", "dragon-fly", "odonata"]
            for variant in dragonfly_variants:
                if variant in species_lower or variant in full_text:
                    return True
        
        return False
    
    def get_category_summary(self, classifications):
        """
        Get summary statistics from multiple classifications
        Note: uncertain and no_identification are combined as no_identification
        
        Args:
            classifications: List of classification dicts
            
        Returns:
            Dict with summary statistics
        """
        total = len(classifications)
        if total == 0:
            return {
                "total": 0,
                "correct_species": 0,
                "incorrect_species": 0,
                "no_identification": 0,
                "accuracy": 0.0,
            }
        
        counts = {
            "correct_species": 0,
            "incorrect_species": 0,
            "no_identification": 0,
        }
        
        for classification in classifications:
            category = classification.get("category", "no_identification")
            # Combine uncertain with no_identification
            if category == "uncertain":
                category = "no_identification"
            counts[category] = counts.get(category, 0) + 1
        
        # Calculate accuracy (correct / total * 100)
        # "No Identification" and "Incorrect Species" both count as failures
        correct = counts["correct_species"]
        total = counts["correct_species"] + counts["incorrect_species"] + counts["no_identification"]
        accuracy = (correct / total * 100) if total > 0 else 0.0
        
        return {
            "total": total,
            **counts,
            "accuracy": round(accuracy, 2),
        }

