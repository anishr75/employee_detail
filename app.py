from flask import Flask, request, redirect, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
import mysql.connector
from flask import Flask, request, redirect, render_template, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

app.secret_key = os.getenv("SECRET_KEY")

UPLOAD_FOLDER = "uploads"

os.makedirs("uploads/cv", exist_ok=True)
os.makedirs("uploads/aadhaar", exist_ok=True)
os.makedirs("uploads/lightbill", exist_ok=True)
os.makedirs("uploads/certificates", exist_ok=True)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

@app.route("/register", methods=["POST"])
def register():

    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    hashed_password = generate_password_hash(password)

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO users(username,email,password) VALUES(%s,%s,%s)",
        (username, email, hashed_password)
    )

    db.commit()
    cursor.close()
    db.close()

    return redirect("/?tab=login")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return redirect("/")

    login_id = request.form.get("login_id")
    password = request.form.get("password")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM users
        WHERE email=%s OR username=%s
    """, (login_id, login_id))

    user = cursor.fetchone()

    cursor.close()
    db.close()

    if user and check_password_hash(user["password"], password):

        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return redirect("/employees")

    return "Invalid Login"

@app.route("/")
def form():
    return render_template("auth.html")

@app.route("/submit", methods=["POST"])
def submit():
    if "user_id" not in session:
         return redirect("/")

    user_id = session["user_id"]
    name = request.form.get("name")
    mobile = request.form.get("mobile")
    alt_mobile = request.form.get("alt_mobile")
    department = request.form.get("department")
    joining_date = request.form.get("joining_date")

    spouse = request.form.get("spouse")
    parents = request.form.get("parents")
    siblings = request.form.get("siblings")

    address = request.form.get("address")

    education = request.form.get("education")
    technical = request.form.get("technical")

    experience = request.form.get("experience")

    aadhaar = request.form.get("aadhaar")

    system_details = request.form.get("system_details")
    assets = request.form.get("assets")

    pants = request.form.get("pants")
    shirts = request.form.get("shirts")
    other_items = request.form.get("other_items")

    # FILES
    cv = request.files.get("cv")
    aadhaar_file = request.files.get("aadhaar_image")
    lightbill = request.files.get("lightbill")
    certificate = request.files.get("certificates")

    cv_filename = None
    aadhaar_filename = None
    lightbill_filename = None
    certificate_filename = None

    if cv and cv.filename != "":
        cv_filename = secure_filename(cv.filename)
        cv.save(os.path.join("uploads/cv", cv_filename))

    if aadhaar_file and aadhaar_file.filename != "":
        aadhaar_filename = secure_filename(aadhaar_file.filename)
        aadhaar_file.save(os.path.join("uploads/aadhaar", aadhaar_filename))

    if lightbill and lightbill.filename != "":
        lightbill_filename = secure_filename(lightbill.filename)
        lightbill.save(os.path.join("uploads/lightbill", lightbill_filename))

    if certificate and certificate.filename != "":
        certificate_filename = secure_filename(certificate.filename)
        certificate.save(os.path.join("uploads/certificates", certificate_filename))

    db = get_db_connection()
    cursor = db.cursor()

    sql = """
    INSERT INTO employees
    (
    user_id,
    name,
    department,
    joining_date,
    mobile,
    alt_mobile,
    spouse,
    parents,
    siblings,
    address,
    education,
    technical,
    experience,
    aadhaar,
    system_details,
    assets,
    pants,
    shirts,
    other_items,
    cv_file,
    aadhaar_file,
    lightbill_file,
    certificate_file
    )

    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.execute(sql, (
    user_id,
    name,
    department,
    joining_date,
    mobile,
    alt_mobile,
    spouse,
    parents,
    siblings,
    address,
    education,
    technical,
    experience,
    aadhaar,
    system_details,
    assets,
    pants,
    shirts,
    other_items,
    cv_filename,
    aadhaar_filename,
    lightbill_filename,
    certificate_filename

))
    db.commit()
    cursor.close()
    db.close()

    return redirect("/employees")

@app.route("/employee-form")
def employee_form():

    if "user_id" not in session:
        return redirect("/")

    return render_template("employee_form.html")

@app.route("/employees")
def employees():

    if "user_id" not in session:
        return redirect("/")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM employees ORDER BY id DESC")
    employees = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("employees.html", employees=employees)

@app.route("/employee/<int:id>")
def employee_view(id):

    if "user_id" not in session:
        return redirect("/")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM employees WHERE id=%s",(id,))
    employee = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template("employee_view.html", employee=employee)

@app.route("/employee/delete/<int:id>")
def delete_employee(id):
    if "user_id" not in session:
        return redirect("/")
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("DELETE FROM employees WHERE id=%s",(id,))

    db.commit()
    cursor.close()
    db.close()

    return redirect("/employees")

@app.route("/employee/edit/<int:id>")
def edit_employee(id):
    if "user_id" not in session:
        return redirect("/")
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM employees WHERE id=%s",(id,))
    employee = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template("employee_edit.html", employee=employee)

@app.route("/employee/update/<int:id>", methods=["POST"])
def update_employee(id):

    name = request.form.get("name")
    department = request.form.get("department")
    joining_date = request.form.get("joining_date")
    mobile = request.form.get("mobile")
    alt_mobile = request.form.get("alt_mobile")
    aadhaar = request.form.get("aadhaar")

    spouse = request.form.get("spouse")
    parents = request.form.get("parents")
    siblings = request.form.get("siblings")

    address = request.form.get("address")

    education = request.form.get("education")
    technical = request.form.get("technical")

    experience = request.form.get("experience")

    system_details = request.form.get("system_details")
    assets = request.form.get("assets")

    pants = request.form.get("pants")
    shirts = request.form.get("shirts")
    other_items = request.form.get("other_items")

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE employees SET
        name=%s,
        department=%s,
        joining_date=%s,
        mobile=%s,
        alt_mobile=%s,
        aadhaar=%s,
        spouse=%s,
        parents=%s,
        siblings=%s,
        address=%s,
        education=%s,
        technical=%s,
        experience=%s,
        system_details=%s,
        assets=%s,
        pants=%s,
        shirts=%s,
        other_items=%s
        WHERE id=%s
    """, (
        name, department, joining_date, mobile, alt_mobile, aadhaar,
        spouse, parents, siblings, address,
        education, technical, experience,
        system_details, assets,
        pants, shirts, other_items,
        id
    ))

    cv = request.files.get("cv")
    aadhaar_file = request.files.get("aadhaar_image")
    lightbill = request.files.get("lightbill")
    certificate = request.files.get("certificates")

    if cv and cv.filename != "":
        cv_filename = secure_filename(cv.filename)
        cv.save(os.path.join("uploads/cv", cv_filename))
        cursor.execute("UPDATE employees SET cv_file=%s WHERE id=%s",(cv_filename,id))

    if aadhaar_file and aadhaar_file.filename != "":
        aadhaar_filename = secure_filename(aadhaar_file.filename)
        aadhaar_file.save(os.path.join("uploads/aadhaar", aadhaar_filename))
        cursor.execute("UPDATE employees SET aadhaar_file=%s WHERE id=%s",(aadhaar_filename,id))

    if lightbill and lightbill.filename != "":
        lightbill_filename = secure_filename(lightbill.filename)
        lightbill.save(os.path.join("uploads/lightbill", lightbill_filename))
        cursor.execute("UPDATE employees SET lightbill_file=%s WHERE id=%s",(lightbill_filename,id))

    if certificate and certificate.filename != "":
        certificate_filename = secure_filename(certificate.filename)
        certificate.save(os.path.join("uploads/certificates", certificate_filename))
        cursor.execute("UPDATE employees SET certificate_file=%s WHERE id=%s",(certificate_filename,id))

    db.commit()
    cursor.close()
    db.close()

    return redirect("/employees")

@app.route('/uploads/<path:filename>')
def uploaded_files(filename):
    return send_from_directory('uploads', filename)

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")

if __name__ == "__main__":


    print("Server starting...")

    app.run(debug=True)