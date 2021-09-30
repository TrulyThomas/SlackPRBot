import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
import json
import random

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/events', app)
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

def GetUsersFromFile():
    with open('developers.txt', 'r') as outfile:
        return outfile.read()
        
fileData = eval(GetUsersFromFile())
if(len(fileData) == 0):
    userList = []
else:
    userList = fileData

def SaveUsersToFile():
    result = client.users_list()
    for member in result['members']:
        if(member['is_bot'] == False and member['deleted'] == False and member['real_name'] != 'Slackbot'):
            userList.append([member['id'], member['real_name']])
    
    random.shuffle(userList)

    with open('developers.txt', 'w') as outfile:
        outfile.write('[')
        for user in userList[:-1]:
            outfile.write(f"{user},")
        outfile.write(f'{userList[len(userList) - 1]}]')


def SaveCurrentUsersToFile():
    if(len(userList) == 0):
        SaveUsersToFile()
    with open('developers.txt', 'w') as outfile:
        outfile.write('[')
        for user in userList[:-1]:
            outfile.write(f"{user},")
        outfile.write(f'{userList[len(userList) - 1]}]')


def AddUser(user_id, real_name):
    data['users'].append({
        'slack_id': user_id,
        'real_name': real_name
    })


def PRAssignedToUsers():
    if(len(userList) > 2):
        user0 = userList.pop()
        user1 = userList.pop()
    elif(len(userList) == 1):
        user0 = userList.pop()
        SaveUsersToFile()
        userList.remove(user0)
        user1 = userList.pop()
        userList.append(user0)
    else:
        SaveUsersToFile()
    SaveCurrentUsersToFile()
    return [user0, user1]

if(len(userList) == 0):
    SaveUsersToFile()

@slack_events_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    text = event.get('text')
    if "Pull request opened by" in text:
        assignees = PRAssignedToUsers()
        client.chat_postMessage(
            channel="#pr", text=f"<@{assignees[0][0]}> and <@{assignees[1][0]}> should review")

if __name__ == "__main__":
    app.run(debug=True)
