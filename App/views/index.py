from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify
from App.models import db
from App.models import Internship,User
from datetime import datetime, timedelta
from App.main import create_app

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def index_page():
    return render_template('index.html')

@index_views.route('/init', methods=['GET']) 
def init():
    """Creates and initializes the database with sample data."""
    db.drop_all()
    db.create_all()

    company = User(
        username='bob',
        email='bob@gmail.com',
        password='bobpass',
        account_type='company',
        company_name='TRINITECH'
    )
    db.session.add(company)

    student = User(
        username='rob',
        email='rob@student.edu',
        password='robpass',
        account_type='student'
    )
    db.session.add(student)

    # Commit the users to the database to get their ids
    db.session.commit()

    # Sample internships
    internships = [
        Internship(
            title='Software Development Intern',
            description='Assist in developing enterprise-level software applications.',
            requirements='Knowledge of Python, Flask',
            duration='6 months',
            company_id=company.id,
            location='Remote',
            deadline=datetime.utcnow() + timedelta(days=180), 
            active=True
        ),
        Internship(
            title='Marketing Intern',
            description='Support our marketing team in crafting campaign strategies.',
            requirements='Familiarity with digital marketing tools',
            duration='3 months',
            company_id=company.id,
            location='New York or Remote',
            deadline=datetime.utcnow() + timedelta(days=90),
            active=True
        ),
        Internship(
            title='Data Analysis Intern',
            description='Help analyze large datasets to derive actionable insights.',
            requirements='Experience with Python and SQL',
            duration='3 months',
            company_id=company.id,
            location='Remote',
            deadline=datetime.utcnow() + timedelta(days=90),
            active=True
        )
    ]

    db.session.bulk_save_objects(internships)
    db.session.commit()

    return jsonify(message='db initialized!')


@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})

