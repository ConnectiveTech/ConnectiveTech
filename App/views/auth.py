from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies
from App.database import db
from App.models import User,Internship,Application

from datetime import datetime

from.index import index_views

from App.controllers import (
    login,    
)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')


'''
Page/Action Routes
'''    
@auth_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)


@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")
   
@auth_views.route('/login', methods=['GET'])
def show_login_form():
    return render_template('creds.html')




@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    token = login(data['username'], data['password'])
    response = redirect(request.referrer)
    if not token:
        flash('Bad username or password given'), 401
    else:
        flash('Login Successful')
        set_access_cookies(response, token)
    return response


@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect('/login')
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response




@auth_views.route('/register', methods=['GET'])
def show_register_form():
    return render_template('creds.html')


@auth_views.route('/register', methods=['POST'])
def register():
    # Retrieve form data
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    account_type = request.form.get('accountType')
    company_name = request.form.get('companyName') if account_type == 'company' else None

    # Check if username or email already exists
    user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
    if user_exists:
        flash('An account with this username or email already exists.', 'error')
        return redirect(url_for('auth_views.show_register_form'))

    
    new_user = User(username=username, email=email, password=generate_password_hash(password), account_type=account_type, company_name=company_name)
    db.session.add(new_user)
    db.session.commit()

    flash('Registration successful. Please log in.', 'success')
    return redirect(url_for('auth_views.login_form'))  # Redirect to the login page



@auth_views.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    if current_user.account_type == 'company':
        internships = Internship.query.filter_by(company_id=current_user.id).all()
        return render_template('company_dashboard.html', internships=internships, current_user=current_user)

    elif current_user.account_type == 'student':
        internships = Internship.query.filter(Internship.active == True).all()
        applications = Application.query.filter_by(applicant_id=current_user.id).all()

        applied_internship_ids = {app.internship_id for app in applications}
        shortlisted_ids = {app.internship_id for app in applications if app.status == 'shortlisted'}

        return render_template('student_dashboard.html', internships=internships,
                               applied_internship_ids=applied_internship_ids,
                               shortlisted_ids=shortlisted_ids, current_user=current_user)

    else:
        flash('You do not have access to this page.', 'error')
        return redirect(url_for('auth_views.login_action'))




'''
API Routes
'''

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
  data = request.json
  token = login(data['username'], data['password'])
  if not token:
    return jsonify(message='bad username or password given'), 401
  response = jsonify(access_token=token) 
  set_access_cookies(response, token)
  return response

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response


if __name__ == "__main__":
  app.run(debug=True)



