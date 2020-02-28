from flask import Flask, render_template, request, redirect
import requests
import pandas as pd
import datetime
import dateutil
import re

from bokeh.plotting import figure
from bokeh.embed import components

app = Flask(__name__)

@app.route('/')
def main():
    return redirect('/userform')

@app.route('/userform',methods=['GET'])
def userstockform():
    return render_template('userstockform.html')

@app.route('/results',methods=['POST'])
def stockresults():

    # Read user input from form
    tickersymbol = request.form['tickersymbol']

    # Get data and create dataframe
    dataurl = 'https://www.quandl.com/api/v3/datasets/WIKI/' + tickersymbol + '.json'
    r = requests.get(dataurl)
    dataset_df = pd.DataFrame(r.json())['dataset'].apply(pd.Series)
    data = dataset_df.ix['data',:].apply(pd.Series)
    data.columns = dataset_df.ix['column_names',0:12]
    data['Date'] = pd.to_datetime(data['Date'])
    today = datetime.date.today()
    lastmonth = today - dateutil.relativedelta.relativedelta(months=1)
    data_lastmonth = data[data['Date']>lastmonth]

    name = re.search("(^.*\))",dataset_df.ix['name',0]).group(1)

    p = figure(title=name,plot_width=600,plot_height=400,
        x_axis_type="datetime",
        x_range=(lastmonth,today),
        x_axis_label = "Date",
        y_axis_label = "USD")
    if 'openingprice' in request.form:
        p.line(data_lastmonth['Date'],data_lastmonth['Open'],line_color='blue',legend='Opening price')
    if 'adjopeningprice' in request.form:
        p.line(data_lastmonth['Date'],data_lastmonth['Adj. Open'],line_color='blue',line_dash=[4,4],legend='Adj. opening price')
    if 'closingprice' in request.form:
        p.line(data_lastmonth['Date'],data_lastmonth['Close'],line_color='red',legend='Closing price')
    if 'adjclosingprice' in request.form:
        p.line(data_lastmonth['Date'],data_lastmonth['Adj. Close'],line_color='red',line_dash=[4,4],legend='Adj. closing price')
    p.legend.orientation = 'top_left'

    script, div = components(p)

    return render_template('results.html',name=name, tickersymbol=tickersymbol, script=script, div=div)



if __name__ == '__main__':
    app.run(port=33507)
