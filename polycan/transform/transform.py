## This program exposes many different data transformations for CAN dataframe
## Written by Morgan Swanson

from transform import j1939
from pkg_resources import resource_filename

def decode_j1939(dataframe):
    """Takes a dataframe and returns a dataframe"""
    spec = j1939.read_spec(resource_filename(__name__, "J1939DA_202007.xlsx"))
    return j1939.analyze_can_log(dataframe, spec)
