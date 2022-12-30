from flask import Flask, request, abort
from utils.discord import create_dm, send_dm, send_webhook
from dotenv import load_dotenv
import os
import pymongo
import datetime

load_dotenv()
app = Flask(__name__)
app.mongo = pymongo.MongoClient(os.environ['MONGO_URL'])
app.db = app.mongo.tgk_database
app.outh = app.db.outh
app.votes = app.db.Votes

@app.route('/')
def index():
    abort(404)

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