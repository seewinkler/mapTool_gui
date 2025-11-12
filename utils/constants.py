# utils/constants.py

# Mapping von Layernamen (GUI-Auswahl) zu Boundary-Level
LAYER_TO_BOUNDARY = {
    "adm_adm_0": "ADM_0",
    "adm_adm_1": "ADM_1",
    "adm_adm_2": "ADM_2",
    "adm_adm_3": "ADM_3",
    "adm_adm_4": "ADM_4",
}

# Mapping von Boundary-Level zu Spaltennamen im GeoDataFrame
BOUNDARY_TO_COLUMN = {
    "ADM_0": "GID_0",
    "ADM_1": "GID_1",
    "ADM_2": "GID_2",
    "ADM_3": "GID_3",
    "ADM_4": "GID_4",
}