import os
from pathlib import Path
from typing import Optional, List, Callable
import requests
from huggingface_hub import snapshot_download, hf_hub_download
import tqdm

from config.config import Config

class ModelDownloader:
    def __init__(self):
        self.models_dir = Config.MODELS_DIR
        self.download_queue = []
    
    def download_model(self, repo_id: str, model_type: str = "3d", 
                   progress_callback: Optional[Callable] = None) -> Path:
        """
        Download a model from Hugging Face Hub.
        
        Args:
            repo_id: Model repository ID (e.g., "stabilityai/stable-diffusion-2-1")
            model_type: Type of model ("3d", "llm", "image")
            progress_callback: Optional callback function for progress updates
        
        Returns:
            Path to downloaded model
        """
        try:
            print(f"Downloading model: {repo_id}")
            
            if model_type == "3d":
                target_dir = self.models_dir / "3d" / repo_id.replace("/", "_")
            elif model_type == "llm":
                target_dir = self.models_dir / "llm" / repo_id.replace("/", "_")
            elif model_type == "image":
                target_dir = self.models_dir / "image" / repo_id.replace("/", "_")
            else:
                target_dir = self.models_dir / repo_id.replace("/", "_")
            
            target_dir.mkdir(parents=True, exist_ok=True)
            
            downloaded_path = snapshot_download(
                repo_id=repo_id,
                local_dir=target_dir,
                local_dir_use_symlinks=False,
                progress_bar=progress_callback or True
            )
            
            print(f"Model downloaded to: {downloaded_path}")
            return target_dir
        
        except Exception as e:
            print(f"Error downloading model: {e}")
            raise
    
    def download_model_url(self, url: str, output_name: str, 
                         progress_callback: Optional[Callable] = None) -> Path:
        """
        Download a model from a direct URL.
        
        Args:
            url: Direct URL to model file
            output_name: Name to save the model as
            progress_callback: Optional callback function for progress updates
        
        Returns:
            Path to downloaded model
        """
        try:
            output_path = self.models_dir / output_name
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"Downloading from URL: {url}")
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            if progress_callback:
                progress_callback(0, total_size)
            
            chunk_size = 8192
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if progress_callback and total_size > 0:
                        progress_callback(downloaded, total_size)
            
            print(f"Model downloaded to: {output_path}")
            return output_path
        
        except Exception as e:
            print(f"Error downloading from URL: {e}")
            raise
    
    def get_available_disk_space(self) -> int:
        """Get available disk space in bytes."""
        import shutil
        return shutil.disk_usage(self.models_dir).free
    
    def get_model_size(self, repo_id: str) -> Optional[int]:
        """
        Get model size from Hugging Face Hub info.
        
        Returns:
            Size in bytes, or None if not available
        """
        try:
            from huggingface_hub import model_info
            info = model_info(repo_id)
            if info.safetensors:
                return sum(f.safetensors.size for f in info.safetensors)
            return None
        except Exception as e:
            print(f"Error getting model size: {e}")
            return None
    
    def auto_download_required_models(self, force: bool = False) -> List[Path]:
        """
        Automatically download commonly used models if not present.
        
        Args:
            force: Force download even if models exist
        
        Returns:
            List of downloaded model paths
        """
        required_models = [
            ("openai/shap-e", "3d"),
            ("stabilityai/triposr", "3d"),
        ]
        
        downloaded_paths = []
        
        for repo_id, model_type in required_models:
            model_dir = self.models_dir / model_type / repo_id.replace("/", "_")
            
            if not model_dir.exists() or force:
                try:
                    print(f"Auto-downloading: {repo_id}")
                    path = self.download_model(repo_id, model_type)
                    downloaded_paths.append(path)
                except Exception as e:
                    print(f"Failed to auto-download {repo_id}: {e}")
            else:
                print(f"Model already exists: {repo_id}")
                downloaded_paths.append(model_dir)
        
        return downloaded_paths

class ProgressCallback:
    """Custom progress callback for model downloads."""
    
    def __init__(self, description: str):
        self.description = description
        self.progress_bar = None
    
    def __call__(self, progress: int, total: int):
        if total > 0:
            percent = (progress / total) * 100
            print(f"\r{self.description}: {progress}/{total} bytes ({percent:.1f}%)", end="", flush=True)
        else:
            print(f"\r{self.description}: {progress} bytes", end="", flush=True)
        
        if progress >= total:
            print()  # New line after completion

def create_progress_callback(description: str) -> ProgressCallback:
    """Create a progress callback with a description."""
    return ProgressCallback(description)

model_downloader = ModelDownloader()
