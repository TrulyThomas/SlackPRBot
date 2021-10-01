import random

def PopulateUserlist(client, userList):
    result = client.users_list()
    for member in result['members']:
        if(member['is_bot'] == False and member['deleted'] == False and member['real_name'] != 'Slackbot'):
            userList.append(member['id'])
    random.shuffle(userList)

def SaveUsersToFile(userList):
    with open('dev-stack.txt', 'w') as outfile:
        outfile.write('[')
        for user in userList[:-1]:
            outfile.write(f"'{user}',")
        if (len(userList) != 0):
            outfile.write(f"'{userList[len(userList) - 1]}']")
        else:
            outfile.write("]")

def PRAssignedToUsers(client, userList):
    if(len(userList) > 1):
        user0 = userList.pop()
        user1 = userList.pop()
    elif(len(userList) == 1):
        user0 = userList.pop()
        PopulateUserlist(client, userList)
        userList.remove(user0)
        user1 = userList.pop()
        userList.append(user0)
    else:
        PopulateUserlist(client, userList)
        user0 = userList.pop()
        user1 = userList.pop()

    SaveUsersToFile(userList)
    return [user0, user1]

def GetUsersFromFile():
    with open('dev-stack.txt', 'r') as outfile:
        return outfile.read()