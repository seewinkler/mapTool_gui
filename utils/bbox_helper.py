# utils/bbox_helper.py

def compute_bbox(gdf, aspect_ratio: float, padding_factor: float = 0.05):
    minx, miny, maxx, maxy = gdf.total_bounds
    width, height = maxx - minx, maxy - miny
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2

    current_ratio = width / height
    if current_ratio > aspect_ratio:
        new_width  = width
        new_height = width / aspect_ratio
    else:
        new_height = height
        new_width  = height * aspect_ratio

    new_width  *= 1 + padding_factor
    new_height *= 1 + padding_factor

    xmin = cx - new_width / 2
    xmax = cx + new_width / 2
    ymin = cy - new_height / 2
    ymax = cy + new_height / 2

    return xmin, xmax, ymin, ymax