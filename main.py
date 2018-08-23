import os

from flask import Flask, request, g, session, redirect, url_for
from flask_github import GitHub

app = Flask(__name__)
app.config['GITHUB_CLIENT_ID'] = os.getenv("GITHUB_CLIENT_ID")
app.config['GITHUB_CLIENT_SECRET'] = os.getenv("GITHUB_CLIENT_SECRET")

github = GitHub(app)


@github.access_token_getter
def token_getter():
    user = g.user
    if user is not None:
        return user.github_access_token

@app.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
    next_url = request.args.get('next') or url_for('logged')
    if oauth_token is None:
        flash("Authorization failed.")
        return redirect(next_url)

    user = User.query.filter_by(github_access_token=oauth_token).first()
    if user is None:
        user = User(oauth_token)
        db_session.add(user)

    user.github_access_token = oauth_token
    db_session.commit()
    return redirect(next_url)

@app.route("/")
def index():
    return github.authorize()

@app.route("/logged")
def logged():
    return "You are on GitHub"


if __name__ == "__main__":
    app.run()