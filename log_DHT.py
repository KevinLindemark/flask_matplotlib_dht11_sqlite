#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  logDHT.py
#
#  Developed by Marcelo Rovai, MJRoBot.org @ 10Jan18
#  
#  Capture data from a DHT22 sensor and save it on a database

import time
import sqlite3
import schedule
import Adafruit_DHT

db_name='sensors_data.db'

# get data from DHT sensor
def get_DHT_data():	
	
	DHT11_sensor = Adafruit_DHT.DHT11
	DHT_pin = 4
	hum, temp = Adafruit_DHT.read_retry(DHT11_sensor, DHT_pin)
	
	if hum != None and temp != None:
		hum = round(hum)
		temp = round(temp, 1)
	return temp, hum

# log sensor data on database
def log_data (temp, hum):
	conn=sqlite3.connect(db_name)
	curs=conn.cursor()
	curs.execute("INSERT INTO DHT_data values(datetime('now'), (?), (?))", (temp, hum))
	conn.commit()
	conn.close()

# main function
def main():
	print("running main")
	temp, hum = get_DHT_data()
	log_data(temp, hum)
		
def weekend():
	schedule.clear('working-days')
	#07:00, 12:00, 17:00 og 23:00 i weekender.
	schedule.every().saturday.at("07:00").do(main).tag('weekend-days')
	schedule.every().saturday.at("12:00").do(main).tag('weekend-days')
	schedule.every().saturday.at("17:00").do(main).tag('weekend-days')
	schedule.every().saturday.at("23:00").do(main).tag('weekend-days')

	schedule.every().sunday.at("07:00").do(main).tag('weekend-days')
	schedule.every().sunday.at("12:00").do(main).tag('weekend-days')
	schedule.every().sunday.at("17:00").do(main).tag('weekend-days')
	schedule.every().sunday.at("23:00").do(main).tag('weekend-days')

def workdays():
	schedule.clear('weekend-days')
	schedule.every(20).minutes.do(main).tag('working-days')

# ------------ Execute program 

schedule.every().saturday.do(weekend)
schedule.every().monday.do(workdays)
def run():
	while True:
		schedule.run_pending()
		time.sleep(1)
