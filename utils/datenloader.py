import os, json

def get_asset_path(filename):
    base_path = os.path.abspath(os.path.dirname(__file__))
    asset_path = os.path.join(base_path, '..', 'assets', filename)
    return os.path.normpath(asset_path)

def load_epsg_list():
    with open(get_asset_path('epsg_list.json'), 'r', encoding='utf-8') as f:
        return json.load(f)