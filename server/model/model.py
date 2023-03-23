from __future__ import annotations

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm.exc import NoResultFound

from typing import Optional

db = SQLAlchemy()


class UserType:
    """Data class to represent types of users involved in the system"""

    FREELANCER = 'FREELANCER'
    EMPLOYER = 'EMPLOYER'


class ExperienceLevel:
    """Data class to represent experience level required by the job."""

    ENTRY = 'ENTRY'
    INTERMEDIATE = 'INTERMEDIATE'
    EXPERT = "EXPERT"


class ContractStatus:
    """Data class to represent whether contract is accepted or rejected"""

    ACCEPTED = 'A'
    REJECTED = 'R'
    FINISED = 'F'
    CANCELLED = 'C'
    PENDING_CANCEL = 'P'


class ContentType:
    """Data class to represent types of message contents supported by messaging functionality"""

    TEXT = 'TEXT'
    FILE = 'FILE'
    EVENT = 'EVENT'


class User(db.Model, UserMixin):
    """
    User database model

    Parameters:
        id (int): unique id that identify single user
        firstname (str): user's first name
        lastname (str): user's last name
        email (str): user's email
        password (str): user's hashed password
        date_of_birth (datetime): user's birth date
        user_type (str): one of supported user types specified under UserType class        
        token (str): user's authentication token
        balance (float): the amount of money a user has in the system
        initiated_chats (list[Chat]): list of Chat objects initiated by this user
        joined_chats (list[Chat]): list of Chat objects joined by this user
        resume_id (str): file id referencing user resume
    """

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    date_of_birth = db.Column(db.DateTime)
    user_type = db.Column(db.Enum(UserType.FREELANCER, UserType.EMPLOYER))
    token = db.Column(db.String(200))
    balance = db.Column(db.Float, default=0)
    resume_id = db.Column(db.String(36))

    @property
    def chats(self):
        """Gets all chats associated with user

        Returns:
            list: list of Chat objects
        """

        all_chats = []
        all_chats.extend(self.initiated_chats)
        all_chats.extend(self.joined_chats)
        return all_chats

    @staticmethod
    def get(user_id: int) -> Optional[User]:
        """Gets user by id

        Args:
            user_id (int): user id

        Returns:
            User: user object if user is found, None otherwise
        """

        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """Gets user by email

        Args:
            email (int): user email

        Returns:
            User: user object if user is found, None otherwise
        """
        return User.query.filter_by(email=email).first()

    def get_posted_jobs(self):
        """Get jobs posted by an Employer

        Args:
            id (int): id of employer
        Returns:
            jobs (list): list of jobs with owner_id of id
        """

        jobs = Job.query.filter(
            Job.owner_id == self.id
        ).all()

        return jobs

    def get_fund_in_escrow(self):
        if self.user_type == UserType.FREELANCER:
            amount = 0
            for contract in self.contracts:
                if contract.status in [ContractStatus.FINISED, ContractStatus.REJECTED]:
                    continue
                for e in contract.escrow:
                    amount += e.amount

            return float(amount)

        else:
            amount = 0
            for job in self.get_posted_jobs():
                for contract in Contract.query.filter_by(job_id=job.id).all():
                    if contract.status in [ContractStatus.FINISED, ContractStatus.REJECTED]:
                        continue
                    for e in contract.escrow:
                        amount += e.amount
            return float(amount)

    def get_contracts(self):
        if self.user_type == UserType.FREELANCER:
            return self.contracts

        contracts = []
        for job in self.get_posted_jobs():
            for contract in Contract.query.filter_by(job_id=job.id).all():
                contracts.append(contract)

        return contracts

    def __repr__(self):
        return f"User(id={self.id}, email={self.email})"


class Chat(db.Model):
    """Chat database model

    Parameters:
        id (str): unique chat id
        user_1 (str): chat initiator id
        user_2 (str): second user id in chat
        u1 (User): chat initiator User object
        u2 (User): second User object
        messages (list): list of messages sent in the chat
    """

    id = db.Column(db.Integer, primary_key=True)
    user_1 = db.Column(db.Integer, db.ForeignKey(User.id))
    user_2 = db.Column(db.Integer, db.ForeignKey(User.id))

    u1 = db.relationship(User, backref='initiated_chats',
                         foreign_keys=[user_1])
    u2 = db.relationship(User, backref='joined_chats',
                         foreign_keys=[user_2])

    @staticmethod
    def get(chat_id: int) -> Optional[User]:
        """Gets chat by id

        Args:
            chat_id (int): chat id

        Returns:
            Chat: chat object if chat is found, None otherwise
        """

        return Chat.query.filter_by(id=chat_id).first()

    @staticmethod
    def get_chat(user_1, user_2):
        """Gets chat associating two users

        Args:
            user_1 (int): id of one user
            user_2 (int): id of other user

        Returns:
            Chat: chat object if chat associating the users is found, None otherwise
        """

        chat = Chat.query.filter(
            db.or_(
                db.and_(
                    Chat.user_1 == user_1,
                    Chat.user_2 == user_2
                ),
                db.and_(
                    Chat.user_1 == user_2,
                    Chat.user_2 == user_1
                )
            )
        )
        return chat.first()

    def __repr__(self):
        return f"Chat(id={self.id}, user_1={self.u1.firstname}, user_2={self.u2.lastname})"


class Message(db.Model):
    """Message database model

    Parameters:
        id (str): unique message id
        chat_id (str): chat containing two users        
        sender_id (str): the user id of sender of the message
        time_stamp (datetime): sent time
        content (str): the message sent
        content_type (str): specifies how to interpret the content
            (default is 'TEXT')
        sender (User): sender of the message
        chat (Chat): the chat the message belongs to
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chat_id = db.Column(db.Integer, db.ForeignKey(Chat.id), primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey(User.id))
    time_stamp = db.Column(db.DateTime, default=datetime.now)
    content = db.Column(db.String(200))
    content_type = db.Column(
        db.Enum(ContentType.TEXT, ContentType.FILE, ContentType.EVENT))

    sender = db.relationship(User, foreign_keys=[sender_id])
    chat = db.relationship(Chat, backref=db.backref(
        'messages', order_by='Message.time_stamp'), foreign_keys=[chat_id])

    @property
    def receiver(self):
        """Gets receiver of message

        Returns:
            User: the recepient of message
        """

        if self.chat.u1.id == self.sender_id:
            return self.chat.u2
        return self.chat.u1

    def __repr__(self):
        return f"{self.content_type.title()}(id={self.id}, chat_id={self.chat_id}, sender={self.sender.firstname}, receiver={self.receiver.firstname}, content={self.content})"


class File(db.Model):
    """File database model

    Parameters:
        id (str): unique file id
        file_name (str): name of file
        file_path (str): path to file on local drive
        mime_type (str): MIME type of file
    """

    id = db.Column(db.String(36), primary_key=True)
    file_name = db.Column(db.String(30))
    file_path = db.Column(db.String(260))
    mime_type = db.Column(db.String(128))

    @staticmethod
    def get(file_id: str) -> Optional[File]:
        """Gets file by id

        Args:
            file_id (str): file id

        Returns:
            File: file object if file is found, None otherwise
        """

        return File.query.filter_by(id=file_id).first()

    def __repr__(self):
        return f"File(id={self.id}, file_name={self.file_name}, mime_type={self.mime_type})"


class Attachment(db.Model):
    """Job database model

    Parameters:
        id (str): unique id        
        file_id (str): id for file
    """

    id = db.Column(db.String(36), primary_key=True)
    file_id = db.Column(db.String(36), db.ForeignKey(
        File.id), primary_key=True)

    file = db.relationship(File)


class Job(db.Model):
    """Job database model

    Parameters:
        id (str): unique job id
        title (str): title of job
        description (str): description about the job
        experience_level (str): required experience level
        attachment_id (str): unique attachment id
        budget (float): budget allocated for the job
        owner_id (int): id of job poster
        post_time (datetime): time of job post
        attachment (Attachment): attachment file
        owner (User): job poster
    """

    id = db.Column(db.String(36), primary_key=True)
    title = db.Column(db.String(50))
    description = db.Column(db.String(500))
    experience_level = db.Column(
        db.Enum(
            ExperienceLevel.ENTRY,
            ExperienceLevel.INTERMEDIATE,
            ExperienceLevel.EXPERT))
    attachment_id = db.Column(db.String(50), db.ForeignKey(Attachment.id))
    budget = db.Column(db.Float)
    owner_id = db.Column(db.Integer, db.ForeignKey(User.id))
    post_time = db.Column(db.DateTime, default=datetime.now)

    attachments = db.relationship(Attachment, foreign_keys=[attachment_id])
    owner = db.relationship(User, foreign_keys=[owner_id])

    @staticmethod
    def get(job_id: str) -> Optional[Job]:
        """Queries job from data base

        Args:
            job_id (str): job id

        Returns:
            Job: Job object if job is found or None
        """
        try:
            job = Job.query.filter_by(id=job_id).first()
            return job
        except:
            return None

    @staticmethod
    def filter_job(key: str, level) -> Optional[Job]:
        """Filters job using a key

        Args:
            key (str): key word in - name of job
                                   - description of job
                                   - experience level of job
        Returns:
                Job: job object if job associated with they key is found, None otherwise
        """

        if level:
            query = db.and_(
                db.or_(
                    Job.title.like(f"%{key}%"),
                    Job.description.like(f"%{key}%"),
                    Job.budget.like(f"%{key}%")
                ),

                Job.experience_level == level
            )
        else:
            query = db.or_(Job.title.like(f"%{key}%"),
                           Job.description.like(f"%{key}%"),
                           Job.experience_level.like(f"%{key}%"),
                           Job.budget.like(f"%{key}%"))

        job = Job.query.filter(query).all()

        return job

    @staticmethod
    def get_jobs(owner_id: int) -> Optional[Job]:
        """Gets jobs owned by user

        Args:
            owner_id (int): user id

        Returns:
                Job: job object if job owned by user is found, None otherwise
        """

        jobs = Job.query.filter(
            Job.owner_id == owner_id
        )
        return jobs

    @staticmethod
    def get_all_jobs() -> list[Job]:
        """Gets all posted Jobs
        Args:
            None
        Returns:
            list: list of jobs
        """
        job = Job.query.all()
        return job

    @staticmethod
    def deleteJob(id: str) -> None:
        """Deletes a job post of an employer
        Args: 
            id (str): Job id
        Returns:
            None
        """
        Job.query.filter_by(id=id).delete()

    def __repr__(self):
        return f"Job(id={self.id}, job_title={self.title}, experience_level={self.experience_level}, job_owner={self.owner_id}, post_time={self.post_time}, job_description={self.description})"


class Contract(db.Model):
    """Contract is created when worker and job poster reach on agreement

    Parameters:
        id (str): unique contract id
        job_id (str): the job id
        worker_id (str): the freelancer id
        deadline (datetime): last date for work submission
        status (string): accepted or rejected by the worker

    `If the contract is not fullfilled before deadline, fund in escrow will 
    be refunded to job owner`
    """

    id = db.Column(db.String(36), primary_key=True)
    job_id = db.Column(db.String(36), db.ForeignKey(Job.id))
    worker_id = db.Column(db.String(36), db.ForeignKey(User.id))
    deadline = db.Column(db.DateTime)
    status = db.Column(db.String(1))

    job = db.relationship(Job, backref='contract',
                          foreign_keys=[job_id], uselist=False)
    worker = db.relationship(User, backref='contracts',
                             foreign_keys=[worker_id])

    @staticmethod
    def get(contract_id: str) -> Optional[User]:
        """Gets user by id

        Args:
            contract_id (str): user id

        Returns:
            Contract: user object if user is found, None otherwise
        """

        return Contract.query.filter_by(id=contract_id).first()

    def already_exists(job_id, worker_id):
        try:
            contract = Contract.query.filter(Contract.job_id == job_id,
                                             Contract.worker_id == worker_id,
                                             db.or_(
                                                 Contract.status == ContractStatus.ACCEPTED,
                                                 Contract.status == None)
                                             ).one()
            if contract:
                return True
        except NoResultFound:
            return False


class Escrow(db.Model):
    """Escrow holds funds transfered from job owner to the system.
    When contract is fullfilled fund will be released to worker.

    Parameters:
        id (str): unique escrow id
        contract_id (str): the contract id
        amount (float): amount (in ETB) to be trasfered to worker when contract is fullfilled
        date_of_initiation (datetime): date when escrow was funded
    """

    id = db.Column(db.String(36), primary_key=True)
    contract_id = db.Column(db.String(36), db.ForeignKey(Contract.id))
    amount = db.Column(db.Float)
    date_of_initiation = db.Column(db.DateTime, default=datetime.now)

    contract = db.relationship(Contract, backref='escrow', uselist=False)

    @staticmethod
    def get(escrow_id: str) -> Optional[Escrow]:
        """Gets escrow by id

        Args:
            escrow_id (str): escrow id

        Returns:
            Escrow: escrow object if escrow is found, None otherwise
        """

        return Escrow.query.filter_by(id=escrow_id).first()

    def __repr__(self):
        return f"Escrow(id={self.id}, contract={self.contract_id}, amount={self.amount})"


class Proposal(db.Model):
    """Proposal is created when worker applies for a job

    Parameters:
        job_id (str): unique job id
        worker_id (str): the freelancer id
        content (str): cover letter highlighting freelancers skills
        attachment_id (str): attached files
        sent_time (datetime): date of application
    """

    worker_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)
    job_id = db.Column(db.String(36), db.ForeignKey(Job.id), primary_key=True)
    attachment_id = db.Column(
        db.String(36), db.ForeignKey(Attachment.id))
    content = db.Column(db.String(500))
    sent_time = db.Column(db.DateTime, default=datetime.now)

    job = db.relationship(Job, backref='proposals',
                          foreign_keys=[job_id])
    sender = db.relationship(User, backref='proposals',
                             foreign_keys=[worker_id])
    attachments = db.relationship(Attachment, foreign_keys=[attachment_id])


class Work(db.Model):
    """Work is created when worker submits a completed work for a contract

    Parameters:
        id (str): unique id for submission
        contract_id (str): unique contract id        
        attachment_id (str): attached files
        submission_date (datetime): date of submission
    """

    id = db.Column(
        db.Integer, primary_key=True)
    contract_id = db.Column(
        db.String(36), db.ForeignKey(Contract.id))
    attachment_id = db.Column(
        db.String(36), db.ForeignKey(Attachment.id))
    submission_date = db.Column(
        db.DateTime, default=datetime.now, primary_key=True)

    contract = db.relationship(Contract, backref='submissions',
                               foreign_keys=[contract_id])
    attachment = db.relationship(Attachment, foreign_keys=[
                                 attachment_id], uselist=True)


# class UserBalance(db.Model):
#     """Represents user balance in the system

#     Parameters:
#         user_id (int): the user id
#         balance (float): the amount of money (in ETB) in the balance
#     """

#     user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)
#     amount = db.Column(db.Float)

#     user = db.relationship(User, backref=db.backref("balance", uselist=False), uselist=False)

#     @staticmethod
#     def get(user_id: str) -> Optional[UserBalance]:
#         """Gets balance of user

#         Args:
#             user_id (str): user id

#         Returns:
#             UserBalance: UserBalance object if user is found, None otherwise
#         """

#         return UserBalance.query.filter_by(id=user_id).first()

#     def __repr__(self):
#         return f"UserBalance(user_id={self.user_id}, balance={self.amount})"
