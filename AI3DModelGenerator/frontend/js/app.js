class APIManager {
    constructor() {
        this.baseUrl = 'http://localhost:5000/api';
    }
    
    async get(endpoint) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API Error:', error);
            return { error: error.message };
        }
    }
    
    async post(endpoint, data) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('API Error:', error);
            return { error: error.message };
        }
    }
}

class Viewer3D {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(
            75,
            this.canvas.clientWidth / this.canvas.clientHeight,
            0.1,
            1000
        );
        this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true });
        
        this.mesh = null;
        this.wireframeMode = false;
        this.autoRotate = false;
        this.layerPlanes = [];
        
        this.init();
    }
    
    init() {
        this.renderer.setSize(this.canvas.clientWidth, this.canvas.clientHeight);
        this.renderer.setClearColor(0x000000);
        
        this.camera.position.z = 5;
        
        const ambientLight = new THREE.AmbientLight(0x404040, 0.5);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(5, 5, 5);
        this.scene.add(directionalLight);
        
        const controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        
        this.controls = controls;
        this.animate();
        
        window.addEventListener('resize', () => this.onWindowResize());
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        if (this.autoRotate && this.mesh) {
            this.mesh.rotation.y += 0.01;
        }
        
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
    
    onWindowResize() {
        this.camera.aspect = this.canvas.clientWidth / this.canvas.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.canvas.clientWidth, this.canvas.clientHeight);
    }
    
    loadMesh(geometry) {
        if (this.mesh) {
            this.scene.remove(this.mesh);
        }
        
        const material = new THREE.MeshStandardMaterial({
            color: 0x4a9eff,
            metalness: 0.3,
            roughness: 0.7,
            wireframe: this.wireframeMode
        });
        
        this.mesh = new THREE.Mesh(geometry, material);
        this.scene.add(this.mesh);
        
        const box = new THREE.Box3().setFromObject(this.mesh);
        const center = box.getCenter(new THREE.Vector3());
        this.mesh.position.sub(center);
        
        this.centerCamera();
    }
    
    loadPLY(url) {
        const loader = new THREE.PLYLoader();
        loader.load(url, (geometry) => {
            geometry.computeVertexNormals();
            this.loadMesh(geometry);
        });
    }
    
    loadOBJ(url) {
        const loader = new THREE.OBJLoader();
        loader.load(url, (object) => {
            if (this.mesh) {
                this.scene.remove(this.mesh);
            }
            
            this.mesh = object;
            object.traverse((child) => {
                if (child.isMesh) {
                    child.material = new THREE.MeshStandardMaterial({
                        color: 0x4a9eff,
                        metalness: 0.3,
                        roughness: 0.7,
                        wireframe: this.wireframeMode
                    });
                }
            });
            
            this.scene.add(object);
            this.centerCamera();
        });
    }
    
    centerCamera() {
        if (!this.mesh) return;
        
        const box = new THREE.Box3().setFromObject(this.mesh);
        const size = box.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z);
        
        this.camera.position.z = maxDim * 2;
        this.camera.lookAt(0, 0, 0);
    }
    
    resetView() {
        this.centerCamera();
        if (this.mesh) {
            this.mesh.rotation.set(0, 0, 0);
        }
    }
    
    toggleWireframe() {
        this.wireframeMode = !this.wireframeMode;
        if (this.mesh) {
            this.mesh.traverse((child) => {
                if (child.isMesh) {
                    child.material.wireframe = this.wireframeMode;
                }
            });
        }
    }
    
    toggleAutoRotate() {
        this.autoRotate = !this.autoRotate;
    }
    
    addLayerPlane(z, color = 0xff0000) {
        const geometry = new THREE.PlaneGeometry(10, 10);
        const material = new THREE.MeshBasicMaterial({
            color: color,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.5
        });
        
        const plane = new THREE.Mesh(geometry, material);
        plane.rotation.x = Math.PI / 2;
        plane.position.z = z;
        
        this.scene.add(plane);
        this.layerPlanes.push(plane);
    }
    
    clearLayerPlanes() {
        this.layerPlanes.forEach(plane => this.scene.remove(plane));
        this.layerPlanes = [];
    }
}

class App {
    constructor() {
        this.api = new APIManager();
        this.viewer = new Viewer3D('viewer');
        this.currentMeshPath = null;
        this.currentSlicerId = null;
        this.currentLayer = 0;
        this.totalLayers = 0;
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        document.getElementById('enhance-btn').addEventListener('click', () => this.enhancePrompt());
        document.getElementById('generate-btn').addEventListener('click', () => this.generateModel());
        
        const sliders = ['guidance', 'steps', 'frame'];
        sliders.forEach(slider => {
            const element = document.getElementById(slider);
            const valueElement = document.getElementById(`${slider}-value`);
            
            element.addEventListener('input', () => {
                valueElement.textContent = element.value;
            });
        });
        
        document.getElementById('reset-view').addEventListener('click', () => this.viewer.resetView());
        document.getElementById('wireframe-toggle').addEventListener('click', () => this.viewer.toggleWireframe());
        document.getElementById('auto-rotate').addEventListener('click', () => this.viewer.toggleAutoRotate());
        
        document.getElementById('slice-btn').addEventListener('click', () => this.sliceModel());
        document.getElementById('prev-layer').addEventListener('click', () => this.previousLayer());
        document.getElementById('next-layer').addEventListener('click', () => this.nextLayer());
    }
    
    updateStatus(message, type = 'normal') {
        const statusElement = document.getElementById('status');
        statusElement.textContent = message;
        statusElement.className = 'status ' + type;
    }
    
    showProgress(show) {
        document.getElementById('progress-bar').style.display = show ? 'block' : 'none';
    }
    
    setProgress(value) {
        document.getElementById('progress-fill').style.width = value + '%';
    }
    
    async enhancePrompt() {
        const provider = document.getElementById('llm-provider').value;
        const prompt = document.getElementById('prompt').value;
        
        if (provider === 'none') {
            this.updateStatus('Please select an LLM provider', 'error');
            return;
        }
        
        if (!prompt.trim()) {
            this.updateStatus('Please enter a prompt', 'error');
            return;
        }
        
        this.updateStatus('Enhancing prompt...');
        
        const result = await this.api.post('/llm/generate-prompt', {
            input: prompt,
            provider: provider
        });
        
        if (result.error) {
            this.updateStatus(result.error, 'error');
        } else {
            document.getElementById('prompt').value = result.prompt || prompt;
            this.updateStatus('Prompt enhanced successfully', 'success');
        }
    }
    
    async generateModel() {
        const prompt = document.getElementById('prompt').value;
        
        if (!prompt.trim()) {
            this.updateStatus('Please enter a prompt', 'error');
            return;
        }
        
        const generateBtn = document.getElementById('generate-btn');
        generateBtn.disabled = true;
        
        this.showProgress(true);
        this.setProgress(0);
        this.updateStatus('Creating generator...');
        
        const genResult = await this.api.post('/generator/create', {
            type: 'text-to-3d'
        });
        
        if (genResult.error) {
            this.updateStatus(genResult.error, 'error');
            this.showProgress(false);
            generateBtn.disabled = false;
            return;
        }
        
        this.setProgress(20);
        this.updateStatus('Generating 3D model...');
        
        const generatorId = genResult.generator_id;
        const result = await this.api.post('/generator/text-to-3d', {
            generator_id: generatorId,
            prompt: prompt,
            guidance_scale: parseFloat(document.getElementById('guidance').value),
            num_inference_steps: parseInt(document.getElementById('steps').value),
            frame_size: parseInt(document.getElementById('frame').value)
        });
        
        if (result.error) {
            this.updateStatus(result.error, 'error');
            this.showProgress(false);
            generateBtn.disabled = false;
            return;
        }
        
        this.setProgress(100);
        this.currentMeshPath = result.mesh_path;
        
        this.updateStatus('Loading mesh into viewer...');
        
        const filename = result.output_filename;
        this.viewer.loadPLY(`/api/output/${filename}`);
        
        this.updateStatus('Model generated successfully!', 'success');
        this.showProgress(false);
        generateBtn.disabled = false;
    }
    
    async sliceModel() {
        if (!this.currentMeshPath) {
            this.updateStatus('No model to slice', 'error');
            return;
        }
        
        const sliceBtn = document.getElementById('slice-btn');
        sliceBtn.disabled = true;
        
        this.updateStatus('Initializing slicer...');
        
        const slicerResult = await this.api.post('/slicer/create', {
            layer_height: parseFloat(document.getElementById('layer-height').value),
            nozzle_diameter: parseFloat(document.getElementById('nozzle').value),
            fill_density: parseFloat(document.getElementById('fill').value)
        });
        
        if (slicerResult.error) {
            this.updateStatus(slicerResult.error, 'error');
            sliceBtn.disabled = false;
            return;
        }
        
        this.updateStatus('Loading mesh into slicer...');
        
        const loadResult = await this.api.post('/slicer/load', {
            slicer_id: slicerResult.slicer_id,
            mesh_path: this.currentMeshPath
        });
        
        if (loadResult.error) {
            this.updateStatus(loadResult.error, 'error');
            sliceBtn.disabled = false;
            return;
        }
        
        this.updateStatus('Slicing model...');
        
        const sliceResult = await this.api.post('/slicer/slice', {
            slicer_id: slicerResult.slicer_id
        });
        
        if (sliceResult.error) {
            this.updateStatus(sliceResult.error, 'error');
            sliceBtn.disabled = false;
            return;
        }
        
        this.currentSlicerId = slicerResult.slicer_id;
        this.totalLayers = sliceResult.total_layers;
        this.currentLayer = 0;
        
        document.getElementById('total-layers').textContent = this.totalLayers;
        document.getElementById('current-layer').textContent = this.currentLayer;
        
        this.updateStatus('Slicing complete!', 'success');
        sliceBtn.disabled = false;
    }
    
    async showLayer(layerIndex) {
        if (!this.currentSlicerId) return;
        
        const result = await this.api.get(`/slicer/layer/${this.currentSlicerId}/${layerIndex}`);
        
        if (!result.error) {
            document.getElementById('z-height').textContent = result.z_height.toFixed(3);
            this.currentLayer = layerIndex;
            document.getElementById('current-layer').textContent = layerIndex;
            
            this.viewer.clearLayerPlanes();
            this.viewer.addLayerPlane(result.z_height);
        }
    }
    
    previousLayer() {
        if (this.currentLayer > 0) {
            this.showLayer(this.currentLayer - 1);
        }
    }
    
    nextLayer() {
        if (this.currentLayer < this.totalLayers - 1) {
            this.showLayer(this.currentLayer + 1);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});
