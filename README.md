🎓 Classroom Management System

Web-Based Classroom Platform Built with Flask (Semester Project – Group of 4)



👥 <b>Team Members<b>

| Member                    | GitHub Profile                               |
| ------------------------- | -------------------------------------------- |
| Yuvraj Yadav              | https://github.com/Yuvraj-Yadav-dev          |
| Mayuresh Sangale          | https://github.com/mayurloading              |
| Dhwani Shetty             | https://github.com/DhwaniShetty              |
| Siddhantaditiyaa Vettakal | https://github.com/siddhanthaditiyaa-beep    |



 📌 <b>Project Overview<b>

The <b>Classroom Management System<b> is a web-based platform built using <b>Flask<b>,<b>Flask-SQLAlchemy<b>, and <b>Flask-Login<b> .
It provides a simple yet effective environment for teachers and students to interact digitally.

The application supports:

* Teachers creating classes
* Students joining classes
* Uploading and managing notes
* Creating and submitting assignments
* Tracking submissions
* Secure user login and role-based dashboards

The project automatically initializes the database using:

with app.app_context():
    db.create_all()


🌟 <b>Key Features<b>

 👩‍🏫 Teacher Module

* Create classes with unique class codes
* Upload, edit, and delete notes
* Create and update tasks/assignments
* View assignment submissions from students
* Delete classes along with related data

 👨‍🎓 Student Module

* Join classes using class codes
* View class notes and tasks
* Submit assignments
* Edit or delete their submissions
* Leave classes anytime

 🔐 Authentication

* Register & login system
* Role-based access control (Teacher/Student)
* Session management using Flask-Login

 📁 File Management

* Secure file uploads using `secure_filename()`
* Upload folder auto-created
* Supports notes and task submissions


🛠 <b>Technology Stack<b>

| Category       | Technologies            |
| -------------- | ----------------------- |
| Backend        | Flask, Python           |
| Database       | SQLite (SQLAlchemy ORM) |
| Authentication | Flask-Login             |
| Templates      | HTML, CSS, Jinja2       |
| File Handling  | Werkzeug                |

---

📂 <b>Folder Structure<b>

project/
│── app.py
│── templates/
│   ├── register.html
│   ├── login.html
│   ├── dashboard_student.html
│   ├── dashboard_teacher.html
│   ├── create_class.html
│   ├── view_class.html
│   ├── upload_note.html
│   ├── create_task.html
│   └── ...
│── static/
│── uploads/          # Auto-created for uploaded files
│── database.db       # Auto-generated on first run
│── README.md


 ⚙️ <b>Installation & Setup<b>
 
 1️⃣ Clone or Download the Project

git clone <repository-url>
cd project

 2️⃣ Install Required Packages

pip install flask flask_sqlalchemy flask_login

 3️⃣ Run the Application

python app.py


4️⃣ Access in Browser

http://127.0.0.1:5000/


The database tables are created automatically thanks to:
with app.app_context():
    db.create_all()


🧱 <b>Database Models Overview<b>

🔹 User

Stores student/teacher details.

🔹 Classes

Created by teachers. Each class has a unique code.

🔹 ClassMembers

Links students with classes.

🔹 Notes

Files uploaded by teachers.

🔹 Tasks

Assignments created by teachers.

🔹 TaskSubmissions

Assignment uploads submitted by students.


🧭 <b>Major Application Routes<b>

| Route                | Role          | Description             |
| -------------------- | ------------- | ----------------------- |
| `/register`          | All           | User Registration       |
| `/login`             | All           | User Login              |
| `/dashboard_teacher` | Teacher       | Teacher Home            |
| `/dashboard_student` | Student       | Student Home            |
| `/create_class`      | Teacher       | Create a Class          |
| `/join_class`        | Student       | Join a Class using Code |
| `/upload_note`       | Teacher       | Upload Study Notes      |
| `/create_task`       | Teacher       | Create Assignments      |
| `/submit_task`       | Student       | Submit Assignment       |
| `/uploads/<file>`    | Authenticated | View Uploaded Files     |
| `/logout`            | All           | Logout                  |




📜 <b> Conclusion <b>

This Classroom Management System demonstrates how <b>Flask<b> can be used to build a fully functional web application with:

* User authentication
* Role-based dashboards
* Database-driven components
* File uploads
* CRUD operations
* Real classroom-like interactions

It fulfills all requirements of a <b>college-level<b> semester project and can be expanded further with analytics, grading, chat, or notifications.

📄 License

This project is for academic and learning purposes only.

