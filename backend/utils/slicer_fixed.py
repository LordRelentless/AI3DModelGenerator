            spacing = self.config.nozzle_diameter / self.config.fill_density
            
            lines_x = np.arange(min_x, max_x, spacing)
            lines_y = np.arange(min_y, max_y, spacing)
            
            for x in lines_x:
                line = np.array([[x, min_y], [x, max_y], z=layer.z_height])
                layer.infill.append(line)
                
            for y in lines_y:
                line = np.array([[min_x, y], [max_x, y], z=layer.z_height])
                layer.infill.append(line)
            
            layer.supports = [line for line in layer.infill]
