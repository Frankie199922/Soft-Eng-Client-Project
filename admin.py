from flask import Flask, render_template, request, redirect, url_for, session
from flask_admin.menu import MenuLink
from flask_login import LoginManager
from flask_admin.form import ImageUploadField
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
import pymysql
import re
import MySQLdb.cursors
from flask_admin.contrib.fileadmin import FileAdmin
import os.path as op
from werkzeug.exceptions import abort

# Connect MYSQL db to pymysql
connection = 'mysql+pymysql://root:root@localhost/RealEstate'

app = Flask(__name__, static_folder='static')

@property
def is_authenticated(self):
  return True

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == "root" and request.form.get("password") == "root":
            session['logged_in'] = True
            return redirect("/admin")
        else:
            return render_template("login.html")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# Connect to SQLAlchemy
app.secret_key = 'SECRET'
app.config['SQLALCHEMY_DATABASE_URI'] = connection
db = SQLAlchemy(app)

# Instantiate admin class
admin = Admin(app)

#add logout button
admin.add_link(MenuLink(name='Logout', category='', url="/logout"))

# establish path and ModelView for Picture upload
base_path = op.join(op.dirname(__file__), 'static/pictures')
admin.add_view(FileAdmin(base_path, '/static/', name='Pictures'))


# Modelling database tables
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
    Pictures = db.Column(db.String(1000), unique=False, nullable=False)


class User(db.Model):
    UserID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(255), unique=True, nullable=False)
    Password = db.Column(db.String(255), unique=True, nullable=False)


class AboutMe(db.Model):
    AboutID = db.Column(db.Integer, primary_key=True)
    Description = db.Column(db.String(255), unique=False, nullable=False)
    Pictures = db.Column(db.String(255), unique=False, nullable=False)


# Override ModelView
class messageModelView(ModelView) :
    # ModelView Functionality
    def is_accessible(self):
        if "logged_in" in session:
            return True
        else:
            abort(403)
    
    can_edit = False
    can_create = False
    page_size = 20

    form_columns = ['FirstName', 'LastName', 'PhoneNumber', 'Email', 'Comment']
    column_labels = dict(FirstName="First Name", LastName='Last Name',
                         PhoneNumber='Phone Number',
                         Email='Email', Comment='Comment')


class aboutMeModelView(ModelView) :
    def is_accessible(self):
        if "logged_in" in session:
            return True
        else:
            abort(403)

    page_size = 1

    form_columns = ['AboutID', 'Description', 'Pictures']
    column_labels = dict(Description="Description", Pictures='Picture')

    can_edit = True
    can_delete = False
    can_create = False


class clientModelView(ModelView) :
    # ModelView Functionality  
    def is_accessible(self):
        if "logged_in" in session:
            return True
        else:
            abort(403)
            
    page_size = 20

    form_columns = ['FirstName', 'LastName', 'PhoneNumber', 'Email']
    column_labels = dict(FirstName="First Name", LastName='Last Name',
                         PhoneNumber='Phone Number',
                         Email='Email')


class listingsModelView(ModelView) :
    # ModelView Functionality  
    def is_accessible(self):
        if "logged_in" in session:
            return True
        else:
            abort(403)
            
    page_size = 20

    form_columns = ['Location', 'City', 'State', 'Zip',
                    'Price', 'Bedroom', 'Bathroom', 'SquareFeet',
                    'Description', 'Pictures']
    column_labels = dict(Location="Street Address", City='City', State='State',
                         Zip='Zip Code', Price='Price',
                         Bedroom='Bedroom', Bathroom='Bathroom',
                         SquareFeet='Square Feet',
                         Description='Description', Pictures='Picture')

    form_overrides = dict(Pictures=ImageUploadField)
    form_args = {
        'Pictures': {
            'label': 'File',
            'base_path': base_path,
            'allow_overwrite': True
        }
    }


@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/listings')
def listings():
    db = MySQLdb.connect(host="localhost", user="root", password="root", db="realestate")
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM listings ', )
    loc=cur.fetchall()
    return render_template('listings.html', loc=loc)


@app.route('/listing/<int:pageNumber>')
def listingsOther(pageNumber):
    db = MySQLdb.connect(host="localhost", user="root", password="root", db="realestate")
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    pageNum=pageNumber
    cur.execute('SELECT * FROM listings ', )
    locInfo=cur.fetchall()
    return render_template('altListings.html')


@app.route('/listings/<int:propID>')
def propertyPage(propID):
    db = MySQLdb.connect(host="localhost", user="root", password="root", db="realestate")
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    selection=''
    cur.execute('SELECT * FROM listings Where PropertyID='+str(propID))
    loc=cur.fetchall()
    #return a view of the detailed property listing
    return render_template('detailedListing.html',loc=loc)


# db.create_all()


# Creating ModelView for each table for use with Flask-Admin
admin.add_view(clientModelView(Clients, db.session))
admin.add_view(messageModelView(Messages, db.session))
admin.add_view(listingsModelView(Listings, db.session))
admin.add_view(aboutMeModelView(AboutMe, db.session))


if __name__ == '__main__':

    # Should be able to access admin from localhost/admin in url
    app.run(debug=True)

    # Use only first time to create otherwise comment out!
    # If not you may have to use cmd prompt to make db instead.
    # db.create_all()
