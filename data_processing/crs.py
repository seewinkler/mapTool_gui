# data_processing/crs.py

def reproject(gdf, target_crs: str):
    return gdf.to_crs(target_crs)

def compute_bbox(gdf, aspect_ratio: float):
    """
    Berechnet ein Bounding Box–Tuple (xmin, xmax, ymin, ymax),
    das das gegebene GeoDataFrame mit dem gewünschten Seitenverhältnis
    plus 5%-Padding umschließt.
    """
    # ursprüngliche Bounds
    minx, miny, maxx, maxy = gdf.total_bounds
    width, height = maxx - minx, maxy - miny
    center_x, center_y = (minx + maxx) / 2, (miny + maxy) / 2

    current_ratio = width / height
    if current_ratio > aspect_ratio:
        new_width = width
        new_height = width / aspect_ratio
    else:
        new_height = height
        new_width = height * aspect_ratio

    # 5% Buffer
    new_width *= 1.05
    new_height *= 1.05

    # wirklich zurückgebende Variablen
    xmin = center_x - new_width / 2
    xmax = center_x + new_width / 2
    ymin = center_y - new_height / 2
    ymax = center_y + new_height / 2

    return xmin, xmax, ymin, ymax