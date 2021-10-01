import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
import json
import service

userList = []
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/events', app)
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

fileData = eval(service.GetUsersFromFile())
if(len(fileData) == 0):
    service.PopulateUserlist(client, userList)
else:
    userList = fileData

@slack_events_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    text = event.get('text')
    if "Pull request opened by" in text:
        assignees = service.PRAssignedToUsers(client, userList)
        client.chat_postMessage(
            channel="#pr", text=f"<@{assignees[0]}> and <@{assignees[1]}> should review")
    elif "!github" in text.lower():
        github = text.replace("!github ", "")
        print(github)
        
if __name__ == "__main__":
    app.run(debug=True)
