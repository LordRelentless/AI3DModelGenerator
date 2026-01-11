# AI 3D Model Generator

An AI-powered 3D model generation application with LLM integration, slicer preview, and multiple interface options (desktop GUI and web-based).

## Features

- **AI/LLM Input as Primary Interface**: Use natural language to describe 3D models with automatic LLM enhancement
- **Text-to-3D Generation**: Generate 3D models from text descriptions using Shap-E and Stable Diffusion models
- **Image Recognition**: Convert 2D images to 3D models using TripoSR
- **Local-First LLM**: Prioritizes local LLM (GLM 4.7, others) with fallback to cloud providers (OpenAI, Anthropic, OpenRouter)
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

## Quick Start (One-Click)

### Windows Users

Double-click `run.bat` to:
1. Create/activate virtual environment
2. Install dependencies automatically
3. Create `.env` file from template
4. Start the application with interactive menu

### Linux/Mac Users

```bash
chmod +x run.sh
./run.sh
```

This will:
1. Create/activate virtual environment
2. Install dependencies automatically
3. Create `.env` file from template
4. Start the application with interactive menu

### One-Click Options

Both scripts offer these modes:
1. **Desktop GUI** (Recommended) - Full-featured PyQt6 interface
2. **Web Interface** - Browser-based with WebGL viewer
3. **API Server** - Backend only (for developers)

### Manual Installation (Advanced)

If you prefer manual setup or want to customize installation:

1. **Clone repository** and navigate to project directory:
```bash
cd AI3DModelGenerator
```

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

The one-click scripts handle this automatically!

4. Configure environment variables:

**For One-Click Users:**
The `.env` file is created automatically on first run. Edit it to add your API keys (optional).

**For Manual Installation:**
```bash
cp .env.example .env
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

## Configuration

Edit `.env` file to configure application:

```env
# API Keys (optional - only needed if local LLM is unavailable)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Device (auto, cuda, mps, cpu)
DEVICE=auto

# API Server
SERVER_HOST=0.0.0.0  # Server bind address (0.0.0.0 listens on all interfaces)
API_HOST=127.0.0.1   # Client connection address (127.0.0.1 for local, server IP for remote)
API_PORT=5000

# Local LLM Configuration
DEFAULT_LLM=auto  # auto, local, openai, anthropic, openrouter
LOCAL_LLM_ENABLED=True
LOCAL_LLM_PATH=./models/llm
LOCAL_LLM_TYPE=transformers  # Options: transformers, glm4
# For GLM 4.7: LOCAL_LLM_PATH=THUDM/glm-4-9b-chat

# Networked LLM Configuration (e.g., LM Studio, oobabooga)
NETWORKED_LLM_URL=
NETWORKED_LLM_API_KEY=

# Model Auto-Download Configuration
AUTO_DOWNLOAD_MODELS=false  # Automatically download models on startup
AUTO_DOWNLOAD_3D_MODELS=true  # Download Shap-E, TripoSR
AUTO_DOWNLOAD_LLM_MODELS=false  # Download LLM models

# 3D Generation
DEFAULT_INFERENCE_STEPS=50
DEFAULT_GUIDANCE_SCALE=7.5
DEFAULT_FRAME_SIZE=256
MESH_RESOLUTION=256

**Default LLM Priority:**
1. Local LLM (if enabled and available) - Priority 1
2. Anthropic (if API key available) - Priority 90
3. OpenRouter (if API key available) - Priority 80
4. OpenAI (if API key available) - Priority 100

**Important:** The application automatically uses local LLM first. Remote/cloud providers are only used as fallback if local LLM is not available or if specifically selected.

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

### Model Management

- `POST /api/models/download` - Download model from Hugging Face Hub
- `POST /api/models/download-url` - Download model from direct URL
- `POST /api/models/auto-download` - Auto-download required models
- `GET /api/models/disk-space` - Get available disk space
- `GET /api/models/size?repo_id=<id>` - Get model size

### LLM Configuration

- `POST /api/llm/test-connection` - Test LLM provider connection
- `GET /api/llm/providers` - List available LLM providers (with priority info)
- `POST /api/llm/generate-prompt` - Generate enhanced 3D prompts using LLM

### Slicer

- `POST /api/slicer/create` - Create slicer instance
- `POST /api/slicer/load` - Load mesh into slicer
- `POST /api/slicer/slice` - Slice loaded mesh
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
- **ROCm**: AMD GPUs with ROCm support (including RX 9000 series: RX 9060, RX 9070 XT)
- **MPS**: Apple Silicon (M1/M2/M3) GPUs
- **CPU**: Fallback for systems without GPU support

All CUDA-specific operations have been replaced with PyTorch's device-agnostic operations.

## LLM Providers

### Default Behavior: Local-First
The application automatically prioritizes local LLMs for privacy and reduced latency. Remote/cloud providers are only used as fallback if local LLM is unavailable.

### Local LLM (Default - Highest Priority)
- **No API required** - Runs entirely on your machine
- **Privacy** - All processing stays local
- **Supported Models**:
  - GLM 4.7 (THUDM/glm-4-9b-chat) - Excellent for Chinese/English
  - Llama 2/3
  - Mistral
  - Any Hugging Face transformers model
- **Configuration**: Set `LOCAL_LLM_ENABLED=True` and provide `LOCAL_LLM_PATH`
- **Model Types**:
  - `transformers` (default): Standard Hugging Face models
  - `glm4`: GLM 4.7 specific optimizations

### OpenRouter (Fallback Priority 1)
- Requires API key in `.env`
- Access to 100+ models through single API
- Supports Anthropic, OpenAI, Google, Meta, etc.
- Cost-effective compared to direct provider APIs
- Models: `anthropic/claude-3-opus`, `openai/gpt-4`, `google/gemini-pro`, etc.

### Networked Local LLM (Fallback Priority 2)
- No API required (optional key for authenticated servers)
- Connect to local LLM servers (LM Studio, Oobabooga, Text-Generation-WebUI, etc.)
- **Privacy**: All processing on your local network
- **Configuration**: Set `NETWORKED_LLM_URL` in `.env`
- **Auto-Detection**: Test connections automatically
- Example URLs:
  - `http://localhost:5000` (LM Studio default)
  - `http://192.168.1.100:5000` (Local network server)
  - `https://your-server.com` (Remote server)

### Anthropic (Fallback Priority 2)
- Requires API key in `.env`
- Alternative to OpenAI
- Strong prompt engineering capabilities
- Models: Claude 3 Opus, Sonnet, Haiku

### OpenAI (Fallback Priority 3)
- Requires API key in `.env`
- Best for prompt enhancement
- High-quality 3D model descriptions
- Models: GPT-4, GPT-3.5 Turbo

**Note:** API keys for remote providers are optional. The application works fine with local LLM only, which is the recommended default configuration.

## Model Auto-Downloader

The application includes automatic model downloading for all AI models:

### Features
- **Hugging Face Integration**: Download models directly from Hugging Face Hub
- **Direct URL Support**: Download from any model URL
- **Auto-Download**: Automatically download required models on startup
- **Progress Tracking**: Real-time download progress with progress bars
- **Disk Space Check**: Verify available space before downloading
- **Model Size Info**: Get model sizes before downloading
- **Organized Storage**: Models organized by type (3d, llm, image)

### Configuration
```env
# Auto-Download Settings
AUTO_DOWNLOAD_MODELS=false  # Automatically download models on startup
AUTO_DOWNLOAD_3D_MODELS=true  # Download Shap-E, TripoSR
AUTO_DOWNLOAD_LLM_MODELS=false  # Download LLM models
```

### API Endpoints
- `POST /api/models/download` - Download from Hugging Face Hub
- `POST /api/models/download-url` - Download from direct URL
- `POST /api/models/auto-download` - Download all required models
- `GET /api/models/disk-space` - Check available disk space
- `GET /api/models/size?repo_id=<id>` - Get model size info

### Usage
```bash
# Download a specific model
curl -X POST http://localhost:5000/api/models/download \
  -H "Content-Type: application/json" \
  -d '{
    "repo_id": "openai/shap-e",
    "model_type": "3d",
    "show_progress": true
  }'

# Auto-download all required models
curl -X POST http://localhost:5000/api/models/auto-download

# Check disk space
curl http://localhost:5000/api/models/disk-space
```

## One-Click Run Scripts

The project includes one-click run scripts for easy setup and launch:

### Windows: `run.bat`

Double-click `run.bat` to:
- ✅ Create/activate Python virtual environment
- ✅ Install all dependencies via pip
- ✅ Create `.env` configuration file from template
- ✅ Interactive mode selection (GUI/Web/API)
- ✅ Color-coded progress with step numbers
- ✅ Auto-detect and use best available Python

### Linux/Mac: `run.sh`

```bash
chmod +x run.sh
./run.sh
```

This will:
- ✅ Create/activate Python virtual environment
- ✅ Install all dependencies via pip
- ✅ Create `.env` configuration file from template
- ✅ Interactive mode selection (GUI/Web/API)
- ✅ Auto-detect python3 vs python
- ✅ Open browser automatically for web mode

### Script Features

**Setup Process:**
- Creates virtual environment if not exists
- Upgrades pip to latest version
- Installs all requirements from requirements.txt
- Creates .env from .env.example if missing
- Creates required directories (output/, models/, logs/, etc.)

**Mode Selection:**
- Desktop GUI: Starts PyQt6 application (default)
- Web Interface: Opens browser at http://localhost:5000/
- API Server: Starts Flask API only (for developers)
- Auto-prompt: Interactive mode selection

**Platform Detection:**
- Windows: Uses `venv\Scripts\activate.bat`
- Linux/Mac: Uses `source venv/bin/activate`
- Auto-detects python3 or python
- Tries to open browser automatically for web mode

**No more manual setup!** Just run the script and you're ready.

### Command-Line Options

The scripts also support command-line arguments:

**Windows:**
```batch
run.bat --gui    # Force GUI mode
run.bat --web    # Force web mode
run.bat --api    # Force API mode
```

**Linux/Mac:**
```bash
./run.sh --gui    # Force GUI mode
./run.sh --web    # Force web mode
./run.sh --api    # Force API mode
```

### Manual Installation (Advanced)

For users who prefer manual control over installation process:

1. Clone repository and navigate to project directory:

```bash
cd AI3DModelGenerator
```

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

## Troubleshooting

### Installation Issues

**"Module not found" errors**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt --upgrade
```

**"No matching distribution found" for open3d**
- This package is not required for basic usage
- 3D visualization is handled via WebGL (web) or PyQt6 (desktop)
- The application doesn't use open3d library

**Python version compatibility**
- Minimum Python version: 3.8
- Recommended Python version: 3.9 or 3.10
- For Python 3.11+: Ensure all packages are updated
```bash
# Check Python version
python --version

# Update pip and packages
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --upgrade
```

**Virtual environment issues**
```bash
# Remove existing venv and recreate
rm -rf venv
python -m venv venv

# Windows
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate
```

### Runtime Issues

**Out of memory errors**
- Reduce `frame_size` in generation parameters (try 128 instead of 256)
- Reduce `num_inference_steps` (try 25 instead of 50)
- Use CPU mode if GPU memory is limited
- Close other applications to free up memory
- Check memory usage: `GET /api/device/info`

**Slow generation**
- Verify GPU is being used: Check `GET /api/device/info`
- Ensure PyTorch is installed with GPU support
- NVIDIA: `pip install torch --index-url https://download.pytorch.org/whl/cu118`
- AMD: Use ROCm-enabled PyTorch from official AMD sources
- Apple Silicon: MPS is automatically detected
- Reduce inference steps for faster (but lower quality) results

**Local LLM not working**
- Check `LOCAL_LLM_ENABLED=True` in `.env`
- Verify model path: Ensure `LOCAL_LLM_PATH` is correct
- For GLM 4.7: Use `LOCAL_LLM_PATH=THUDM/glm-4-9b-chat`
- Check transformers is installed: `pip install transformers`
- Verify model files exist in specified directory
- Check logs for error messages

**Networked LLM connection failed**
- Test connection: Use `POST /api/llm/test-connection`
- Verify URL format: Should include `http://` or `https://`
- Check if server is running (e.g., LM Studio: `lm-studio --listen`)
- Check firewall settings
- Verify API key if server requires authentication
- Try different port if using custom server

**Model download failures**
- Check disk space: Use `GET /api/models/disk-space`
- Verify internet connection
- Try manual download: Use `POST /api/models/download-url`
- Check Hugging Face Hub status: https://huggingface.co/
- Ensure write permissions to models/ directory
- Try with `show_progress=true` to see detailed errors

### GPU Detection Issues

**AMD GPU not detected as ROCm**
- Ensure ROCm is installed from AMD: https://rocm.docs.amd.com/
- Install ROCm-enabled PyTorch
- Check device detection: Use `GET /api/device/info`
- Verify AMD GPU is recognized by ROCm

**Apple Silicon not detected**
- PyTorch 2.0+ includes MPS support
- Install latest PyTorch: `pip install torch --upgrade`
- Restart application after PyTorch upgrade

**CUDA not available on NVIDIA GPU**
- Update GPU drivers to latest version
- Install CUDA-enabled PyTorch
- Check PyTorch version compatibility with CUDA version
- Reinstall PyTorch: `pip uninstall torch && pip install torch`

### Application Issues

**Desktop GUI not starting**
- Ensure PyQt6 is installed: `pip install PyQt6`
- Check if port 5000 is available (API server conflict)
- Try API mode: `python main.py --mode api`
- Check logs/ directory for error messages

**Web interface not loading**
- Verify API server is running
- Check browser console for CORS errors
- Clear browser cache
- Try different browser (Chrome, Firefox, Edge)
- Disable browser extensions temporarily

**Slicer not working**
- Ensure mesh file is valid format (PLY, OBJ, STL)
- Check trimesh is installed: `pip install trimesh`
- Verify mesh is not corrupted
- Try with simpler geometry first
- Check file permissions for output directory

### Getting Help

- Check full README.md for detailed documentation
- Review API endpoints at `http://localhost:5000/`
- Ensure all dependencies are properly installed
- Verify your GPU drivers are up to date
- Check logs/ directory for detailed error messages
- Open GitHub issue: https://github.com/LordRelentless/AI3DModelGenerator/issues
- Include your system information: OS, Python version, GPU details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- GitHub Issues: https://github.com/LordRelentless/AI3DModelGenerator/issues
- Documentation: https://github.com/LordRelentless/AI3DModelGenerator/wiki
