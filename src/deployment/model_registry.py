"""
Model Registry

Version control and storage for trained models with metadata tracking.
"""

from __future__ import annotations

import hashlib
import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


class ModelRegistry:
    """
    Model versioning and storage system.

    Features:
    - Model serialization and deserialization
    - Version tracking with metadata
    - Performance metrics storage
    - Model comparison utilities
    - Automatic rollback support
    """

    def __init__(self, registry_path: str = "models"):
        """
        Initialize model registry.

        Args:
            registry_path: Base directory for model storage
        """
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)

        self.metadata_file = self.registry_path / "registry.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> dict[str, Any]:
        """Load registry metadata from disk."""
        if self.metadata_file.exists():
            with open(self.metadata_file) as f:
                return json.load(f)
        return {"models": {}, "active": None}

    def _save_metadata(self):
        """Save registry metadata to disk."""
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=2, default=str)

    def _compute_checksum(self, model_path: Path) -> str:
        """Compute SHA256 checksum of model file."""
        sha256_hash = hashlib.sha256()
        with open(model_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def register_model(
        self,
        model: Any,
        name: str,
        version: str,
        metrics: dict[str, float],
        hyperparameters: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        set_active: bool = True,
    ) -> str:
        """
        Register a new model version.

        Args:
            model: Trained model object
            name: Model name
            version: Version identifier
            metrics: Performance metrics
            hyperparameters: Model hyperparameters
            metadata: Additional metadata
            set_active: Whether to set as active model

        Returns:
            Model ID (name:version)
        """
        model_id = f"{name}:{version}"
        model_dir = self.registry_path / name
        model_dir.mkdir(exist_ok=True)

        # Save model
        model_path = model_dir / f"{version}.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(model, f)

        # Compute checksum
        checksum = self._compute_checksum(model_path)

        # Store metadata
        self.metadata["models"][model_id] = {
            "name": name,
            "version": version,
            "path": str(model_path),
            "checksum": checksum,
            "registered_at": datetime.now().isoformat(),
            "metrics": metrics,
            "hyperparameters": hyperparameters or {},
            "metadata": metadata or {},
            "size_bytes": model_path.stat().st_size,
        }

        if set_active:
            self.metadata["active"] = model_id

        self._save_metadata()

        return model_id

    def load_model(self, name: str, version: str | None = None) -> Any:
        """
        Load a model by name and version.

        Args:
            name: Model name
            version: Version identifier (None = active version)

        Returns:
            Loaded model object
        """
        if version is None:
            # Load active model
            active_id = self.metadata.get("active")
            if not active_id:
                raise ValueError("No active model set")
            if not active_id.startswith(f"{name}:"):
                raise ValueError(f"Active model is not '{name}'")
            model_id = active_id
        else:
            model_id = f"{name}:{version}"

        if model_id not in self.metadata["models"]:
            raise ValueError(f"Model {model_id} not found")

        model_info = self.metadata["models"][model_id]
        model_path = Path(model_info["path"])

        # Verify checksum
        current_checksum = self._compute_checksum(model_path)
        if current_checksum != model_info["checksum"]:
            raise ValueError(f"Checksum mismatch for {model_id}")

        with open(model_path, "rb") as f:
            return pickle.load(f)

    def get_active_model(self) -> tuple[Any, dict[str, Any]]:
        """
        Get active model and its metadata.

        Returns:
            Tuple of (model, metadata)
        """
        active_id = self.metadata.get("active")
        if not active_id:
            raise ValueError("No active model set")

        name, version = active_id.split(":")
        model = self.load_model(name, version)
        metadata = self.metadata["models"][active_id]

        return model, metadata

    def set_active_model(self, name: str, version: str):
        """
        Set a model version as active.

        Args:
            name: Model name
            version: Version identifier
        """
        model_id = f"{name}:{version}"
        if model_id not in self.metadata["models"]:
            raise ValueError(f"Model {model_id} not found")

        self.metadata["active"] = model_id
        self._save_metadata()

    def list_models(self, name: str | None = None) -> pd.DataFrame:
        """
        List all registered models.

        Args:
            name: Filter by model name (None = all models)

        Returns:
            DataFrame with model information
        """
        models = []
        for model_id, info in self.metadata["models"].items():
            if name is None or info["name"] == name:
                models.append(
                    {
                        "model_id": model_id,
                        "name": info["name"],
                        "version": info["version"],
                        "registered_at": info["registered_at"],
                        "size_mb": info["size_bytes"] / 1024 / 1024,
                        "is_active": model_id == self.metadata.get("active"),
                        **info["metrics"],
                    }
                )

        return pd.DataFrame(models)

    def compare_models(self, model_ids: list[str], metric: str = "roi") -> pd.DataFrame:
        """
        Compare multiple model versions.

        Args:
            model_ids: List of model IDs to compare
            metric: Primary metric for comparison

        Returns:
            Comparison DataFrame sorted by metric
        """
        comparisons = []
        for model_id in model_ids:
            if model_id not in self.metadata["models"]:
                continue

            info = self.metadata["models"][model_id]
            comparisons.append(
                {
                    "model_id": model_id,
                    "version": info["version"],
                    "registered_at": info["registered_at"],
                    **info["metrics"],
                }
            )

        df = pd.DataFrame(comparisons)
        if metric in df.columns:
            df = df.sort_values(metric, ascending=False)

        return df

    def delete_model(self, name: str, version: str, force: bool = False):
        """
        Delete a model version.

        Args:
            name: Model name
            version: Version identifier
            force: Allow deletion of active model
        """
        model_id = f"{name}:{version}"

        if model_id not in self.metadata["models"]:
            raise ValueError(f"Model {model_id} not found")

        if model_id == self.metadata.get("active") and not force:
            raise ValueError(f"Cannot delete active model {model_id} (use force=True)")

        # Delete model file
        model_path = Path(self.metadata["models"][model_id]["path"])
        if model_path.exists():
            model_path.unlink()

        # Remove from metadata
        del self.metadata["models"][model_id]

        # Clear active if this was it
        if self.metadata.get("active") == model_id:
            self.metadata["active"] = None

        self._save_metadata()

    def get_model_info(self, name: str, version: str) -> dict[str, Any]:
        """
        Get detailed information about a model.

        Args:
            name: Model name
            version: Version identifier

        Returns:
            Model metadata dictionary
        """
        model_id = f"{name}:{version}"
        if model_id not in self.metadata["models"]:
            raise ValueError(f"Model {model_id} not found")

        return self.metadata["models"][model_id].copy()

    def rollback_to_version(self, name: str, version: str):
        """
        Rollback active model to a previous version.

        Args:
            name: Model name
            version: Version to rollback to
        """
        self.set_active_model(name, version)

    def cleanup_old_versions(self, name: str, keep_latest: int = 3):
        """
        Remove old model versions, keeping only the latest N.

        Args:
            name: Model name
            keep_latest: Number of latest versions to keep
        """
        # Get all versions for this model
        versions = [
            (model_id, info)
            for model_id, info in self.metadata["models"].items()
            if info["name"] == name
        ]

        # Sort by registration date
        versions.sort(key=lambda x: x[1]["registered_at"], reverse=True)

        # Delete old versions
        active_id = self.metadata.get("active")
        for model_id, info in versions[keep_latest:]:
            if model_id != active_id:  # Never delete active model
                version = info["version"]
                self.delete_model(name, version, force=False)
