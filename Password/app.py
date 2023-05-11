from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_pymongo import PyMongo
import bcrypt
import jwt
import datetime

app = Flask(__name__)
app.config['MONGO_URI'] = 'your-mongo-uri'
app.config['SECRET_KEY'] = 'secret-key'

mongo = PyMongo(app)
try:
    mongo = PyMongo(app)
except Exception as e:
    print(e)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'email': request.form['email']})
    if login_user:
           login_pass = users.find_one({'password': request.form['password']})
           if login_pass:
            response = make_response(redirect(url_for('dashboard')))
            
            response.set_cookie('token', "pojnhhhn")
            return response
    return 'Invalid email combination'


@app.route('/dashboard')
def dashboard():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('index'))
    else:
        return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
