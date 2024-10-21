from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import re
from config import Config

app = Flask(__name__)

# Load config from Config class
app.config.from_object(Config)

app.secret_key = app.config['SECRET_KEY']

# Connect to MongoDB using the URI from the config
client = MongoClient(app.config['MONGO_URI'], server_api=ServerApi('1'))
db = client['money']

# Collections
accounts_collection = db['accounts']
user_data_collection = db['user_data']
expenses_collection = db['expenses']

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account = accounts_collection.find_one({'username': username, 'password': password})
        if account:
            session['loggedin'] = True
            session['id'] = str(account['_id'])
            session['username'] = account['username']
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect username / password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        existing_account = accounts_collection.find_one({'username': username})
        if existing_account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            user_data = {'username': username, 'password': password, 'email': email}
            accounts_collection.insert_one(user_data)
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'loggedin' in session:
        user_id = session['id']
        user_data = user_data_collection.find_one({'user_id': user_id})
        if request.method == 'POST':
            # Save or update user data
            full_name = request.form['name']
            email = request.form['email']
            job = request.form['job']
            monthly_income = float(request.form['monthlyIncome'])
            annual_income = float(request.form['annualIncome'])
            savings = float(request.form['savings'])
            if user_data:
                user_data_collection.update_one({'user_id': user_id}, {
                    '$set': {
                        'full_name': full_name,
                        'email': email,
                        'job': job,
                        'monthly_income': monthly_income,
                        'annual_income': annual_income,
                        'savings': savings
                    }
                })
            else:
                user_data_collection.insert_one({
                    'user_id': user_id,
                    'full_name': full_name,
                    'email': email,
                    'job': job,
                    'monthly_income': monthly_income,
                    'annual_income': annual_income,
                    'savings': savings
                })
            return redirect(url_for('expense_tracker'))
        elif request.method == 'GET':
            if not user_data:
                return render_template('index.html', message='No data available. Please enter your information.')
            return render_template('index.html', user_data=user_data)
    return redirect(url_for('login'))

@app.route('/expense_tracker', methods=['GET', 'POST'])
def expense_tracker():
    if 'loggedin' in session:
        user_id = session['id']
        user_data = user_data_collection.find_one({'user_id': user_id})
        
        if request.method == 'POST':
            response = {}
            if 'depositAmount' in request.form:
                deposit_amount = float(request.form['depositAmount'])
                new_savings = user_data['savings'] + deposit_amount
                user_data_collection.update_one({'user_id': user_id}, {'$set': {'savings': new_savings}})
                response = {'success': True, 'new_savings': new_savings}
            elif 'expenseAmount' in request.form:
                expense_date = request.form['expenseDate']
                expense_usage = request.form['expenseUsage']
                expense_amount = float(request.form['expenseAmount'])
                new_savings = user_data['savings'] - expense_amount
                user_data_collection.update_one({'user_id': user_id}, {'$set': {'savings': new_savings}})
                expenses_collection.insert_one({
                    'user_id': user_id,
                    'date': expense_date,
                    'usage': expense_usage,
                    'amount': expense_amount
                })
                response = {'success': True, 'new_savings': new_savings}
            return jsonify(response)
        elif request.method == 'GET':
            expenses = list(expenses_collection.find({'user_id': user_id}))
            return render_template('expense-tracker.html', expenses=expenses, savings=user_data['savings'])
    return redirect(url_for('login'))

@app.route('/get_user_data')
def get_user_data():
    if 'loggedin' in session:
        user_id = session['id']
        user_data = user_data_collection.find_one({'user_id': user_id})
        if user_data:
            return jsonify({
                'full_name': user_data['full_name'],
                'email': user_data['email'],
                'job': user_data['job'],
                'monthly_income': user_data['monthly_income'],
                'annual_income': user_data['annual_income'],
                'savings': user_data['savings']
            })
        return jsonify({'error': 'No data available.'}), 404
    return redirect(url_for('login'))

@app.route('/user_data')
def user_data():
    if 'loggedin' in session:
        return render_template('user-data.html')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
