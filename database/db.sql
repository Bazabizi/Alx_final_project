DROP DATABASE IF EXISTS FreelancePlatform;

CREATE DATABASE FreelancePlatform;

USE FreelancePlatform;


CREATE TABLE User(
    id INT PRIMARY KEY AUTO_INCREMENT,
    firstname VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    `password` VARCHAR(300) NOT NULL,
    date_of_birth DATETIME NOT NULL,
    user_type ENUM('FREELANCER', 'EMPLOYER'),
    token VARCHAR(200),
    balance FLOAT DEFAULT 0,
    resume_id VARCHAR(36)
);


CREATE TABLE Chat(
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_1 INT NOT NULL, -- chat initiator
    user_2 INT NOT NULL,

    FOREIGN KEY (user_1) REFERENCES User(id),
    FOREIGN KEY (user_2) REFERENCES User(id)
);

CREATE TABLE `Message`(
    id INT AUTO_INCREMENT,
    chat_id INT NOT NULL,
    sender_id INT NOT NULL,
    time_stamp DATETIME NOT NULL DEFAULT NOW(),

    content_type ENUM('TEXT', 'FILE', 'EVENT') default 'TEXT',
    content VARCHAR(4000) NOT NULL,

    FOREIGN KEY (chat_id) REFERENCES Chat(id),
    FOREIGN KEY (sender_id) REFERENCES User(id),
    PRIMARY KEY (id, chat_id)    
);

CREATE TABLE `File`(
    id CHAR(36) PRIMARY KEY,
    file_name VARCHAR(30),
    file_path VARCHAR(260),
    mime_type VARCHAR(128) 
);

CREATE TABLE Job (
    id CHAR(36) PRIMARY KEY,
    title VARCHAR(50) NOT NULL,
    `description` VARCHAR(500) NOT NULL,
    experience_level ENUM('ENTRY', 'INTERMEDIATE', 'EXPERT') NOT NULL,
    attachment_id CHAR(36),
    budget float,
    owner_id int not null,
    post_time DATETIME not null DEFAULT NOW()
);

CREATE TABLE Contract (    
    id CHAR(36) PRIMARY KEY,
    job_id CHAR(36) NOT NULL,
    worker_id INT NOT NULL,
    deadline DATETIME NOT NULL,   
    `status` CHAR(1),

    FOREIGN KEY (worker_id) REFERENCES User(id),
    FOREIGN KEY (job_id) REFERENCES Job(id)    
);

CREATE TABLE Escrow (
    id CHAR(36) PRIMARY KEY,
    contract_id CHAR(36) NOT NULL,
    amount FLOAT NOT NULL,
    date_of_initiation DATETIME NOT NULL DEFAULT NOW(),

    FOREIGN KEY (contract_id) REFERENCES Contract(id)
);

CREATE TABLE `Attachment`(
    id CHAR(36) NOT NULL,
    file_id CHAR(36) NOT NULL,

    FOREIGN KEY (file_id) REFERENCES `File`(id),
    PRIMARY KEY (id, file_id)
);

CREATE TABLE User_balance (
    user_id INT PRIMARY KEY,
    amount FLOAT NOT NULL DEFAULT 0
);

CREATE TABLE Proposal(
    worker_id INT not null,
    job_id CHAR(36) not null,
    attachment_id CHAR(36),
    content varchar(500),
    sent_time datetime not null,
    
    foreign key (worker_id) references User(id),
    foreign key (job_id) references Job(id),
    foreign key (attachment_id) references Attachment(id),
    PRIMARY Key (worker_id, job_id)
);

CREATE TABLE Work(
    id char(36) PRIMARY KEY,
    contract_id CHAR(36) NOT NULL,
    attachment_id CHAR(36),
    submission_date DATETIME default now(),

    foreign key (contract_id) references `Contract`(id),
    foreign key (attachment_id) references Attachment(id)    
);