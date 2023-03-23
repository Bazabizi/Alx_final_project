import os
import json
from flask import Blueprint, render_template, request, jsonify, make_response, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user
from utils import FileManager
from uuid import uuid4

from model import User, UserType, Job, Attachment, File, db


job_bp = Blueprint('job_bp', __name__,
                   static_folder='static', template_folder='templates')

file_mgr = FileManager(os.getenv('UPLOAD_FOLDER'))


@job_bp.route('/')
@login_required
def job():
    message = request.args.get("message")
    if current_user.user_type == UserType.EMPLOYER:
        return render_template('employer_job.html', message=message)
    return redirect(url_for("search"))


@job_bp.route('/<id>')
def get_job(id):
    job = Job.get(id)
    if job:
        return render_template('job.html', job=job)

    return redirect(url_for('job_bp.search'))


@job_bp.route('/search')
def search():
    print(">>>")
    return render_template('filter_job.html')


@job_bp.route('/', methods=['POST'])
@login_required
def post():
    id = uuid4()
    title = request.form.get("title")
    description = request.form.get("description")
    experience_level = request.form.get("experience-level")
    budget = request.form.get("budget")
    owner_id = current_user.id

    new_job = Job(id=id, title=title, description=description,
                  experience_level=experience_level,
                  budget=budget, owner_id=owner_id
                  )

    db.session.add(new_job)
    db.session.commit()

    return redirect(url_for('job_bp.job', message="Job posted successfully."))


@job_bp.route('/user/<user_id>', methods=['GET'])
def see_posted_jobs(user_id):
    jobs = User.get(user_id).get_posted_jobs()
    jsonList = []

    for job in jobs:
        jsonList.append({"id": job.id,
                         "title": job.title,
                         "description": job.description,
                         "experience_level": job.experience_level,
                         "owner_id": job.owner_id,
                         "budget": job.budget
                         })
    response = make_response(
        jsonify(jsonList),
        200
    )
    response.headers["Content-Type"] = "application/json"
    return response


@job_bp.route('/filterJob', methods=['POST'])
def filter():
    key = request.json.get("key")
    level = request.json.get("level")
    jobs = Job.filter_job(key, level)
    jsonList = []
    for job in jobs:
        jsonList.append({"id": job.id,
                         "title": job.title,
                         "description": job.description,
                         "experience_level": job.experience_level,
                         "owner_id": job.owner_id,
                         "budget": job.budget
                         })
    response = make_response(
        jsonify(jsonList),
        200
    )
    response.headers["Content-Type"] = "application/json"
    return response


@job_bp.route('/delete', methods=['POST'])
def delete():
    id = request.json.get("id")
    job = db.session.query(Job).filter(Job.id == id).first()

    if not len(job.contract):
        for proposal in job.proposals:
            db.session.delete(proposal)

        db.session.delete(job)
        db.session.commit()

    return ""


@job_bp.route('/uploadfile', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return ""

    file = request.files['file']
    if file and file.filename:
        file_id = file_mgr.save(file)
        return json.dumps({'status': 'success', 'file_id': file_id})

    return json.dumps({'status': 'failure'})
