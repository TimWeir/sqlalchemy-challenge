##sqlalchemy-challenge

#import the libraries
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create session
session = Session(engine)

# Flask Setup
app = Flask(__name__)


#query for most recent date in DB
recent_date = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())

#calculate date of 1 year prior to most recent date in DB
recent_date = dt.datetime.strptime(recent_date.date, '%Y-%m-%d')
recent_date_y = int(dt.datetime.strftime(recent_date, '%Y'))
recent_date_m = int(dt.datetime.strftime(recent_date, '%m'))
recent_date_d = int(dt.datetime.strftime(recent_date, '%d'))
year_ago_date = dt.date(recent_date_y-1,recent_date_m,recent_date_d)
recent_date = dt.date(recent_date_y,recent_date_m,recent_date_d)


# Flask Routes
@app.route("/")
def home():
    """Welcome, navigation list appears below."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - Precipitation stats for the most recent year of data<br/>"
        f"/api/v1.0/stations - List of stations in the dataset<br/>"
        f"/api/v1.0/tobs - List of stations in the dataset<br/>"
        f"/api/v1.0/{recent_date} - list of the minimum temperature, the average temperature, and the max temperature for a given start date</br>"
        f"/api/v1.0/{recent_date}/{year_ago_date} - list of the minimum temperature, the average temperature, and the max temperature for a given date range "
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    results = (session.query(Measurement.date, Measurement.prcp)
                      .filter(Measurement.date > year_ago_date)
                      .order_by(Measurement.date)
                      .all())
    
    prcpdata = []
    for result in results:
        prcpdict = {result.date: result.prcp}
        prcpdata.append(prcpdict)

    return jsonify(prcpdata)


@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    station_freq = session.query(Measurement.station,func.count(Measurement.id).label('qty')).group_by(Measurement.station).\
            order_by(desc('qty')).first()
    max_station = station_freq[0]

    results = (session.query(Measurement.station, Measurement.date, Measurement.tobs)
                      .filter(Measurement.date > year_ago_date)
                      .filter(Measurement.station == max_station)
                      .all())
    
    tobsdata = []
    for result in results:
        tobsdict = {result.date: result.tobs}
        tobsdata.append(tobsdict)

    return jsonify(tobsdata)


if __name__ == "__main__":
    app.run(debug=True)