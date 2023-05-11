from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from pymongo import MongoClient
import random

app = Flask(__name__)

# Configure Flask-Mail settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email' # Enter your own email address
app.config['MAIL_PASSWORD'] = 'your-app-id' # Enter your app password
mail = Mail(app)

# Connect to MongoDB database
client = MongoClient('your-mongo-uri')
db = client['test']
users = db['users']

# Define routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        user = users.find_one({'email': email})
        if user:
            otp = str(random.randint(100000, 999999)) # Generate a random 6-digit OTP
            # Send the OTP to the user's email
            msg = Message('MFA OTP', sender='your-email', recipients=[email])
            msg.body = 'Your MFA OTP is: ' + otp
            mail.send(msg)
            # Store the OTP in the session
            session['otp'] = otp
            # Redirect to the OTP page
            return redirect(url_for('otp'))
        else:
            return render_template('index.html', error='Invalid email')
    else:
        return render_template('index.html')

@app.route('/otp', methods=['GET', 'POST'])
def otp():
    if request.method == 'POST':
        user_otp = request.form['otp']
        # Check if the user entered the correct OTP
        if user_otp == session['otp']:
            session.pop('otp', None)
            return redirect(url_for('dashboard'))
        else:
            return render_template('otp.html', error='Invalid OTP')
    else:
        return render_template('otp.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.secret_key = 'secret-key' # Enter your own secret key
    app.run(debug=True)
