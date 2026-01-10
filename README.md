# AI 3D Model Generator

An AI-powered 3D model generation application with LLM integration, slicer preview, and multiple interface options (desktop GUI and web-based).

## Features

- **AI/LLM Input as Primary Interface**: Use natural language to describe 3D models with optional LLM enhancement
- **Text-to-3D Generation**: Generate 3D models from text descriptions using Shap-E and Stable Diffusion models
- **Image Recognition**: Convert 2D images to 3D models using TripoSR
- **Multiple LLM Providers**: Support for OpenAI, Anthropic, and local LLM models
- **GPU Agnostic**: Works with NVIDIA CUDA, AMD ROCm, Apple Silicon (MPS), and CPU
- **Slicer Preview**: Built-in 3D slicer for print preparation with G-code export
- **Multiple Interfaces**: 
  - Desktop GUI (PyQt6)
  - Web interface (Three.js WebGL viewer)
  - API-only mode

## Requirements

- Python 3.8+
- pip
- (Optional) CUDA-capable GPU with CUDA 11.8+
- (Optional) Apple Silicon Mac (M1/M2/M3) with MPS support
- (Optional) AMD GPU with ROCm support

## Installation

1. Clone the repository:
```bash
git clone https://github.com/LordRelentless/AI3DModelGenerator.git
cd AI3DModelGenerator
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

## Configuration

Edit the `.env` file to configure the application:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Device (auto, cuda, mps, cpu)
DEVICE=auto

# API Server
API_HOST=0.0.0.0
API_PORT=5000

# LLM Configuration
DEFAULT_LLM=openai
LOCAL_LLM_ENABLED=False
LOCAL_LLM_PATH=./models/llm

# 3D Generation
DEFAULT_INFERENCE_STEPS=50
DEFAULT_GUIDANCE_SCALE=7.5
DEFAULT_FRAME_SIZE=256
MESH_RESOLUTION=256
```

## Usage

### Run as API Server Only

```bash
python main.py --mode api
```

### Run with Desktop GUI (PyQt6)

```bash
python main.py --mode gui
```

This will start both the API server and the PyQt6 desktop application.

### Run with Web Interface

```bash
python main.py --mode web
```

This will start the API server and provide a web interface at `http://localhost:5000/`

## API Endpoints

### Health & Device

- `GET /api/health` - Health check
- `GET /api/device/info` - Device information

### LLM Integration

- `GET /api/llm/providers` - List available LLM providers
- `POST /api/llm/generate-prompt` - Generate enhanced 3D prompts using LLM

### 3D Generation

- `POST /api/generator/create` - Create a generator instance
- `POST /api/generator/text-to-3d` - Generate 3D model from text
- `POST /api/generator/image-to-3d` - Generate 3D model from image

### Slicer

- `POST /api/slicer/create` - Create slicer instance
- `POST /api/slicer/load` - Load mesh into slicer
- `POST /api/slicer/slice` - Slice the loaded mesh
- `GET /api/slicer/layer/<slicer_id>/<layer_index>` - Get layer preview
- `POST /api/slicer/export/gcode` - Export to G-code
- `POST /api/slicer/export/json` - Export to JSON

## Desktop GUI Features

The PyQt6-based desktop application includes:

- **Text-to-3D Tab**: Generate 3D models from text with LLM enhancement
- **Slicer Preview Tab**: Preview slices and export G-code
- Real-time progress tracking
- Device information display
- Mesh and slicer statistics

## Web Interface Features

The web-based interface includes:

- **Three.js WebGL Viewer**: Interactive 3D model visualization
- Real-time generation progress
- Layer-by-layer slicer preview
- Responsive design
- Auto-rotate and wireframe modes

## Supported 3D Models

- PLY (Polygon File Format)
- OBJ (Wavefront OBJ)
- STL (Stereolithography)

## GPU Agnostic Design

The application automatically detects and uses the best available hardware:

- **CUDA**: NVIDIA GPUs with CUDA support
- **MPS**: Apple Silicon (M1/M2/M3) GPUs
- **CPU**: Fallback for systems without GPU support

All CUDA-specific operations have been replaced with PyTorch's device-agnostic operations.

## LLM Providers

### OpenAI (GPT-4/GPT-3.5)
- Requires API key in `.env`
- Best for prompt enhancement
- High-quality 3D model descriptions

### Anthropic (Claude)
- Requires API key in `.env`
- Alternative to OpenAI
- Strong prompt engineering

### Local LLM
- No API required
- Requires local model installation
- Supports various open-source models (Llama, Mistral, etc.)

## Examples

### Generate a 3D Model from Text

```bash
curl -X POST http://localhost:5000/api/generator/create \
  -H "Content-Type: application/json" \
  -d '{"type": "text-to-3d"}'

curl -X POST http://localhost:5000/api/generator/text-to-3d \
  -H "Content-Type: application/json" \
  -d '{
    "generator_id": "your_generator_id",
    "prompt": "A detailed medieval castle with towers and moat",
    "guidance_scale": 7.5,
    "num_inference_steps": 50,
    "frame_size": 256
  }'
```

### Slice a 3D Model

```bash
curl -X POST http://localhost:5000/api/slicer/create \
  -H "Content-Type: application/json" \
  -d '{
    "layer_height": 0.2,
    "nozzle_diameter": 0.4,
    "fill_density": 0.2
  }'

curl -X POST http://localhost:5000/api/slicer/load \
  -H "Content-Type: application/json" \
  -d '{
    "slicer_id": "your_slicer_id",
    "mesh_path": "/path/to/model.ply"
  }'

curl -X POST http://localhost:5000/api/slicer/slice \
  -H "Content-Type: application/json" \
  -d '{"slicer_id": "your_slicer_id"}'
```

## Troubleshooting

### Out of Memory Errors
- Reduce `frame_size` or `inference_steps`
- Use CPU mode instead of GPU
- Close other applications

### Slow Generation
- Check if GPU is being used: `GET /api/device/info`
- Reduce `inference_steps`
- Use smaller `frame_size`

### Model Download Issues
- Ensure internet connection for first-time model download
- Models are cached locally after first download

## Building Standalone Executable

Using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=assets/icon.ico \
  --name="AI3DModelGenerator" \
  --add-data="frontend:frontend" \
  --add-data="config:config" \
  --add-data="backend:backend" \
  main.py
```

## Project Structure

```
AI3DModelGenerator/
├── backend/
│   ├── api/          # Flask API server
│   ├── core/         # Core functionality (device, LLM)
│   ├── models/       # 3D generation models
│   └── utils/        # Utilities (slicer)
├── config/           # Configuration management
├── frontend/
│   ├── gui/          # PyQt6 desktop application
│   ├── web/          # Web interface HTML
│   └── js/           # WebGL JavaScript
├── output/           # Generated models and exports
├── models/           # Cached AI models
├── logs/             # Application logs
├── main.py          # Entry point
├── requirements.txt # Python dependencies
└── .env            # Environment configuration
```

## License

MIT License - see LICENSE file for details

## Acknowledgments

- OpenAI Shap-E for text-to-3D generation
- Stability AI TripoSR for image-to-3D conversion
- Diffusers library for model integration
- Three.js for WebGL 3D rendering
- PyQt6 for desktop GUI

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- GitHub Issues: https://github.com/LordRelentless/AI3DModelGenerator/issues
- Documentation: https://github.com/LordRelentless/AI3DModelGenerator/wiki
