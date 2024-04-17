from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

from datetime import datetime, timedelta

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)
    company_name = db.Column(db.String(120), nullable=True)
    resume_url = db.Column(db.String(255))  

    def __init__(self, username, email, password, account_type, company_name=None):
        self.username = username
        self.email = email
        self.set_password(password)
        self.account_type = account_type
        self.company_name = company_name
        self.resume_url = None

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Internship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=True)
    duration = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean, default=True)
    company_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    company = db.relationship('User', backref=db.backref('internships', lazy=True))


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(db.Integer, db.ForeignKey('internship.id'))
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(50), default='submitted')
    apply_date = db.Column(db.DateTime, default=datetime.utcnow)
    cover_letter = db.Column(db.Text, nullable=True)  # New field for storing the application letter
    internship = db.relationship('Internship', backref=db.backref('applications', lazy=True))
    applicant = db.relationship('User', backref=db.backref('applications', lazy=True))


class Shortlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(db.Integer, db.ForeignKey('internship.id'))
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    added_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    internship = db.relationship('Internship', backref=db.backref('shortlisted_applicants', lazy='dynamic'))
    applicant = db.relationship('User', backref=db.backref('shortlisted_positions', lazy='dynamic'))
