## This program uses the SAE J1939 excel sheet to convert raw can dumps
## into time series data
## Written by Morgan Swanson

import pandas as pd
import numpy as np
import os, struct
from pathlib import Path

def get_bitshift(position):
    _position = str(position).split("-")[0]
    _position = _position.split(".")
    if len(_position) > 1:
        # Convert bits and bytes to zero-index and convert to bits
        shift = (int(_position[0]) - 1) * 8 + int(_position[1]) - 1
    else:
        # Convert bytes to zero-index and convert to bits
        shift = (int(_position[0]) - 1) * 8
    return shift

def get_datalength(length):
    amt, unit = length.split(" ")
    if unit == "bytes" or unit == "byte":
        return int(amt) * 8
    else:
        return int(amt)

def convert_data(data, position, length):
    # Remove Spaces and Convert to bytes
    _data = bytes.fromhex(data.replace(" ", ""))
    # Produce number
    _data = int.from_bytes(_data, "little")
    # Mask the Correct Data
    _shift = get_bitshift(position)
    _length = get_datalength(length)
    mask = (2 ** (_length + _shift) -2 ** (_shift))
    _data = (mask & _data) >> _shift
    print(data, position, length, _length, _data)
    return _data

def read_spec(filename):
    return pd.read_excel(filename, dtype=str, sheet_name="SPs & PGs", skiprows=3) \
             .drop(columns=['Revised',
                            'PG Revised',
                            'SP Revised',
                            'SP to PG Map Revised',
                            'SP Reference',
                            'SP Document',
                            'PG Document',
                            'SP Created or Modified Date',
                            'PG Created or Modified Date',
                            'SP to PG Mapping Created or Modified Date',
                            'SLOT Identifier',
                            'SLOT Name'])

def analyze_can_log(log, spec):
    combine = log.merge(spec, how='inner', left_on='pgn', right_on='PGN') \
                 .dropna(subset=['SP Position in PG', 'SP Length'])
    combine['data'] = np.vectorize(convert_data)(combine['data'],
                                                 combine['SP Position in PG'],
                                                 combine['SP Length'])
    combine = combine[["time",
                       "SP Label",
                       "SP Description",
                       "data",
                       "Resolution",
                       "Units",
                       "Data Range",
                       "SPN",
                       "priority",
                       "source",
                       "destination",
                       ]]
    return combine
