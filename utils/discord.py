import requests
import json
import os
import datetime
import dotenv

dotenv.load_dotenv()
headers = {
    'Authorization': f"Bot {os.environ['DISCORD_TOKEN']}",
    'Content-Type': 'application/json'
}

webhook_headers = {
    'Content-Type': 'application/json'
}

base_url = 'https://discord.com/api/v10'

def create_dm(user_id):
    data = {
        'recipient_id': user_id
    }
    r = requests.post(f'{base_url}/users/@me/channels', headers=headers, data=json.dumps(data))
    return r.json()['id']

def send_dm(dm_id:int, total_votes:int, streak:int):
    embed = {
        'type': 'rich',
        'title': '<a:tgk_redcrown:1005473874693079071> Thank you for voting!',
        'description': f"You have voted for [The Gambler's Kingdom](https://discord.gg/tgk) and have gotten the `࿔･ﾟ♡ TGK Voter's ♡ ࿔･ﾟ` role for 12 hours!" +"\nYou will be reminded to vote again in 12 hours (<t:" + str(int(datetime.datetime.timestamp(datetime.datetime.now() + datetime.timedelta(hours=12)))) + ":R>).",
        'color': 8257405,
        'url': 'https://discord.gg/yEPYYDZ3dD',
        'footer':{
            'text': "The Gambler's Kingdom - We appreciate your kind support!💖", 'icon_url': 'https://cdn.discordapp.com/icons/785839283847954433/a_23007c59f65faade4c973506d9e66224.gif?size=1024',
        },
        'fields': [
            {'name': "Total Votes: ", 'value': f"{total_votes}", 'inline': True},
            {'name': "Streak: ", 'value': f"{streak}", 'inline': True}
        ]
    }
    payload = {'embeds': [embed]}

    r = requests.post(f'{base_url}/channels/{dm_id}/messages', headers=headers, data=json.dumps(payload))
    return r.status_code

def send_webhook(user_id, total_votes, streak):
    user = requests.get(f'{base_url}/users/{user_id}', headers=headers).json()
    user_name = user['username'] + '#' + user['discriminator']
    embed = {
        'type': 'rich',
        'title': f'<a:tgk_redcrown:1005473874693079071> Thank you for voting! {user_name}',
        "description": f"You have voted for [The Gambler's Kingdom](https://discord.gg/tgk) and have gotten the <@&786884615192313866> role for 12 hours!" +"\nYou will be reminded to vote again in 12 hours (<t:" + str(int(datetime.datetime.timestamp(datetime.datetime.now() + datetime.timedelta(hours=12)))) + ":R>).",
        "color": int("7dff7d", 16),
        "url": "https://discord.gg/yEPYYDZ3dD",
        "thumbnail": {
                "url": "https://cdn.discordapp.com/emojis/830519601384128523.gif?v=1"
            },
        "fields": [
            {"name": "Total Votes: ", "value": f"{total_votes}", "inline": True},
            {"name": "Streak: ", "value": f"{streak}", "inline": True}
        ],
        "footer": {"text": "The Gambler's Kingdom - We appreciate your kind support!💖", "icon_url": "https://cdn.discordapp.com/icons/785839283847954433/a_23007c59f65faade4c973506d9e66224.gif?size=1024"},
    }
    payload = {'embeds': [embed], 'username': f'OCT∆NΞ Logging', 'avatar_url': 'https://cdn.discordapp.com/avatars/816699167824281621/1bf01631b86f25cb052d64b69759e8d4.png?size=4096'}

    r = requests.post(os.environ['WEBHOOK_URL'], headers=webhook_headers, data=json.dumps(payload))
    return r.status_code