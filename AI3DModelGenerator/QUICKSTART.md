# Quick Start Guide

## Installation

1. **Clone the repository** and navigate to the project directory:
```bash
cd AI3DModelGenerator
```

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys (optional):
```env
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## Running the Application

### Option 1: API Server Only
For backend access or custom frontend:

```bash
python main.py --mode api
```

Server will be available at: `http://localhost:5000`

### Option 2: Desktop GUI (Recommended)
Full-featured desktop application:

```bash
python main.py --mode gui
```

This launches both the API server and PyQt6 desktop application.

### Option 3: Web Interface
Browser-based interface with WebGL viewer:

```bash
python main.py --mode web
```

Access at: `http://localhost:5000/`

## First Time Use

### Generate a Simple 3D Model

1. Start the application (e.g., `python main.py --mode gui`)
2. In the "Text to 3D" tab, enter a prompt like:
   ```
   A red coffee mug with handle
   ```
3. Click "Generate 3D Model"
4. Wait for generation to complete
5. View the generated mesh

### Using LLM Enhancement

1. Enter a basic description: "A spaceship"
2. Select an LLM provider (e.g., "openai")
3. Click "Enhance with LLM"
4. The prompt will be expanded with more details
5. Click "Generate 3D Model" with the enhanced prompt

### Slicing a Model for 3D Printing

1. Generate or load a 3D model
2. Switch to the "Slicer Preview" tab
3. Enter the mesh file path (or browse)
4. Configure slicing parameters:
   - Layer Height: 0.2mm
   - Nozzle Diameter: 0.4mm
   - Fill Density: 0.2
5. Click "Slice Model"
6. Preview layers using the layer controls
7. Export to G-code for your printer

## Common Issues

### "Module not found" errors
Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

### CUDA out of memory
- Reduce frame_size (try 128 instead of 256)
- Reduce inference_steps (try 25 instead of 50)
- Use CPU mode by setting `DEVICE=cpu` in `.env`

### Slow generation
- Check if GPU is detected via API: `GET /api/device/info`
- Ensure PyTorch is installed with CUDA support (if using NVIDIA GPU)
- Reduce inference steps for faster but lower quality results

### API key errors
- Add your API keys to `.env` file
- Ensure no extra spaces around the keys
- Verify the keys are valid and active

## Project Structure

```
AI3DModelGenerator/
├── backend/
│   ├── api/          # Flask REST API server
│   ├── core/         # Device manager, LLM integration
│   ├── models/       # 3D generation (Shap-E, TripoSR)
│   └── utils/        # Slicer, utilities
├── config/           # Configuration management
├── frontend/
│   ├── gui/          # PyQt6 desktop application
│   ├── web/          # HTML web interface
│   └── js/           # WebGL JavaScript
├── output/           # Generated models (auto-created)
├── models/           # Cached AI models (auto-created)
└── logs/             # Application logs (auto-created)
```

## Next Steps

- Explore different prompts for better 3D models
- Try different LLM providers for prompt enhancement
- Experiment with slicer settings for optimal print quality
- Integrate with your 3D printer's workflow
- Contribute improvements to the project!

## Getting Help

- Check the full README.md for detailed documentation
- Review API endpoints at `http://localhost:5000/`
- Ensure all dependencies are properly installed
- Verify your GPU drivers are up to date

## Tips for Better Results

### Prompts
- Be specific about materials (e.g., "wooden", "metallic", "glass")
- Include scale references (e.g., "life-size", "miniature")
- Describe orientation and pose
- Mention lighting conditions for textures

### LLM Enhancement
- Use simple descriptions and let LLM expand them
- Different providers may give different results
- Can combine: start simple, enhance, then edit manually

### Slicing
- Lower layer height = better quality, longer print time
- Higher fill density = stronger parts, more material used
- Adjust based on your printer's capabilities
