from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import json

class BaseLLMProvider(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    async def generate_3d_prompt(self, user_input: str) -> Dict:
        pass

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=api_key)
            self.available = True
        except ImportError:
            self.client = None
            self.available = False
    
    async def generate_text(self, prompt: str, model: str = "gpt-4", **kwargs) -> str:
        if not self.available:
            raise RuntimeError("OpenAI library not installed")
        
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response.choices[0].message.content
    
    async def generate_3d_prompt(self, user_input: str) -> Dict:
        system_prompt = """You are a 3D model generation assistant. 
        Analyze the user's input and create a detailed prompt for 3D model generation.
        
        Return your response as JSON with these fields:
        - "prompt": The main text-to-3D prompt
        - "negative_prompt": Things to avoid in the 3D model
        - "style": The artistic style (realistic, stylized, cartoon, etc.)
        - "quality": Quality settings (high, medium, low)
        - "guidance_scale": Recommended guidance scale (1-20)
        - "inference_steps": Recommended number of inference steps (10-100)"""
        
        user_prompt = f"""Convert this user request into a 3D model generation prompt:
        
        User input: {user_input}
        
        Consider:
        - What object should be created?
        - What are the key visual details?
        - What materials should be used?
        - What size and proportions?
        - Any specific poses or orientations?"""
        
        response = await self.generate_text(
            prompt=f"{system_prompt}\n\n{user_prompt}",
            model="gpt-4",
            temperature=0.7
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "prompt": user_input,
                "negative_prompt": "",
                "style": "realistic",
                "quality": "high",
                "guidance_scale": 7.5,
                "inference_steps": 50
            }

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
            self.available = True
        except ImportError:
            self.client = None
            self.available = False
    
    async def generate_text(self, prompt: str, model: str = "claude-3-opus-20240229", **kwargs) -> str:
        if not self.available:
            raise RuntimeError("Anthropic library not installed")
        
        response = await self.client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    async def generate_3d_prompt(self, user_input: str) -> Dict:
        system_prompt = """You are a 3D model generation assistant. 
        Analyze the user's input and create a detailed prompt for 3D model generation.
        
        Return your response as JSON with these fields:
        - "prompt": The main text-to-3D prompt
        - "negative_prompt": Things to avoid in the 3D model
        - "style": The artistic style (realistic, stylized, cartoon, etc.)
        - "quality": Quality settings (high, medium, low)
        - "guidance_scale": Recommended guidance scale (1-20)
        - "inference_steps": Recommended number of inference steps (10-100)"""
        
        user_prompt = f"""Convert this user request into a 3D model generation prompt:
        
        User input: {user_input}
        
        Consider:
        - What object should be created?
        - What are the key visual details?
        - What materials should be used?
        - What size and proportions?
        - Any specific poses or orientations?"""
        
        response = await self.generate_text(
            prompt=f"{system_prompt}\n\n{user_prompt}",
            model="claude-3-opus-20240229"
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "prompt": user_input,
                "negative_prompt": "",
                "style": "realistic",
                "quality": "high",
                "guidance_scale": 7.5,
                "inference_steps": 50
            }

class LocalLLMProvider(BaseLLMProvider):
    def __init__(self, model_path: str):
        super().__init__("")
        self.model_path = model_path
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            print(f"Loading local LLM from {model_path}...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            self.available = True
            print("Local LLM loaded successfully")
        except Exception as e:
            print(f"Failed to load local LLM: {e}")
            self.model = None
            self.available = False
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        if not self.available:
            raise RuntimeError("Local LLM not available")
        
        inputs = self.tokenizer(prompt, return_tensors="pt")
        if hasattr(self.model, 'device'):
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            do_sample=True
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response[len(prompt):]
    
    async def generate_3d_prompt(self, user_input: str) -> Dict:
        system_prompt = """You are a 3D model generation assistant. 
        Analyze the user's input and create a detailed prompt for 3D model generation.
        
        Return your response as JSON with these fields:
        - "prompt": The main text-to-3D prompt
        - "negative_prompt": Things to avoid in the 3D model
        - "style": The artistic style (realistic, stylized, cartoon, etc.)
        - "quality": Quality settings (high, medium, low)
        - "guidance_scale": Recommended guidance scale (1-20)
        - "inference_steps": Recommended number of inference steps (10-100)"""
        
        user_prompt = f"""Convert this user request into a 3D model generation prompt:
        
        User input: {user_input}
        
        Consider:
        - What object should be created?
        - What are the key visual details?
        - What materials should be used?
        - What size and proportions?
        - Any specific poses or orientations?"""
        
        full_prompt = f"{system_prompt}\n\n{user_prompt}\n\nResponse:"
        
        response = await self.generate_text(full_prompt)
        
        try:
            import json
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "prompt": user_input,
                "negative_prompt": "",
                "style": "realistic",
                "quality": "high",
                "guidance_scale": 7.5,
                "inference_steps": 50
            }

class LLMManager:
    def __init__(self):
        self.providers = {}
    
    def add_provider(self, name: str, provider: BaseLLMProvider) -> None:
        self.providers[name] = provider
    
    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        return self.providers.get(name)
    
    async def generate_3d_prompt(self, provider_name: str, user_input: str) -> Dict:
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider {provider_name} not found")
        return await provider.generate_3d_prompt(user_input)

llm_manager = LLMManager()
