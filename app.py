from flask import Flask , render_template , request , redirect ,flash ,get_flashed_messages ,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,LoginManager,login_user, login_required, logout_user,current_user


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'my_secret'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100),nullable =False)
    email = db.Column(db.String(100),unique =True)
    password = db.Column(db.String(100), unique =True,nullable =False)
    role = db.Column(db.String(20),nullable =False)

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
   
@app.route('/login',methods=['GET','POST'])   
def login():
   if request.method == 'POST':
      email = request.form['email']
      password = request.form['password']

      user = User.query.filter_by(email=email, password=password).first()

      if user:
         login_user(user)
         flash("Login Successful")
         return redirect(url_for('dashboard'))
      else:
         flash("Invalid User email or password.")
   return render_template("login.html")     

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username, email=current_user.email,role =current_user.role)

if __name__ == "__main__":
 with app.app_context():
     db.create_all()
app.run(debug=True) 