from flask import Flask, jsonify

import numpy as np
import datetime as dt

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

#Home: display available routes
@app.route("/")
def home():
    return(
        f'Available routes <br/>'
        f'----------------- <br/>'
        f'Precipitation information: /api/v1.0/precipitation <br/>'
        f'List of stations: /api/v1.0/stations <br/>'
        f'Temperature observations of the most active station for the last year of data: /api/v1.0/tobs <br/>'
        f'Minimum, average and maximum temperature observed, calculated from a given start date through the most recent date: /api/v1.0/YOUR_START_DATE <br/>'
        f'(Enter date as 4 digit year, 2 digit month and 2 digit day: xxxx-xx-xx) <br/>'
        f'Minimum, average and maximum temperature observed, calculated from a given start date through a given end date: /api/v1.0/YOUR_START_DATE/YOUR_END_DATE  <br/>'
        f'(Enter date as 4 digit year, 2 digit month and 2 digit day: xxxx-xx-xx)'
    )

#Route for displaying all precipiation data from all stations
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

#Route for displaying all stations (I also displayed station name with number)
@app.route('/api/v1.0/stations')
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

#Route for displaying temperature readings from the most active station for the last year of data (using information found in jupyter notebook analysis) 
@app.route('/api/v1.0/tobs')
def temps():
    session = Session(engine)
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    sel = [Measurement.date, Measurement.tobs]
    result = session.query(*sel).filter(Measurement.date >= last_year).filter(Measurement.station == "USC00519281").all()

    temps = []
    for date, temp in result:
        temps_dict = {}
        temps_dict["Date"] = date
        temps_dict["Temperature"] = temp
        temps.append(temps_dict)
    return jsonify (temps)

#Route for displaying the min, avg, and max temps over a range from a given start date through the remainder of the data
@app.route('/api/v1.0/<start>')
def temps_start(start):
    session = Session(engine)
    temp_stats_start = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    temp_start = []
    for min, avg, max in temp_stats_start:
        temp_start_dict = {}
        temp_start_dict["Min Temp"] = min
        temp_start_dict["Average Temp"] = avg
        temp_start_dict["Max Temp"] = max
        temp_start.append(temp_start_dict)

    return jsonify(temp_start)

#Route for displaying the min, avg and max temps over a range from a given start and end date
@app.route('/api/v1.0/<start>/<end>')
def temps_stop(start,end):
    session = Session(engine)
    temp_stats_stop = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date<= end).all()
    session.close()

    temp_stop = []
    for min, avg, max in temp_stats_stop:
        temp_stop_dict = {}
        temp_stop_dict["Min Temp"] = min
        temp_stop_dict["Average Temp"] = avg
        temp_stop_dict["Max Temp"] = max
        temp_stop.append(temp_stop_dict)

    return jsonify(temp_stop)
    #return jsonify(f'{temp_stop} between the dates of {start}, {end}') - looks weird in display

#Define main behavior
if __name__ == "__main__":
    app.run(debug=True)
