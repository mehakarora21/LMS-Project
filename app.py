from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'FictionBooks'

# MySQL Configuration (add this section)
app.config['MYSQL_HOST'] = 'localhost'  # Use your MySQL host
app.config['MYSQL_USER'] = 'root'  # Your MySQL username
app.config['MYSQL_PASSWORD'] = 'Tanu@1234'  # Your MySQL password
app.config['MYSQL_DB'] = 'library_db'  # Name of the database you created

# Initialize MySQL
mysql = MySQL(app)

# Existing routes and HTML rendering code

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/members')
def members():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Member")
    members_data = cur.fetchall()  # Fetch all rows from the query
    cur.close()
    return render_template('members.html', members=members_data)

@app.route('/books')
def books():
    return render_template('books.html')

@app.route('/issue')
def issue():
    return render_template('issue.html')

@app.route('/return')
def return_book():
    return render_template('return.html')

# Test DB Connection (optional, for troubleshooting)
@app.route('/test-db')
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SHOW TABLES")
        tables = cur.fetchall()
        return f"Tables: {tables}"
    except Exception as e:
        return f"Error: {e}"

@app.route('/add_member', methods=['POST'])
def add_member():
    if request.method == 'POST':
        name = request.form['name']
        ph_num = request.form['ph_num']
        membership_date = request.form['membership_date']
        address = request.form['address']
        status = request.form.get('status', 'active')  # Default to 'active' if not provided

        # Insert the new member into the database
        cur = mysql.connection.cursor()
        query = """INSERT INTO Member (name, ph_num, membership_date, address, status)
                   VALUES (%s, %s, %s, %s, %s)"""
        cur.execute(query, (name, ph_num, membership_date, address, status))
        mysql.connection.commit()
        cur.close()

        flash(f"Member '{name}' added successfully!")  # Flash a success message
        # Redirect back to the members page
        return redirect(url_for('members'))
    
@app.route('/edit_member/<int:member_id>', methods=['GET', 'POST'])
def edit_member(member_id):
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Member WHERE member_ID = %s", (member_id,))
        member = cur.fetchone()  # Fetch the specific member's details
        cur.close()
        return render_template('edit_member.html', member=member)

    elif request.method == 'POST':
        # Get the updated data from the form
        name = request.form['name']
        ph_num = request.form['ph_num']
        membership_date = request.form['membership_date']
        address = request.form['address']
        status = request.form['status']

        # Update the database
        cur = mysql.connection.cursor()
        query = """UPDATE Member
                   SET name = %s, ph_num = %s, membership_date = %s, address = %s, status = %s
                   WHERE member_ID = %s"""
        cur.execute(query, (name, ph_num, membership_date, address, status, member_id))
        mysql.connection.commit()
        cur.close()

        flash(f"Member '{name}' updated successfully!")
        return redirect(url_for('members'))


if __name__ == "__main__":
    app.run(debug=True)

