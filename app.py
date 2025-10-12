from flask import Flask , render_template , request , redirect ,flash ,get_flashed_messages ,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,LoginManager,login_user, login_required, logout_user,current_user
from werkzeug.utils import secure_filename
import os, random, string

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
app.config['SECRET_KEY'] = 'my_secret'
db = SQLAlchemy(app)


app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100),nullable =False)
    email = db.Column(db.String(100),unique =True)
    password = db.Column(db.String(100), unique =True,nullable =False)
    role = db.Column(db.String(20),nullable =False)

class Classes(db.Model):
   id = db.Column(db.Integer,primary_key=True)
   class_name = db.Column(db.String(50),nullable=False)
   teacher_id = db.Column(db.Integer,db.ForeignKey('user.id'))
   class_code = db.Column(db.String(20),nullable=False,unique=True)

class ClassMembers(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
   student_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    title = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(100), nullable=False)

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(100), nullable=True)  
    due_date = db.Column(db.String(20), nullable=True)

class TaskSubmissions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id): 
    return User.query.get(int(user_id))

@app.route('/')
def index():
   return render_template('register.html')

@app.route('/register',methods =["POST","GET"])
def register():
   if request.method == 'POST':
      username = request.form['username']
      email = request.form['email']
      password = request.form['password']
      role = request.form['role']

      existing_user = User.query.filter_by(email=email).first()
      if existing_user:
         flash("Email already registered!. Use another.")
         return redirect(url_for('register'))
      new_user = User(username = username,email=email,password = password,role=role)
      db.session.add(new_user)
      db.session.commit()
      flash("Registration successful! Please login.")
      return redirect(url_for('login'))
   return render_template("register.html")

# login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            login_user(user)
            flash("Login Successful")
            if user.role == 'student':   
                return redirect(url_for('dashboard_student'))
            elif user.role == 'teacher':
                return redirect(url_for('dashboard_teacher'))
            else:
                flash("Role not recognized!")
                return redirect(url_for('login'))
        else:
            flash("Invalid User email or password.")
    return render_template("login.html")
     
# dashboard of Teacher and Student.
@app.route('/dashboard_teacher')
@login_required
def dashboard_teacher():
   if current_user.role == 'teacher':
      flash("Welcome!!")   
   classes = Classes.query.filter_by(teacher_id=current_user.id).all()
   return render_template('dashboard_teacher.html',classes = classes, name=current_user.username,email=current_user.email,role=current_user.role)

@app.route('/dashboard_student')
@login_required
def dashboard_student():
 if current_user.role == 'student':
  joined = ClassMembers.query.filter_by(student_id=current_user.id).all()
  my_classes = [Classes.query.get(c.class_id) for c in joined]
  return render_template('dashboard_student.html', classes=my_classes,name=current_user.username,email=current_user.email,role=current_user.role)

#creating class
@app.route('/create_class', methods=['GET','POST'])
@login_required
def create_class():
   if current_user.role == 'teacher':
      if request.method =='POST':
         class_name = request.form['class_name']
         code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))  
         new_class = Classes(class_name=class_name,teacher_id=current_user.id,class_code=code)
         db.session.add(new_class)
         db.session.commit()
         flash(f"Class created! Code: {code}")
         return redirect(url_for('dashboard_teacher'))
   return render_template('create_class.html')

# uploading notes
@app.route('/upload_note/<int:class_id>', methods=['GET', 'POST'])
@login_required
def upload_note(class_id):
    if current_user.role != 'teacher':
        flash("Access denied.")
        return redirect(url_for('dashboard_teacher'))
    if request.method == 'POST':
        title = request.form['title']
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            note = Notes(class_id=class_id, title=title, filename=filename)
            db.session.add(note)
            db.session.commit()
            flash("Note uploaded successfully!")
            return redirect(url_for('view_class', class_id=class_id))
    return render_template('upload_note.html', class_id=class_id)

# Updating the  notes
@app.route('/update_note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def update_note(note_id):
    note = Notes.query.get_or_404(note_id)
    cls = Classes.query.get(note.class_id)
    if current_user.id != cls.teacher_id:
        flash("You can only edit your own class notes.")
        return redirect(url_for('view_class', class_id=cls.id))

    if request.method == 'POST':
        note.title = request.form['title']
        file = request.files.get('file')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            note.filename = filename  # update the filename

        db.session.commit()
        flash("Note updated successfully!")
        return redirect(url_for('view_class', class_id=cls.id))

    return render_template('update_note.html', note=note)

# Deleting the notes
@app.route('/delete_note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Notes.query.get_or_404(note_id)
    cls = Classes.query.get(note.class_id)
    
    if current_user.id != cls.teacher_id:
        flash("You can only delete your own class notes.")
        return redirect(url_for('view_class', class_id=cls.id))
    
    db.session.delete(note)
    db.session.commit()
    flash("Notes deleted successfully.")
    return redirect(url_for('view_class', class_id=cls.id))

# creating task 
@app.route('/create_task/<int:class_id>', methods=['GET', 'POST'])
@login_required
def create_task(class_id):
    if current_user.role == 'teacher':
      if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        file = request.files.get('file')
        filename = None
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        task = Tasks(class_id=class_id, title=title, description=description, filename=filename)
        db.session.add(task)
        db.session.commit()
        flash("Task created successfully!")
        return redirect(url_for('view_class', class_id=class_id))
    return render_template('create_task.html', class_id=class_id)

#updating the task
@app.route('/update_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    task = Tasks.query.get_or_404(task_id)
    cls = Classes.query.get(task.class_id)
    if current_user.id != cls.teacher_id:
        flash("You are not authorized to edit this task.")
        return redirect(url_for('view_class', class_id=cls.id))

    if request.method == 'POST':
        task.title = request.form.get('title', task.title)
        task.description = request.form.get('description', task.description)

        file = request.files.get('file')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            task.filename = filename

        db.session.commit()
        flash("Task updated successfully!")
        return redirect(url_for('view_class', class_id=task.class_id))

    return render_template('update_task.html', task=task)


# Deleting the task
@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Tasks.query.get_or_404(task_id)
    cls = Classes.query.get(task.class_id)

    if current_user.id != cls.teacher_id:
        flash("You are not authorized to delete this task.")
        return redirect(url_for('view_class', class_id=cls.id))

    if task.filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], task.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    db.session.delete(task)
    db.session.commit()

    flash("Task deleted successfully!")
    return redirect(url_for('view_class', class_id=cls.id))

#  viewing classes created.
@app.route('/class/<int:class_id>')
@login_required
def view_class(class_id):
    cls = Classes.query.get_or_404(class_id)

    if current_user.role == 'student':
        membership = ClassMembers.query.filter_by(class_id=class_id, student_id=current_user.id).first()
        if not membership:
            flash("You are not a member of this class.")
            return redirect(url_for('dashboard_student'))

    notes = Notes.query.filter_by(class_id=class_id).all()
    tasks = Tasks.query.filter_by(class_id=class_id).all()

    task_submissions = {}
    for task in tasks:
        submissions = TaskSubmissions.query.filter_by(task_id=task.id).all()
        submissions_with_names = []
        for sub in submissions:
            student = User.query.get(sub.student_id)
            submissions_with_names.append({'filename': sub.filename, 'student_name': student.username})
        task_submissions[task.id] = submissions_with_names
    student_submissions = {}
    if current_user.role == 'student':
        for task in tasks:
            sub = TaskSubmissions.query.filter_by(task_id=task.id, student_id=current_user.id).first()
            if sub:
                student_submissions[task.id] = sub

    return render_template('view_class.html', cls=cls, notes=notes, tasks=tasks, task_submissions=task_submissions, student_submissions=student_submissions)

# Edit submission
@app.route('/edit_submission/<int:submission_id>', methods=['GET', 'POST'])
@login_required
def edit_submission(submission_id):
    submission = TaskSubmissions.query.get_or_404(submission_id)
    
    if submission.student_id != current_user.id:
        flash("You are not authorized to edit this submission.")
        return redirect(url_for('dashboard_student'))

    # fetch the related task
    task = Tasks.query.get(submission.task_id)
    
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            submission.filename = filename
            db.session.commit()
            flash("Submission updated successfully!")
            return redirect(url_for('view_class', class_id=task.class_id))

    # pass both submission and task to template
    return render_template('edit_submission.html', submission=submission, task=task)



# Delete submission
@app.route('/delete_submission/<int:submission_id>', methods=['POST'])
@login_required
def delete_submission(submission_id):
    submission = TaskSubmissions.query.get_or_404(submission_id)

    if submission.student_id != current_user.id:
        flash("You are not authorized to delete this submission.")
        return redirect(url_for('dashboard_student'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], submission.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(submission)
    db.session.commit()
    flash("Submission deleted successfully!")

    task = Tasks.query.get(submission.task_id)
    return redirect(url_for('view_class', class_id=task.class_id))



# joining the classes created.
@app.route('/join_class', methods=['GET', 'POST'])
@login_required
def join_class():
    if current_user.role != 'student':
        flash("Only students can join classes.")
        return redirect(url_for('dashboard_teacher'))
    
    if request.method == 'POST':
        class_code = request.form['class_code']
        cls = Classes.query.filter_by(class_code=class_code).first()
        if not cls:
            flash("Invalid class code.")
            return redirect(url_for('dashboard_student'))
        already = ClassMembers.query.filter_by(student_id=current_user.id, class_id=cls.id).first()
        if already:
            flash("You have already joined this class.")
            return redirect(url_for('dashboard_student'))
        
        membership = ClassMembers(student_id=current_user.id, class_id=cls.id)
        db.session.add(membership)
        db.session.commit()
        flash(f"Joined class '{cls.class_name}' successfully!")
        return redirect(url_for('dashboard_student'))

    return render_template('join_class.html')

#submitting the task.
@app.route('/submit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def submit_task(task_id):
    task = Tasks.query.get_or_404(task_id)

    if current_user.role != 'student':
        flash("Only students can submit tasks.")
        return redirect(url_for('dashboard_teacher'))

    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            submission = TaskSubmissions(
                task_id=task.id,
                student_id=current_user.id,
                filename=filename
            )
            db.session.add(submission)
            db.session.commit()
            flash("Task submitted successfully!")
            return redirect(url_for('view_class', class_id=task.class_id))

    submissions = TaskSubmissions.query.filter_by(task_id=task.id, student_id=current_user.id).all()
    return render_template('submit_task.html', task_id=task.id, submissions=submissions)



# Deleting the class
@app.route('/delete_class/<int:class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    cls = Classes.query.get_or_404(class_id)

    if current_user.id != cls.teacher_id:
        flash("You are not authorized to delete this class.")
        return redirect(url_for('view_class', class_id=class_id))

    Notes.query.filter_by(class_id=class_id).delete()
    tasks = Tasks.query.filter_by(class_id=class_id).all()
    for task in tasks:
        TaskSubmissions.query.filter_by(task_id=task.id).delete()
    Tasks.query.filter_by(class_id=class_id).delete()
    ClassMembers.query.filter_by(class_id=class_id).delete()
    db.session.delete(cls)
    db.session.commit()

    flash("Class deleted successfully!")
    return redirect(url_for('dashboard_teacher'))


# leaving the class (Students)
@app.route('/leave_class/<int:class_id>', methods=['POST'])
@login_required
def leave_class(class_id):
    if current_user.role != 'student':
        flash("Only students can leave classes.")
        return redirect(url_for('dashboard_teacher'))
    
    membership = ClassMembers.query.filter_by(student_id=current_user.id, class_id=class_id).first()

    if membership:
        db.session.delete(membership)
        db.session.commit()
        flash("You have left the class.")
    else:
        flash("You are not a member of this class.")
    
    return redirect(url_for('dashboard_student'))

from flask import send_from_directory

# To access the uploaded files
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))

if __name__ == "__main__":
 with app.app_context():
     db.create_all()
