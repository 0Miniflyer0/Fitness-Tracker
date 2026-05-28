from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Workout, Exercise
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import date

app = Flask(__name__)

app.config["SECRET_KEY"] = "your_secret_key_here"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fitness.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists"
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("signup.html")

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

@app.route("/dashboard")
@login_required
def dashboard():
    workouts = Workout.query.filter_by(user_id=current_user.id)

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    month = request.args.get("month")

    if start_date and end_date:
        workouts = workouts.filter(Workout.date >= start_date, Workout.date <= end_date)
    elif month:
        workouts = workouts.filter(Workout.date.like(f"{month}%"))

    workouts = workouts.order_by(Workout.date.desc()).all()

    return render_template("dashboard.html", workouts=workouts, today=date.today())

@app.route("/add_workout", methods=["GET", "POST"])
@login_required
def add_workout():
    if request.method == "POST":
        workout_name = request.form["workout_name"]
        new_workout = Workout(
            name=workout_name,
            date=request.form["workout_date"],
            user_id=current_user.id
        )
        db.session.add(new_workout)
        db.session.flush()

        exercise_names = request.form.getlist("exercise_name")
        sets_list = request.form.getlist("sets")
        reps_list = request.form.getlist("reps")
        weights_list = request.form.getlist("weight")

        for i in range(len(exercise_names)):
            if exercise_names[i]:
                ex = Exercise(
                    name=exercise_names[i],
                    sets=int(sets_list[i]),
                    reps=int(reps_list[i]),
                    weight=float(weights_list[i]) if weights_list[i] else None,
                    workout_id=new_workout.id
                )
                db.session.add(ex)

        db.session.commit()
        return redirect(url_for("dashboard"))
    return render_template("add_workout.html", today=date.today())

@app.route("/edit_workout/<int:workout_id>", methods=["GET", "POST"])
@login_required
def edit_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    if workout.user_id != current_user.id:
        return "Not allowed", 403

    if request.method == "POST":
        workout.name = request.form["workout_name"]
        workout.date = request.form["workout_date"]

        Exercise.query.filter_by(workout_id=workout.id).delete()

        exercise_names = request.form.getlist("exercise_name")
        sets_list = request.form.getlist("sets")
        reps_list = request.form.getlist("reps")
        weights_list = request.form.getlist("weight")

        for i in range(len(exercise_names)):
            if exercise_names[i]:
                ex = Exercise(
                    name=exercise_names[i],
                    sets=int(sets_list[i]),
                    reps=int(reps_list[i]),
                    weight=float(weights_list[i]) if weights_list[i] else None,
                    workout_id=workout.id
                )
                db.session.add(ex)

        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template("edit_workout.html", workout=workout)

@app.route("/delete_workout/<int:workout_id>")
@login_required
def delete_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    if workout.user_id != current_user.id:
        return "Not allowed", 403
    Exercise.query.filter_by(workout_id=workout.id).delete()
    db.session.delete(workout)
    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)