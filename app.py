from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Records.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///States.db'
db0 = SQLAlchemy(app)

# Define the Meter model
class Records(db.Model):
    meter_id = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    voltage = db.Column(db.Float, nullable=False)
    current = db.Column(db.Float, nullable=False)
    energy = db.Column(db.Float, nullable=False)

class States(db0.Model):
    meter_id = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    is_on = db0.Column(db.Boolean, nullable=False)
    is_active = db0.Column(db.Boolean, nullable=False)
    interval = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Float, nullable=False)

# Create the database tables within the application context
with app.app_context():
    db.create_all()
    db0.create_all()

@app.route('/')
def index():
    # Display existing meter data
    records = Records.query.all()
    return render_template('/index.html', meters=records)

# @app.route('/add_meter', methods=['GET'])
# def add_meter():
#     meter_id = request.args.get('meter_id')
#     voltage = request.args.get('voltage')
#     current = request.args.get('current')
#     energy = request.args.get('energy')
#     new_record = Records(meter_id=meter_id, voltage=voltage, current=current, energy=energy)
#     db.session.add(new_record)
#     db.session.commit()

#     return redirect(url_for('index'))

@app.route('/create-meter', methods=['GET'])
def add_meter():
    meter_id = request.args.get('meter_id')
    is_active = True
    is_on = True
    interval = 15
    balance = 1000
    new_state = States(meter_id=meter_id, is_active=is_active, is_on=is_on, interval=interval, balance=balance)
    db0.session.add(new_state)
    db0.session.commit()
    return 'Success'

if __name__ == '__main__':
    app.run(debug=True)
