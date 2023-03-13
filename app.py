#!/usr/bin/env python

'''
	RPi WEb Server for DHT captured data with Gage and Graph plot  
'''
from threading import Thread
from datetime import datetime
import log_DHT
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io

from flask import Flask, render_template, make_response, request
import sqlite3

app = Flask(__name__)

logger = Thread(target=log_DHT.run)
logger.start()

conn=sqlite3.connect('sensors_data.db', check_same_thread=False)
curs=conn.cursor()

# Retrieve LAST data from database
def get_last_data():
	for row in curs.execute("SELECT * FROM DHT_data ORDER BY timestamp DESC LIMIT 1"):
		time = str(row[0])
		temp = row[1]
		hum = row[2]
	#conn.close()
	return time, temp, hum

# Get 'x' samples of historical data
def get_hist_data(num_samples):	
        query = "SELECT * FROM DHT_data ORDER BY timestamp DESC LIMIT ?"
        data = (num_samples, )
        curs.execute(query, data)
        #curs.execute("SELECT * FROM DHT_data ORDER BY timestamp DESC LIMIT "+str(num_samples)) 
        data = curs.fetchall()
        dates = []
        temps = []
        hums = []
        for row in reversed(data):
                dates.append(row[0])
                temps.append(row[1])
                hums.append(row[2])
                temps, hums = tested_data(temps, hums)
        return dates, temps, hums

# Test data for cleanning possible "out of range" values
def tested_data(temps, hums):
	n = len(temps)
	for i in range(0, n-1):
		if (temps[i] < -10 or temps[i] >50):
			temps[i] = temps[i-2]
		if (hums[i] < 0 or hums[i] >100):
			hums[i] = temps[i-2]
	return temps, hums


# Get Max number of rows (table size)
def max_rows_table():
	for row in curs.execute("select COUNT(temp) from DHT_data"):
		max_number_rows=row[0]
	return max_number_rows

# Get sample frequency in minutes
def freq_sample():
	times, temps, hums = get_hist_data(2)
	fmt = '%Y-%m-%d %H:%M:%S'
	tstamp0 = datetime.strptime(times[0], fmt)
	tstamp1 = datetime.strptime(times[1], fmt)
	freq = tstamp1-tstamp0
	freq = int(round(freq.total_seconds()/60))
	return (freq)

# define and initialize global variables
global num_samples
num_samples = max_rows_table()
if (num_samples > 101):
        num_samples = 100

global freq_samples
freq_samples = freq_sample()

global range_time
range_time = 100
				
		
# main route 
@app.route("/")
def index():
	time, temp, hum = get_last_data()
	date = datetime.now()
	date = date.strftime("%Y")
	template_data = {
      'time'		: time,
      'temp'		: temp,
      'hum'		: hum,
      'freq'		: freq_samples,
      'range_time'	: range_time,
      'date'		: date
	}
	return render_template('index.html', **template_data)


@app.route('/', methods=['POST'])
def my_form_post():
    global num_samples 
    global freq_samples
    global range_time
    range_time = int (request.form['range_time'])
    if (range_time < freq_samples):
        range_time = freq_samples + 1
    num_samples = range_time//freq_samples
    num_max_samples = max_rows_table()
    if (num_samples > num_max_samples):
        num_samples = (num_max_samples-1)
    
    time, temp, hum = get_last_data()
    
    template_data = {
	  'time'		: time,
      'temp'		: temp,
      'hum'			: hum,
      'freq'		: freq_samples,
      'range_time'	: range_time
	}
    return render_template('index.html', **template_data)
	
	
@app.route('/plot/temp')
def plot_temp():
	times, temps, hums = get_hist_data(num_samples)
	ys = temps
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("Temperature [°C]")
	axis.set_xlabel("Samples")
	axis.grid(True)
	xs = range(num_samples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

@app.route('/plot/hum')
def plot_hum():
	times, temps, hums = get_hist_data(num_samples)
	ys = hums
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("Humidity [%]")
	axis.set_xlabel("Samples")
	axis.grid(True)
	xs = range(num_samples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response
	
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=False)

