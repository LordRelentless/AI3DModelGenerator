import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = Path(__file__).parent.parent
    
    API_KEYS = {
        'openai': os.getenv('OPENAI_API_KEY', ''),
        'anthropic': os.getenv('ANTHROPIC_API_KEY', '')
    }
    
    DEVICE = os.getenv('DEVICE', 'auto')
    
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    DEFAULT_LLM = os.getenv('DEFAULT_LLM', 'openai')
    LOCAL_LLM_ENABLED = os.getenv('LOCAL_LLM_ENABLED', 'False').lower() == 'true'
    LOCAL_LLM_PATH = os.getenv('LOCAL_LLM_PATH', './models/llm')
    
    SHAP_E_MODEL = os.getenv('SHAP_E_MODEL', 'openai/shap-e')
    TRIPOSR_MODEL = os.getenv('TRIPOSR_MODEL', 'stabilityai/triposr')
    
    DEFAULT_INFERENCE_STEPS = int(os.getenv('DEFAULT_INFERENCE_STEPS', 50))
    DEFAULT_GUIDANCE_SCALE = float(os.getenv('DEFAULT_GUIDANCE_SCALE', 7.5))
    DEFAULT_FRAME_SIZE = int(os.getenv('DEFAULT_FRAME_SIZE', 256))
    MESH_RESOLUTION = int(os.getenv('MESH_RESOLUTION', 256))
    
    OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', './output'))
    MODELS_DIR = Path(os.getenv('MODELS_DIR', './models'))
    LOGS_DIR = Path(os.getenv('LOGS_DIR', './logs'))
    
    WINDOW_WIDTH = int(os.getenv('WINDOW_WIDTH', 1400))
    WINDOW_HEIGHT = int(os.getenv('WINDOW_HEIGHT', 900))
    
    WEB_PORT = int(os.getenv('WEB_PORT', 8000))
    
    @classmethod
    def ensure_directories(cls):
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)

Config.ensure_directories()
