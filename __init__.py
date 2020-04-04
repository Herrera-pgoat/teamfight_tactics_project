from flask import Flask, render_template

app = Flask(__name__)

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

#I am bringing in the lower function to make strings lowercase to the jinja template engine
app.jinja_env.globals.update(lower=str.lower)
app.jinja_env.globals.update(border_color=border_color)


from . import pages
app.register_blueprint(pages.bp)
