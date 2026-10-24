import sqlite3
from pathlib import Path
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_from_directory,
    abort
)
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "segmafusion.db"

PROJECT_DIR = BASE_DIR.parent
DATASET_DIR = PROJECT_DIR / "Dataset" / "DeepGlobe"

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# Development only. Use an environment variable for deployment.
app.config["SECRET_KEY"] = "change-this-to-a-random-secret-before-deployment"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_db_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)


initialize_database()


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        try:
            with get_db_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO users (name, email, password_hash)
                    VALUES (?, ?, ?)
                    """,
                    (name, email, password_hash)
                )
        except sqlite3.IntegrityError:
            flash("An account with this email already exists.", "error")
            return redirect(url_for("register"))

        flash("Account created successfully. Please sign in.", "success")
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        with get_db_connection() as connection:
            user = connection.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")
        return redirect(url_for("home"))

    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("home"))

    return render_template("dashboard.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# Dataset Explorer
@app.route("/dataset")
def dataset():
    if "user_id" not in session:
        return redirect(url_for("login"))

    train_dir = DATASET_DIR / "train"
    samples = []

    if train_dir.exists():
        for image_path in sorted(train_dir.glob("*_sat.jpg")):
            image_id = image_path.stem.removesuffix("_sat")
            mask_path = train_dir / f"{image_id}_mask.png"

            if mask_path.exists():
                samples.append({
                    "id": image_id,
                    "image": f"{image_id}_sat.jpg",
                    "mask": f"{image_id}_mask.png"
                })

    return render_template("dataset.html", samples=samples)

@app.route("/dataset-files/<path:filename>")
def dataset_files(filename):
    if "user_id" not in session:
        return redirect(url_for("login"))

    train_dir = (DATASET_DIR / "train").resolve()
    requested_file = (train_dir / filename).resolve()

    if requested_file.parent != train_dir:
        abort(404)

    if not requested_file.is_file():
        abort(404)

    if requested_file.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        abort(404)

    return send_from_directory(train_dir, filename)

@app.route("/satellite")
def satellite():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("satellite.html")
 
@app.route("/upload", methods=["GET", "POST"])
def upload_image():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        if "image" not in request.files:
            flash("Please select an image.")
            return redirect(url_for("upload_image"))

        file = request.files["image"]

        if file.filename == "":
            flash("Please select an image.")
            return redirect(url_for("upload_image"))

        filename = secure_filename(file.filename)

        if "." not in filename:
            flash("Invalid filename.")
            return redirect(url_for("upload_image"))

        extension = filename.rsplit(".", 1)[1].lower()

        if extension not in {"jpg", "jpeg", "png"}:
            flash("Please upload a JPG, JPEG, or PNG image.")
            return redirect(url_for("upload_image"))

        saved_filename = f"{uuid.uuid4().hex}.{extension}"
        save_path = UPLOAD_DIR / saved_filename

        try:
            file.save(save_path)

            from PIL import Image

            with Image.open(save_path) as image:
                image.verify()

        except Exception:
            save_path.unlink(missing_ok=True)
            flash("The uploaded file is not a valid image.")
            return redirect(url_for("upload_image"))

        flash("Image uploaded successfully!")
        return render_template(
            "upload.html",
            uploaded_image=saved_filename
        )

    return render_template("upload.html", uploaded_image=None)

if __name__ == "__main__":
    app.run(debug=True)
