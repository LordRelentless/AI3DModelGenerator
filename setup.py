from setuptools import setup, find_packages
from pathlib import Path

readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="ai-3d-model-generator",
    version="1.0.0",
    author="LordRelentless",
    description="AI-powered 3D model generation with LLM integration and slicer preview",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LordRelentless/AI3DModelGenerator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: 3D Modeling",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "diffusers>=0.28.0",
        "transformers>=4.39.0",
        "accelerate>=0.28.0",
        "torch>=2.1.0",
        "torchvision>=0.16.0",
        "Pillow>=10.0.0",
        "numpy>=1.24.0",
        "trimesh>=4.0.0",
        "open3d>=0.17.0",
        "openai>=1.12.0",
        "anthropic>=0.18.0",
        "requests>=2.31.0",
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "PyQt6>=6.6.0",
        "pyopengl>=3.1.7",
        "pyqtgraph>=0.13.0",
        "numpy-stl>=3.0.0",
        "plyfile>=1.0.0",
        "plotly>=5.18.0",
        "python-dotenv>=1.0.0",
        "onnxruntime>=1.16.0",
        "onnx>=1.15.0",
        "aiohttp>=3.9.0",
        "websockets>=12.0",
        "scipy>=1.12.0",
        "scikit-learn>=1.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "build": [
            "pyinstaller>=6.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai3d=main:main",
        ],
    },
    package_data={
        "ai3d": [
            "frontend/web/*.html",
            "frontend/js/*.js",
            "config/*.example",
        ],
    },
    include_package_data=True,
)
