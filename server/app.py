import os
from dotenv import load_dotenv

from werkzeug.security import generate_password_hash
from flask import Flask, render_template, request, url_for, redirect, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError

from model import User, UserType, db, File, Message, ContentType
from chat import chat_bp, socketio
from docs.doc import doc_bp
from job import job_bp
from proposal import proposal_bp
from payment import payment_bp
from contract import contract_bp
from auth import AuthenticationManager
from utils import FileManager

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')

file_mgr = FileManager(os.getenv('UPLOAD_FOLDER'))

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

socketio.init_app(app)

app.register_blueprint(chat_bp, url_prefix='/messages')
app.register_blueprint(doc_bp, url_prefix='/docs')
app.register_blueprint(job_bp, url_prefix='/job')
app.register_blueprint(proposal_bp, url_prefix='/proposal')
app.register_blueprint(payment_bp, url_prefix='/payment')
app.register_blueprint(contract_bp, url_prefix='/contract')

auth_manager = AuthenticationManager(os.getenv('FLASK_SECRET_KEY'))


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/finance")
@login_required
def finance():
    if current_user.user_type == UserType.EMPLOYER:
        return render_template('emp_finance.html')
    return render_template('free_finance.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        redirect_url = request.form.get('redirect', url_for('home'))

        if auth_manager.verify_credentials(email, password):
            user = User.get_by_email(email)
            user.token = auth_manager.generate_auth_token(user.id)
            db.session.commit()

            login_user(user)
            return redirect(redirect_url)
        else:
            return render_template("login.html", message="Invalid credentials")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    user = User.get(current_user.id)
    user.token = None
    db.session.commit()
    logout_user()

    return redirect(url_for('home'))


@app.route("/register")
def register():
    return render_template("choose_account.html")


@app.route("/register-freelancer", methods=["GET", "POST"])
def register_freelancer():
    if request.method == "POST":
        fname = request.form.get("firstname")
        lname = request.form.get("lastname")
        date = request.form.get("date")
        email = request.form.get("email")
        password = request.form.get("password")
        resume = request.files.get("file")

        file_id = None
        if resume:
            file_id = file_mgr.save(resume)

        new_user = User(firstname=fname, lastname=lname,
                        email=email, password=generate_password_hash(password),
                        date_of_birth=date, resume_id=file_id, user_type=UserType.FREELANCER)

        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return render_template("register.html", message="Email already exists", register_handler="register_freelancer")

        return redirect(url_for('login'))

    return render_template("register.html", register_handler="register_freelancer")


@app.route("/register-employer", methods=["GET", "POST"])
def register_employer():
    if request.method == "POST":
        fname = request.form.get("firstname")
        lname = request.form.get("lastname")
        date = request.form.get("date")
        email = request.form.get("email")
        password = request.form.get("password")

        new_user = User(firstname=fname, lastname=lname,
                        email=email, password=generate_password_hash(password),
                        date_of_birth=date, user_type=UserType.EMPLOYER)

        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return render_template("register.html", message="Email already exists", register_handler="register_employer")

        return redirect(url_for('login'))

    return render_template("register.html", register_handler="register_employer")


@app.route('/files/<id>')
@login_required
def files(id):
    message = Message.query.filter_by(
        content_type=ContentType.FILE, content=id).first()
    return send_file(File.get(id).file_path)
    # if current_user.id in [message.chat.u1.id, message.chat.u2.id]:
    #     return send_file(File.get(id).file_path)

    # return "Unauthorize file access"


if __name__ == "__main__":
    socketio.run(app, debug=True)
