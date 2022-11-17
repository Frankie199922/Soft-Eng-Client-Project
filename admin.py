import ast
import os.path as op
import re
import MySQLdb.cursors
import pymysql
from flask import (Flask, abort, redirect, render_template, request, session)
from flask_admin import Admin
from flask_admin._backwards import Markup
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import PrimaryKeyConstraint
from werkzeug.exceptions import abort
from imageupload import customImageUploadField

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
    __tablename__ = 'Clients'
    ClientID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(25), unique=False, nullable=True)
    LastName = db.Column(db.String(25), unique=False, nullable=True)
    PhoneNumber = db.Column(db.String(12), unique=True, nullable=True)
    Email = db.Column(db.String(320), unique=True, nullable=True)


class Messages(db.Model):
    __tablename__ = 'Messages'
    MessageID = db.Column(db.Integer, primary_key=True)
    Comment = db.Column(db.String(1000), unique=False, nullable=False)

class ClientMessage(db.Model):
    __table_args__ = (
        PrimaryKeyConstraint('Client_ID', 'Message_ID'),
    )
    Client_ID = db.Column(db.Integer, db.ForeignKey('Clients.ClientID'))
    Message_ID = db.Column(db.Integer, db.ForeignKey('Messages.MessageID'))
    Message_Date = db.Column(db.DATE)

class Listings(db.Model):
    __tablename__ = 'Listings'
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

class ClientMessage(ModelView) :
   # ModelView Functionality
   def is_accessible(self):
       if "logged_in" in session:
           return True
       else:
           abort(403)
          
class messageModelView(ModelView) :
    # ModelView Functionality
    def is_accessible(self):
        if "logged_in" in session:
            return True
        else:
            abort(403)
    
    can_edit = False
    can_create = False
    can_delete = True
    page_size = 20

    form_columns = ['Comment']
    column_labels = dict(Comment='Comment')


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

    def _list_thumbnail(view, model):

        if not model.image:
            return ''

        return Markup("<br />".join([(image) for image in ast.literal_eval(model.image)]))
    

    form_extra_fields = {'Pictures' : customImageUploadField('Pictures',
        base_path = op.join(op.dirname(__file__), 'static/pictures'),
        url_relative_path="/static/pictures/",
        thumbnail_size=(1000, 800, 1))
        }


    def create_model(self, form):
        return super().create_model(form)


@app.route('/',methods=["GET","POST"])
def homepage():
    db = MySQLdb.connect(host="localhost", user="root", password="root", db="realestate")
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM listings ', )
    loc = cur.fetchone()
    loc2= cur.fetchone()
    loc3= cur.fetchone()



    return render_template('FrontEndWebsite.html',loc=loc,loc2=loc2,loc3=loc3)


@app.route('/listings',methods=["GET","POST"])
def listings():
    db = MySQLdb.connect(host="localhost", user="root", password="root", db="realestate")
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM listings ', )
    loc=cur.fetchall()
    if request.method=="POST":
        zpc=request.form.get("zp")
        l="/listings/"
        newL=l+zpc
        return redirect(newL)

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
    loc=cur.fetchone()
    #return a view of the detailed property listing
    return render_template('detailedListing.html',loc=loc)


@app.route('/#contact', methods=['POST'])
def contactMe():
    comment = request.form.get('Comment')
    if comment != '':
        m = Messages(Comment=comment)
        db.session.add(m)
        db.session.commit()
        return redirect('/')
    else:
        return redirect('/')


# Use to create databases
# db.create_all()


# If db.create_all() does not work use this!!
#with app.app_context():
    #db.create_all()


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
