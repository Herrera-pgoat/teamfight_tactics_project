from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
#I need to import this stuff for the password checking and hashing
from werkzeug.security import check_password_hash, generate_password_hash
#doing these imports to get data from the api
import json
import requests

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
    #I am getting the url for the json file that has the id for the username
    apicall_username = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key=RGAPI-38025a0a-63c7-4d01-82c7-fe9b65496279'.format(username)
    username_response  = requests.get(apicall_username).text
    apicall_username_info = json.loads(username_response)
    #getting all the information from the json file I have loaded which are different ways to id the user
    summoner_name = apicall_username_info['name']
    id = apicall_username_info['id']
    account_id = apicall_username_info['accountId']
    puuid = apicall_username_info['puuid']

    #okay I have different ways to id the user now I want to get my most recent tft game and put my placing in the thing
    #first get api call to all the matches and using the puuid to get list of matches
    apicall_matches = 'https://americas.api.riotgames.com/tft/match/v1/matches/by-puuid/{}/ids?count=20&api_key=RGAPI-38025a0a-63c7-4d01-82c7-fe9b65496279'.format(puuid)
    matches_response = requests.get(apicall_matches).text
    apicall_matches_info = json.loads(matches_response)
    #getting the id of the last match this user has played
    last_match_id = apicall_matches_info[0]

    #now I literally want to get the api call for the match that was played
    apicall_game = 'https://americas.api.riotgames.com/tft/match/v1/matches/{}?api_key=RGAPI-38025a0a-63c7-4d01-82c7-fe9b65496279'.format(last_match_id)
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
        #creating a tuple with the information about the trait like how many units the tier I was in the number of tiers
        trait_info = (trait['name'],trait['num_units'],trait['tier_current'],trait['tier_total'])
        traits_list.append(trait_info)
    #traits_list now has all the relevent information

    unit_info_list = list()
    for unit in user_game_info['units']:
        #I am getting every item that the unit has [:] gets me everythign in the list even if it is empty!
        unit_info_items = (unit['items'][:])
        #I am adding the character name. #unit_info_items unpacks the tuple and puts its items here
        unit_info = (unit['character_id'],*unit_info_items,unit['rarity'],unit['tier'])
        unit_info_list.append(unit_info)
    #now unit_info_list has all relevent information about the units I had in this game 
    return 'Hello {}'.format(unit_info_list)

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
