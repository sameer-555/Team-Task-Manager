from flask import (
    request,
    url_for,
    g,
    Flask,
    render_template,
    request,
    redirect,
    send_file,
)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
from io import BytesIO

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Tasks(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    task_subject = db.Column(db.String(300))
    task_description = db.Column(db.String(400))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(180))
    assigned_to = db.Column(db.String(180))
    is_complete = db.Column(db.SmallInteger)


class Files(db.Model):
    file_id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(300))
    task_id = db.Column(db.Integer)
    data = db.Column(db.LargeBinary)

    def __repr__(self):
        return "<Task %r" % self.task_id


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/new_task", methods=["POST", "GET"])
def new_task():
    if request.method == "POST":
        subject = request.form["ts"]
        description = request.form["td"]
        creator = request.form["cb"]
        doer = request.form["at"]
        new_task = Tasks(
            task_subject=subject,
            task_description=description,
            created_by=creator,
            assigned_to=doer,
        )
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("task_list")
        except:
            return "there was an issue."
    else:
        return render_template("tasks.html")


@app.route("/task_list", methods=["GET"])
def index():
    if request.method == "GET":
        tasks = Tasks.query.order_by(Tasks.created_at).all()
        task = []
        [task.append(i) for i in tasks if not i.is_complete]
        return render_template("task_list.html", tasks=task)


@app.route("/task_completed", methods=["GET"])
def completed_task():
    if request.method == "GET":
        tasks = Tasks.query.filter(Tasks.is_complete == 1).all()
        return render_template("task_list.html", tasks=tasks)


@app.route("/upload_file", methods=["GET", "POST"])
def upload_file():
    if request.method == "GET":
        return render_template("upload_file.html")
    if request.method == "POST":
        file = request.files["file"]
        newFile = Files(
            file_name=file.filename, task_id=request.form["fti"], data=file.read(
            ),
        )
        db.session.add(newFile)
        db.session.commit()
        return "File Uploded sucessfully"
    else:
        return "there was an issue while uploading"


@app.route("/uploaded_file", methods=["GET"])
def file_list():
    if request.method == "GET":
        files = Files.query.all()
        file = []
        [file.append({'data': BytesIO(i.data), 'file_name': i.file_name,
                      'task_id': i.task_id, 'file_id': i.file_id}) for i in files]
        return render_template("file_list.html", files=file)


@app.route("/open_file/<int:file_id>", methods=["GET"])
def open_file(file_id):
    if request.method == "GET":
        file = Files.query.filter_by(file_id=file_id).first()
        return send_file(BytesIO(file.data), attachment_filename=file.file_name, as_attachment=True)


@app.route("/update/<int:id>", methods=["POST", "GET"])
def view_task(id):
    if request.method == "GET":
        try:
            task = Tasks.query.get_or_404(id)
            return render_template("task.html", task=task)
        except:
            return "there was an issue."
    if request.method == "POST":
        try:
            task = Tasks.query.get_or_404(id)
            task.is_complete = request.form["tc"]
            db.session.commit()
            tasks = Tasks.query.order_by(Tasks.created_at).all()
            return render_template("task_list.html", tasks=tasks)
        except:
            return "there was an issue."


@app.route("/update", methods=["POST"])
def update_task():
    if request.method == "POST":
        try:
            task = Tasks.query.get_or_404(request.form["ti"])
            if request.form["tc"]:
                task.is_complete = 1
            db.session.commit()
            return redirect("task_completed")
        except:
            return "there was an issue."


if __name__ == "__main__":
    # db.create_all()
    app.run(debug=True)
