from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os
from Modelss import User, Winner, db

app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)






with app.app_context():
    db.create_all()  
    

@app.route("/")
def home():
    users = User.query.all()
    winners = Winner.query.all()
    return render_template("home.html", users=users, winners=winners, current_time=datetime.now())

@app.route('/add', methods=['POST'])
def add():
    username = request.form.get("username")
    email = request.form.get("email")
    
    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()
    
    
    return redirect(url_for('home'))

@app.route("/site1/")
def site1():
    winners = Winner.query.all()
    return render_template("site1.html", winners=winners)

@app.route("/site2/")
def site2():
    users = User.query.all()
    return render_template("site2.html", users=users)

if __name__ == ('__main__'):
    app.run(host="0.0.0.0", debug=False)

