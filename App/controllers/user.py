from App.models import User
from App.database import db

def create_user(username, email, password, account_type, company_name=None):
    """
    Create a new user with the given details.

    Args:
        username (str): The username of the new user.
        email (str): The email address of the new user.
        password (str): The password for the new user.
        account_type (str): The type of account ('student' or 'company').
        company_name (str, optional): The name of the company, required if account_type is 'company'.

    Returns:
        User: The newly created user object.
    """
    # Ensure that company_name is provided if the account_type is 'company'
    if account_type == 'company' and not company_name:
        raise ValueError("Company name must be provided for company accounts.")

    # Create a new User instance
    new_user = User(
        username=username,
        email=email,
        password=password,
        account_type=account_type,
        company_name=company_name
    )

    # Add the new user to the database session and commit
    db.session.add(new_user)
    try:
        db.session.commit()
    except Exception as e:
        # Rollback the session in case of an error
        db.session.rollback()
        raise Exception("Failed to create user: " + str(e))

    return new_user


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def get_user(id):
    return User.query.get(id)

def get_all_users():
    return User.query.all()

def get_all_users_json():
    users = User.query.all()
    if not users:
        return []
    users = [user.get_json() for user in users]
    return users

def update_user(id, username):
    user = get_user(id)
    if user:
        user.username = username
        db.session.add(user)
        return db.session.commit()
    return None
    