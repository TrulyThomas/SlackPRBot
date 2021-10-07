from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request
import service

userList = []
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
app = Flask(__name__)

service.AuthorizeGithubInstallation()
userList = service.GetUsersFromFile(userList)

@app.route('/github/events', methods=['POST'])
def GithubEvent():
    action = request.json.get('action')
    if (action == 'opened' or action == 'reopened'):
        service.AssignReviewers(request.json.get('pull_request'), userList)
    return "return"

if __name__ == "__main__":
    app.run(debug=True)