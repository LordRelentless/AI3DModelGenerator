import torch
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, Union
from PIL import Image

from .device_manager import get_device, get_dtype

class TextTo3DGenerator:
    def __init__(self, model_path: str = "openai/shap-e"):
        self.model_path = model_path
        self.pipe = None
        self.device = get_device()
        self._load_model()
    
    def _load_model(self) -> None:
        try:
            from diffusers import ShapEPipeline
            
            print(f"Loading Shap-E model from {self.model_path}...")
            dtype = get_dtype()
            
            self.pipe = ShapEPipeline.from_pretrained(
                self.model_path,
                torch_dtype=dtype,
                variant="fp16" if dtype == torch.float16 else None
            )
            self.pipe = self.pipe.to(self.device)
            
            if self.device.type == 'cuda':
                self.pipe.enable_model_cpu_offload()
            
            print("Shap-E model loaded successfully")
        except Exception as e:
            print(f"Error loading Shap-E model: {e}")
            self.pipe = None
    
    def generate_mesh(
        self,
        prompt: str,
        guidance_scale: float = 15.0,
        num_inference_steps: int = 64,
        frame_size: int = 256
    ) -> Optional[Any]:
        if not self.pipe:
            raise RuntimeError("Model not loaded")
        
        try:
            result = self.pipe(
                prompt,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
                frame_size=frame_size,
                output_type="mesh"
            )
            return result.images[0]
        except Exception as e:
            print(f"Error generating mesh: {e}")
            return None
    
    def generate_gif(
        self,
        prompt: str,
        guidance_scale: float = 15.0,
        num_inference_steps: int = 64,
        frame_size: int = 256
    ) -> Optional[Any]:
        if not self.pipe:
            raise RuntimeError("Model not loaded")
        
        try:
            result = self.pipe(
                prompt,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
                frame_size=frame_size
            )
            return result.images[0]
        except Exception as e:
            print(f"Error generating GIF: {e}")
            return None
    
    def export_mesh_to_ply(self, mesh: Any, output_path: Union[str, Path]) -> bool:
        try:
            from diffusers.utils import export_to_ply
            export_to_ply(mesh, str(output_path))
            return True
        except Exception as e:
            print(f"Error exporting mesh to PLY: {e}")
            return False

class ImageTo3DGenerator:
    def __init__(self, model_path: str = "stabilityai/triposr"):
        self.model_path = model_path
        self.model = None
        self.device = get_device()
        self._load_model()
    
    def _load_model(self) -> None:
        try:
            print(f"Loading TripoSR model from {self.model_path}...")
            
            from diffusers import DiffusionPipeline
            
            dtype = get_dtype()
            
            self.model = DiffusionPipeline.from_pretrained(
                self.model_path,
                torch_dtype=dtype,
                trust_remote_code=True
            )
            self.model = self.model.to(self.device)
            
            print("TripoSR model loaded successfully")
        except Exception as e:
            print(f"Error loading TripoSR model: {e}")
            self.model = None
    
    def generate_mesh_from_image(
        self,
        image: Union[Image.Image, str, Path],
        resolution: int = 256,
        threshold: float = 25.0
    ) -> Optional[Any]:
        if not self.model:
            raise RuntimeError("Model not loaded")
        
        try:
            if isinstance(image, (str, Path)):
                image = Image.open(image).convert("RGB")
            
            image = image.resize((resolution, resolution), Image.Resampling.LANCZOS)
            
            scene_codes = self.model([image], device=self.device)
            meshes = self.model.extract_mesh(
                scene_codes,
                resolution=resolution,
                threshold=threshold
            )
            
            return meshes[0]
        except Exception as e:
            print(f"Error generating mesh from image: {e}")
            return None

class PointCloudToMesh:
    @staticmethod
    def convert_ply_to_obj(ply_path: Union[str, Path], output_path: Union[str, Path]) -> bool:
        try:
            import trimesh
            
            mesh = trimesh.load(str(ply_path))
            mesh.export(str(output_path))
            return True
        except Exception as e:
            print(f"Error converting PLY to OBJ: {e}")
            return False
    
    @staticmethod
    def simplify_mesh(mesh_path: Union[str, Path], output_path: Union[str, Path], face_count: int = 50000) -> bool:
        try:
            import trimesh
            
            mesh = trimesh.load(str(mesh_path))
            
            if hasattr(mesh, 'simplify_quadric_decimation'):
                simplified = mesh.simplify_quadric_decimation(face_count)
            else:
                simplified = mesh
            
            simplified.export(str(output_path))
            return True
        except Exception as e:
            print(f"Error simplifying mesh: {e}")
            return False

class TextToImageTo3DPipeline:
    def __init__(
        self,
        text_to_image_model: str = "stabilityai/stable-diffusion-2-1",
        image_to_3d_model: str = "stabilityai/triposr"
    ):
        self.text_to_3d = TextTo3DGenerator()
        self.image_to_3d = ImageTo3DGenerator(image_to_3d_model)
        self.text_to_image_pipe = None
        self.device = get_device()
        self._load_text_to_image_model(text_to_image_model)
    
    def _load_text_to_image_model(self, model_path: str) -> None:
        try:
            from diffusers import StableDiffusionPipeline
            
            print(f"Loading Stable Diffusion model from {model_path}...")
            dtype = get_dtype()
            
            self.text_to_image_pipe = StableDiffusionPipeline.from_pretrained(
                model_path,
                torch_dtype=dtype,
                safety_checker=None
            )
            self.text_to_image_pipe = self.text_to_image_pipe.to(self.device)
            
            if self.device.type == 'cuda':
                self.text_to_image_pipe.enable_model_cpu_offload()
            
            print("Stable Diffusion model loaded successfully")
        except Exception as e:
            print(f"Error loading Stable Diffusion model: {e}")
            self.text_to_image_pipe = None
    
    def generate_image(self, prompt: str, num_inference_steps: int = 50) -> Optional[Image.Image]:
        if not self.text_to_image_pipe:
            raise RuntimeError("Text-to-image model not loaded")
        
        try:
            result = self.text_to_image_pipe(
                prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=7.5
            )
            return result.images[0]
        except Exception as e:
            print(f"Error generating image: {e}")
            return None
    
    def generate_3d_from_text(
        self,
        prompt: str,
        use_text_to_3d: bool = True,
        use_image_pipeline: bool = False,
        **kwargs
    ) -> Optional[Any]:
        if use_text_to_3d:
            return self.text_to_3d.generate_mesh(prompt, **kwargs)
        
        if use_image_pipeline:
            image = self.generate_image(prompt)
            if image:
                return self.image_to_3d.generate_mesh_from_image(image, **kwargs)
        
        return None

def create_generator(model_type: str = "text-to-3d", model_path: str = None) -> Any:
    if model_type == "text-to-3d":
        model_path = model_path or "openai/shap-e"
        return TextTo3DGenerator(model_path)
    elif model_type == "image-to-3d":
        model_path = model_path or "stabilityai/triposr"
        return ImageTo3DGenerator(model_path)
    elif model_type == "pipeline":
        return TextToImageTo3DPipeline()
    else:
        raise ValueError(f"Unknown model type: {model_type}")
