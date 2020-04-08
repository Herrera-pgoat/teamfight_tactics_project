from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
#I need to import this stuff for the password checking and hashing
from werkzeug.security import check_password_hash, generate_password_hash
#doing these imports to get data from the api
import json
import requests
import os
#importing the models I needs
from . import db
from .models import User
#importing a lot of helper functions from another file
from .pages_helper import unit_info_helper,apiInfoHelper,gameInfoHelper_callApi,gameInfoHelper_giveApi,getUserInfo

#this is the blueprint for the website
#This site is going to be so small that I probably didn't need a blueprint but I wanted to have all of my views in one place
#the empty '' says that we don't want any of the views below prepended by any thing like /something then it would look like /something/about.html
bp = Blueprint('', __name__)


@bp.route('/',methods=['GET','POST'])
def mainPage():
    #We get a post when we try to login
    if( request.method =="POST"):
        #We are in a post method which means they tried to log in
        #I need to check for the user name they put in and if the password they put in matches the password with that username
        username = request.form['usernameForm']
        password = request.form['passwordForm']

        user = User.query.filter_by(username=username).first()
        if(user is None):
            #That username is not in the db so they can't log in
            flash("That username is not in the database. Try creating an account!")
            return redirect(url_for('.login'))
        elif (check_password_hash(user.password_hash,password)):
            #The username is in the database and the password matches
            session.clear()
            print('someone has logged in ')
            #if we are here then the user is 'logged in'
            session['username'] = username
            return redirect(url_for('.mainPage') )
        else:
            flash("The password does not match the usernames")
            return redirect(url_for('.login'))

    #Here if they are logged in I will get the information of the person they are following
    if g.user is None or g.user.following_user is None:
        return render_template('homepage.html')
    else:
        #getting tuple of user information
        user_info = getUserInfo(g.user.following_user)
        #if the tuple is of length one theen the user name does not exist
        if (len(user_info) ==1):
            flash('No one has the summoner name {}'.format(g.user.following_user))
            return render_template('homepage.html',match_history = list())

        #otherwise the username does exist and we are assigning all the variables here
        summoner_name,id,account_id,puuid = user_info

        #Getting the list of matches they have played through the api call here
        apicall_matches_info = apiInfoHelper('https://americas.api.riotgames.com/tft/match/v1/matches/by-puuid/{}/ids?count=20&api_key=RGAPI-5084794a-2f12-467d-9284-d78f9687b09c',puuid)

        #if they have no tft games played we give them an error
        if len(apicall_matches_info) == 0:
            flash('{} has no tft games'.format(summoner_name))
            return render_template('homepage.html',match_history = list())

        #I am going to return the last two games they have played
        match_history_list = list()
        for i in range(0,3):
            if( (1+i) > len(apicall_matches_info ) ):
                break

            #getting the id of the last match this user has played
            last_match_id = apicall_matches_info[i]

            #calling a function that gets me all the game info
            game_info = gameInfoHelper_callApi(last_match_id, id,puuid)
            match_history_list.append( game_info  )

        return render_template('homepage.html',match_history =match_history_list)


@bp.route('/login',methods=['GET','POST'])
def login():
    if(request.method =='POST'):
        #Getting the information they put in from the form
        username = request.form['usernameForm']
        password = request.form['passwordForm']
        passwordConfirm = request.form['passwordConfirmForm']
        #if the user did not enter the same password twice for some reason
        if(password == passwordConfirm):
            #Here we should check whether the user exists already or not
            user = User.query.filter_by(username=username).first()
            if(user is None):
                #If we enter this then no user of that name exists so we put this user in the tableTypes
                #This is correctly adding the user to the user table with a hashed password. sha256 and salt
                newUser = User(username= username,password_hash= generate_password_hash(password))
                db.session.add(newUser)
                db.session.commit()
            else:
                flash('That username already exists! Pick a new one!')
                return redirect(url_for('.createAccount'))
        else:
            #Flash is stores the message we pass as argument and sends what it stores
            #to the register.html and in there I will put out a message that says what is in the flash !
            flash('Passwords do not match')
            return redirect(url_for('.createAccount'))
            #If we enter this one we should send an error and still go to register.html
        #We are fine and created an account
        flash('You have successfully created an account!')

    return render_template('login.html')

#This is the logout function that deals with that route /logout
@bp.route('/logout')
def logout():
    #clears the session so we are no longer logged in :)
    session.clear()
    return redirect(url_for('.mainPage'))

#This is the create account route handler. When we see /createAccount we go in here and put this out
@bp.route('/createAccount',methods=['GET','POST'])
def createAccount():
    return render_template('createAccount.html')

#this is where we deal with the about route request
@bp.route('/about',methods=['GET','POST'])
def about():
    return render_template('about.html')

#This is wehre we deal with userSettings route Request.
@bp.route('/userSettings',methods=['GET','POST'])
def userSettings():
    #getting the user name
    username = session.get('username')
    user = User.query.filter_by(username=username).first()
    following = user.following_user
    #Here I will check if they are trying to add a new user\
    if (request.method == 'POST'):
        new_following = request.form['summonerName']
        user.following_user = new_following
        follwing = new_following
        db.session.commit()
        return redirect(url_for('.userSettings',following=following))

    return render_template('user_settings.html',following=following)

#The string:username says that we have an argument that is a string type and name is username and we return the suer name in the request return
@bp.route('/find/<string:username>',methods=['GET','POST'])
def findUser(username):
    #getting tuple of user information
    user_info = getUserInfo(username)
    #if the tuple is of length one theen the user name does not exist
    if (len(user_info) ==1):
        flash('No one has the summoner name {}'.format(username))
        return redirect (url_for('.mainPage') )

    #otherwise the username does exist and we are assigning all the variables here
    summoner_name,id,account_id,puuid = user_info

    #Getting the list of matches they have played through the api call here
    apicall_matches_info = apiInfoHelper('https://americas.api.riotgames.com/tft/match/v1/matches/by-puuid/{}/ids?count=20&api_key=RGAPI-5084794a-2f12-467d-9284-d78f9687b09c',puuid)

    #if they have no tft games played we give them an error
    if len(apicall_matches_info) == 0:
        flash('{} has no tft games'.format(summoner_name))
        return redirect (url_for('.mainPage') )

    #I am going to return the last two games they have played
    match_history_list = list()
    for i in range(0,5):
        if( (1+i) > len(apicall_matches_info ) ):
            break

        #getting the id of the last match this user has played
        last_match_id = apicall_matches_info[i]

        #calling a function that gets me all the game info
        game_info = gameInfoHelper_callApi(last_match_id, id,puuid)
        match_history_list.append( game_info  )

    return render_template('match_history.html',summoner_name=summoner_name, match_history=match_history_list)

#i am going to be sorting by the first thing in the placement
def sortingFunctionPlacement(participant):
    return participant[0][0]

#We are giving a match history with the persepctive of the user
@bp.route('/find/<string:summoner_name>/<string:match_id>',methods=['GET','POST'])
def findMatch(summoner_name,match_id):
    #first with the summoner name I need my id stuff
    summoner_name_user,id_user,account_id_user,puuid_user= getUserInfo(summoner_name)
    #I now have all this person's id

    #Then with the match id I get the information about everyone in the match.
    #Getting information from the game the played through the api
    apicall_game_info = apiInfoHelper('https://americas.api.riotgames.com/tft/match/v1/matches/{}?api_key=RGAPI-5084794a-2f12-467d-9284-d78f9687b09c',match_id)
    summoner_names_list_match = list()
    puuid_list_match = list()
    for puuid in apicall_game_info['metadata']['participants']:
        #I am getting both of them in the order they will appear in the info about the match
        #I am going through each puuid in the match and am going to get their summoner name as well
        puuid_list_match.append(puuid)
        #I am getting the summoner name of each person in the match
        summoner_names_list_match.append( apiInfoHelper('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{}?api_key=RGAPI-5084794a-2f12-467d-9284-d78f9687b09c',puuid)['name'] )

    #now I want a list of information where it is sorted by place that contanins all the match information about this game for each person
    #getting the match info for each person by going through each person in the for loop
    participants_game_info = list()
    for (participant,summoner) in zip(apicall_game_info['info']['participants'],summoner_names_list_match):
        #getting information for this participant from the match that we want
        participants_game_info.append( gameInfoHelper_giveApi(summoner,participant['puuid'],apicall_game_info) )
    #Then I order id information for each person in the match. I sort by the placement number using python sort function for list
    #each element in this list has the summoner name of the person in the list
    participants_game_info.sort(key=sortingFunctionPlacement)
    #now we are going to return the template with the participant_game_info
    return render_template('game_info_details.html',participants_game_info=participants_game_info)

#This is a helper function that will give the findUser the argument it needs ot work
@bp.route('/find/help',methods=['GET','POST'])
def findUserHelper():
    if request.method =='POST':
        name = request.form['username']
        #I send the username they typed as the name
        return redirect(url_for('.findUser',username=name))
    #if they just typed this /find/help in they would get cofeebean which I think is me :D
    else:
        return redirect(url_for('.findUser',username='COFEEBAN'))

#Here we are loading in the logged in user before a request
@bp.before_app_request
def load_logged_in_user():
    username = session.get('username')
    if username is None:
        g.user = None
    else:
        g.user = User.query.filter_by(username=username).first()
