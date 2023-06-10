from flask import Flask, render_template, jsonify
from pandas import read_csv
from numpy import NaN

app = Flask(__name__)
stations = read_csv("data/stations.txt", skiprows=17)[
    ["STAID", "STANAME                                 "]
].to_html()


@app.route("/")
def home():
    return render_template("home.html", table=stations)


@app.route("/api/v1/<station>/date/<date>")
def temp_for_date(station, date):
    try:
        filename = rf"data/TG_STAID{station.zfill(6)}.txt"
        df = read_csv(filename, skiprows=20, parse_dates=["    DATE"])
        df["   TG"] = df["   TG"].replace([-9999], NaN)
        temperature = df.loc[df["    DATE"] == date]["   TG"].squeeze() / 10
        return jsonify(
            {"Station ID": station, "Date": date, "Temperature": temperature}
        )
    except TypeError:
        return {}


@app.route("/api/v1/<station>")
def temp_for_all_dates(station):
    filename = rf"data/TG_STAID{station.zfill(6)}.txt"
    df = read_csv(filename, skiprows=20, parse_dates=["    DATE"])
    df["    DATE"] = df["    DATE"].astype(str)
    df["   TG"] = df["   TG"].replace([-9999], NaN)
    result = df.loc[:, ["    DATE", "STAID", "   TG"]]
    result["   TG"] = result["   TG"].div(10)
    result.rename(
        columns={"    DATE": "Date", "STAID": "Station ID", "   TG": "Temperature"},
        inplace=True,
    )
    return result.to_dict(orient="records")


@app.route("/api/v1/<station>/year/<year>")
def temp_for_year(station, year):
    filename = rf"data/TG_STAID{station.zfill(6)}.txt"
    df = read_csv(filename, skiprows=20, parse_dates=["    DATE"])
    df["    DATE"] = df["    DATE"].astype(str)
    df["   TG"] = df["   TG"].replace([-9999], NaN)
    result = df.loc[df["    DATE"].str.startswith(year)]
    if result.empty:
        return []
    else:
        result = result.loc[:, ["    DATE", "STAID", "   TG"]]
        result["   TG"] = result["   TG"].div(10)
        result.rename(
            columns={"    DATE": "Date", "STAID": "Station ID", "   TG": "Temperature"},
            inplace=True,
        )
        return result.to_dict(orient="records")


if __name__ == "__main__":
    app.run(debug=True)
