import numpy as np
import datetime as dt
from datetime import datetime, date, time, timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all data
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    #Create a dictionary 
    precipitation_data = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        precipitation_data.append(precipitation_dict)

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all data
    results = session.query(Station.station, Station.name).all()

    session.close()

    #Create a dictionary 
    station_data = []
    for station, name in results:
        station_dict = {}
        station_dict["Station ID"] = station
        station_dict["Station Name"] = name
        station_data.append(station_dict)

    return jsonify(station_data)



@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for the last date of the year
    last_date_query = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    last_date = dt.datetime.strptime(last_date_query[0], '%Y-%m-%d').date()

    # Date one year ago
    date_one_year_ago = last_date - dt.timedelta(days=366)

    # Query for the temparture for the last year
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= date_one_year_ago).all()

    session.close()

    #Create a dictionary 
    temperature_data = []
    for date, tobs in results:
        temperature_dict = {}
        temperature_dict["Date"] = date
        temperature_dict["Temperature"] = tobs
        temperature_data.append(temperature_dict)

    return jsonify(temperature_data)


@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Start Date equation
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    
    #Temp stats Query
    temp_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),\
        func.avg(Measurement.tobs).filter(Measurement.date >= start_date).all())

    session.close()

    temp_stats_data = list(np.ravel(temp_stats))
    min_temp = temp_stats_data[0]
    max_temp = temp_stats_data[1]
    avg_temp = temp_stats_data[2]

    #Create a dictionary 
    temp_stats_data = []
    temp_stats_dict = [{'Start Date': start,
                        'Minimum Temperature': min_temp,
                        'Maximum Temperature': max_temp,
                        'Average Temperature': avg_temp}]
                            
    temp_stats_data.append(temp_stats_dict)

    return jsonify(temp_stats_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create our session from Python to the DB
    session = Session(engine)

    # Start Date equation
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    
    #Temp stats Query
    temp_stats2 = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),\
        func.avg(Measurement.tobs).\
            filter(Measurement.date >= start_date).filter(Measurement.date >= end_date).all())
    
    session.close()

    temp_stats2_results = list(np.ravel(temp_stats2))
    min_temp = temp_stats2_results[0]
    max_temp = temp_stats2_results[1]
    avg_temp = temp_stats2_results[2]

    #Create a dictionary 
    temp_stats2_data = []
    temp_stats2_dict = [{'Start Date': start,
                        'End Date': end_date,
                        'Minimum Temperature': min_temp,
                        'Maximum Temperature': max_temp,
                        'Average Temperature': avg_temp}]
                            
    temp_stats2_results.append(temp_stats2_dict)

    return jsonify(temp_stats2_data)


if __name__ == '__main__':
    app.run(debug=True)
