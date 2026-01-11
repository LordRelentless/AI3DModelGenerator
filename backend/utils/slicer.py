    def generate_infill(self, layer_height: float) -> List[Layer]:
            lines_x = np.arange(min_x, max_x, spacing)
            lines_y = np.arange(min_y, max_y, spacing)
            
            # Create line segments
            for y in lines_y:
                segment_lines = []
                for x in lines_x:
                    line = np.array([[x, y], [x, max_y], z=layer_height])
                    segment_lines.append(line)
                
                layer = Layer(
                    z_height=layer_height,
                    layer_index=len(self.layers),
                    contours=segment_lines,
                    infill=[],
                    supports=[],
                    z_height=layer_height
                )
                self.layers.append(layer)
            
            return self.layers