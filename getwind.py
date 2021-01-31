import requests  
import json
from typing import Tuple, Dict
import mysql.connector
from datetime import datetime
from geopy import Point
from geopy.distance import lonlat, distance, geodesic
import numpy as np
import yaml



def getURL(lat, lon, hours, key ):
    websiteURL = 'https://api.weatherbit.io'
    version = 'v2.0'
    type = 'forecast'
    subtype = 'hourly'

    URL= f"{websiteURL}/{version}/{type}/{subtype}?lat={lat}&lon={lon}&units=S&key={key}&hours={hours}"
    response = requests.get(URL) 
    timestamp = [a['ts'] for a in response.json()['data']]
    timestamp_utc = [datetime.fromtimestamp(a['ts']).strftime('%Y-%m-%d %H:%M:%S') for a in response.json()['data']]

    wind_dir_forecast = [a['wind_dir'] for a in response.json()['data']]
    wind_spd_forecast = [a['wind_spd'] for a in response.json()['data']]

    return [timestamp[0]]* hours, timestamp, [timestamp_utc[0]]* hours, timestamp_utc, [lat]*hours, [lon]*hours, wind_spd_forecast, wind_dir_forecast

def createSearchArray(config):  
    lat1,lat2 = config["field"]["coordinates"][0]
    lon1,lon2 = config["field"]["coordinates"][1]
    resolution = config["field"]["resolution"]
    leny= geodesic((lat1, lon1), (lat2,lon1)).km
    lenx= geodesic((lat1, lon1), (lat1,lon2)).km
    num_lon = int(np.round(leny/resolution))
    num_lat = int(np.round(lenx/resolution))
    
    cols = np.linspace(lat1, lat2, num=num_lon)
    rows = np.linspace(lon1, lon2, num=num_lat) 
    combs  = np.array(np.meshgrid(cols,rows)).T.reshape(-1,2).tolist() 
    return combs

# response = requests.get(getURL(lat,lon,hours, key)) 
def getWindArrayData(cent_lat, cent_lon, hours, key):
    #TODO: Calculate an array of surrounding valid coordinates to get wind data
    

    return getURL(cent_lat, cent_lon, hours, key)

def insertNewData(config):
    cnxn=createDBConnection(config)
    crsr = cnxn.cursor()
    try: 
        # crsr.execute("DROP TABLE windset")
        crsr.execute("CREATE TABLE windset \
        ( originTimestamp INT, \
        forecastedTimestamp INT, \
        originTimeUTC DATETIME, \
        forecastedTimeUTC DATETIME, \
        lat FLOAT NOT NULL, \
        lon FLOAT NOT NULL,\
        wind_spd FLOAT, \
        wind_dir SMALLINT )")
    except:
        pass


    sql = "INSERT INTO windset (originTimestamp,forecastedTimestamp, originTimeUTC,forecastedTimeUTC, lat, lon, wind_spd, wind_dir ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"    
    
    listCoord = createSearchArray(config)
    for lat,lon in listCoord:
        response = getWindArrayData(lat, lon, config["field"]["saveHorizon"], config["key"])
        responseT = list(map(tuple, zip(*response)))
        crsr.executemany(sql, responseT)
    cnxn.commit()

    print(crsr.rowcount, "was inserted.")
    return 
def selectData(crsr,hrzn,time,targetLatitude,targetLongitude):    
    horizon = hrzn* 3600
    crsr.execute(f"SELECT wind_dir,wind_spd, lat, lon FROM windset \
    WHERE (forecastedTimestamp BETWEEN {time} AND {time+horizon}) AND \
    (lat BETWEEN {targetLatitude[0]} AND {targetLatitude[1]}) AND \
    (lon BETWEEN {targetLongitude[0]} AND {targetLongitude[1]}) \
    ORDER BY lat, lon")
    myresult = crsr.fetchall()
    
    print(len(myresult))
    lats = set(list(zip(*myresult))[2])
    lons = set(list(zip(*myresult))[3])

    windangle=np.array(list(zip(*myresult))[0]).reshape(len(lats),len(lons),-1)
    windspd=np.array(list(zip(*myresult))[0]).reshape(len(lats),len(lons),-1)
    if windangle.shape[2]<hrzn:
        print('Selected Horizon is longer than existing data.')
    return windangle,windspd
def createDBConnection(config): 
    cnxn  = mysql.connector.connect(
    host=config["dbEntry"]["host"],
    user=config["dbEntry"]["user"],
    password=config["dbEntry"]["password"],
    database=config["dbEntry"]["database"]
    )
    return cnxn
class WindAtPoint:
    def __init__(self, twa: float, tws: float) -> None:
        self.tws = tws
        self.twa = twa

class WindField:
    def wind_at(self, coordinates: Point, time: float) -> WindAtPoint:
        """Get TWA and TWS at a specific location and time"""
        raise NotImplementedError

    def get_wind_data_for_viz(self, time: float) -> Dict[Point, WindAtPoint]:
        raise NotImplementedError

    def get_field_bounds(self) -> Dict[str, float]:
        raise NotImplementedError
class DBWindField(WindField):
    def __init__(self, config: dict,backendconfig: dict) -> None:
        super().__init__()
        self.targetLatitude = config["windfield"]["field"]["coordinates"][0]
        self.targetLongitude = config["windfield"]["field"]["coordinates"][1]
        self.horizon =  config["horizon"]
        self.timestamp = config["tzero"]
        cnxn=createDBConnection(backendconfig)
        crsr = cnxn.cursor()
        self.twa, self.tws = selectData(crsr,self.horizon,self.timestamp,self.targetLatitude,self.targetLongitude)
        print('Done')

    
    
class WindFieldFactory:
    supported_wind_field_types = {"WindDB"}

    def make_wind_field(self, config: dict,backendconfig:dict) -> WindField:
        wind_field_type = config["windfield"]["type"]
        if not wind_field_type in self.supported_wind_field_types:
            raise ValueError(
                f"{wind_field_type} is not one of the supported wind field types, which are: {self.supported_wind_field_types}"
            )

        if wind_field_type == "WindDB":
            return DBWindField(config=config,backendconfig=backendconfig)
    
if __name__ == "__main__":
    with open("backend.yaml", 'r') as stream:
        try:
            backendconfig = yaml.safe_load(stream)
        except yaml.YAMLError as config:
            print(backendconfig)   
    insertNewData(backendconfig)


    with open("scenario.yaml", 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as config:
            print(config)   
    wind_field: WindField = WindFieldFactory().make_wind_field(config=config,backendconfig=backendconfig)
