from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies
from App.database import db

from App.models import User,Internship,Application

from datetime import datetime

from.index import index_views

from App.controllers import (
    login,    
)

student_views= Blueprint('student_views', __name__, template_folder='../templates')




@student_views.route('/dashboard/student', methods=['GET'])
@jwt_required()
def student_dashboard():
    internships = Internship.query.filter(Internship.active == True).all()
    applied_internship_ids = {app.internship_id for app in current_user.applications}
    shortlisted_ids = {app.internship_id for app in current_user.applications if app.status == 'shortlisted'}
    return render_template('student_dashboard.html', internships=internships, shortlisted_ids=shortlisted_ids, applied_internship_ids=applied_internship_ids, current_user=current_user)

@student_views.route('/internships/apply/<int:internship_id>', methods=['POST'])
@jwt_required()
def apply_for_internship(internship_id):
    internship = Internship.query.get_or_404(internship_id)
    application_note = request.form.get('application_note', '')

    existing_application = Application.query.filter_by(applicant_id=current_user.id, internship_id=internship_id).first()
    if existing_application:
        flash('You have already applied for this internship.', 'info')
        return redirect(url_for('student_views.dashboard'))  

    # Create a new application if none exists
    new_application = Application(
        internship_id=internship_id,
        applicant_id=current_user.id,
        status='submitted',
        cover_letter=application_note
    )
    db.session.add(new_application)
    db.session.commit()

    flash('Application submitted successfully!', 'success')
    return redirect(url_for('auth_views.dashboard'))  

@student_views.route('/student/resources', methods=['GET'])
@jwt_required()
def student_resources():
    return render_template('student_resources.html')

@student_views.route('/internships/view_applications/<int:internship_id>', methods=['GET'])
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

@student_views.route('/internships/<int:internship_id>/shortlist/<int:applicant_id>', methods=['POST'])
@jwt_required()
def shortlist_applicant(internship_id, applicant_id):
    if current_user.account_type != 'company' or current_user.id != Internship.query.get(internship_id).company_id:
        flash("Unauthorized access.", 'danger')
        return redirect(url_for('auth_views.dashboard'))  
    
    application = Application.query.filter_by(internship_id=internship_id, applicant_id=applicant_id).first()
    if application:
        if application.status != 'shortlisted':
            application.status = 'shortlisted'
            db.session.commit()
            flash('Applicant shortlisted successfully!', 'success')
        else:
            flash('Applicant is already shortlisted.', 'info')
    else:
        flash('Application not found.', 'error')

    return redirect(url_for('student_views.view_applications', internship_id=internship_id))

@student_views.route('/download_resume/<filename>')
@jwt_required()
def download_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == "__main__":
  app.run(debug=True)
