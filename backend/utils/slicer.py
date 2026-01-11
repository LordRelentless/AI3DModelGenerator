        # Simplified clean infill loop
        lines_x = np.arange(min_x, max_x, spacing)
        lines_y = np.arange(min_y, max_y, spacing)
        
        # Track x positions to find lines with matching y
        line_map = {}
        for i, y in enumerate(lines_y):
            line_map.setdefault(y, [])
        
        for x in lines_x:
            # Find which y position(s) this x line intersects with
            intersecting_ys = []
            for y_pos in line_map:
                # Check if y coordinate is close to this line
                if abs(y - y_pos) < spacing:
                    intersecting_ys.append(y_pos)
            
            if intersecting_ys:
                # Mark all these y positions as used
                for y_pos in intersecting_ys:
                    line_map[y_pos].append(x)
        
        # Build lines using marked positions to avoid duplicates
        for y in lines_y:
            lines = line_map[y]
            if not lines:  # Skip if no positions found for this y
                continue
                
            # Sort by x position to maintain consistent order
            positions = sorted(line_map[y].keys())
            
            # Generate infill lines
            for x in positions:
                # Create horizontal line at this x and y
                line = np.array([[x, y], [x, y], z=layer.z_height])
                layer.infill.append(line)
        
        return True