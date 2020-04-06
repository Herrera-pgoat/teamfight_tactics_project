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
            #if we are here then the user is 'logged in'
            session['username'] = username
        else:
            flash("The password does not match the usernames")
            return redirect(url_for('.login'))

    return render_template('homepage.html')
    #return render_template('path_from_template_folder')

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
        #if we are here then we came from the create account

        #HERE I WILL CHECK IF THE USER ENTERED OKAY INFORMATION TO CREATE AN ACCOUNT AND IF THEY did I will create an account and go to login.path_from_template_folder
        #otherwise if they entered bad info we will go to create account again :(
        flash('You have successfully created an account!')

    return render_template('login.html')

@bp.route('/createAccount',methods=['GET','POST'])
def createAccount():
    #sometimes we come here from the login function
    return render_template('createAccount.html')

@bp.route('/about',methods=['GET','POST'])
def about():
    return render_template('about.html')

#helper funciton that gets me the unit ifnrmation
def unit_info_helper(user_game_info):
    unit_info_list = list()
    item_num_list = list()
    for unit in user_game_info['units']:
        #I am getting every item that the unit has [:] gets me everythign in the list even if it is empty!
        unit_info_items = (unit['items'][:])

        #basically if the item is 1 charcter we add a zero to the front of it
        item_list_unit = list()
        for item in unit_info_items:
            if((item) > 9):
                item_list_unit.append(item)
            else:
                item_list_unit.append('0'+str(item))
        item_num_list.append(item_list_unit)
        #I want to give the items the name they deserve
        #have to give this new values to delete the old ones incase this new unit doesn't have any new items
        unit_info_items_named = list()
        #if there are items I will try to rename them otherwise I will not
        if( len(unit_info_items) > 0):
            #Getting the path of the local json file
            THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
            my_file = os.path.join(THIS_FOLDER, 'tft_info/items.json')
            with open(my_file, 'r') as myfile:
                data=myfile.read()
            #THis is the json file with all the item names
            item_num_to_name = json.loads(data)
            #going through each item the champion has.
            for item_num in unit_info_items:
                for item in item_num_to_name:
                    if item_num == item['id']:
                        unit_info_items_named.append(item['name'])
                    else:
                        #nothing
                        print('hi')
        #I am adding the character name. #unit_info_items unpacks the tuple and puts its items here
        unit_info = (unit['character_id'],*unit_info_items_named,unit['rarity'],unit['tier'])
        unit_info_list.append(unit_info)
    return (unit_info_list,item_num_list)
    #now unit_info_list has all relevent information about the units I had in this game

#The string:username says that we have an argument that is a string type and name is username and we return the suer name in the request return
@bp.route('/find/<string:username>',methods=['GET','POST'])
def findUser(username):
    #I should try to do soemthing if there is an error

    #I am getting the url for the json file that has the id for the username
    apicall_username = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key=RGAPI-fc307e03-ef97-4626-956b-a19957386943'.format(username)
    username_response  = requests.get(apicall_username).text
    apicall_username_info = json.loads(username_response)
    #getting all the information from the json file I have loaded which are different ways to id the user

    #if the user name is not in the rito databse we give them an error
    if len(apicall_username_info) == 1:
        flash('No one has the summoner name {}'.format(username))
        return redirect (url_for('.mainPage') )

    summoner_name = apicall_username_info['name']
    id = apicall_username_info['id']
    account_id = apicall_username_info['accountId']
    puuid = apicall_username_info['puuid']

    #okay I have different ways to id the user now I want to get my most recent tft game and put my placing in the thing
    #first get api call to all the matches and using the puuid to get list of matches
    apicall_matches = 'https://americas.api.riotgames.com/tft/match/v1/matches/by-puuid/{}/ids?count=20&api_key=RGAPI-fc307e03-ef97-4626-956b-a19957386943'.format(puuid)
    matches_response = requests.get(apicall_matches).text
    apicall_matches_info = json.loads(matches_response)

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
        #now I literally want to get the api call for the match that was played
        apicall_game = 'https://americas.api.riotgames.com/tft/match/v1/matches/{}?api_key=RGAPI-fc307e03-ef97-4626-956b-a19957386943'.format(last_match_id)
        game_response = requests.get(apicall_game).text
        apicall_game_info = json.loads(game_response)

        #now we are going to do some thing
        participant_number = 0
        number = 0
        for id in apicall_game_info['metadata']['participants']:
            if id == puuid:
                participant_number = number
                break
            number +=1

        #now with participant_number I have the number that the user is in the list of json thing
        user_game_info = apicall_game_info['info']['participants'][participant_number]

        #I got my placements in the thing
        user_placement = user_game_info['placement']

        #I am going to get the traits I had
        traits_list = list()
        for trait in user_game_info['traits']:
            if(trait['name'] == 'TemplateTrait'):
                continue
            #creating a tuple with the information about the trait like how many units the tier I was in the number of tiers
            trait_info = (trait['name'],trait['num_units'],trait['tier_current'],trait['tier_total'])
            traits_list.append(trait_info)
        #traits_list now has all the relevent information

        #calling a function that gets all the informatio about units
        unit_info_list_and_items = unit_info_helper(user_game_info)
        unit_info_list = unit_info_list_and_items[0]
        item_num_list = unit_info_list_and_items[1]
        #now unit_info_list has all relevent information about the units I had in this game

        match_history_list.append( (user_placement,traits_list,unit_info_list,item_num_list) )
#,place=user_placement,traits=traits_list,team=unit_info_list,item_list=item_num_list
    return render_template('match_history.html',match_history=match_history_list)


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
