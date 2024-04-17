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
    create_user('bob', 'bob@gmail.com', 'bobpass','company','MICROBOB')#Bob is by default a Company Account
    create_user('rob','rob@gmail.com','robpass','student')#Rob is by default a Student Account
    return jsonify(message='db initialized!')

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})