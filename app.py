from flask import Flask, make_response, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

Tariff = 100

app = Flask(__name__, template_folder='templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Records.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///States.db'
db0 = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Registry.db'
db1 = SQLAlchemy(app)

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

# Create the database tables within the application context
with app.app_context():
    db.create_all()
    db0.create_all()
    db1.create_all()

@app.route('/')
def index():
    # Display existing meter data
    records = Records.query.all()
    return render_template('/index.html', meters=records)
    
@app.route('/api/create-meter/', methods=['POST', 'GET'])
def create_meter():
    mid = request.args.get('mid')
    if Registry.query.get(mid):
        res = {"error": "mid taken"}
        return jsonify(res), 403
    else:
        fname = request.args.get('fname')
        lname = request.args.get('lname')
        usrname = request.args.get('usrname')
        addr = request.args.get('addr')
        new_registry = Registry(mid=mid, name=fname, surname=lname, address=addr, username=usrname)
        db1.session.add(new_registry)
        db1.session.commit()
        new_state = States(mid=mid, is_active=True, is_on=True, interval=15, balance=1000.0)
        db0.session.add(new_state)
        db0.session.commit()
        res = {"success": "meter created"}
        return jsonify(res), 200

@app.route('/api/feedback/', methods=['GET', 'POST'])
def feedback():
    mid = request.args.get('mid')
    if not Registry.query.get(mid):
        jsonify([0, 0, 15, 0]), 200
    else:
        voltage = request.args.get('vol')
        current = request.args.get('amp')
        energy = request.args.get('kwh')
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
            res = [int(states.is_active), int(states.is_on), states.interval, states.balance]
            return jsonify(res), 200
        else:
            return jsonify([0, 0, 15, 0]), 200

@app.route('/api/activate-meter/', methods=['GET', 'POST'])
def activate_meter():
    mid = request.args.get('mid')
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
    mid = request.args.get('mid')
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
    mid = request.args.get('mid')
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
