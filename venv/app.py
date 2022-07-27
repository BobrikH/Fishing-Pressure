from dash import Dash, dcc, html, Input, Output, dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import sqlite3
import requests
from datetime import date,datetime,time
from threading import Thread
import time
DATABASE = "DataBase.db"
APPID = "P2SU64HWKZ3qC"
password = "1661a35ab21825a49827ddf2461c4a81"  #hashlib.md5("kjfb7959")
uuid = "f7e6c85504ce6e82442c770f7c8606f0"
user_date = str(date.today())

def insert_varible_into_table(p,d,t):
    try:
        sqlite_connection = sqlite3.connect('DataBase.db')
        cursor = sqlite_connection.cursor()

        sqlite_insert_with_param = """INSERT INTO PressureInfo
                              (Pressure, Date, Time)
                              VALUES (?, ?, ?);"""

        data_tuple = (p, d, t)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqlite_connection.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()

def getPressure(key,uid):
    r = requests.get(f"http://narodmon.ru/api/sensorsOnDevice?devices=2318&uuid={uid}&api_key={key}&lang=ru")
    pressureRaw = r.json()
    pressure = float(pressureRaw["devices"][0]["sensors"][0]["value"])
    return pressure

def PressureIntoDB(timer):
    while 1==1:
        currentTime = str(datetime.now().time())[:5]
        currentDate = datetime.now().date()
        p = getPressure(APPID,uuid)
        insert_varible_into_table(p,currentDate,currentTime)
        time.sleep(timer)
th_pressure = Thread(target=PressureIntoDB, args=(3602,))
th_pressure.start()

def read_limited_rows(row_size):
    try:
        sqlite_connection = sqlite3.connect('DataBase.db')
        cursor = sqlite_connection.cursor()
        sqlite_select_query = """SELECT * from PressureInfo"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchmany(row_size)

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
    return records

def read_sqlite_table():
    try:
        sqlite_connection = sqlite3.connect('DataBase.db')
        cursor = sqlite_connection.cursor()

        sqlite_select_query = """SELECT * from PressureInfo"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
    return records

def drawInfo(records,default_date):
    res = []
    for i in records:
        if i[1] == default_date:
            res.append((i[0],i[2]))
        if default_date == 0:
            res.append((i[0], i[2]))
    return res

app = dash.Dash(__name__)
server = app.server
def draw():
    while 1==1:
        rawData = read_sqlite_table()
        rawWeekData = read_limited_rows(336)
        weekData = drawInfo(rawWeekData,0)
        week_y = []
        week_x = []
        dates = set()
        for i in weekData:
            week_y.append(i[0])
            week_x.append(i[1])
        for j in rawData:
            dates.add(j[1])

        app.layout = html.Div(
            children=[
                dcc.Graph(
                    id = "graf",

                    style={
                        "width": "500px",
                    }
                ),

                html.Div(children="Дата", className="menu-title",id = "menu-title"),
                dcc.Dropdown(
                    id="date-filter",
                    options=[
                        {"label": dat, "value": dat}
                        for dat in dates
                    ],
                    value = date.today(),
                    clearable=False,
                    className="dropdown",
                    style={
                        "width" : "500px"
                    }
                ),
                dcc.Graph(
                    id="week-graf",
                    figure={
                        "data": [
                            {
                                "x": week_x,
                                "y": week_y,
                                "type": "lines",
                            },
                        ],
                        "layout": {
                            "title": {
                                "text": "График давления за последнюю неделю",
                            },
                        },
                    }
                ),
            ]
        )
th_draw = Thread(target = draw, args=() )
th_draw.start()
@app.callback(
    Output('graf', 'figure'),
    Input('date-filter', 'value')
)
def update_output(value):
    user_date = value
    rawData = read_sqlite_table()
    data = drawInfo(rawData,value)
    abcis = []
    ordinat = []
    dates = set()
    for i in data:
        abcis.append(i[1])
        ordinat.append(i[0])
    figure = {
        "data": [
            {
                "x": abcis,
                "y": ordinat,
                "type": "lines",
            },
        ],
        "layout": {"title": "График изменения давления"},
    }
    return figure


if __name__ == "__main__":
    app.run_server(debug=False)
