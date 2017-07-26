#!/usr/bin/env python2
import os
import re
import redis
import json
from flask import Flask, render_template, redirect, request, url_for, make_response
from werkzeug import secure_filename
from pymongo import MongoClient
import pymongo

global DB_NAME

if 'VCAP_SERVICES' in os.environ:
    VCAP_SERVICES = json.loads(os.environ['VCAP_SERVICES'])
    CREDENTIALS = VCAP_SERVICES["rediscloud"][0]["credentials"]
    r = redis.Redis(host=CREDENTIALS["hostname"], port=CREDENTIALS["port"], password=CREDENTIALS["password"])
    MONCRED = VCAP_SERVICES["mlab"][0]["credentials"]
    client = MongoClient(MONCRED["uri"])
    DB_NAME = str(MONCRED["uri"].split("/")[-1])
    
else:
    r = redis.Redis(host='127.0.0.1', port='6379')
    client = MongoClient('127.0.0.1:27017')
    DB_NAME = "FoodBlog"

print "Connecting to database : " + DB_NAME
db = client[DB_NAME]
print db


app = Flask(__name__)

@app.route('/')
def mainpage():

    CalorieCount = r.get('caloriecount')
        
    response = """
    <HTML>
    <head>
    <title>Full Blog</title>
    <meta http-equiv="Expires" content="0">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="apple-touch-icon" href="/static/apple-touch-icon.png">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">
    </head>
    <body>
    <div class="container">
    <h1>Foodies Blog</h1>
    <h2>
    <img src="static/fork.jpg"> <a href="/newmeal">New Meal</a><br>
    <img src="static/fork.jpg"> <a href="/dumpmeals">Show Blog</a><br>
    <img src="static/fork.jpg"> <a href="/badmeals">Terrible Meals</a><br>
    </h2>
    <h3>Calories so far: <b>{}</b><h3>
    </body>
    """.format(str(CalorieCount))
    return response

@app.route('/newmeal')
def survey():
    resp = make_response(render_template('newmeal.html'))
    return resp

@app.route('/mealthankyou.html', methods=['POST'])
def mealthankyou():

    global r
    d = request.form['mealdate']
    m = request.form['mealtype']
    c = request.form['calories']
    t = request.form['description']

    print "Meal Date is " + d
    print "Meal Type is " + m
    print "Calories are " + c
    print "Description: " + t

    r.incrby('caloriecount',int(c))
    
    print "Storing the meal now"
    db.meals.insert_one({'mealdate':d, 'mealtype':m,'calories':int(c), 'description':t})
	
    resp = """
    <h3>New entry added to the blog</h3>
    <a href="/">Back to main menu</a>
    """
    return resp

@app.route('/dumpmeals')
def dumpmeals():

    global r
    response = """
        <head>
        <title>Full Blog</title>
	<meta http-equiv="Expires" content="0">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="apple-touch-icon" href="/static/apple-touch-icon.png">
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">
	</head>
	<body>
	<div class="container">
	<div class="row">
	   <div class="col-xs-12">
	   <h1 >Meals to date</h1>
	<div class="row">"""
	   
    print "Reading back from Mongo"
    cursor = db.meals.find().sort("mealdate")
    for each_meal in cursor:
        response += """<div class="col-sm-3">"""
        response += "Meal Date   : " + each_meal['mealdate'] + "<br>"
        response += "Meal Type   : " + each_meal['mealtype'] + "<br>"
        response += "Calories    : " + str(each_meal['calories']) + "<br>"
        response += "Description : " + each_meal['description'] + "<br>"
        response += "<hr>"
        response += "</div>"

    return response

@app.route('/badmeals')
def badmeals():

    global r
    response = """
        <head>
        <title>Full Blog</title>
	<meta http-equiv="Expires" content="0">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="apple-touch-icon" href="/static/apple-touch-icon.png">
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">
	</head>
	<body>
	<div class="container">
	<div class="row">
	   <div class="col-xs-12">
	   <h1 >Meals to date</h1>
	<div class="row">"""

    print "Reading back from Mongo"
    cursor = db.meals.find({"calories" : {"$gt" : 2000} })
    for each_meal in cursor:
        response += """<div class="col-sm-3">"""
        response += "Meal Date   : " + each_meal['mealdate'] + "<br>"
        response += "Meal Type   : " + each_meal['mealtype'] + "<br>"
        response += "Calories    : " + str(each_meal['calories']) + "<br>"
        response += "Description : " + each_meal['description'] + "<br>"
        response += "<hr>"
        response += "</div>"
    
    return response


if __name__ == "__main__":
	app.run(debug=False, host='0.0.0.0', \
                port=int(os.getenv('PORT', '5000')), threaded=True)
