from flask import Flask, make_response, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from json import dumps

Tariff = 100

app = Flask(__name__, template_folder='templates')

app.config['SECRET_KEY'] = 'temporal_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Records.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///States.db'
db0 = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Registry.db'
db1 = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Users.db'
db2 = SQLAlchemy(app)

class Records(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mid = db.Column(db.String(255), nullable=False)
    voltage = db.Column(db.Float, nullable=False)
    current = db.Column(db.Float, nullable=False)
    energy = db.Column(db.Float, nullable=False)

class States(db0.Model):
    mid = db.Column(db.String(255), primary_key=True, nullable=False)
    is_on = db0.Column(db.Boolean, nullable=False)
    is_active = db0.Column(db.Boolean, nullable=False)
    interval = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Float, nullable=False)

class Registry(db1.Model):
    mid = db1.Column(db.String(255), primary_key=True, nullable=False)
    name = db1.Column(db.String(255), nullable=False)
    surname = db1.Column(db.String(255), nullable=False)
    username = db1.Column(db.String(255), nullable=True)
    address = db1.Column(db.String(255), nullable=False)
    date_created = db1.Column(db.DateTime, default=datetime.utcnow())

class Users(db2.Model):
    id = db2.Column(db.Integer, autoincrement=True)
    username = db2.Column(db.String(50), primary_key=True, unique=True, nullable=False)
    firstname = db2.Column(db.String(50), nullable=False)
    lastname = db2.Column(db.String(50), nullable=False)
    email = db2.Column(db.String(120), unique=True, nullable=False)
    password_hash = db2.Column(db.String(128), nullable=False)
    country = db2.Column(db.String(50), nullable=False)

# Create the database tables within the application context
with app.app_context():
    db.create_all()
    db0.create_all()
    db1.create_all()
    db2.create_all()

@app.route('/')
def index():
    # Display existing meter data
    records = Records.query.all()
    return render_template('/index.html', meters=records)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        print('post request')
        username = request.form['username']
        password = request.form['password']
        print(username, password)
        password_hash = generate_password_hash(password, method='sha256')
        print(username, password_hash)
        if not Users.query.get(username):
            print('User not found')
            return redirect(url_for('sign_up'))
        else:
            user = Users.query.get(username)
            if check_password_hash(user.password_hash, password_hash):
                session['username'] = username
                session['email'] = user.email
                session['name'] = user.firstname
                session['surname'] = user.lastname
                return redirect(url_for('userprofile'))
            else:
                print('passwords dont match')
                return render_template('/login.html')
    return render_template('/login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('name', None)
    session.pop('email', None)
    session.pop('surname', None)
    return redirect(url_for('login', username='guest'))

@app.route('/user-profile')
def userprofile():
    username = session.get('username')
    email = session.get('email')
    name = session.get('name')
    surname = session.get('surname')
    if username and email and name and surname:
        return render_template('/userprofile.html', username=username, email=email, name=name, surname=surname)
    else:
        return redirect(url_for('login', username='guest'))

@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        username = request.form['usrname']
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        password = request.form['password']
        country = request.form['country']

        if Users.query.get(username):
            print('user exists')
            return redirect(url_for('sign_up'))
        else:
            print(username, password)
            password_hash = generate_password_hash(password, method='sha256')
            print(username, password_hash)

            new_user = Users(username=username, email=email, password_hash=password_hash, firstname=fname, lastname=lname, country=country)
            db2.session.add(new_user)
            db2.session.commit()

            session['username'] = new_user.username
            session['email'] = new_user.email
            session['name'] = new_user.firstname
            session['surname'] = new_user.lastname

            return redirect(url_for('userprofile'))
    return render_template('signup.html')
    
@app.route('/api/create-meter/', methods=['POST', 'GET'])
def create_meter():
    if request.method == 'GET':
        mid = request.args.get('mid')
    elif request.method == 'POST':
        try:
            json_data = request.get_json()
            if json_data:
                mid = json_data.get('mid')
            else:
                return make_response('', 422)
        except Exception:
            return make_response('', 422)
    if Registry.query.get(mid):
        response = {"error": "mid taken"}
        response = dumps(response)
        response = make_response(response, 403)
        return response
    else:
        if request.method == 'GET':
            fname = request.args.get('fname')
            lname = request.args.get('lname')
            usrname = request.args.get('usrname')
            addr = request.args.get('addr')
        elif request.method == 'POST':
            try:
                json_data = request.get_json()
                if json_data:
                    fname = json_data.get('fname')
                    lname = json_data.get('lname')
                    usrname = json_data.get('usrname')
                    addr = json_data.get('addr')
                else:
                    return make_response('', 422)
            except Exception:
                return make_response('', 422)
        new_registry = Registry(mid=mid, name=fname, surname=lname, address=addr, username=usrname)
        db1.session.add(new_registry)
        db1.session.commit()
        new_state = States(mid=mid, is_active=True, is_on=True, interval=15, balance=1000.0)
        db0.session.add(new_state)
        db0.session.commit()
        response = {"success": "meter created"}
        response = dumps(response)
        response = make_response(response, 200)
        return response

@app.route('/api/feedback/', methods=['GET', 'POST'])
def feedback():
    if request.method == 'GET':
        mid = request.args.get('mid')
    elif request.method == 'POST':
        try:
            json_data = request.get_json()
            if json_data:
                mid = json_data.get('mid')
            else:
                return make_response('', 422)
        except Exception:
            return make_response('', 422)
    if not Registry.query.get(mid):
        return dumps([0, 0, 15, 0]), 200
    else:
        if request.method == 'GET':
            voltage = request.args.get('vol')
            current = request.args.get('amp')
            energy = request.args.get('kwh')
        elif request.method == 'POST':
            try:
                json_data = request.get_json()
                if json_data:
                    voltage = json_data.get('usage')['vol']
                    current = json_data.get('usage')['amp']
                    energy = json_data.get('usage')['kwh']
                else:
                    return make_response('', 422)
            except Exception:
                return make_response('', 422)
        new_records = Records(mid=mid, voltage=voltage, current=current, energy=energy)
        db.session.add(new_records)
        db.session.commit()
        state = States.query.get(mid)
        if state:
            state.balance -= (float(energy) * Tariff)
            if state.balance <= 0.0:
                state.balance = 0.0
                state.is_on = False
            db0.session.commit()
        else:
            return str([0, 0, 15, 0])
        states = States.query.get(mid)
        if states:
            res = [int(states.is_active), int(states.is_on), states.interval, round(states.balance, 2)]
            return dumps(res), 200
        else:
            return dumps([0, 0, 15, 0]), 200

@app.route('/api/activate-meter/', methods=['GET', 'POST'])
def activate_meter():
    if request.method == 'GET':
        mid = request.args.get('mid')
    elif request.method == 'POST':
        try:
            json_data = request.get_json()
            if json_data:
                mid = json_data.get('mid')
            else:
                return make_response('', 422)
        except Exception:
            return make_response('', 422)
    if not Registry.query.get(mid):
        return make_response('', 403)
    else:
        state = States.query.get(mid)
        if state:
            state.is_on = True
            db0.session.commit()
        return make_response('', 200)

@app.route('/api/deactivate-meter/', methods=['GET', 'POST'])
def deactivate_meter():
    if request.method == 'GET':
        mid = request.args.get('mid')
    elif request.method == 'POST':
        try:
            json_data = request.get_json()
            if json_data:
                mid = json_data.get('mid')
            else:
                return make_response('', 422)
        except Exception:
            return make_response('', 422)
    if not Registry.query.get(mid):
        return make_response('', 403)
    else:
        state = States.query.get(mid)
        if state:
            state.is_on = False
            db0.session.commit()
        return make_response('', 200)
    
@app.route('/api/topup-meter/', methods=['GET', 'POST'])
def topup_meter():
    if request.method == 'GET':
        mid = request.args.get('mid')
    elif request.method == 'POST':
        try:
            json_data = request.get_json()
            if json_data:
                mid = json_data.get('mid')
            else:
                return make_response('', 422)
        except Exception:
            return make_response('', 422)
    if not Registry.query.get(mid):
        return make_response('', 403)
    else:
        return make_response('', 200)

@app.route('/api/show-records')
def show_records():
    records = Records.query.all()
    return render_template('/records.html', records=records)

@app.route('/api/show-registry')
def show_registry():
    registry = Registry.query.all()
    return render_template('/registry.html', registry=registry)

if __name__ == '__main__':
    app.run(debug=True)
