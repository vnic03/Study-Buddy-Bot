from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Creates a User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
     
    whatsapp_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    
    points = db.Column(db.Integer, default=0)
    achievements = db.Column(db.String, default='')

    def __repr__(self):
        return f'<User {self.name}>' 
    



