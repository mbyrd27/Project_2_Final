# Dependencies
import os
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

# Flask
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

from collections import Counter

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data/classicrock.sqlite"
db = SQLAlchemy(app)

Base = automap_base()
Base.prepare(db.engine, reflect=True)

Rocks = Base.classes.rock_data_id
# Testing for Viiji
# Songs = Base.classes.songdata

@app.route("/")
def home():
    return render_template("index.html")

# Testing for Viiji
# @app.route("/songs/<artist>")
# def sngcount(artist):

#   stmt = db.session.query(Rocks).statement
#   df = pd.read_sql_query(stmt, db.session.bind)

#   df_artist = df.loc[df["ARTISTCLEAN"]==artist]


#   print(df_artist)



#   return jsonify(df_artist.to_dict(orient="record"))

# @app.route("/artistnames")
# def other_artistnames():

#   results = db.session.query(Rocks.ARTISTCLEAN).distinct().all()
# #    df = pd.read_sql_query(stmt, db.session.bind)

# #    df_artist = df.loc[df["ARTISTCLEAN"]==artist]
#   artistList = []
#   for result in results:
#        artistList.append(result[0])
#   return jsonify(artistList)


# #    print(stmt)



#   return jsonify(stmt)


@app.route("/map")
def coords():
    stmt = db.session.query(Rocks).statement
    df = pd.read_sql_query(stmt, db.session.bind)

    new_df = df.groupby(['CITY', 'LAT', 'LON', 'CALLSIGN', 'MedianAge']).count()
    new_df = new_df.reset_index()

    cities = list(new_df['CITY'])
    lats = list(new_df['LAT'])
    lons = list(new_df['LON'])
    calls = list(new_df['CALLSIGN'])
    median_age = list(new_df['MedianAge'])

    def get_popular_artist(location):
        songs = df[['CITY', 'SongClean', 'ARTISTCLEAN']].groupby(['ARTISTCLEAN', 'CITY']).count()
        songs = songs.reset_index()
        artist_df = songs.loc[songs["CITY"] == location, ["ARTISTCLEAN", "SongClean"]]
        artist_df = artist_df.sort_values("SongClean", ascending=False)
        return artist_df.iloc[0]['ARTISTCLEAN']

    data = []
    for i in range(len(cities)):
        city_dict = {}
        city_dict['City'] = cities[i]
        city_dict['Lat'] = lats[i]
        city_dict['Lon'] = lons[i]
        city_dict['Callsign'] = calls[i]
        city_dict['MedianAge'] = median_age[i]
        city_dict['Most_common_artist'] = get_popular_artist(cities[i])
        data.append(city_dict)

    return jsonify(data)

@app.route("/artists")
def artist_list():
    artists = db.session.query(Rocks.ARTISTCLEAN).distinct().all()
    artists = [x[0] for x in artists]
    return jsonify(artists)

@app.route("/artists/<artist>")
def pie_data(artist):
    # Good effort
    # selected_artist = db.session.query(Rocks.SongClean).filter(Rocks.ARTISTCLEAN == artist).all()
    # selected_artist = [x[0] for x in selected_artist]
    # songslist = Counter(selected_artist)
    stmt = db.session.query(Rocks).statement
    df = pd.read_sql_query(stmt, db.session.bind)

    # Pandas to the rescue...again
    songcount = df.loc[df['ARTISTCLEAN'] == artist].groupby(df['SongClean']).count()
    songcount = songcount['id']
    songcount = songcount.reset_index()
    to_json = songcount.rename(columns={'SongClean': 'Song', 'id': 'Count'})
    song = list(to_json['Song'])
    count = list(to_json['Count'])
    to_piechart = []
    for i in range(len(song)):
        songcount_dict = {}
        songcount_dict['song'] = song[i]
        songcount_dict['count'] = count[i]
        to_piechart.append(songcount_dict)
    
    return jsonify(to_piechart)

@app.route("/times/<artist>")
def popular_times(artist):
    stmt = db.session.query(Rocks).statement
    df = pd.read_sql_query(stmt, db.session.bind)

    df['TIME'] = pd.to_datetime(df['TIME'], unit='s')

    df = df.replace(' ', '%20')
    ts = list(df['TIME'])
    new_ts = []
    for i in ts:
        new_ts.append(i.hour)
    
    df['Hour'] = new_ts
    conditions = [
        (df['Hour'] >= 0) & (df['Hour'] < 5),
        (df['Hour'] >= 5) & (df['Hour'] < 8),
        (df['Hour'] >= 8) & (df['Hour'] < 12),
        (df['Hour'] >= 12) & (df['Hour'] < 16),
        (df['Hour'] >= 16) & (df['Hour'] < 20)]

    choices = ['Wee Hours', 'Morning', 'Mid-Day', 'Afternoon', 'Evening']
    df['TimeSlot'] = np.select(conditions, choices, default='Late-Night')
    to_timeslot = df.groupby(['ARTISTCLEAN', 'TimeSlot']).size().reset_index()
    timeslot = to_timeslot.loc[to_timeslot['ARTISTCLEAN'] == artist]
    time_data = []
    times = list(timeslot['TimeSlot'])
    counts = list(timeslot[0])
    for i in range(len(times)):
        slot_dict = {}
        slot_dict['Time'] = times[i]
        slot_dict['Count'] = counts[i]
        time_data.append(slot_dict)

        chart_order = ['Wee Hours', 'Morning', 'Mid-Day', 'Afternoon', 'Evening', 'Late-Night']
    ordered_times = []
    def order_json(x):
        for i in range(len(time_data)):
            if time_data[i]['Time'] == x:
                ordered_times.append(time_data[i])
    for i in range(len(chart_order)):
        order_json(chart_order[i])
    return jsonify(ordered_times)

@app.route("/byartist")
def page_two():
    return render_template("artist.html")

## Matt - base heatmap - backup
@app.route("/heatmap/<artist>")
def heatmap(artist):
    stmt = db.session.query(Rocks).statement
    df = pd.read_sql_query(stmt, db.session.bind)

    to_heatmap = df.groupby(['ARTISTCLEAN', 'CITY','LON','LAT']).size().reset_index()
    to_heatmap = to_heatmap.rename(columns={0: "Songcount"})

    heatmap = to_heatmap.loc[to_heatmap['ARTISTCLEAN'] == artist]

    city = list(heatmap['CITY'])
    lat = list(heatmap['LAT'])
    lon = list(heatmap['LON'])
    songcount = list(heatmap['Songcount'])

    heatmap_data = []
    for i in range(len(city)):
        heatmap_dict = {}
        heatmap_dict['City'] = city[i]
        heatmap_dict['Lat'] = lat[i]
        heatmap_dict['Lon'] = lon[i]
        heatmap_dict['Songcount'] = songcount[i]
        heatmap_data.append(heatmap_dict)

    return jsonify(heatmap_data)

# @app.route("/byartist")
# def artistnames():

#   results = db.session.query(Rocks.ARTISTCLEAN).distinct().all()
# #    df = pd.read_sql_query(stmt, db.session.bind)

# #    df_artist = df.loc[df["ARTISTCLEAN"]==artist]
#   artistList = []
#   for result in results:
#        artistList.append(result[0])
#   return jsonify(artistList)

if __name__ == "__main__":
    app.run(port=5001)