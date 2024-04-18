from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify
from App.models import db
from App.controllers import create_user

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def index_page():
    return render_template('index.html')

@index_views.route('/init', methods=['GET']) 
def init():
    db.drop_all()
    db.create_all()
    create_user('bob', 'bob@gmail.com', 'bobpass','company','TRINITECH')#Bob is by default a Company Account
    create_user('rob','rob@gmail.com','robpass','student')#Rob is by default a Student Account
    
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

