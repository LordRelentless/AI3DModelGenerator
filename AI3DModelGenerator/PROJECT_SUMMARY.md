# AI 3D Model Generator - Project Summary

## Overview

A comprehensive AI-powered 3D model generation application with the following features:

- ✅ **AI/LLM Input**: Natural language interface with LLM enhancement (OpenAI, Anthropic, Local)
- ✅ **Text-to-3D Generation**: Generate 3D models from text using Shap-E
- ✅ **Image-to-3D Conversion**: Convert 2D images to 3D meshes using TripoSR
- ✅ **GPU Agnostic**: Supports NVIDIA CUDA, AMD ROCm, Apple Silicon MPS, and CPU
- ✅ **Slicer Preview**: Built-in 3D slicer with G-code export
- ✅ **Multiple Interfaces**: Desktop GUI (PyQt6) and Web (Three.js WebGL)
- ✅ **REST API**: Full-featured API for integration
- ✅ **Standalone Executable**: Can be compiled with PyInstaller

## Project Structure

```
AI3DModelGenerator/
├── backend/
│   ├── api/                    # Flask REST API
│   │   └── app.py            # API endpoints for all functionality
│   ├── core/                   # Core functionality
│   │   ├── device_manager.py  # GPU-agnostic device management
│   │   └── llm_manager.py     # LLM provider integration
│   ├── models/                 # 3D generation
│   │   └── generator.py      # Shap-E, TripoSR, text-to-3D pipelines
│   └── utils/                 # Utilities
│       └── slicer.py          # 3D model slicer with G-code export
├── config/
│   └── config.py              # Configuration management
├── frontend/
│   ├── gui/                   # PyQt6 desktop application
│   │   └── main.py          # Desktop GUI with 3D viewer
│   ├── web/                   # Web interface
│   │   └── index.html        # HTML interface
│   └── js/                    # WebGL JavaScript
│       └── app.js            # Three.js 3D viewer and API client
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── setup.py                  # Package installation
├── README.md                 # Full documentation
├── QUICKSTART.md            # Quick start guide
└── .env.example             # Environment configuration template
```

## Key Components

### 1. Device Manager (`backend/core/device_manager.py`)
- Automatic device detection (CUDA, MPS, CPU)
- GPU memory management
- Device information reporting
- Cache clearing and optimization

### 2. LLM Manager (`backend/core/llm_manager.py`)
- Support for multiple LLM providers:
  - OpenAI (GPT-4, GPT-3.5)
  - Anthropic (Claude)
  - Local models (Llama, Mistral, etc.)
- Prompt enhancement for 3D generation
- Async API calls

### 3. 3D Generator (`backend/models/generator.py`)
- **Text-to-3D**: Shap-E pipeline for direct text-to-3D
- **Image-to-3D**: TripoSR for 2D-to-3D conversion
- **Pipeline**: Combined text-to-image-to-3D workflow
- GPU-agnostic PyTorch operations
- Multiple output formats (PLY, OBJ)

### 4. Slicer (`backend/utils/slicer.py`)
- Layer-by-layer slicing
- Configurable parameters (layer height, fill density, etc.)
- G-code generation
- JSON export for custom workflows
- Layer preview data

### 5. REST API (`backend/api/app.py`)
Complete API with endpoints for:
- Health and device info
- LLM prompt generation
- 3D model generation
- Image-to-3D conversion
- Slicing and layer preview
- File serving

### 6. Desktop GUI (`frontend/gui/main.py`)
PyQt6 application with:
- Text-to-3D generation tab
- Slicer preview tab
- Real-time progress tracking
- Device information display
- File browser integration

### 7. Web Interface (`frontend/web/index.html` + `frontend/js/app.js`)
Browser-based interface featuring:
- Three.js WebGL 3D viewer
- Real-time generation
- LLM prompt enhancement
- Slicer controls
- Layer-by-layer preview
- Auto-rotate and wireframe modes

## Technology Stack

### Backend
- **Python 3.8+**
- **Flask**: REST API server
- **PyTorch**: Deep learning framework
- **Diffusers**: Hugging Face diffusion models
- **Transformers**: LLM integration
- **Trimesh**: 3D mesh processing

### Frontend
- **PyQt6**: Desktop GUI
- **Three.js**: WebGL 3D rendering
- **HTML5/CSS3**: Web interface
- **JavaScript**: Client-side logic

### AI Models
- **Shap-E** (OpenAI): Text-to-3D generation
- **TripoSR** (Stability AI): Image-to-3D conversion
- **Stable Diffusion**: Text-to-image generation

## GPU Agnostic Implementation

All CUDA-specific operations replaced with PyTorch device-agnostic code:

```python
# Instead of: torch.cuda.is_available()
if self.device.type == 'cuda':

# Automatic device selection
device = DeviceManager.get_device()  # Returns cuda, mps, or cpu

# Device-agnostic tensor operations
tensor = tensor.to(device)
```

Supported hardware:
- **NVIDIA GPUs**: CUDA with PyTorch CUDA support
- **AMD GPUs**: ROCm (requires ROCm-enabled PyTorch)
- **Apple Silicon**: MPS (Metal Performance Shaders)
- **CPU**: Fallback for all systems

## Usage Modes

### 1. API Only
```bash
python main.py --mode api
```
Access at: `http://localhost:5000/api/`

### 2. Desktop GUI
```bash
python main.py --mode gui
```
Launches PyQt6 application

### 3. Web Interface
```bash
python main.py --mode web
```
Access at: `http://localhost:5000/`

## Configuration

Environment variables (`.env` file):
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `DEVICE`: auto, cuda, mps, or cpu
- `API_HOST`: Server host (default: 0.0.0.0)
- `API_PORT`: Server port (default: 5000)
- `DEFAULT_LLM`: Default LLM provider
- `LOCAL_LLM_ENABLED`: Enable local LLM support

## Installation

```bash
# Clone repository
git clone <repository_url>
cd AI3DModelGenerator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run application
python main.py --mode gui
```

## API Endpoints

### Health & Device
- `GET /api/health` - Health check
- `GET /api/device/info` - Device information

### LLM Integration
- `GET /api/llm/providers` - List providers
- `POST /api/llm/generate-prompt` - Generate enhanced prompt

### 3D Generation
- `POST /api/generator/create` - Create generator instance
- `POST /api/generator/text-to-3d` - Generate from text
- `POST /api/generator/image-to-3d` - Generate from image

### Slicer
- `POST /api/slicer/create` - Create slicer
- `POST /api/slicer/load` - Load mesh
- `POST /api/slicer/slice` - Slice mesh
- `GET /api/slicer/layer/<id>/<index>` - Get layer preview
- `POST /api/slicer/export/gcode` - Export G-code
- `POST /api/slicer/export/json` - Export JSON

## Building Standalone Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

Output: `dist/main.exe` (Windows) or `dist/main` (Linux/Mac)

## Features Implemented

### ✅ Completed Features

1. **GPU Agnostic Design**
   - Device auto-detection
   - Support for CUDA, MPS, CPU
   - Memory management

2. **LLM Integration**
   - OpenAI (GPT-4/3.5)
   - Anthropic (Claude)
   - Local models
   - Prompt enhancement

3. **3D Generation**
   - Text-to-3D with Shap-E
   - Image-to-3D with TripoSR
   - Combined pipelines
   - Multiple output formats

4. **Slicer**
   - Layer-based slicing
   - G-code generation
   - JSON export
   - Configurable parameters

5. **Desktop GUI**
   - PyQt6 interface
   - Text-to-3D tab
   - Slicer preview tab
   - Real-time progress

6. **Web Interface**
   - Three.js WebGL viewer
   - Responsive design
   - Layer preview
   - API integration

7. **REST API**
   - Comprehensive endpoints
   - JSON responses
   - Error handling
   - File serving

## Next Steps for Users

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Add API keys (optional)
   - Configure device preference

3. **Run Application**
   ```bash
   python main.py --mode gui
   ```

4. **Generate First Model**
   - Enter a simple prompt
   - Click "Generate"
   - View results

5. **Try Advanced Features**
   - Use LLM enhancement
   - Slice for 3D printing
   - Export to different formats

## Notes

- Model downloads happen on first use and are cached locally
- GPU acceleration requires appropriate PyTorch installation
- API keys are optional (LLM features available with keys)
- CPU fallback works but is significantly slower
- Memory usage depends on model size and settings

## Troubleshooting

**CUDA not available?**
- Install PyTorch with CUDA support
- Update GPU drivers
- Check CUDA version compatibility

**Out of memory?**
- Reduce `frame_size`
- Reduce `inference_steps`
- Use CPU mode

**Slow generation?**
- Verify GPU is being used
- Check `GET /api/device/info`
- Reduce inference steps

## License

MIT License

## Contributing

Contributions welcome! Areas for improvement:
- Additional 3D generation models
- More slicer features
- Better error handling
- More GUI options
- Performance optimizations
