from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask import abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'TECH TITANS'
app.config['UPLOAD_FOLDER'] = 'uploads'

DATABASE = 'database.db'


# Database creation function
def create_tables():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    staff_number INTEGER,
                    admin_number INTEGER,
                    student_number INTEGER,
                    email TEXT,
                    password TEXT,
                    role TEXT
                )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS issues (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    staff_member_id INTEGER,
                    severity INTEGER,
                    description TEXT,
                    status TEXT,
                    campus TEXT,
                    block TEXT,
                    room TEXT,
                    selected issues TEXT,
                    selected_staff TEXT,
                    floor INTEGER,
                    issue_type TEXT,
                    image TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(staff_member_id) REFERENCES users(id)
                )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS staff_members (
                       id INTEGER PRIMARY KEY,
                       user_id INTEGER,
                       FOREIGN KEY(user_id) REFERENCES users(id)
                   )''')
    conn.commit()
    conn.close()


create_tables()


# Function to get database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Function to close database connection
def close_db_connection(conn):
    conn.close()


create_tables()


@app.route('/')
def index():
    return render_template('home.html')


users = []


@app.route('/sign_up')
def sign_up():
    return render_template('sign_up.html', users=users)


@app.route('/Staff_signup')
def staff_signup():
    return render_template('staff_signup.html', )


# Routes
@app.route('/Admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        admin_number = request.form['admin_number']  # Corrected field name
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']
        email = request.form['email']

        if password1 != password2:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('admin_signup'))

        if not (admin_number.isdigit() and len(admin_number) == 8):
            flash('Admin number must consist of 8 digits exactly.', 'error')
            return redirect(url_for('admin_signup'))

        if len(username) > 20:
            flash('Username must not exceed 20 characters.', 'error')
            return redirect(url_for('admin_signup'))

        if not email.startswith(admin_number) or not email.endswith('@dutadmin.ac.za'):  # Corrected domain
            flash('Admin email does not meet requirements.', 'error')
            return redirect(url_for('admin_signup'))

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                    (username, email, password1, 'admin'))
        conn.commit()
        conn.close()

        flash('You have successfully signed up as an admin!', 'success')
        return redirect(url_for('login'))  # Redirect to admin route

    return render_template('admin_signup.html')


@app.route('/Student_signup', methods=['GET', 'POST'])
def student_signup():
    if request.method == 'POST':
        student_number = request.form['student_number']  # Corrected field name
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']
        email = request.form['email']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                    (username, email, password1, 'student'))
        conn.commit()
        conn.close()

        flash('You have successfully signed up as an student!', 'success')
        return redirect(url_for('login'))  # Redirect to admin route

    return render_template('student_signup.html')


# Routes
@app.route('/Staff_member_signup', methods=['GET', 'POST'])
def staff_member_signup():
    if request.method == 'POST':
        staff_number = request.form['staff_number']  # Corrected field name
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']
        email = request.form['email']

        # Check if passwords match

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                    (username, email, password1, 'staff'))
        conn.commit()
        close_db_connection(conn)

        flash('You have successfully signed up as a staff member!', 'success')
        return redirect(url_for('login'))  # Redirect to staff_member route

    return render_template('staff_member_signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('logout'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect('database.db') as db:
            cursor = db.cursor()
            cursor.execute('''SELECT * FROM users WHERE email = ?''', (email,))
        user = cursor.fetchone()

        if user and user[-2] == password:  # Verify hashed password
            session['user_id'] = user[0]  # Store user ID in session
            if user[-1] == 'admin':
                return redirect(url_for('admin'))
            elif user[-1] == 'student':
                return redirect(url_for('student'))
            elif user[-1] == 'staff':
                return redirect(url_for('staff_member'))
        else:
            flash('Invalid email or password', 'error')  # Flash message for unsuccessful login

    return render_template('login.html')


@app.route('/Staff_member')
def staff_member():
    conn = get_db_connection()
    cur = conn.cursor()

    staff_id = session['user_id']
    if request.method == 'POST':
        # Assuming the staff member has accepted the issue
        issue_id = request.form['issue_id']
        # Here you can update the issue status to 'accepted' or any appropriate status
        # This part can be modified based on your database structure
        cur.execute("UPDATE issues SET status = 'accepted' WHERE id = ?", (issue_id,))
        conn.commit()
        close_db_connection(conn)

        return redirect(url_for('issue_fixed'))
    cur.execute("SELECT * FROM issues WHERE status=? AND staff_member_id=?", ('issue is being fixed', staff_id))
    allocated_issues = cur.fetchall()
    conn.close()

    return render_template('staff_member.html', allocated_issues=allocated_issues)


@app.route('/Student')
def student():
    return render_template('student.html')


@app.route('/Admin')
def admin():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM issues ORDER BY severity DESC")
    issues = cur.fetchall()
    close_db_connection(conn)
    return render_template('admin.html', issues=issues)


UPLOAD_FOLDER = 'uploads'

# Ensure the 'uploads' directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/Report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':

        campus = request.form.get('campus')
        block = request.form.get('block')
        room = request.form.get('room')
        floor = request.form.get('floor')
        issue_type = request.form.get('issue_type')
        description = request.form.get('description')
        severity = request.form.get('severity')

        image = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename != '':
                image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
                image_file.save(image_path)
                image = image_path

        # Store the issue report in the database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO issues 
                        (campus,user_id, block, room, floor, issue_type, description, severity, image, status) 
                        VALUES (?, ?,?, ?, ?, ?, ?, ?, ?, ?)''',
                    (campus, session.get('user_id'), block, room, floor, issue_type, description, severity, image,
                     'issue/complaint received'
                     ))
        conn.commit()
        conn.close()

        flash('Issue reported successfully!', 'success')
        return redirect(url_for('student'))  # Redirect to the student page after reporting the issue
    else:
        # Render the report form
        return render_template('Report.html')


@app.route('/Reported')
def reported():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM issues WHERE status=?", ('issue/complaint received',))
    reported_issues = cur.fetchall()
    conn.close()

    return render_template('reported.html', reported_issues=reported_issues)


def get_staff_members():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''SELECT u.username, u.email
                      FROM users u
                      INNER JOIN staff_members s ON u.id = s.user_id''')
    staff = cur.fetchall()
    close_db_connection(conn)
    return staff


@app.route('/allocate_issue/<int:id>', methods=['GET', 'POST'])
def allocate_issue(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        selected_issue = request.form['selected_issue']
        selected_staff = request.form['selected_staff']

        # Update the issue in the database with the selected staff member
        cur.execute("UPDATE issues SET status = 'issue to be fixed', user_id = ? WHERE id = ?",
                    (selected_staff, selected_issue))
        conn.commit()
        close_db_connection(conn)

        return redirect(url_for('status'))  # Redirect to status page after allocation

    # Fetch issues and staff members from the database
    cur.execute("SELECT * FROM issues WHERE id = ?", (id,))
    issues = cur.fetchall()
    cur.execute("SELECT * FROM users WHERE role = 'staff'")
    staff_members = cur.fetchall()

    close_db_connection(conn)

    return render_template('allocate_issue.html', issues=issues, staff_members=staff_members)


@app.route('/Issue_fixed', methods=['GET', 'POST'])
def issue_fixed():
    if request.method == 'POST':

        staff_member_id = request.form['staff_member_id']
        issue_id = request.form['issue_id']
        fixed_time = request.form['fixed_time']
        fixing_duration = request.form['fixing_duration']
        fixing_description = request.form['fixing_description']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''UPDATE issues SET status=?, staff_member_id=?, fixed_time=?, fixing_duration=?, 
        fixing_description=? WHERE id=?''', ('issue fixed', staff_member_id, fixed_time, fixing_duration,
                                             fixing_description, issue_id))  # Fixed the status assignment
        conn.commit()
        conn.close()

        flash('Issue fixed successfully!', 'success')
        return redirect(url_for('staff_member'))  # Redirect to the Staff Member page after fixing the issue
    else:
        # Render the issue fixed form
        issue_id = request.args.get('issue_id')
        return render_template('issue_fixed.html', issue_id=issue_id)


def get_fixed_issues():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM issues WHERE status=?", ('issue is being fixed',))
        all_fixed_issues = cur.fetchall()
        return all_fixed_issues
    except sqlite3.Error as e:
        print("Database error:", e)
        return []


@app.route('/Fixed_issue')
def fixed_issues():
    all_fixed_issues = get_fixed_issues()
    return render_template('fixed_issues.html', all_fixed_issues=all_fixed_issues)


@app.route('/Status')
def status():
    if 'user_id' not in session:
        flash('You need to be logged in to view this page.', 'error')
        return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM issues")
    issues = cur.fetchall()
    close_db_connection(conn)

    return render_template('status.html', issues=issues)


@app.route('/About')
def about():
    return render_template('About.html')


@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id', None)
        flash('You have been logged out.', 'success')
    else:
        flash('You are not logged in.', 'error')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
