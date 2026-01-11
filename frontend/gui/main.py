import sys
import asyncio
from pathlib import Path
from typing import Optional
import requests
import json

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QComboBox, QSpinBox, QDoubleSpinBox,
    QTabWidget, QProgressBar, QFileDialog, QMessageBox, QGroupBox,
    QFormLayout, QScrollArea, QMenuBar, QMenu, QDialog, QLineEdit,
    QCheckBox, QGroupBox, QHBoxLayout, QVBoxLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap

from config.config import Config

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setModal(True)
        self.resize(500, 400)

        layout = QVBoxLayout()

        # API Keys section
        api_group = QGroupBox("API Keys")
        api_layout = QFormLayout()

        self.openai_key = QLineEdit(Config.API_KEYS.get('openai', ''))
        self.openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("OpenAI API Key:", self.openai_key)

        self.anthropic_key = QLineEdit(Config.API_KEYS.get('anthropic', ''))
        self.anthropic_key.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("Anthropic API Key:", self.anthropic_key)

        self.openrouter_key = QLineEdit(Config.API_KEYS.get('openrouter', ''))
        self.openrouter_key.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("OpenRouter API Key:", self.openrouter_key)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # Local LLM section
        local_group = QGroupBox("Local LLM Settings")
        local_layout = QFormLayout()

        self.llm_enabled = QCheckBox("Enable Local LLM")
        self.llm_enabled.setChecked(Config.LOCAL_LLM_ENABLED)
        local_layout.addRow(self.llm_enabled)

        self.llm_path = QLineEdit(Config.LOCAL_LLM_PATH)
        local_layout.addRow("Local LLM Path:", self.llm_path)

        self.llm_type = QComboBox()
        self.llm_type.addItems(['transformers', 'glm4'])
        self.llm_type.setCurrentText(Config.LOCAL_LLM_TYPE)
        local_layout.addRow("LLM Type:", self.llm_type)

        self.networked_url = QLineEdit(Config.NETWORKED_LLM_URL or '')
        local_layout.addRow("Networked LLM URL:", self.networked_url)

        self.networked_api_key = QLineEdit(Config.NETWORKED_LLM_API_KEY or '')
        self.networked_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        local_layout.addRow("Networked API Key:", self.networked_api_key)

        local_group.setLayout(local_layout)
        layout.addWidget(local_group)

        # Export section
        export_group = QGroupBox("Export Settings")
        export_layout = QFormLayout()

        self.output_dir = QLineEdit(str(Config.OUTPUT_DIR))
        export_layout.addRow("Output Directory:", self.output_dir)

        self.models_dir = QLineEdit(str(Config.MODELS_DIR))
        export_layout.addRow("Models Directory:", self.models_dir)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_settings(self):
        return {
            'openai_key': self.openai_key.text(),
            'anthropic_key': self.anthropic_key.text(),
            'openrouter_key': self.openrouter_key.text(),
            'llm_enabled': self.llm_enabled.isChecked(),
            'llm_path': self.llm_path.text(),
            'llm_type': self.llm_type.currentText(),
            'networked_url': self.networked_url.text(),
            'networked_api_key': self.networked_api_key.text(),
            'output_dir': self.output_dir.text(),
            'models_dir': self.models_dir.text()
        }

class APIClient:
    def __init__(self, base_url: str = f"http://{Config.API_HOST}:{Config.API_PORT}"):
        self.base_url = base_url
    
    def get(self, endpoint: str) -> dict:
        try:
            response = requests.get(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def post(self, endpoint: str, data: dict) -> dict:
        try:
            response = requests.post(f"{self.base_url}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}

class GeneratorThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, client: APIClient, prompt: str, params: dict):
        super().__init__()
        self.client = client
        self.prompt = prompt
        self.params = params
    
    def run(self):
        self.progress.emit("Creating generator...")
        gen_result = self.client.post('/api/generator/create', {
            'type': self.params.get('type', 'text-to-3d'),
            'model_path': self.params.get('model_path')
        })
        
        if 'error' in gen_result:
            self.error.emit(gen_result['error'])
            return
        
        generator_id = gen_result['generator_id']
        self.progress.emit("Generating 3D model...")
        
        result = self.client.post('/api/generator/text-to-3d', {
            'generator_id': generator_id,
            'prompt': self.prompt,
            'guidance_scale': self.params.get('guidance_scale', 7.5),
            'num_inference_steps': self.params.get('num_inference_steps', 50),
            'frame_size': self.params.get('frame_size', 256)
        })
        
        if 'error' in result:
            self.error.emit(result['error'])
        else:
            self.finished.emit(result)

class SlicerThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int, int)
    
    def __init__(self, client: APIClient, mesh_path: str, config: dict):
        super().__init__()
        self.client = client
        self.mesh_path = mesh_path
        self.config = config
    
    def run(self):
        self.progress.emit(0, 100)
        
        self.progress.emit(10, 100)
        slicer_result = self.client.post('/api/slicer/create', self.config)
        
        if 'error' in slicer_result:
            self.error.emit(slicer_result['error'])
            return
        
        slicer_id = slicer_result['slicer_id']
        self.progress.emit(20, 100)
        
        load_result = self.client.post('/api/slicer/load', {
            'slicer_id': slicer_id,
            'mesh_path': self.mesh_path
        })
        
        if 'error' in load_result:
            self.error.emit(load_result['error'])
            return
        
        self.progress.emit(40, 100)
        
        slice_result = self.client.post('/api/slicer/slice', {
            'slicer_id': slicer_id
        })
        
        if 'error' in slice_result:
            self.error.emit(slice_result['error'])
        else:
            slice_result['slicer_id'] = slicer_id
            self.progress.emit(100, 100)
            self.finished.emit(slice_result)

class TextTo3DTab(QWidget):
    def __init__(self, client: APIClient):
        super().__init__()
        self.client = client
        self.current_mesh_path = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        input_group = QGroupBox("Text Input")
        input_layout = QVBoxLayout()
        
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Describe the 3D model you want to generate...")
        self.prompt_input.setMaximumHeight(100)
        
        self.llm_combo = QComboBox()
        self.llm_combo.addItems(['auto', 'none', 'openai', 'anthropic', 'openrouter', 'local', 'networked'])
        self.llm_combo.currentTextChanged.connect(self.on_llm_provider_changed)

        self.networked_url_input = QLineEdit()
        self.networked_url_input.setPlaceholderText("http://localhost:5000 or http://192.168.1.100:5000")
        self.networked_url_input.hide()  # Hidden by default
        
        enhance_btn = QPushButton("Enhance with LLM")
        enhance_btn.clicked.connect(self.enhance_prompt)
        
        input_layout.addWidget(QLabel("Prompt:"))
        input_layout.addWidget(self.prompt_input)
        input_layout.addWidget(QLabel("LLM Provider:"))
        input_layout.addWidget(self.llm_combo)
        input_layout.addWidget(QLabel("Networked LLM URL:"))
        input_layout.addWidget(self.networked_url_input)
        input_layout.addWidget(enhance_btn)
        input_group.setLayout(input_layout)
        
        params_group = QGroupBox("Generation Parameters")
        params_layout = QFormLayout()
        
        self.guidance_spin = QDoubleSpinBox()
        self.guidance_spin.setRange(1.0, 20.0)
        self.guidance_spin.setValue(7.5)
        self.guidance_spin.setSingleStep(0.5)
        
        self.steps_spin = QSpinBox()
        self.steps_spin.setRange(10, 100)
        self.steps_spin.setValue(50)
        
        self.resolution_spin = QSpinBox()
        self.resolution_spin.setRange(64, 512)
        self.resolution_spin.setValue(256)
        self.resolution_spin.setSingleStep(64)
        
        params_layout.addRow("Guidance Scale:", self.guidance_spin)
        params_layout.addRow("Inference Steps:", self.steps_spin)
        params_layout.addRow("Frame Size:", self.resolution_spin)
        params_group.setLayout(params_layout)
        
        self.generate_btn = QPushButton("Generate 3D Model")
        self.generate_btn.clicked.connect(self.generate_model)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        self.status_label = QLabel("Ready")
        
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()
        
        self.output_path_label = QLabel("No model generated yet")
        self.output_path_label.setWordWrap(True)
        
        output_layout.addWidget(self.output_path_label)
        output_group.setLayout(output_layout)
        
        layout.addWidget(input_group)
        layout.addWidget(params_group)
        layout.addWidget(self.generate_btn)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(output_group)
        
        layout.addStretch()
        
        self.setLayout(layout)
    
    def on_llm_provider_changed(self, provider):
        """Show/hide networked URL input based on provider selection"""
        if provider == 'networked':
            self.networked_url_input.show()
        else:
            self.networked_url_input.hide()

    def enhance_prompt(self):
        provider = self.llm_combo.currentText()
        if provider == 'none':
            return

        prompt = self.prompt_input.toPlainText()
        if not prompt:
            QMessageBox.warning(self, "Warning", "Please enter a prompt first")
            return

        # Add networked URL if using networked provider
        data = {
            'input': prompt,
            'provider': provider
        }

        if provider == 'networked':
            url = self.networked_url_input.text().strip()
            if not url:
                QMessageBox.warning(self, "Warning", "Please enter a networked LLM URL")
                return
            data['networked_url'] = url

        result = self.client.post('/api/llm/generate-prompt', data)

        if 'error' in result:
            QMessageBox.critical(self, "Error", result['error'])
            return

        enhanced = result.get('prompt', prompt)
        self.prompt_input.setText(enhanced)
    
    def generate_model(self):
        prompt = self.prompt_input.toPlainText()
        if not prompt:
            QMessageBox.warning(self, "Warning", "Please enter a prompt")
            return
        
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Initializing...")
        
        params = {
            'type': 'text-to-3d',
            'guidance_scale': self.guidance_spin.value(),
            'num_inference_steps': self.steps_spin.value(),
            'frame_size': self.resolution_spin.value()
        }
        
        self.thread = GeneratorThread(self.client, prompt, params)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.on_generation_finished)
        self.thread.error.connect(self.on_generation_error)
        self.thread.start()
    
    def update_progress(self, message: str):
        self.status_label.setText(message)
    
    def on_generation_finished(self, result: dict):
        self.current_mesh_path = result.get('mesh_path')
        self.output_path_label.setText(f"Mesh saved to:\n{self.current_mesh_path}")
        self.status_label.setText("Generation complete!")
        self.progress_bar.setValue(100)
        self.generate_btn.setEnabled(True)
    
    def on_generation_error(self, error: str):
        QMessageBox.critical(self, "Error", error)
        self.status_label.setText("Generation failed")
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

class SlicerTab(QWidget):
    def __init__(self, client: APIClient):
        super().__init__()
        self.client = client
        self.current_slicer_id = None
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        mesh_group = QGroupBox("Mesh Input")
        mesh_layout = QVBoxLayout()
        
        self.mesh_path_input = QTextEdit()
        self.mesh_path_input.setMaximumHeight(50)
        self.mesh_path_input.setPlaceholderText("Enter mesh file path...")
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_mesh)
        
        mesh_layout.addWidget(QLabel("Mesh Path:"))
        mesh_layout.addWidget(self.mesh_path_input)
        mesh_layout.addWidget(browse_btn)
        mesh_group.setLayout(mesh_layout)
        
        config_group = QGroupBox("Slicer Configuration")
        config_layout = QFormLayout()
        
        self.layer_height_spin = QDoubleSpinBox()
        self.layer_height_spin.setRange(0.05, 1.0)
        self.layer_height_spin.setValue(0.2)
        self.layer_height_spin.setSingleStep(0.05)
        
        self.nozzle_spin = QDoubleSpinBox()
        self.nozzle_spin.setRange(0.1, 1.0)
        self.nozzle_spin.setValue(0.4)
        self.nozzle_spin.setSingleStep(0.1)
        
        self.fill_spin = QDoubleSpinBox()
        self.fill_spin.setRange(0.0, 1.0)
        self.fill_spin.setValue(0.2)
        self.fill_spin.setSingleStep(0.1)
        
        self.perimeter_spin = QSpinBox()
        self.perimeter_spin.setRange(1, 10)
        self.perimeter_spin.setValue(2)
        
        config_layout.addRow("Layer Height (mm):", self.layer_height_spin)
        config_layout.addRow("Nozzle Diameter (mm):", self.nozzle_spin)
        config_layout.addRow("Fill Density:", self.fill_spin)
        config_layout.addRow("Perimeter Count:", self.perimeter_spin)
        config_group.setLayout(config_layout)
        
        self.slice_btn = QPushButton("Slice Model")
        self.slice_btn.clicked.connect(self.slice_model)
        
        self.progress_bar = QProgressBar()
        
        self.status_label = QLabel("Ready")
        
        export_group = QGroupBox("Export")
        export_layout = QVBoxLayout()
        
        export_gcode_btn = QPushButton("Export G-code")
        export_gcode_btn.clicked.connect(self.export_gcode)
        
        export_json_btn = QPushButton("Export JSON")
        export_json_btn.clicked.connect(self.export_json)
        
        export_layout.addWidget(export_gcode_btn)
        export_layout.addWidget(export_json_btn)
        export_group.setLayout(export_layout)
        
        left_layout.addWidget(mesh_group)
        left_layout.addWidget(config_group)
        left_layout.addWidget(self.slice_btn)
        left_layout.addWidget(self.progress_bar)
        left_layout.addWidget(self.status_label)
        left_layout.addWidget(export_group)
        left_layout.addStretch()
        
        left_panel.setLayout(left_layout)
        left_panel.setFixedWidth(300)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("No model loaded")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(400, 400)
        
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel("No statistics available")
        self.stats_label.setWordWrap(True)
        
        stats_layout.addWidget(self.stats_label)
        stats_group.setLayout(stats_layout)
        
        layer_controls = QHBoxLayout()
        
        self.layer_spin = QSpinBox()
        self.layer_spin.setRange(0, 1000)
        self.layer_spin.valueChanged.connect(self.show_layer)
        
        load_layer_btn = QPushButton("Show Layer")
        load_layer_btn.clicked.connect(self.show_layer)
        
        layer_controls.addWidget(QLabel("Layer:"))
        layer_controls.addWidget(self.layer_spin)
        layer_controls.addWidget(load_layer_btn)
        
        right_layout.addWidget(preview_group)
        right_layout.addWidget(stats_group)
        right_layout.addLayout(layer_controls)
        
        right_panel.setLayout(right_layout)
        
        layout.addWidget(left_panel)
        layout.addWidget(right_panel)
        
        self.setLayout(layout)
    
    def browse_mesh(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Mesh File", "", "Mesh Files (*.ply *.obj *.stl);;All Files (*)"
        )
        if file_path:
            self.mesh_path_input.setText(file_path)
    
    def slice_model(self):
        mesh_path = self.mesh_path_input.toPlainText()
        if not mesh_path:
            QMessageBox.warning(self, "Warning", "Please select a mesh file")
            return
        
        self.slice_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Initializing slicer...")
        
        config = {
            'layer_height': self.layer_height_spin.value(),
            'nozzle_diameter': self.nozzle_spin.value(),
            'fill_density': self.fill_spin.value(),
            'perimeter_count': self.perimeter_spin.value()
        }
        
        self.thread = SlicerThread(self.client, mesh_path, config)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.on_slicing_finished)
        self.thread.error.connect(self.on_slicing_error)
        self.thread.start()
    
    def update_progress(self, current: int, total: int):
        self.progress_bar.setValue(int(current / total * 100))
    
    def on_slicing_finished(self, result: dict):
        self.current_slicer_id = result.get('slicer_id')
        self.status_label.setText(f"Slicing complete! {result.get('total_layers', 0)} layers")
        
        stats = result.get('statistics', {})
        stats_text = f"Total Layers: {stats.get('total_layers', 0)}\n"
        stats_text += f"Total Height: {stats.get('total_height_mm', 0):.2f} mm\n"
        stats_text += f"Estimated Time: {stats.get('estimated_time_minutes', 0):.1f} min"
        self.stats_label.setText(stats_text)
        
        self.layer_spin.setRange(0, result.get('total_layers', 0) - 1)
        
        self.preview_label.setText("Model sliced successfully\nUse layer controls to preview")
        self.slice_btn.setEnabled(True)
    
    def on_slicing_error(self, error: str):
        QMessageBox.critical(self, "Error", error)
        self.status_label.setText("Slicing failed")
        self.slice_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def show_layer(self):
        if not self.current_slicer_id:
            return
        
        layer_index = self.layer_spin.value()
        result = self.client.get(f'/api/slicer/layer/{self.current_slicer_id}/{layer_index}')
        
        if 'error' not in result:
            self.preview_label.setText(f"Layer {layer_index} at Z={result.get('z_height', 0):.3f}")
        else:
            self.preview_label.setText("Error loading layer")
    
    def export_gcode(self):
        if not self.current_slicer_id:
            QMessageBox.warning(self, "Warning", "No sliced model available")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save G-code", "", "G-code Files (*.gcode);;All Files (*)"
        )
        if file_path:
            result = self.client.post('/api/slicer/export/gcode', {
                'slicer_id': self.current_slicer_id,
                'output_filename': Path(file_path).name
            })
            
            if 'error' in result:
                QMessageBox.critical(self, "Error", result['error'])
            else:
                QMessageBox.information(self, "Success", "G-code exported successfully")
    
    def export_json(self):
        if not self.current_slicer_id:
            QMessageBox.warning(self, "Warning", "No sliced model available")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save JSON", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            result = self.client.post('/api/slicer/export/json', {
                'slicer_id': self.current_slicer_id,
                'output_filename': Path(file_path).name
            })
            
            if 'error' in result:
                QMessageBox.critical(self, "Error", result['error'])
            else:
                QMessageBox.information(self, "Success", "JSON exported successfully")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = APIClient()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("AI 3D Model Generator")
        self.setGeometry(100, 100, Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)

        # Create menu bar
        self.create_menu_bar()

        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        header = QLabel("AI 3D Model Generator")
        header.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.device_info_label = QLabel("Checking device...")
        self.device_info_label.setStyleSheet("padding: 5px;")
        
        self.tab_widget = QTabWidget()
        
        self.text_to_3d_tab = TextTo3DTab(self.client)
        self.slicer_tab = SlicerTab(self.client)
        
        self.tab_widget.addTab(self.text_to_3d_tab, "Text to 3D")
        self.tab_widget.addTab(self.slicer_tab, "Slicer Preview")
        
        main_layout.addWidget(header)
        main_layout.addWidget(self.device_info_label)
        main_layout.addWidget(self.tab_widget)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        self.check_device_info()

    def create_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        open_action = file_menu.addAction('Open Model')
        open_action.triggered.connect(self.open_model)

        save_action = file_menu.addAction('Save Model')
        save_action.triggered.connect(self.save_model)

        file_menu.addSeparator()

        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.close)

        # Edit menu
        edit_menu = menubar.addMenu('Edit')

        preferences_action = edit_menu.addAction('Preferences')
        preferences_action.triggered.connect(self.show_preferences)

        # Export menu
        export_menu = menubar.addMenu('Export')

        export_obj_action = export_menu.addAction('Export as OBJ')
        export_obj_action.triggered.connect(lambda: self.export_model('obj'))

        export_stl_action = export_menu.addAction('Export as STL')
        export_stl_action.triggered.connect(lambda: self.export_model('stl'))

        export_ply_action = export_menu.addAction('Export as PLY')
        export_ply_action.triggered.connect(lambda: self.export_model('ply'))

        export_glb_action = export_menu.addAction('Export as GLB')
        export_glb_action.triggered.connect(lambda: self.export_model('glb'))

    def open_model(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open 3D Model", "", "3D Models (*.ply *.obj *.stl);;All Files (*)"
        )
        if file_path:
            # Load the model into the current tab
            current_tab = self.tab_widget.currentWidget()
            if hasattr(current_tab, 'load_model'):
                current_tab.load_model(file_path)

    def save_model(self):
        if hasattr(self.text_to_3d_tab, 'current_mesh_path') and self.text_to_3d_tab.current_mesh_path:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save 3D Model", "", "PLY Files (*.ply);;All Files (*)"
            )
            if file_path:
                import shutil
                shutil.copy2(self.text_to_3d_tab.current_mesh_path, file_path)
                QMessageBox.information(self, "Success", "Model saved successfully!")

    def export_model(self, format_type):
        if not hasattr(self.text_to_3d_tab, 'current_mesh_path') or not self.text_to_3d_tab.current_mesh_path:
            QMessageBox.warning(self, "Warning", "No model to export. Generate a model first.")
            return

        format_ext = {
            'obj': '.obj',
            'stl': '.stl',
            'ply': '.ply',
            'glb': '.glb'
        }

        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Export as {format_type.upper()}", "",
            f"{format_type.upper()} Files (*{format_ext[format_type]});;All Files (*)"
        )

        if file_path:
            try:
                # Convert and export the mesh
                self.convert_and_export_mesh(self.text_to_3d_tab.current_mesh_path, file_path, format_type)
                QMessageBox.information(self, "Success", f"Model exported as {format_type.upper()} successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export model: {str(e)}")

    def convert_and_export_mesh(self, input_path, output_path, format_type):
        """Convert mesh to different formats"""
        try:
            import trimesh

            # Load the mesh
            mesh = trimesh.load(input_path)

            # Ensure it's a Trimesh object
            if isinstance(mesh, trimesh.Scene):
                mesh = trimesh.util.concatenate(
                    tuple(trimesh.Trimesh(vertices=g.vertices, faces=g.faces)
                          for g in mesh.geometry.values())
                )

            # Export in requested format
            if format_type.lower() == 'obj':
                mesh.export(output_path, file_type='obj')
            elif format_type.lower() == 'stl':
                mesh.export(output_path, file_type='stl')
            elif format_type.lower() == 'ply':
                mesh.export(output_path, file_type='ply')
            elif format_type.lower() == 'glb':
                mesh.export(output_path, file_type='glb')
            else:
                raise ValueError(f"Unsupported format: {format_type}")

        except ImportError:
            raise Exception("trimesh library required for mesh conversion")
        except Exception as e:
            raise Exception(f"Mesh conversion failed: {str(e)}")

    def show_preferences(self):
        dialog = PreferencesDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()
            self.apply_preferences(settings)

    def apply_preferences(self, settings):
        """Apply the preferences from the dialog"""
        # Update config values
        Config.API_KEYS['openai'] = settings['openai_key']
        Config.API_KEYS['anthropic'] = settings['anthropic_key']
        Config.API_KEYS['openrouter'] = settings['openrouter_key']

        Config.LOCAL_LLM_ENABLED = settings['llm_enabled']
        Config.LOCAL_LLM_PATH = settings['llm_path']
        Config.LOCAL_LLM_TYPE = settings['llm_type']
        Config.NETWORKED_LLM_URL = settings['networked_url']
        Config.NETWORKED_LLM_API_KEY = settings['networked_api_key']

        Config.OUTPUT_DIR = Path(settings['output_dir'])
        Config.MODELS_DIR = Path(settings['models_dir'])

        # Save to .env file (you might want to implement this)
        self.save_config_to_env(settings)

        QMessageBox.information(self, "Success", "Preferences saved! Restart the application for some changes to take effect.")

    def save_config_to_env(self, settings):
        """Save settings to .env file"""
        try:
            env_content = f"""OPENAI_API_KEY={settings['openai_key']}
ANTHROPIC_API_KEY={settings['anthropic_key']}
OPENROUTER_API_KEY={settings['openrouter_key']}

# Model Configuration
SHAP_E_MODEL=openai/shap-e
TRIPOSR_MODEL=stabilityai/triposr
DEVICE=auto

# Server Configuration
SERVER_HOST=0.0.0.0
API_HOST=127.0.0.1
API_PORT=5000
DEBUG=False

# LLM Configuration
DEFAULT_LLM=auto
LOCAL_LLM_ENABLED={'True' if settings['llm_enabled'] else 'False'}
LOCAL_LLM_PATH={settings['llm_path']}
LOCAL_LLM_TYPE={settings['llm_type']}
NETWORKED_LLM_URL={settings['networked_url']}
NETWORKED_LLM_API_KEY={settings['networked_api_key']}

# 3D Generation Configuration
DEFAULT_INFERENCE_STEPS=50
DEFAULT_GUIDANCE_SCALE=7.5
DEFAULT_FRAME_SIZE=256
MESH_RESOLUTION=256

# Output Configuration
OUTPUT_DIR={settings['output_dir']}
MODELS_DIR={settings['models_dir']}
LOGS_DIR=./logs

# GUI Configuration
WINDOW_WIDTH=1400
WINDOW_HEIGHT=900

# Web Server Configuration
WEB_PORT=8000

# Model Auto-Download Configuration
AUTO_DOWNLOAD_MODELS=false
AUTO_DOWNLOAD_3D_MODELS=true
AUTO_DOWNLOAD_LLM_MODELS=false
"""

            with open('.env', 'w') as f:
                f.write(env_content)

        except Exception as e:
            print(f"Error saving .env file: {e}")

    def check_device_info(self):
        result = self.client.get('/api/device/info')
        if 'error' not in result:
            device_type = result.get('type', 'Unknown')
            if device_type == 'cuda':
                name = result.get('name', 'NVIDIA GPU')
                memory = result.get('memory_total', 0) / (1024**3)
                self.device_info_label.setText(f"Device: {name} ({memory:.1f} GB VRAM)")
            elif device_type == 'mps':
                self.device_info_label.setText("Device: Apple Silicon GPU (MPS)")
            else:
                self.device_info_label.setText("Device: CPU")
        else:
            self.device_info_label.setText("Device: Unknown (API not connected)")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
