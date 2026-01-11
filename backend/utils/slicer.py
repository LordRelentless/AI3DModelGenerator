spacing = self.config.nozzle_diameter / self.config.fill_density
            
            lines_x = np.arange(min_x, max_x, spacing)
            lines_y = np.arange(min_y, max_y, spacing)
            
            for x in lines_x:
                layer.infill.append(line)
                
                for y in lines_y:
                    line = np.array([[min_x, y], [max_x, y], z=layer.z_height])
                
                for y in lines_y:
            
        