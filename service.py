import random
from sys import getdefaultencoding
from jwt import (
    JWT,
    jwk_from_pem
)
from jwt.utils import get_int_from_datetime
from datetime import datetime, timedelta, timezone
import os
import requests
import json
import shutil


def SaveUsersToFile(userList):
    AuthorizeGithubInstallation()
    token = os.environ.get('INSTALL_TOKEN')
    response = requests.get("https://api.github.com/orgs/aau-giraf/teams/2021E/members", headers={
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json'
    }).json()
    

    shutil.copy('developers.json', 'dev_stack.json')
    userList = json.loads(open('dev_stack.json', 'r').read())
    return userList


def PRAssignedToUsers(userList, PROwnerName):
    if(len(userList) > 1):
        user0, user0ID = GetDeveloper(userList, PROwnerName)
        user1, user1ID = GetDeveloper(userList, PROwnerName)
    elif(len(userList) == 1):
        if (list(userList.values())[0] == PROwnerName):
            userList = SaveUsersToFile(userList)
            user0, user0ID = GetDeveloper(userList, PROwnerName)
            user1, user1ID = GetDeveloper(userList, PROwnerName)
        else: 
            user0, user0ID = GetDeveloper(userList, PROwnerName)
            userList = SaveUsersToFile(userList)
            userList.pop(user0ID)
            user1, user1ID = GetDeveloper(userList, PROwnerName)
    else:
        userList = SaveUsersToFile(userList)
        user0, user0ID = GetDeveloper(userList, PROwnerName)
        user1, user1ID = GetDeveloper(userList, PROwnerName)

    with open('dev_stack.json', 'w') as file:
        file.write(json.dumps(userList))

    return [user0, user1]


def GetUsersFromFile(userList):
    with open('dev_stack.json', 'r') as outfile:
        text = outfile.read()
        if (text == ''):
            outfile.close()
            return SaveUsersToFile(userList)
        else:
            return json.loads(text)


def GetGithubInstallations():
    with open('Github_private_key.pem', 'rb') as pem:
        privateKey = jwk_from_pem(pem.read())

    ghToken = JWT().encode({
        'iat': get_int_from_datetime(datetime.now(timezone.utc)),
        'exp': get_int_from_datetime(datetime.now(timezone.utc) + timedelta(minutes=5)),
        'iss': os.environ.get('GIT_APP_ID')
    }, privateKey, alg='RS256')
    os.environ['JWT'] = ghToken

    response = requests.get("https://api.github.com/app/installations", headers={
        'Authorization': f'Bearer {ghToken}',
        'Accept': 'application/vnd.github.v3+json'
    }).json()

    return response


def AuthorizeGithubInstallation():
    JWT = os.environ.get('JWT')
    installations = GetGithubInstallations()
    response = requests.post(installations[0].get('access_tokens_url'), headers={
        'Authorization': f'Bearer {JWT}',
        'Accept': 'application/vnd.github.v3+json'
    }).json()
    if (response.get('token') is not None):
        os.environ['INSTALL_TOKEN'] = response.get('token')


def AssignReviewers(pullRequest, userList):
    PRUrl = pullRequest.get('url')
    assignees = PRAssignedToUsers(userList, pullRequest.get('user').get('login'))
    AuthorizeGithubInstallation()
    response = PostReviewers(PRUrl, assignees)
    print(response)


def PostReviewers(PRUrl, assignees):
    INSTALL_TOKEN = os.environ.get('INSTALL_TOKEN')
    json = {
        'reviewers': assignees
    }
    return requests.post(f'{PRUrl}/requested_reviewers', headers={
        'Authorization': f'Bearer {INSTALL_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }, json=json)

def GetDeveloper(userList, name):
    DevID,DevName = random.choice(list(userList.items()))
    if (DevName == name):
        return GetDeveloper(userList, DevName)
    else:
        userList.pop(DevID)
        return DevName, DevID
        