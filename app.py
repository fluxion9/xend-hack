from flask import Flask, make_response, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from json import dumps

Tariff = 100

app = Flask(__name__, template_folder='templates')

app.config['SECRET_KEY'] = 'temporal_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

class Records(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mid = db.Column(db.String(255), nullable=False)
    voltage = db.Column(db.Float, nullable=False)
    current = db.Column(db.Float, nullable=False)
    energy = db.Column(db.Float, nullable=False)
    time_stamp = db.Column(db.DateTime, default=datetime.utcnow())

class States(db.Model):
    mid = db.Column(db.String(255), primary_key=True, nullable=False)
    is_on = db.Column(db.Boolean, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)
    interval = db.Column(db.Integer, nullable=False)

class Registry(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mid = db.Column(db.String(255), nullable=False, unique=True) 
    name = db.Column(db.String(255), nullable=False)
    surname = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow())

class Users(db.Model):
    id = db.Column(db.Integer, autoincrement=True)
    username = db.Column(db.String(50), primary_key=True, unique=True, nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())

class Shared(db.Model):
    id = db.Column(db.Integer, autoincrement=True)
    username = db.Column(db.String(50), primary_key=True, unique=True, nullable=False)
    balance = db.Column(db.Float, nullable=False)
    tariff = db.Column(db.Float, nullable=False)

# Create the database tables within the application context
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    # Display existing meter data
    records = Records.query.all()
    return render_template('/index.html', meters=records)

@app.route('/login', methods=['POST', 'GET'])
def login():
    session.pop('username', None)
    session.pop('name', None)
    session.pop('email', None)
    session.pop('surname', None)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # password_hash = generate_password_hash(password, method='sha256')
        password_hash = password
        if not Users.query.get(username):
            print('User not found')
            return redirect(url_for('sign_up'))
        else:
            user = Users.query.get(username)
            if user.password_hash == password_hash:
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
    
@app.route('/dashboard')
def dashboard():
    username = session.get('username')
    email = session.get('email')
    name = session.get('name')
    surname = session.get('surname')
    if username and email and name and surname:
        return render_template('/dashboard.html', username=username, email=email, name=name, surname=surname)
    else:
        return redirect(url_for('login', username='guest'))
    
@app.route('/livemeters')
def livemeters():
    username = session.get('username')
    email = session.get('email')
    name = session.get('name')
    surname = session.get('surname')
    if username and email and name and surname:
        return render_template('/livemeter.html', username=username, email=email, name=name, surname=surname)
    else:
        return redirect(url_for('login'))

@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    session.pop('username', None)
    session.pop('name', None)
    session.pop('email', None)
    session.pop('surname', None)
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
            # password_hash = generate_password_hash(password, method='sha256')
            password_hash = password
            new_user = Users(username=username, email=email, password_hash=password_hash, firstname=fname, lastname=lname, country=country)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.username
            session['email'] = new_user.email
            session['name'] = new_user.firstname
            session['surname'] = new_user.lastname
            return redirect(url_for('userprofile'))
    return render_template('signup.html')

@app.route('/api/get-params', methods=['GET'])
def get_params():
    username = session.get('username')
    email = session.get('email')
    name = session.get('name')
    surname = session.get('surname')
    if username and email and name and surname:
        if request.method == 'GET':
            if not Registry.query.filter_by(username=username).first():
                return make_response('', 403)
            else:
                balance = Shared.query.get(username).balance
                registrar = Registry.query.filter_by(username=username).all()
                cnt = len(registrar)
                mids = list()
                is_active = list()
                is_on = list()
                address = list()
                for element in registrar:
                    mids.append(element.mid)
                    address.append(element.address)
                for mid in mids:
                    state = States.query.get(mid)
                    is_active.append(state.is_active)
                    is_on.append(state.is_on)
                response = {'count': cnt, 'mid': mids, 'balance': balance, 'is_active': is_active, 'is_on': is_on, 'address': address}
                response = dumps(response)
                response = make_response(response, 200)
                return response
        else:
            return make_response('', 403)
    else:
        return make_response('', 204)
    
@app.route('/register-meter', methods=['POST', 'GET'])
def register():
    username = session.get('username')
    email = session.get('email')
    name = session.get('name')
    surname = session.get('surname')
    if not username and email and name and surname:
        return redirect(url_for('login'))
    if request.method == 'POST':
        mid = request.form['mid']
        addr = request.form['loc']
        if Users.query.get(username):
            if Registry.query.filter_by(mid=mid).first():
                response = {"error": "mid taken"}
                response = dumps(response)
                return redirect(url_for('register', message=response))
            else:
                new_registry = Registry(mid=mid, name=name, surname=surname, address=addr, username=username)
                db.session.add(new_registry)
                db.session.commit()
                new_state = States(mid=mid, is_active=True, is_on=True, interval=15)
                db.session.add(new_state)
                db.session.commit()
                if not Shared.query.get(username):
                    new_data = Shared(username=username, balance=1000.0, tariff=Tariff)
                    db.session.add(new_data)
                    db.session.commit()
                response = {"success": "meter created"}
                response = dumps(response)
                return redirect(url_for('register', message=response))
        else:
            response = {"error": "user not found"}
            response = dumps(response)
            return redirect(url_for('register', message=response))
    if request.args:
        message = request.args.get('message')
    else:
        message = ""
    return render_template('addMeters.html', message=message)
    
@app.route('/api/register-meter/', methods=['POST', 'GET'])
def register_meter():
    if request.method == 'GET':
        usr = request.args.get('usr')
        mid = request.args.get('mid')
    elif request.method == 'POST':
        try:
            json_data = request.get_json()
            if json_data:
                usr = json_data.get('usr')
                mid = json_data.get('mid')
            else:
                return make_response('', 422)
        except Exception:
            return make_response('', 422)
    if Users.query.get(usr):
        if Registry.query.filter_by(mid=mid).first():
            response = {"error": "mid taken"}
            response = dumps(response)
            response = make_response(response, 403)
            return response
        else:
            if request.method == 'GET':
                fname = request.args.get('fname')
                lname = request.args.get('lname')
                addr = request.args.get('addr')
                mid = request.args.get('mid')
            elif request.method == 'POST':
                try:
                    json_data = request.get_json()
                    if json_data:
                        fname = json_data.get('fname')
                        lname = json_data.get('lname')
                        mid = json_data.get('mid')
                        addr = json_data.get('addr')
                    else:
                        print('Not Json data')
                        return make_response('', 422)
                except Exception:
                    return make_response('', 422)
            new_registry = Registry(mid=mid, name=fname, surname=lname, address=addr, username=usr)
            db.session.add(new_registry)
            db.session.commit()
            new_state = States(mid=mid, is_active=True, is_on=True, interval=15)
            db.session.add(new_state)
            db.session.commit()
            if not Shared.query.get(usr):
                    new_data = Shared(username=usr, balance=1000.0, tariff=Tariff)
                    db.session.add(new_data)
                    db.session.commit()
            response = {"success": "meter created"}
            response = dumps(response)
            response = make_response(response, 200)
            return response
    else:
        response = {"error": "user not found"}
        response = dumps(response)
        response = make_response(response, 404)
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
    if not Registry.query.filter_by(mid=mid).first():
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
        states = States.query.get(mid)
        reg = Registry.query.filter_by(mid=mid).first()
        username = reg.username
        share = Shared.query.get(username)
        if share and states:
            share.balance -= (float(energy) * share.tariff)
            if share.balance <= 0.0:
                share.balance = 0.0
                states.is_on = False
            db.session.commit()
        else:
            return str([0, 0, 15, 0])
        states = States.query.get(mid)
        share = Shared.query.get(username)
        if states and share:
            res = [int(states.is_active), int(states.is_on), states.interval, round(share.balance, 2)]
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
    if not Registry.query.filter_by(mid=mid).first():
        return make_response('', 403)
    else:
        state = States.query.get(mid)
        if state:
            state.is_on = True
            db.session.commit()
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
    if not Registry.query.filter_by(mid=mid).first():
        return make_response('', 403)
    else:
        state = States.query.get(mid)
        if state:
            state.is_on = False
            db.session.commit()
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

@app.route('/api/show-users')
def show_users():
    users = Users.query.all()
    return render_template('/users.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)