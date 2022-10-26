from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
import pymysql
import re
import MySQLdb.cursors

# Connect MYSQL db to pymysql
connection = 'mysql+pymysql://root:root@localhost/RealEstate'

app = Flask(__name__)

# Connect to SQLAlchemy
app.secret_key = 'SECRET'
app.config['SQLALCHEMY_DATABASE_URI'] = connection
db = SQLAlchemy(app)

# Instantiate admin class
admin = Admin(app)


# Modelling databases

class Clients(db.Model):
    ClientID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(25), unique=False, nullable=False)
    LastName = db.Column(db.String(25), unique=False, nullable=False)
    PhoneNumber = db.Column(db.String(12), unique=True, nullable=True)
    Email = db.Column(db.String(320), unique=True, nullable=True)


class Messages(db.Model):
    MessageID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(25), unique=False, nullable=False)
    LastName = db.Column(db.String(25), unique=False, nullable=False)
    PhoneNumber = db.Column(db.String(12), unique=True, nullable=True)
    Email = db.Column(db.String(320), unique=True, nullable=True)
    Comment = db.Column(db.String(1000), unique=False, nullable=False)


class Listings(db.Model):
    PropertyID = db.Column(db.Integer, primary_key=True)
    Location = db.Column(db.String(255), unique=False, nullable=False)
    City = db.Column(db.String(255), unique=False, nullable=False)
    State = db.Column(db.String(2), unique=False, nullable=False)
    Zip = db.Column(db.String(5), unique=False, nullable=False)
    Price = db.Column(db.Float(15, 2), unique=False, nullable=False)
    Bedroom = db.Column(db.Integer, unique=False, nullable=False)
    Bathroom = db.Column(db.Integer, unique=False, nullable=False)
    SquareFeet = db.Column(db.Float(15, 2), unique=False, nullable=False)
    Description = db.Column(db.String(1000), unique=False, nullable=False)


class User(db.Model):
    UserID = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(255), unique=True, nullable=False)


# Use only first time to create otherwise comment out!
# If not you may have to use cmd prompt to make db instead.

# db.create_all()

# Creating ModelView for each table for use with Flask-Admin
admin.add_view(ModelView(Clients, db.session))
admin.add_view(ModelView(Messages, db.session))
admin.add_view(ModelView(Listings, db.session))


@app.route('/index')
def homepage():
    return render_template('index.html')

@app.route('/')
@app.route('/listings')
def listings():
    db = MySQLdb.connect(host="localhost", user="root", password="root", db="realestate")
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM listings ',)
    loc=cur.fetchall()
    return render_template('listings.html', loc=loc)

@app.route('/listing/<int:propID>',methods=['GET','POST'])
def locationListing():
    db = MySQLdb.connect(host="localhost", user="root", password="root", db="realestate")
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT PropertyID FROM listings', )

if __name__ == '__main__':
    # Should be able to access admin from localhost/admin in url
    app.run(debug=True)
