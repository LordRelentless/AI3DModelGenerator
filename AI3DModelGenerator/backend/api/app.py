from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import asyncio
from typing import Dict, Any
import uuid

from config.config import Config
from backend.core.device_manager import get_device, get_device_info
from backend.core.llm_manager import LLMManager, OpenAIProvider, AnthropicProvider, LocalLLMProvider
from backend.models.generator import create_generator
from backend.utils.slicer import Slicer, SlicerConfig

app = Flask(__name__, static_folder='../../frontend/web', static_url_path='/static')
CORS(app)

llm_manager = LLMManager()
generators = {}
slicers = {}

def init_llm_providers():
    if Config.API_KEYS['openai']:
        llm_manager.add_provider('openai', OpenAIProvider(Config.API_KEYS['openai']))
    
    if Config.API_KEYS['anthropic']:
        llm_manager.add_provider('anthropic', AnthropicProvider(Config.API_KEYS['anthropic']))
    
    if Config.LOCAL_LLM_ENABLED:
        llm_manager.add_provider('local', LocalLLMProvider(Config.LOCAL_LLM_PATH))

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'device': get_device_info()
    })

@app.route('/api/device/info', methods=['GET'])
def device_info():
    return jsonify(get_device_info())

@app.route('/api/llm/providers', methods=['GET'])
def list_llm_providers():
    providers = list(llm_manager.providers.keys())
    available = {k: v.available for k, v in llm_manager.providers.items()}
    return jsonify({
        'providers': providers,
        'available': available
    })

@app.route('/api/llm/generate-prompt', methods=['POST'])
async def generate_3d_prompt():
    data = request.json
    user_input = data.get('input', '')
    provider = data.get('provider', Config.DEFAULT_LLM)
    
    if not user_input:
        return jsonify({'error': 'Input is required'}), 400
    
    try:
        result = await llm_manager.generate_3d_prompt(provider, user_input)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generator/create', methods=['POST'])
def create_generator_endpoint():
    data = request.json
    generator_id = str(uuid.uuid4())
    model_type = data.get('type', 'text-to-3d')
    model_path = data.get('model_path')
    
    try:
        generator = create_generator(model_type, model_path)
        generators[generator_id] = generator
        return jsonify({
            'generator_id': generator_id,
            'model_type': model_type,
            'model_path': model_path
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generator/text-to-3d', methods=['POST'])
def text_to_3d():
    data = request.json
    generator_id = data.get('generator_id')
    
    if not generator_id or generator_id not in generators:
        return jsonify({'error': 'Invalid generator ID'}), 400
    
    prompt = data.get('prompt', '')
    guidance_scale = data.get('guidance_scale', Config.DEFAULT_GUIDANCE_SCALE)
    num_inference_steps = data.get('num_inference_steps', Config.DEFAULT_INFERENCE_STEPS)
    frame_size = data.get('frame_size', Config.DEFAULT_FRAME_SIZE)
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    try:
        generator = generators[generator_id]
        mesh = generator.generate_mesh(
            prompt=prompt,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            frame_size=frame_size
        )
        
        if mesh is None:
            return jsonify({'error': 'Failed to generate mesh'}), 500
        
        output_path = Config.OUTPUT_DIR / f"{generator_id}_mesh.ply"
        success = generator.export_mesh_to_ply(mesh, output_path)
        
        if success:
            return jsonify({
                'success': True,
                'mesh_path': str(output_path),
                'output_filename': f"{generator_id}_mesh.ply"
            })
        else:
            return jsonify({'error': 'Failed to export mesh'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generator/image-to-3d', methods=['POST'])
def image_to_3d():
    data = request.json
    generator_id = data.get('generator_id')
    
    if not generator_id or generator_id not in generators:
        return jsonify({'error': 'Invalid generator ID'}), 400
    
    if 'image' not in request.files:
        return jsonify({'error': 'Image file is required'}), 400
    
    image_file = request.files['image']
    resolution = data.get('resolution', Config.MESH_RESOLUTION)
    threshold = data.get('threshold', 25.0)
    
    try:
        from PIL import Image
        import io
        
        image = Image.open(io.BytesIO(image_file.read()))
        
        generator = generators[generator_id]
        mesh = generator.generate_mesh_from_image(
            image=image,
            resolution=resolution,
            threshold=threshold
        )
        
        if mesh is None:
            return jsonify({'error': 'Failed to generate mesh'}), 500
        
        output_path = Config.OUTPUT_DIR / f"{generator_id}_image_mesh.ply"
        
        try:
            import trimesh
            trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces).export(str(output_path))
            
            return jsonify({
                'success': True,
                'mesh_path': str(output_path),
                'output_filename': f"{generator_id}_image_mesh.ply"
            })
        except Exception as e:
            return jsonify({'error': f'Failed to save mesh: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/slicer/create', methods=['POST'])
def create_slicer_endpoint():
    data = request.json
    slicer_id = str(uuid.uuid4())
    
    config = SlicerConfig(
        layer_height=data.get('layer_height', 0.2),
        first_layer_height=data.get('first_layer_height', None),
        nozzle_diameter=data.get('nozzle_diameter', 0.4),
        fill_density=data.get('fill_density', 0.2),
        fill_pattern=data.get('fill_pattern', 'grid'),
        perimeter_count=data.get('perimeter_count', 2),
        top_solid_layers=data.get('top_solid_layers', 3),
        bottom_solid_layers=data.get('bottom_solid_layers', 3)
    )
    
    slicer = Slicer(config)
    slicers[slicer_id] = slicer
    
    return jsonify({
        'slicer_id': slicer_id,
        'config': {
            'layer_height': config.layer_height,
            'nozzle_diameter': config.nozzle_diameter,
            'fill_density': config.fill_density
        }
    })

@app.route('/api/slicer/load', methods=['POST'])
def load_mesh_to_slicer():
    data = request.json
    slicer_id = data.get('slicer_id')
    mesh_path = data.get('mesh_path')
    
    if not slicer_id or slicer_id not in slicers:
        return jsonify({'error': 'Invalid slicer ID'}), 400
    
    if not mesh_path:
        return jsonify({'error': 'Mesh path is required'}), 400
    
    try:
        slicer = slicers[slicer_id]
        success = slicer.load_mesh(mesh_path)
        
        if success:
            stats = slicer.get_statistics()
            return jsonify({
                'success': True,
                'bounding_box': stats.get('bounding_box')
            })
        else:
            return jsonify({'error': 'Failed to load mesh'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/slicer/slice', methods=['POST'])
def slice_mesh():
    data = request.json
    slicer_id = data.get('slicer_id')
    
    if not slicer_id or slicer_id not in slicers:
        return jsonify({'error': 'Invalid slicer ID'}), 400
    
    try:
        slicer = slicers[slicer_id]
        layers = slicer.slice_mesh()
        
        return jsonify({
            'success': True,
            'total_layers': len(layers),
            'statistics': slicer.get_statistics()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/slicer/layer/<slicer_id>/<int:layer_index>', methods=['GET'])
def get_layer_preview(slicer_id, layer_index):
    if slicer_id not in slicers:
        return jsonify({'error': 'Invalid slicer ID'}), 400
    
    try:
        slicer = slicers[slicer_id]
        layer_data = slicer.get_layer_preview(layer_index)
        
        if layer_data:
            return jsonify(layer_data)
        else:
            return jsonify({'error': 'Layer not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/slicer/export/gcode', methods=['POST'])
def export_gcode():
    data = request.json
    slicer_id = data.get('slicer_id')
    output_filename = data.get('output_filename', 'output.gcode')
    
    if not slicer_id or slicer_id not in slicers:
        return jsonify({'error': 'Invalid slicer ID'}), 400
    
    try:
        slicer = slicers[slicer_id]
        output_path = Config.OUTPUT_DIR / output_filename
        success = slicer.export_to_gcode(str(output_path))
        
        if success:
            return jsonify({
                'success': True,
                'output_path': str(output_path)
            })
        else:
            return jsonify({'error': 'Failed to export G-code'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/slicer/export/json', methods=['POST'])
def export_slicer_json():
    data = request.json
    slicer_id = data.get('slicer_id')
    output_filename = data.get('output_filename', 'slicer_data.json')
    
    if not slicer_id or slicer_id not in slicers:
        return jsonify({'error': 'Invalid slicer ID'}), 400
    
    try:
        slicer = slicers[slicer_id]
        output_path = Config.OUTPUT_DIR / output_filename
        success = slicer.export_to_json(str(output_path))
        
        if success:
            return jsonify({
                'success': True,
                'output_path': str(output_path)
            })
        else:
            return jsonify({'error': 'Failed to export JSON'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/output/<path:filename>', methods=['GET'])
def serve_output_file(filename):
    return send_from_directory(Config.OUTPUT_DIR, filename)

@app.route('/', methods=['GET'])
def index():
    web_path = Path(__file__).parent.parent.parent / 'frontend' / 'web' / 'index.html'
    if web_path.exists():
        return send_from_directory(str(web_path.parent), 'index.html')
    return jsonify({
        'name': 'AI 3D Model Generator API',
        'version': '1.0.0',
        'endpoints': [
            '/api/health',
            '/api/device/info',
            '/api/llm/providers',
            '/api/llm/generate-prompt',
            '/api/generator/create',
            '/api/generator/text-to-3d',
            '/api/generator/image-to-3d',
            '/api/slicer/create',
            '/api/slicer/load',
            '/api/slicer/slice',
            '/api/slicer/layer/<slicer_id>/<layer_index>',
            '/api/slicer/export/gcode',
            '/api/slicer/export/json'
        ]
    })

def run_server():
    init_llm_providers()
    print(f"Starting server on {Config.API_HOST}:{Config.API_PORT}")
    app.run(
        host=Config.API_HOST,
        port=Config.API_PORT,
        debug=Config.DEBUG,
        threaded=True
    )

if __name__ == '__main__':
    run_server()
