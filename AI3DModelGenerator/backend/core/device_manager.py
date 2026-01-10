import torch
from typing import Optional, Literal

class DeviceManager:
    _instance = None
    _device = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._device is None:
            self._device = self._detect_device()
    
    @classmethod
    def detect_device_type(cls) -> Literal['cuda', 'rocm', 'mps', 'cpu']:
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0).lower() if torch.cuda.device_count() > 0 else ''
            if 'amd' in device_name or 'radeon' in device_name:
                return 'rocm'
            return 'cuda'
        elif torch.backends.mps.is_available():
            return 'mps'
        else:
            return 'cpu'
    
    def _detect_device(self) -> torch.device:
        device_type = self.detect_device_type()
        if device_type == 'cuda':
            device_count = torch.cuda.device_count()
            if device_count > 0:
                device = torch.device(f'cuda:0')
                torch.cuda.set_device(device)
                device_name = torch.cuda.get_device_name(0).lower()
                
                if 'amd' in device_name or 'radeon' in device_name:
                    print(f"Using ROCm device (AMD GPU): {torch.cuda.get_device_name(0)}")
                else:
                    print(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
                return device
        elif device_type == 'mps':
            print("Using MPS device (Apple Silicon)")
            return torch.device('mps')
        
        print("Using CPU device")
        return torch.device('cpu')
    
    @classmethod
    def get_device(cls) -> torch.device:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance._device
    
    @classmethod
    def set_device(cls, device: str) -> None:
        if cls._instance is None:
            cls._instance = cls()
        cls._instance._device = torch.device(device)
        print(f"Device set to: {device}")
    
    @classmethod
    def get_device_info(cls) -> dict:
        if cls._instance is None:
            cls._instance = cls()
        
        device = cls._instance._device
        info = {
            'type': device.type,
            'index': device.index if device.index is not None else 0
        }
        
        if device.type == 'cuda':
            info.update({
                'name': torch.cuda.get_device_name(device.index),
                'memory_total': torch.cuda.get_device_properties(device.index).total_memory,
                'memory_allocated': torch.cuda.memory_allocated(device.index),
                'memory_reserved': torch.cuda.memory_reserved(device.index),
                'capability': torch.cuda.get_device_capability(device.index)
            })
        elif device.type == 'mps':
            info['name'] = 'Apple Silicon GPU (MPS)'
        
        return info
    
    @classmethod
    def clear_cache(cls) -> None:
        if cls._instance is None:
            cls._instance = cls()
        
        if cls._instance._device.type == 'cuda':
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        elif cls._instance._device.type == 'mps':
            torch.mps.empty_cache()
    
    @classmethod
    def to_device(cls, tensor: torch.Tensor) -> torch.Tensor:
        return tensor.to(cls.get_device())
    
    @classmethod
    def get_dtype(cls) -> torch.dtype:
        device = cls.get_device()
        if device.type in ['cuda', 'mps']:
            return torch.float16
        return torch.float32

def get_device() -> torch.device:
    return DeviceManager.get_device()

def get_device_info() -> dict:
    return DeviceManager.get_device_info()

def clear_cache() -> None:
    DeviceManager.clear_cache()

def to_device(tensor: torch.Tensor) -> torch.Tensor:
    return DeviceManager.to_device(tensor)

def get_dtype() -> torch.dtype:
    return DeviceManager.get_dtype()
