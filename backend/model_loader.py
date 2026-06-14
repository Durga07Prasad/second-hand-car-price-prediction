"""
Singleton model loader — loads all ML artifacts once at startup.
All other modules access artifacts through this loader instance.
"""
import os
import json
import logging

import joblib
import numpy as np

from config import MODEL_DIR

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Loads and holds all ML artifacts needed for inference.

    Usage:
        loader = ModelLoader()           # loads everything
        model = loader.get_model()       # CatBoost regressor
        scaler = loader.get_scaler()     # StandardScaler
        ...
    """

    def __init__(self):
        self._model = None
        self._scaler = None
        self._brand_encoder = None
        self._feature_columns = None
        self._metadata = None
        self._shap_explainer = None
        self._load_all()

    # ── Private loading ───────────────────────────────────────────────

    def _require_file(self, filename: str) -> str:
        """Return full path if file exists, else raise FileNotFoundError."""
        path = os.path.join(MODEL_DIR, filename)
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"Required model artifact not found: {path}. "
                f"Ensure all .pkl files are in '{MODEL_DIR}/'."
            )
        return path

    def _load_all(self):
        """Load every artifact. Called once on init."""
        logger.info("Loading model artifacts from %s ...", MODEL_DIR)

        # 1. CatBoost model
        path = self._require_file("best_model.pkl")
        self._model = joblib.load(path)
        logger.info("  Loaded model: %s", type(self._model).__name__)

        # 2. Standard scaler
        path = self._require_file("scaler.pkl")
        self._scaler = joblib.load(path)
        logger.info("  Loaded scaler: %s", type(self._scaler).__name__)

        # 3. Brand label encoder
        path = self._require_file("brand_encoder.pkl")
        self._brand_encoder = joblib.load(path)
        logger.info(
            "  Loaded brand encoder with %d classes",
            len(self._brand_encoder.classes_),
        )

        # 4. Feature column order
        path = self._require_file("feature_columns.pkl")
        self._feature_columns = joblib.load(path)
        logger.info("  Loaded %d feature columns", len(self._feature_columns))

        # 5. Model metadata
        path = self._require_file("model_metadata.json")
        with open(path, "r", encoding="utf-8") as f:
            self._metadata = json.load(f)
        logger.info("  Loaded metadata (model: %s)", self._metadata.get("best_model_name"))

        # 6. SHAP explainer (optional — graceful degradation)
        try:
            path = os.path.join(MODEL_DIR, "shap_explainer.pkl")
            if os.path.isfile(path):
                self._shap_explainer = joblib.load(path)
                logger.info("  Loaded SHAP explainer")
            else:
                logger.warning("  shap_explainer.pkl not found — explanations will use fallback")
        except Exception as exc:
            logger.warning("  Failed to load SHAP explainer: %s — using fallback", exc)
            self._shap_explainer = None

        logger.info("All artifacts loaded successfully.")

    # ── Public accessors ──────────────────────────────────────────────

    def get_model(self):
        """Return the trained CatBoost model."""
        return self._model

    def get_scaler(self):
        """Return the fitted StandardScaler."""
        return self._scaler

    def get_brand_encoder(self):
        """Return the fitted LabelEncoder for brand."""
        return self._brand_encoder

    def get_feature_columns(self) -> list:
        """Return the ordered list of 18 feature column names."""
        return self._feature_columns

    def get_metadata(self) -> dict:
        """Return model metadata dict."""
        return self._metadata

    def get_shap_explainer(self):
        """Return the SHAP TreeExplainer (or None if unavailable)."""
        return self._shap_explainer

    def is_model_loaded(self) -> bool:
        """Quick check if core model is available."""
        return self._model is not None
