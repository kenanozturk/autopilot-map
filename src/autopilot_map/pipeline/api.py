import uvicorn
from fastapi import FastAPI

import autopilot_map.pipeline.db_manager as manager

from autopilot_map.pipeline.model import WindAtCoordinate

app = FastAPI(title="Autopilot Map API", description="""
Data management interface for Autopilot
""")

@app.get('/', tags=['default'])
def root() -> str:
    return "Welcome to Autopilot"

@app.get('/hello_{name}', tags=['Debugging'])
def hello_world(name: str) -> str:
    """
    Hello world!
    """
    return f"Hello {name}"

@app.get('/winddata_lat{lat}_lon{lon}', tags=['Wind Data'], response_model=WindAtCoordinate)
def get_wind_data(lat: float, lon: float) -> str:
    """
    Hello world!
    """
    return manager.get_data(lat, lon)

# if __name__ == '__main__':
#     uvicorn.run(app, host="localhost", port=5000)