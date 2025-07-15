"""Model downloader utility for downloading pre-trained models from Hugging Face."""

import logging
import os
from pathlib import Path
from typing import Optional
import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)


class ModelDownloader:
    """Downloads pre-trained models from Hugging Face."""
    
    # Model configurations from docling
    LAYOUT_MODEL = {
        "repo_id": "ds4sd/docling-models",
        "revision": "v2.2.0",
        "model_path": "model_artifacts/layout",
        "cache_folder": "layout"
    }
    
    TABLE_MODEL = {
        "repo_id": "ds4sd/docling-models", 
        "revision": "v2.2.0",
        "model_path": "model_artifacts/tableformer",
        "cache_folder": "tableformer"
    }
    
    OCR_MODEL = {
        "repo_id": "ds4sd/docling-models",
        "revision": "v2.2.0", 
        "model_path": "model_artifacts/easyocr",
        "cache_folder": "easyocr"
    }
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the model downloader.
        
        Args:
            cache_dir: Directory to cache downloaded models
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "llm_converter" / "models"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Model cache directory: {self.cache_dir}")
    
    def download_models(self, force: bool = False, progress: bool = True) -> Path:
        """Download all required models.
        
        Args:
            force: Force re-download even if models exist
            progress: Show download progress
            
        Returns:
            Path to the models directory
        """
        logger.info("Downloading pre-trained models...")
        
        models_to_download = [
            ("Layout Model", self.LAYOUT_MODEL),
            ("Table Structure Model", self.TABLE_MODEL),
            ("OCR Model", self.OCR_MODEL)
        ]
        
        for model_name, model_config in models_to_download:
            logger.info(f"Downloading {model_name}...")
            self._download_model(model_config, force, progress)
        
        logger.info("All models downloaded successfully!")
        return self.cache_dir
    
    def _download_model(self, model_config: dict, force: bool, progress: bool):
        """Download a specific model.
        
        Args:
            model_config: Model configuration dictionary
            force: Force re-download
            progress: Show progress
        """
        model_dir = self.cache_dir / model_config["cache_folder"]
        
        if model_dir.exists() and not force:
            logger.info(f"Model already exists at {model_dir}")
            return
        
        # Create model directory
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Download from Hugging Face using docling's logic
        self._download_from_hf(
            repo_id=model_config["repo_id"],
            revision=model_config["revision"],
            local_dir=model_dir,
            force=force,
            progress=progress
        )
    
    def _download_from_hf(self, repo_id: str, revision: str, local_dir: Path, 
                          force: bool, progress: bool):
        """Download model from Hugging Face using docling's logic.
        
        Args:
            repo_id: Hugging Face repository ID
            revision: Git revision/tag
            local_dir: Local directory to save model
            force: Force re-download
            progress: Show progress
        """
        try:
            from huggingface_hub import snapshot_download
            from huggingface_hub.utils import disable_progress_bars
            
            if not progress:
                disable_progress_bars()
            
            download_path = snapshot_download(
                repo_id=repo_id,
                force_download=force,
                local_dir=str(local_dir),
                revision=revision,
            )
            
            logger.info(f"Successfully downloaded {repo_id} to {download_path}")
            
        except ImportError:
            logger.error("huggingface_hub not available. Please install it: pip install huggingface_hub")
            raise
        except Exception as e:
            logger.error(f"Failed to download model {repo_id}: {e}")
            raise
    
    def get_model_path(self, model_type: str) -> Optional[Path]:
        """Get the path to a specific model.
        
        Args:
            model_type: Type of model ('layout', 'table', 'ocr')
            
        Returns:
            Path to the model directory, or None if not found
        """
        model_mapping = {
            'layout': self.LAYOUT_MODEL["cache_folder"],
            'table': self.TABLE_MODEL["cache_folder"], 
            'ocr': self.OCR_MODEL["cache_folder"]
        }
        
        if model_type not in model_mapping:
            logger.error(f"Unknown model type: {model_type}")
            return None
        
        model_path = self.cache_dir / model_mapping[model_type]
        
        if not model_path.exists():
            logger.warning(f"Model {model_type} not found at {model_path}")
            return None
        
        return model_path 

    def are_models_cached(self) -> bool:
        """Check if all required models are cached.
        
        Returns:
            True if all models are cached, False otherwise
        """
        layout_path = self.get_model_path('layout')
        table_path = self.get_model_path('table')
        ocr_path = self.get_model_path('ocr')
        
        return layout_path is not None and table_path is not None and ocr_path is not None
    
    def get_cache_info(self) -> dict:
        """Get information about cached models.
        
        Returns:
            Dictionary with cache information
        """
        info = {
            'cache_dir': str(self.cache_dir),
            'models': {}
        }
        
        for model_type in ['layout', 'table', 'ocr']:
            path = self.get_model_path(model_type)
            info['models'][model_type] = {
                'cached': path is not None,
                'path': str(path) if path else None
            }
        
        return info 