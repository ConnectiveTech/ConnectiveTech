from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies

from.index import index_views

from App.controllers import (
    login
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
   
    # Assume User model and db session are correctly set up
    new_user = User(username=username, email=email, password=password, account_type=account_type, company_name=company_name)
    db.session.add(new_user)
    db.session.commit()
   
    flash('Registration successful. Please log in.')
    return redirect(url_for('auth_views.login_action'))


@auth_views.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    # Fetch internships for the logged-in user's company or available internships for students
    if current_user.account_type == 'company':
        internships = Internship.query.filter_by(company_id=current_user.id).all()
        return render_template('company_dashboard.html', internships=internships, current_user=current_user)
    elif current_user.account_type == 'student':
        internships = Internship.query.filter(Internship.active == True).all() # Make sure to fetch only active internships
        return render_template('student_dashboard.html', internships=internships, current_user=current_user)
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


# Students Routes
@auth_views.route('/dashboard/student', methods=['GET'])
@jwt_required()
def student_dashboard():
    internships = Internship.query.filter(Internship.active == True).all()
    applied_internship_ids = {app.internship_id for app in current_user.applications}
    shortlisted_ids = {app.internship_id for app in current_user.applications if app.status == 'shortlisted'}
    return render_template('student_dashboard.html', internships=internships, shortlisted_ids=shortlisted_ids, applied_internship_ids=applied_internship_ids, current_user=current_user)


@auth_views.route('/internships/apply/<int:internship_id>', methods=['POST'])
@jwt_required()
def apply_for_internship(internship_id):
    internship = Internship.query.get_or_404(internship_id)
    application_note = request.form.get('application_note', '')


    existing_application = Application.query.filter_by(applicant_id=current_user.id, internship_id=internship_id).first()
    if existing_application:
        flash('You have already applied for this internship.', 'info')
    else:
        new_application = Application(
            internship_id=internship_id,
            applicant_id=current_user.id,
            status='submitted',
            cover_letter=application_note  # Assuming your Application model has a field for application_note
        )
        db.session.add(new_application)
        db.session.commit()
        flash('Application submitted successfully!', 'success')


    return redirect(url_for('auth_views.student_dashboard'))


@auth_views.route('/update_profile', methods=['POST'])
@jwt_required()
def update_student_profile():
    email = request.form['email']
    resume = request.files.get('resume')  # Ensure you handle the case where no file is uploaded


    if resume and allowed_file(resume.filename):
        filename = secure_filename(resume.filename)
        resume.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        # Assuming you have a field in your user model to store the resume URL
        current_user.resume_url = url_for('auth_views.uploaded_file', filename=filename, _external=True)


    current_user.email = email
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('auth_views.student_dashboard'))


# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}


@auth_views.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@auth_views.route('/student/resources', methods=['GET'])
@jwt_required()
def student_resources():
    return render_template('student_resources.html')


@auth_views.route('/internships/view_applications/<int:internship_id>', methods=['GET'])
@jwt_required()
def view_applications(internship_id):
    if not current_user or current_user.account_type != 'company':
        flash("Access denied.", 'danger')
        return redirect(url_for('auth_views.login_action'))
   
    internship = Internship.query.get_or_404(internship_id)
    if internship.company_id != current_user.id:
        flash("Unauthorized access.", 'danger')
        return redirect(url_for('auth_views.dashboard'))
   
    applications = Application.query.filter_by(internship_id=internship_id).all()
    return render_template('view_applications.html', applications=applications, internship=internship)


@auth_views.route('/internships/<int:internship_id>/shortlist/<int:applicant_id>', methods=['POST'])
@jwt_required()
def shortlist_applicant(internship_id, applicant_id):
    if current_user.account_type != 'company' or current_user.id != Internship.query.get(internship_id).company_id:
        flash("Unauthorized access.", 'danger')
        return redirect(url_for('auth_views.dashboard'))


    application = Application.query.filter_by(internship_id=internship_id, applicant_id=applicant_id).first()
    if application:
        if application.status != 'shortlisted':  # Check if not already shortlisted
            application.status = 'shortlisted'
            db.session.commit()
            flash('Applicant shortlisted successfully!', 'success')
        else:
            flash('Applicant is already shortlisted.', 'info')
    else:
        flash('Application not found.', 'error')


    return redirect(url_for('auth_views.view_applications', internship_id=internship_id))


@auth_views.route('/download_resume/<filename>')
@jwt_required()
def download_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Company Internship Routes

@auth_views.route('/internships', methods=['GET'])
@jwt_required()
def list_internships():
    # Assuming current_user has a property `id` that links to their company
    internships = Internship.query.filter_by(company_id=current_user.id).all()
    return render_template('internships.html', internships=internships)

@auth_views.route('/internships/create', methods=['POST'])
@jwt_required()
def create_internship():
    try:
        data = request.form
        # Ensure required fields are present
        if not data['title'] or not data['description']:
            flash('Title and description are required.', 'error')
            return redirect(url_for('auth_views.dashboard'))
        
        # Convert 'deadline' from string to datetime object
        deadline = datetime.strptime(data['deadline'], '%Y-%m-%d')  # Adjust the format string as necessary

        new_internship = Internship(
            title=data['title'],
            description=data['description'],
            requirements=data.get('requirements', ''),
            duration=data['duration'],
            company_id=current_user.id,
            location=data['location'],
            posted_date=datetime.now(),  # Ensure this is correct if you want to set it manually
            deadline=deadline,  # Now passing a datetime object
            active=data.get('active', 'True') == 'True'
        )
        db.session.add(new_internship)
        db.session.commit()
        flash('New internship created successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to create internship. Error: {str(e)}', 'error')
    
    return redirect(url_for('auth_views.dashboard'))

@auth_views.route('/internships/update/<int:internship_id>', methods=['GET', 'POST'])
@jwt_required()
def update_internship(internship_id):
    internship = Internship.query.get_or_404(internship_id)
    if request.method == 'POST':
        try:
            internship.title = request.form.get('title', internship.title)
            internship.description = request.form.get('description', internship.description)
            internship.requirements = request.form.get('requirements', internship.requirements)
            internship.duration = request.form.get('duration', internship.duration)
            internship.location = request.form.get('location', internship.location)
            deadline_str = request.form.get('deadline')
            if deadline_str:
                try:
                    internship.deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
                except ValueError:
                    flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
                    return render_template('edit_internship.html', internship=internship)

            internship.active = request.form.get('active', 'True') == 'True'
            db.session.commit()
            flash('Internship updated successfully!', 'success')
            return redirect(url_for('auth_views.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating internship: {str(e)}', 'error')
            return render_template('edit_internship.html', internship=internship)
    
    # Pass the formatted deadline for the form
    formatted_deadline = internship.deadline.strftime('%Y-%m-%d') if internship.deadline else ''
    return render_template('edit_internship.html', internship=internship, formatted_deadline=formatted_deadline)


@auth_views.route('/internships/delete/<int:internship_id>', methods=['POST'])
@jwt_required()
def delete_internship(internship_id):
    internship = Internship.query.get_or_404(internship_id)
    if internship.company_id != current_user.id:
        flash("Unauthorized access.", 'danger')
        return redirect(url_for('auth_views.dashboard'))

    db.session.delete(internship)
    db.session.commit()
    flash('Internship deleted successfully!', 'success')
    return redirect(url_for('auth_views.dashboard'))


if __name__ == "__main__":
  app.run(debug=True)



