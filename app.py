from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meters.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)

# Define the Meter model
class Meter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meter_id = db.Column(db.Integer, unique=True, nullable=False)
    voltage = db.Column(db.Float, nullable=False)
    current = db.Column(db.Float, nullable=False)
    energy = db.Column(db.Float, nullable=False)

# Create the database tables within the application context
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # Display existing meter data
    meters = Meter.query.all()
    return render_template('/index.html', meters=meters)

@app.route('/add_meter', methods=['GET'])
def add_meter():
    # Add new meter data to the database
    meter_id = request.args.get('meter_id')
    voltage = request.args.get('voltage')
    current = request.args.get['current']
    energy = request.args.get['energy']

    new_meter = Meter(meter_id=meter_id, voltage=voltage, current=current, energy=energy)
    db.session.add(new_meter)
    db.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
