from flask import Flask, request, abort, redirect
from utils.discord import create_dm, send_dm, send_webhook, get_code, get_user_data, refresh_token
from dotenv import load_dotenv
import os
import pymongo
import datetime

load_dotenv()
app = Flask(__name__)
app.mongo = pymongo.MongoClient(os.environ['MONGO_URL'])
app.db = app.mongo.tgk_database
app.auth = app.db.auth
app.votes = app.db.Votes

@app.route('/')
def index():
    return "Unauthorized", 401

@app.route('/api/vote', methods=['POST'])
def vote():
    if request.method != 'POST' or request.content_type != 'application/json' or request.headers['Authorization'] != os.environ['VOTE_PASSWORD']:
        return "Unauthorized", 401
    
    user_data = app.votes.find_one({'_id': int(request.json['user'])})
    if user_data is None:
        user_data = {'_id': int(request.json['user']),'dm_id': None, 'votes': 0,'streak': 0,'last_vote': datetime.datetime.now(),'reminded': False}
        dm_id = create_dm(user_data['_id'])
        user_data['dm_id'] = int(dm_id)
        app.votes.insert_one(user_data)
    
    user_data['votes'] += 1
    if (datetime.datetime.now() - user_data['last_vote']).total_seconds() > 108000:
        user_data['streak'] = 0
    else:
        user_data['streak'] += 1
    
    user_data['last_vote'] = datetime.datetime.now()
    user_data['reminded'] = False

    app.votes.update_one({'_id': int(request.json['user'])}, {'$set': user_data})
    if user_data['dm_id'] is None:
        dm_id = create_dm(user_data['_id'])
        user_data['dm_id'] = int(dm_id)
        app.votes.update_one({'_id': int(request.json['user'])}, {'$set': user_data})
    send_dm(dm_id=user_data['dm_id'], total_votes=user_data['votes'], streak=user_data['streak'])
    send_webhook(user_data['_id'], user_data['votes'], user_data['streak'])
    return "OK", 200

@app.route('/api/linked-role/auth')
def linked_role_auth():
    
    #check if code argument is present
    if request.args.get('code') is None:
        return redirect('https://discord.com/api/oauth2/authorize?client_id=816699167824281621&redirect_uri=https%3A%2F%2Ftgk-api.vercel.app%2Fapi%2Flinked-role%2Fauth&response_type=code&scope=identify%20role_connections.write')
    
    user_token = get_code(request.args.get('code'))

    user_data = get_user_data(user_token['access_token'])

    data = app.auth.find_one({'_id': int(user_data['id'])})
    if data is None:
        data = {
            '_id': int(user_data['id']),
            'access_token': user_token['access_token'],
            'refresh_token': user_token['refresh_token'],
            'expires_in': user_token['expires_in'],
            'expires_at': datetime.datetime.now() + datetime.timedelta(seconds=user_token['expires_in']),
            'username': user_data['username'],
            'discriminator': user_data['discriminator'],            
        }
        app.auth.insert_one(data)
    else:
        data['access_token'] = user_token['access_token']
        data['refresh_token'] = user_token['refresh_token']
        data['expires_in'] = user_token['expires_in']
        data['expires_at'] = datetime.datetime.now() + datetime.timedelta(seconds=user_token['expires_in'])
        data['username'] = user_data['username']
        data['discriminator'] = user_data['discriminator']
        app.auth.update_one({'_id': int(user_data['id'])}, {'$set': data})
    
    return redirect('https://discord.gg/yEPYYDZ3dD')