import os
from uuid import uuid4
from flask import Blueprint, render_template, request, jsonify, make_response, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from model import User, Job, ContractStatus, Contract, Escrow, UserType, Work, Attachment, db
from utils import FileManager


contract_bp = Blueprint('contract_bp', __name__,
                        static_folder='static', template_folder='templates')

file_mgr = FileManager(os.getenv('UPLOAD_FOLDER'))


@contract_bp.route("/", methods=["POST"])
@login_required
def create_contract():
    job_id = request.form.get("job_id")
    worker_id = request.form.get("worker_id")
    budget = request.form.get("budget")
    deadline = datetime.strptime(request.form.get("deadline"), "%Y-%m-%d")

    try:
        if current_user.balance < float(budget):
            return render_template("contract.html", message="Insufficient balance to set up escrow.", status=400)
    except:
        return render_template("contract.html", message="Insufficient balance to set up escrow.", status=400)

    job = Job.get(job_id)
    worker = User.get(worker_id)

    if job.owner.id != current_user.id:
        return redirect(url_for('login'))

    if job and worker and not Contract.already_exists(job_id, worker_id):
        contract_id = uuid4()

        new_contract = Contract(id=contract_id,
                                job_id=job_id, worker_id=worker_id, deadline=deadline)

        new_escrow = Escrow(id=uuid4(),
                            contract_id=contract_id, amount=float(budget))

        try:
            db.session.add(new_contract)
            db.session.add(new_escrow)
            current_user.balance -= float(budget)
            db.session.commit()

        except IntegrityError:
            return render_template("contract.html", message="Contract already exists.", status=400)

        return render_template("contract.html", status=200, worker=worker)

    return render_template("contract.html", message="Contract already exists.", status=400)


@contract_bp.route("/<contract_id>/<response>")
@login_required
def accept_or_reject_contract(contract_id, response):
    contract = Contract.get(contract_id)

    if contract.status != None:
        return "Unauthorized"

    if contract.worker_id == current_user.id:
        if response == "accept":
            contract.status = ContractStatus.ACCEPTED
            contract.escrow[0].date_of_initiation = datetime.now()
        elif response == "reject":
            contract.status = ContractStatus.REJECTED
            escrow = contract.escrow[0]
            employer = User.get(contract.job.owner_id)
            employer.balance += escrow.amount
            # db.session.delete(contract)
        db.session.commit()

        return redirect(url_for("contract_bp.contracts"))

    return "Unauthorized"


@contract_bp.route("/")
@login_required
def contracts():
    if current_user.user_type == UserType.EMPLOYER:
        return render_template("contract_employer.html")

    return render_template("contract_freelancer.html")


@contract_bp.route("/<contract_id>", methods=["POST"])
@login_required
def submit_work(contract_id):
    contract = Contract.get(contract_id)

    if not contract or contract.worker_id != current_user.id:
        return redirect(url_for("contract_bp.contracts"))

    files = request.files.getlist("files")

    attachment_id = None
    if files and files[0].filename:
        attachment_id = uuid4()

        for file in files:
            file_id = file_mgr.save(file)
            attachment = Attachment(id=attachment_id)
            attachment.file_id = file_id
            db.session.add(attachment)

    submission = Work(id=uuid4(), contract_id=contract_id,
                      attachment_id=attachment_id)
    db.session.add(submission)
    db.session.commit()

    return redirect(url_for("contract_bp.contracts"))


@contract_bp.route("/complete/<contract_id>", methods=["POST"])
@login_required
def close_contract(contract_id):
    contract = Contract.get(contract_id)

    if not contract or contract.job.owner_id != current_user.id:
        return redirect(url_for("contract_bp.contracts"))

    contract.status = ContractStatus.FINISED

    escrow = contract.escrow[0]

    worker = User.get(contract.worker_id)
    worker.balance += escrow.amount

    db.session.commit()

    return redirect(url_for("contract_bp.contracts"))


@contract_bp.route("/cancel/<contract_id>")
@login_required
def request_refund(contract_id):
    contract = Contract.get(contract_id)

    if not contract or contract.job.owner_id != current_user.id:
        return redirect(url_for("contract_bp.contracts"))

    contract.status = ContractStatus.PENDING_CANCEL

    db.session.commit()

    return render_template("request_refund.html", status=200, worker=contract.worker)


@contract_bp.route("/refund/<contract_id>/<response>")
@login_required
def accept_or_reject_refund(contract_id, response):
    contract = Contract.get(contract_id)
    print(contract, "<<<<<<<")
    if contract.status != ContractStatus.PENDING_CANCEL:
        return "Unauthorized"

    if contract.worker_id == current_user.id:
        if response == "accept":
            contract.status = ContractStatus.CANCELLED
            escrow = contract.escrow[0]
            employer = User.get(contract.job.owner_id)
            employer.balance += escrow.amount
            escrow.amount = 0
        elif response == "reject":
            contract.status = ContractStatus.ACCEPTED

            # db.session.delete(contract)
        db.session.commit()

        return redirect(url_for("contract_bp.contracts"))

    return "Unauthorized"
