import os
from flask import Blueprint, render_template, request, jsonify, make_response, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from uuid import uuid4
from utils import FileManager
from model import User, Job, UserType, Proposal, Attachment, File, db
from payment_gateway import ChapaPaymentHandler


payment_bp = Blueprint('payment_bp', __name__,
                       static_folder='static', template_folder='templates')

file_mgr = FileManager(os.getenv('UPLOAD_FOLDER'))

payment_handler: ChapaPaymentHandler = ChapaPaymentHandler(
    os.getenv('CHAPA_SECRET_KEY'))


@payment_bp.route("/", methods=["POST"])
@login_required
def deposite():
    amount = request.form.get("amount")

    ref = f'TX-{uuid4()}'
    
    checkout_url = payment_handler.generate_checkout_url({
        'amount': amount,
        'currency': 'ETB',
        'email': current_user.email,
        'first_name': current_user.firstname,
        'last_name': current_user.lastname,
        'tx_ref': ref,
        'callback_url': url_for('payment_bp.verify_transaction', _external=True),
        'return_url': url_for('home', _external=True),
        'customization[title]': 'Freelancers',
        'customization[description]': 'Send payment'
    })

    if checkout_url:
        return redirect(checkout_url)
    return redirect(url_for('finance'))


@payment_bp.route("/verify")
def verify_transaction():
    trx_ref = request.args.get("trx_ref")

    if payment_handler.verify_transaction(trx_ref):
        data = payment_handler.get_transaction_data(trx_ref)
        user = User.get_by_email(data['email'])
        user.balance += data["amount"]
        db.session.commit()

        return jsonify(True)
    return jsonify(False)


# @payment_bp.route("/escrow", method=["POST"])
# def create_escrow():
#     request.json.get("job_id")

