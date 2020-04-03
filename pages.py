from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
#I need to import this stuff for the password checking and hashing
from werkzeug.security import check_password_hash, generate_password_hash

#this is the blueprint for the website
#This site is going to be so small that I probably didn't need a blueprint but I wanted to have all of my views in one place
#the empty '' says that we don't want any of the views below prepended by any thing like /something then it would look like /something/about.html
bp = Blueprint('', __name__)


@bp.route('/',methods=['GET','POST'])
def mainPage():
    return render_template('homepage.html')
    #return render_template('path_from_template_folder')

@bp.route('/login',methods=['GET','POST'])
def login():
    return 'login'

@bp.route('/createAccount',methods=['GET','POST'])
def createAccount():
    return 'ca'

#The string:username says that we have an argument that is a string type and name is username and we return the suer name in the request return
@bp.route('/find/<string:username>',methods=['GET','POST'])
def findUser(username):
    return 'username {}'.format(username)

#This is a helper function that will give the findUser the argument it needs ot work
@bp.route('/find/help',methods=['GET','POST'])
def findUserHelper():
    if request.method =='POST':
        name = request.form['username']
        #I send the username they typed as the name
        return redirect(url_for('.findUser',username=name))
    #if they just typed this /find/help in they would get cofeebean which I think is me :D
    else:
        return redirect(url_for('.findUser',username='cofeebean'))
