from flask import Flask, render_template, request, redirect, url_for
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)

# secret key
app.config["SECRET_KEY"] = "your_secret_key_here"

# database settings
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fitness.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db creater
db.init_app(app)

# login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# user load
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# home
@app.route("/")
def home():
    return render_template("index.html")

#  sign up
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        # Check if user exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists"

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("signup.html")

# log in
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))

        return "Invalid username or password"

    return render_template("login.html")

# dashboard 
@app.route("/dashboard")
@login_required
def dashboard():
    return f"Welcome {current_user.username}!"

# log out
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

# create the db tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)