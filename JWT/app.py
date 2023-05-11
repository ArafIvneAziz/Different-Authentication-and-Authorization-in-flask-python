from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_pymongo import PyMongo
import bcrypt
import jwt
import datetime

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongo-uri'
app.config['SECRET_KEY'] = 'secret-key'

mongo = PyMongo(app)
try:
    mongo = PyMongo(app)
except Exception as e:
    print(e)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    users = mongo.db.users
    existing_user = users.find_one({'email': request.form['email']})
    if existing_user is None:
        hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        users.insert_one({'email': request.form['email'], 'password': hashpass})
        return redirect(url_for('dashboard'))
    return 'That email already exists!'


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'email': request.form['email']})
    if login_user:
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), login_user['password']):
            token = jwt.encode({'email': request.form['email'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
            response = make_response(redirect(url_for('dashboard')))
            response.set_cookie('token', token)
            return response
    return 'Invalid email/password combination'


@app.route('/dashboard')
def dashboard():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('index'))
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return render_template('dashboard.html')
    except:
        return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)
