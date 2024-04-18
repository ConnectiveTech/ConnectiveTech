from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies
from App.database import db

from App.models import User,Internship,Application

from datetime import datetime

from.index import index_views

from App.controllers import (
    login,    
)

company_views= Blueprint('company_views', __name__, template_folder='../templates')


# Company Internship Routes

@company_views.route('/internships', methods=['GET'])
@jwt_required()
def list_internships():
    internships = Internship.query.filter_by(company_id=current_user.id).all()
    return render_template('internships.html', internships=internships)

@company_views.route('/internships/create', methods=['POST'])
@jwt_required()
def create_internship():
    try:
        data = request.form
        if not data['title'] or not data['description']:
            flash('Title and description are required.', 'error')
            return redirect(url_for('auth_views.dashboard'))  
        
        deadline = datetime.strptime(data['deadline'], '%Y-%m-%d')  

        new_internship = Internship(
            title=data['title'],
            description=data['description'],
            requirements=data.get('requirements', ''),
            duration=data['duration'],
            company_id=current_user.id,
            location=data['location'],
            deadline=deadline,
            active=data.get('active', 'True') == 'True'
        )
        db.session.add(new_internship)
        db.session.commit()
        flash('New internship created successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to create internship. Error: {str(e)}', 'error')
    
    return redirect(url_for('auth_views.dashboard')) 

@company_views.route('/internships/update/<int:internship_id>', methods=['GET', 'POST'])
@jwt_required()
def update_internship(internship_id):
    internship = Internship.query.get_or_404(internship_id)
    if request.method == 'POST':
        try :
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
    
    formatted_deadline = internship.deadline.strftime('%Y-%m-%d') if internship.deadline else ''
    return render_template('edit_internship.html', internship=internship, formatted_deadline=formatted_deadline)

@company_views.route('/internships/delete/<int:internship_id>', methods=['POST'])
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
