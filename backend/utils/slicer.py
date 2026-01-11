import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import json

try:
    import trimesh
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False

class SlicerConfig:
    def __init__(
        self,
        layer_height: float = 0.2,
        first_layer_height: Optional[float] = None,
        nozzle_diameter: float = 0.4,
        fill_density: float = 0.2,
        fill_pattern: str = "grid",
        perimeter_count: int = 2,
        top_solid_layers: int = 3,
        bottom_solid_layers: int = 3
    ):
        self.layer_height = layer_height
        self.first_layer_height = first_layer_height or layer_height
        self.nozzle_diameter = nozzle_diameter
        self.fill_density = fill_density
        self.fill_pattern = fill_pattern
        self.perimeter_count = perimeter_count
        self.top_solid_layers = top_solid_layers
        self.bottom_solid_layers = bottom_solid_layers

class Layer:
    def __init__(self, z_height: float, layer_index: int):
        self.z_height = z_height
        self.layer_index = layer_index
        self.contours: List[np.ndarray] = []
        self.infill: List[np.ndarray] = []
        self.supports: List[np.ndarray] = []

class Slicer:
    def __init__(self, config: Optional[SlicerConfig] = None):
        self.config = config or SlicerConfig()
        self.mesh = None
        self.layers: List[Layer] = []
        self.bounding_box = None
    
    def load_mesh(self, mesh_path: str) -> bool:
        if not TRIMESH_AVAILABLE:
            print("Trimesh not available, cannot load mesh")
            return False
        
        try:
            self.mesh = trimesh.load(mesh_path)
            
            if isinstance(self.mesh, trimesh.Scene):
                self.mesh = trimesh.util.concatenate(
                    tuple(trimesh.Trimesh(vertices=g.vertices, faces=g.faces)
                          for g in self.mesh.geometry.values())
                )
            
            self._calculate_bounding_box()
            self._center_mesh()
            return True
        except Exception as e:
            print(f"Error loading mesh: {e}")
            return False
    
    def _calculate_bounding_box(self) -> None:
        if self.mesh is not None:
            self.bounding_box = {
                'min': self.mesh.vertices.min(axis=0),
                'max': self.mesh.vertices.max(axis=0),
                'size': self.mesh.vertices.max(axis=0) - self.mesh.vertices.min(axis=0)
            }
    
    def _center_mesh(self) -> None:
        if self.mesh is not None and self.bounding_box is not None:
            center = (self.bounding_box['max'] + self.bounding_box['min']) / 2
            self.mesh.vertices -= center
    
    def slice_mesh(self, progress_callback=None) -> List[Layer]:
        if self.mesh is None:
            raise RuntimeError("No mesh loaded")
        
        if not TRIMESH_AVAILABLE:
            raise RuntimeError("Trimesh not available")
        
        self.layers = []
        z_min = self.bounding_box['min'][2]
        z_max = self.bounding_box['max'][2]
        
        layer_height = self.config.first_layer_height
        z = z_min + layer_height
        
        layer_index = 0
        total_layers = int(np.ceil((z_max - z_min - layer_height) / self.config.layer_height)) + 1
        
        while z < z_max:
            if progress_callback:
                progress_callback(layer_index / total_layers)
            
            layer = Layer(z, layer_index)
            self._slice_layer(z, layer)
            self.layers.append(layer)
            
            layer_index += 1
            z += self.config.layer_height
        
        return self.layers
    
    def _slice_layer(self, z: float, layer: Layer) -> None:
        try:
            section = self.mesh.section(plane_normal=[0, 0, 1], plane_origin=[0, 0, z])
            
            if section is not None and hasattr(section, 'entities'):
                for entity in section.entities:
                    if hasattr(entity, 'discrete'):
                        points = entity.discretize(self.mesh.vertices.shape[0])
                        layer.contours.append(points)
        except Exception as e:
            pass
    
    def generate_infill(self, layer: Layer) -> None:
        if not TRIMESH_AVAILABLE:
            return
        
        if not layer.contours:
            return
        
        try:
            all_contours = np.vstack(layer.contours)
            
            min_x, min_y = all_contours.min(axis=0)[:2]
            max_x, max_y = all_contours.max(axis=0)[:2]
            
            spacing = self.config.nozzle_diameter / self.config.fill_density
            
            if self.config.fill_pattern == "grid":
                lines_x = np.arange(min_x, max_x, spacing)
                lines_y = np.arange(min_y, max_y, spacing)
                
                for x in lines_x:
                    line = np.array([[x, min_y], [x, max_y], z=layer.z_height]])
                    layer.infill.append(line)
                
                for y in lines_y:
                    line = np.array([[min_x, y], [max_x, y, z=layer.z_height]])
                    layer.infill.append(line)
            
        except Exception as e:
            pass
    
    def get_layer_preview(self, layer_index: int) -> Optional[Dict[str, Any]]:
        if 0 <= layer_index < len(self.layers):
            layer = self.layers[layer_index]
            return {
                'z_height': layer.z_height,
                'layer_index': layer.layer_index,
                'contours': [c.tolist() for c in layer.contours],
                'infill': [i.tolist() for i in layer.infill],
                'supports': [s.tolist() for s in layer.supports]
            }
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        if not self.layers:
            return {}
        
        total_height = sum(self.config.layer_height for _ in self.layers)
        first_layer_height = self.layers[0].z_height - (self.bounding_box['min'][2] if self.bounding_box else 0)
        total_height += first_layer_height
        
        return {
            'total_layers': len(self.layers),
            'total_height_mm': total_height,
            'first_layer_height_mm': self.config.first_layer_height,
            'layer_height_mm': self.config.layer_height,
            'bounding_box': self.bounding_box,
            'estimated_time_minutes': total_height / self.config.layer_height * 0.5
        }
    
    def export_to_gcode(self, output_path: str) -> bool:
        try:
            with open(output_path, 'w') as f:
                f.write("; Generated by AI 3D Model Generator Slicer\n")
                f.write(f"; Layer height: {self.config.layer_height}\n")
                f.write(f"; Nozzle diameter: {self.config.nozzle_diameter}\n")
                f.write(f"; Fill density: {self.config.fill_density}\n\n")
                
                f.write("G28 ; Home all axes\n")
                f.write(f"G1 Z{self.config.first_layer_height + 5} F3000\n")
                f.write("G92 E0 ; Reset extruder\n\n")
                
                for i, layer in enumerate(self.layers):
                    f.write(f"; Layer {i} at Z{layer.z_height}\n")
                    f.write(f"G1 Z{layer.z_height} F3000\n")
                    
                    for contour in layer.contours:
                        for j, point in enumerate(contour):
                            if j == 0:
                                f.write(f"G1 X{point[0]:.3f} Y{point[1]:.3f} F1800\n")
                            else:
                                f.write(f"G1 X{point[0]:.3f} Y{point[1]:.3f} E1.0\n")
                    
                    f.write("\n")
            
            return True
        except Exception as e:
            print(f"Error exporting G-code: {e}")
            return False
    
    def export_to_json(self, output_path: str) -> bool:
        try:
            data = {
                'config': {
                    'layer_height': self.config.layer_height,
                    'first_layer_height': self.config.first_layer_height,
                    'nozzle_diameter': self.config.nozzle_diameter,
                    'fill_density': self.config.fill_density,
                    'fill_pattern': self.config.fill_pattern,
                    'perimeter_count': self.config.perimeter_count,
                    'top_solid_layers': self.config.top_solid_layers,
                    'bottom_solid_layers': self.config.bottom_solid_layers
                },
                'bounding_box': self.bounding_box,
                'statistics': self.get_statistics(),
                'layers': [
                    {
                        'z_height': layer.z_height,
                        'layer_index': layer.layer_index,
                        'contours': [c.tolist() for c in layer.contours],
                        'infill': [i.tolist() for i in layer.infill],
                        'supports': [s.tolist() for s in layer.supports]
                    }
                    for layer in self.layers
                ]
            }
            
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
