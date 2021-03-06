import os

from flask import Flask, request, g, session, redirect, url_for, flash
from flask_github import GitHub

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRETKEY")
app.config['GITHUB_CLIENT_ID'] = os.getenv("GITHUB_CLIENT_ID")
app.config['GITHUB_CLIENT_SECRET'] = os.getenv("GITHUB_CLIENT_SECRET")

github = GitHub(app)


@github.access_token_getter
def token_getter():
    return session['token']

@app.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
    next_url = request.args.get('next') or url_for('logged')
    if oauth_token is None:
        return redirect(next_url)

    session['token'] = oauth_token

    return redirect(next_url)

@app.route("/")
def index():
    return github.authorize(scope="gist")

@app.route("/logged")
def logged():
    return "Click <a href=\"/delete\">here</a> to delete all your gists."

@app.route("/delete")
def delete():
    gists = github.get("gists", all_pages=True)

    count = 0
    for gist in gists:
        resource = "gists/{}".format(gist['id'])
        github.delete(resource)
        count += 1
    
    return "Deleted {} gists.".format(count)


if __name__ == "__main__":
    app.run()