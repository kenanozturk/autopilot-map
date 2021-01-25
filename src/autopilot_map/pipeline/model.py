from pydantic import BaseModel, validator, Field


class Coordinate(BaseModel):
    """
    Basic lat/lon coordinate.
    """

    lon: float = Field(title="Longitude")
    lat: float = Field(title="Latitude")

    @validator('lon')
    def lon_within_range(cls, value: float) -> float:
        assert -180 < value <= 180, "Not a valid longitude."
        return value

    @validator('lat')
    def lat_within_range(cls, value: float) -> float:
        assert -90 < value <= 90, "Not a valid latitude."
        return value


class WindAtCoordinate(BaseModel):
    """
    Basic lat/lon coordinate.
    """

    tws: float = Field(title="True Wind Speed")
    twa: float = Field(title="True Wind Angle")

    @validator('tws')
    def positive_tws(cls, value: float) -> float:
        assert value >= 0, f"True wind speed should be positive. Got {value} instead"
        return value

    @validator('twa')
    def twa_within_range(cls, value: float) -> float:
        assert 0 <= value <= 360, f"True wind angle should be between 0 and 360. Got {value} instead"
        return value