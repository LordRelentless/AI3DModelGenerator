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
            model="anthropic/claude-3-opus",
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
    def __init__(self, model_path: str, model_type: str = "transformers"):
        super().__init__("")
        self.model_path = model_path
        self.model_type = model_type
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            print(f"Loading local LLM from {model_path} ({model_type})...")
            
            if model_type == "glm4":
                from transformers import AutoModelForCausalLM, AutoTokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_path,
                    trust_remote_code=True
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None,
                    trust_remote_code=True
                )
            else:
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None
                )
            
            self.available = True
            print(f"Local LLM loaded successfully from {model_path}")
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

class NetworkedLLMProvider(BaseLLMProvider):
    def __init__(self, server_url: str, api_key: Optional[str] = None):
        super().__init__(api_key or "")
        self.server_url = server_url.rstrip('/')
        try:
            import openai
            base_url = self.server_url
            
            if not base_url.startswith('http'):
                base_url = f"http://{base_url}"
            
            self.client = openai.AsyncOpenAI(
                base_url=f"{base_url}/v1",
                api_key=api_key or "dummy-key"
            )
            self.available = True
            print(f"Networked LLM provider initialized: {server_url}")
        except ImportError:
            self.client = None
            self.available = False
            print("Failed to initialize OpenAI client for networked LLM")
    
    async def generate_text(self, prompt: str, model: str = "local-model", **kwargs) -> str:
        if not self.available:
            raise RuntimeError("Networked LLM not available")
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling networked LLM: {e}")
            raise RuntimeError(f"Networked LLM error: {str(e)}")
    
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
            model="local-model",
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

class LLMManager:
    def __init__(self):
        self.providers = {}
        self.provider_priority = []
    
    def add_provider(self, name: str, provider: BaseLLMProvider, priority: int = 100) -> None:
        self.providers[name] = provider
        self.provider_priority.append((priority, name))
        self.provider_priority.sort()
    
    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        return self.providers.get(name)
    
    def get_available_provider(self) -> Optional[str]:
        for priority, name in self.provider_priority:
            provider = self.providers.get(name)
            if provider and provider.available:
                print(f"Using LLM provider: {name} (priority: {priority})")
                return name
        print("No available LLM provider found")
        return None
    
    async def generate_3d_prompt(self, provider_name: str, user_input: str) -> Dict:
        if provider_name == "auto":
            available_provider = self.get_available_provider()
            if not available_provider:
                return {
                    "prompt": user_input,
                    "negative_prompt": "",
                    "style": "realistic",
                    "quality": "high",
                    "guidance_scale": 7.5,
                    "inference_steps": 50,
                    "provider": "none",
                    "message": "No LLM provider available, using basic prompt"
                }
            provider_name = available_provider
        
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider {provider_name} not found")
        
        result = await provider.generate_3d_prompt(user_input)
        result["provider"] = provider_name
        return result

llm_manager = LLMManager()
