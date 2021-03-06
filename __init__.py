from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY='f8e9f4#Ft447F1f48F4T$f556w5gtK(*ty%Er95$ERf89w_',
     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join('C:\\Users\\levih\\Desktop\\flaskStuff\\teamfight_tactics_project', 'tft.db')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#I am probably going to make a function that returns the color we are going to border our unit with here that way I just call the function rather than do 5 ifs
def border_color(unit_rarity):
    #dictionary with all the unit rarity borders I could use
    rarity_border = {
        0:"border: 2px solid rgb(148, 145, 144)",
        1:"border: 2px solid rgb(41, 170, 33)",
        2:"border: 2px solid rgb(0, 166, 247)",
        3:"border: 2px solid rgb(206, 0, 255)",
        4:"border: 2px solid rgb(255, 188, 0)",
    }
    #returning the border css for the rarity this unit is. If not found we return nothing
    return rarity_border.get(unit_rarity,"")

#function that gives us what the color associated with the background of the trait
def trait_color(trait):
    num_tiers = trait[3]
    my_tier = trait[2]
    #this color is gold and will occur if they are both the max value
    if my_tier == num_tiers:
        return "background-color:gold;"
    #This is going to be the silver tier
    elif my_tier == (num_tiers -1):
        return "background-color:#7b9694"
    #We are at the bottom tier
    elif my_tier == 0:
        return "background-color:rgb(30,34,41)"
    #we are at the bronze tier :(
    else:
        return "background-color:rgb(142, 97, 68)"

#function that will give us what the color of the place and the stuff other stuff idk
def place_color(place):
    #first place
    if place == '1st':
        return "gold;"
    #This is going to be the silver tier
    elif place == '2nd':
        return "#7b9694;"
    #We are at the bronze tier :(
    elif place == '3rd':
        return "rgb(142, 97, 68);"
    #we are at the bottom  tier :(
    else:
        return "black;"

#I am bringing in the lower function to make strings lowercase to the jinja template engine
app.jinja_env.globals.update(lower=str.lower)
app.jinja_env.globals.update(trait_color=trait_color)
app.jinja_env.globals.update(border_color=border_color)
app.jinja_env.globals.update(place_color=place_color)
app.jinja_env.globals.update(zip=zip)
app.jinja_env.globals.update(str=str)
app.jinja_env.globals.update(len=len)

from . import pages, models
app.register_blueprint(pages.bp)
