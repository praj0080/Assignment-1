from flask import Flask, redirect, url_for, session, render_template, request
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from datetime import datetime
import os
import logging

# ✅ Load environment variables from .env
load_dotenv()

app = Flask(_name_)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# ✅ Recommended session cookie settings for production (required for Azure HTTPS)
app.config.update(
    SESSION_COOKIE_NAME='flask_session',
    SESSION_COOKIE_DOMAIN=None,
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=True
)

# ✅ Configure structured logging
logging.basicConfig(level=logging.INFO)

# ✅ OAuth setup for Auth0
oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id=os.getenv('AUTH0_CLIENT_ID'),
    client_secret=os.getenv('AUTH0_CLIENT_SECRET'),
    client_kwargs={
        'scope': 'openid profile email',
    },
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

# ✅ Routes

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login')
def login():
    app.logger.info(f"LOGIN_ATTEMPT: IP={request.remote_addr}, timestamp={datetime.utcnow().isoformat()}")
    return auth0.authorize_redirect(redirect_uri=os.getenv("AUTH0_CALLBACK_URL"))


@app.route('/callback')
def callback():
    token = auth0.authorize_access_token()
    userinfo = token.get('userinfo')
    session['user'] = userinfo

    # ✅ Log successful login
    app.logger.info(
        f"LOGIN_SUCCESS: user_id={userinfo.get('sub')}, email={userinfo.get('email')}, timestamp={datetime.utcnow().isoformat()}"
    )

    return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', user=session['user'])
    return redirect('/login')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(
        f'https://{os.getenv("AUTH0_DOMAIN")}/v2/logout?returnTo={os.getenv("APP_BASE_URL")}&client_id={os.getenv("AUTH0_CLIENT_ID")}'
    )


@app.route('/protected')
def protected():
    if 'user' not in session:
        app.logger.warning(
            f"UNAUTHORIZED_ACCESS: IP={request.remote_addr}, route=/protected, timestamp={datetime.utcnow().isoformat()}"
        )
        return redirect('/login')

    app.logger.info(
        f"PROTECTED_ACCESS: user_id={session['user'].get('sub')}, email={session['user'].get('email')}, timestamp={datetime.utcnow().isoformat()}"
    )
    return "This is a protected page for logged-in users only."


@app.errorhandler(401)
def unauthorized_error(e):
    app.logger.warning(
        f"UNAUTHORIZED_ERROR: IP={request.remote_addr}, path={request.path}, timestamp={datetime.utcnow().isoformat()}"
    )
    return "Unauthorized", 401


if _name_ == '_main_':
    app.run(debug=False)