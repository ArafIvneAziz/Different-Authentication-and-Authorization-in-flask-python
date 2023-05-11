import hashlib
import os
from urllib.parse import urlencode
from flask import Flask, render_template, request, redirect, session
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as req
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'secret_key'
# Connect to MongoDB
client = MongoClient('Mongo-URI')
db = client['test']
collection = db['users']

# Google OAuth2 configuration
CLIENT_ID = 'CLIENT_ID'
CLIENT_SECRET = 'CLIENT_SECRET'
AUTH_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'
USERINFO_ENDPOINT = 'https://www.googleapis.com/oauth2/v3/userinfo'

# Flask app routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and password:
            if not collection.find_one({'email': email}):
                collection.insert_one({'email': email, 'password': password})
                return redirect('/')
            else:
                return "Email already registered"
        else:
            return "Invalid email or password"
    else:
        return render_template('register.html')

@app.route('/google-login')
def google_login():
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': request.base_url + '/callback',
        'response_type': 'code',
        'scope': 'openid email'
    }
    auth_url = AUTH_ENDPOINT + '?' + '&'.join([f'{key}={value}' for key, value in params.items()])
    return redirect(auth_url)

@app.route('/google-login/callback')
def google_callback():
    # Exchange the authorization code for an access token
    token_endpoint_headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    token_endpoint_data = {
    'code': request.args.get('code'),
    'client_id': 'CLIENT_ID',
    'client_secret': 'CLIENT_SECRET',
    'redirect_uri': request.base_url,
    'grant_type': 'authorization_code'
    }
    token_response = req.post(TOKEN_ENDPOINT, headers=token_endpoint_headers, data=token_endpoint_data).json()


    access_token = token_response.get('access_token')

    if access_token:
        # Make a request to the Google user information endpoint to get the user's email address
        headers = {'Authorization': 'Bearer ' + access_token}
        userinfo_response = req.get(USERINFO_ENDPOINT, headers=headers).json()
        user_email = userinfo_response.get('email')

        if collection.find_one({'email': user_email}):
            # Set a session cookie with the user's email address and redirect to the dashboard
            session['access_token'] = access_token
            session['user_email'] = user_email
            return redirect('/dashboard')
        else:
            # User not authorized, redirect to home page
            return redirect('/')
    else:
        # Authorization failed, redirect to home page
        return redirect('/')
    

@app.route('/dashboard')
def dashboard():
    if 'user_email' in session:
        user_email = session['user_email']
        return render_template('dashboard.html', user_email=user_email)
    else:
        return redirect('/')
    
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/login', methods=['GET'])
def login():
    if request.method == 'GET':
        # Redirect to the dashboard
        return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)