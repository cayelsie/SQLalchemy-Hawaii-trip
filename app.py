from flask import Flask, jsonify

import numpy as np
from datetime import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
######################################
#Database setup
######################################

#Setting path to the database file
database_path = "Resources/hawaii.sqlite"

# create engine to hawaii.sqlite
engine = create_engine(f"sqlite:///{database_path}")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


######################################
#Flask setup
#####################################
app = Flask(__name__)

#####################################
#Available routes
#####################################

@app.route("/")
def home():
    return(
        f'Available routes <br/>'
        f'----------------- <br/>'
        f'Precipitation information: /api/v1.0/precipitation <br/>'
        f'List of stations: /api/v1.0/stations <br/>'
        f'Temperature observations of the most active station for the last year of data: /api/v1.0/tobs <br/>'
        f'Temperature observations of the most active station from a given start date: /api/v1.0/YOUR_START_DATE_HERE <br/>'
        f'Temperature observations of the most active station from a given date range: /api/v1.0/YOUR_START_DATE_HERE /YOUR_END_DATE_HERE  <br/>'
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    sel = [Measurement.date, Measurement.prcp]
    result = session.query(*sel).all()
    session.close()

    precip = []
    for date, prcp in result:
        precip_dict = {}
        precip_dict['Date'] = date
        precip_dict['Precipitation'] = prcp
        precip.append(precip_dict)

    return jsonify(precip)

@app.route ('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel = [Station.station, Station.name]
    result = session.query(*sel).group_by(Station.station)
    session.close()

    stations = []
    for station, name in result:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        stations.append(station_dict)
    return jsonify (stations)


if __name__ == "__main__":
    app.run(debug=True)
