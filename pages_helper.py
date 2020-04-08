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

#this function returns a way for me to go through the json file in python
def apiInfoHelper(apiLink,id):
    api_response = requests.get(apiLink.format(id)).text
    return (json.loads(api_response))

#returning a nice placement number instead of just a number
def placeHelper(place):
    if place ==1:
        return '1st'
    elif place==2:
        return '2nd'
    elif place ==3:
        return '3rd'
    else:
        return (str(place)+'th')

#This function returns the match info to the user
def gameInfoHelper_callApi(last_match_id, id , puuid):
    #Getting information from the game the played through the api
    apicall_game_info = apiInfoHelper('https://americas.api.riotgames.com/tft/match/v1/matches/{}?api_key=RGAPI-5084794a-2f12-467d-9284-d78f9687b09c',last_match_id)

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

    #I got my placements in the thing.
    user_placement = placeHelper(user_game_info['placement'])
    user_gold_remaining = user_game_info['gold_left']

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
    return ( user_placement,traits_list,unit_info_list,item_num_list,last_match_id,user_gold_remaining )

#This function returns the match info to the user
def gameInfoHelper_giveApi(summoner_name, puuid,apicall_game_info):
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

    #I got my placements in the thing.
    user_placement = placeHelper(user_game_info['placement'])
    user_gold_remaining = user_game_info['gold_left']

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
    return ( user_placement,traits_list,unit_info_list,item_num_list,summoner_name, user_gold_remaining )

#function that gets returns identification information about the user
def getUserInfo(username):
    #Getting user info through the riot api
    apicall_username_info = apiInfoHelper('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key=RGAPI-5084794a-2f12-467d-9284-d78f9687b09c',username)
    #if there is one thing we have an error and a  one length tuple we return as an error
    if len(apicall_username_info) == 1:
        return (1,)
    #otherwise we return all the different ways to id a user as a tuple of length 4
    else:
        summoner_name = apicall_username_info['name']
        id = apicall_username_info['id']
        account_id = apicall_username_info['accountId']
        puuid = apicall_username_info['puuid']
        return (summoner_name,id,account_id,puuid)
