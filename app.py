# Python SQL toolkit and Object Relational Mapper
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, text,inspect
from flask import Flask, jsonify
from datetime import datetime, timedelta

import os

base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, "Resources", "hawaii.sqlite")
engine = create_engine(f"sqlite:///{db_path}")

# create engine to hawaii.sqlite
# engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station


# Initialize the Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Welcome to the Climate App! Visit the following routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    one_year_ago = datetime.strptime(last_date, '%Y-%m-%d') - timedelta(days=365)

    # Query precipitation data for the last 12 months
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year_ago).all()
    session.close()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # Query all stations from the dataset
    results = session.query(station.station, station.name).all()
    session.close()
    # Convert the query results to a list of dictionaries
    station_list = [{"station": station, "name": name} for station, name in results]

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Find the most active station
    most_active_station = session.query(measurement.station).\
        group_by(measurement.station).\
        order_by(func.count().desc()).first()[0]

    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    one_year_ago = datetime.strptime(last_date, '%Y-%m-%d') - timedelta(days=365)

    # Query temperature observations for the most active station in the last 12 months
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station).\
        filter(measurement.date >= one_year_ago).all()
    session.close()
    # Convert the query results to a list of dictionaries
    tobs_data = [{"date": date, "tobs": tobs} for date, tobs in results]

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def temperature_start(start):
    session = Session(engine)
    # Query for TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
    results = session.query(
        func.min(measurement.tobs).label("TMIN"),
        func.avg(measurement.tobs).label("TAVG"),
        func.max(measurement.tobs).label("TMAX")
    ).filter(measurement.date >= start).all()

    session.close()
    # Convert the query results to a dictionary
    temperature_data = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end(start, end):
    session = Session(engine)
    # Query for TMIN, TAVG, and TMAX for dates between the start and end dates (inclusive)
    results = session.query(
        func.min(measurement.tobs).label("TMIN"),
        func.avg(measurement.tobs).label("TAVG"),
        func.max(measurement.tobs).label("TMAX")
    ).filter(measurement.date.between(start, end)).all()

    session.close()
    # Convert the query results to a dictionary
    temperature_data = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    return jsonify(temperature_data)

if __name__ == "__main__":
    app.run(debug=True)

    #   