from typing import Dict

from autopilot_map.pipeline.model import WindAtCoordinate, Coordinate

# TODO connect to database
def get_data(lat: float, lon:float) -> WindAtCoordinate: 
    return WindAtCoordinate.parse_obj(
        {'tws': lat, 'twa': lon}
    )