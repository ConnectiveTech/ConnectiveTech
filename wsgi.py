import click, pytest, sys
from flask import Flask
from flask.cli import with_appcontext, AppGroup
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from App.database import db, get_migrate
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users )
from App.models import Internship,User


# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def initialize():
    db.drop_all()
    db.create_all()
    create_user('bob', 'bob@gmail.com', 'bobpass','company','MICROBOB')
    print('database intialized')



@app.cli.command("init_db")
def initialize():
    """Creates and initializes the database with sample data."""
    db.drop_all()
    db.create_all()
    
    # Create a sample company user with hashed password
    company = User(
        username='bob',
        email='bob@gmail.com',
        password='bobpass',
        account_type='company',
        company_name='MICROBOB'
    )
    db.session.add(company)

    # Create a sample student user with hashed password
    student = User(
        username='alice',
        email='alice@student.edu',
        password='alicepass',
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
            deadline=datetime.utcnow() + timedelta(days=180),  # assuming you import timedelta
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

    # Use bulk_save_objects to efficiently insert data
    db.session.bulk_save_objects(internships)
    db.session.commit()

    print('Database initialized with sample data.')

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
@click.argument("email", default = "rob@gmail.com")
@click.argument("account_type", default = "company")
def create_user_command(username,email, password,account_type):
    create_user(username,email, password,account_type)
    print(f'{username} created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli

'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    

app.cli.add_command(test)