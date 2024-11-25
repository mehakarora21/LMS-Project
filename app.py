from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import datetime

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
    # Fetch all books from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Books")
    books_data = cur.fetchall()
    cur.close()

    # Render the template with books data
    return render_template('books.html', books=books_data)

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


@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        yr_of_publication = request.form['yr_of_publication']
        genre = request.form['genre']
        total_copies = request.form['total_copies']
        available_copies = request.form['available_copies']

        # Insert data into the database
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO Books (isbn, title, author, publisher, yr_of_publication, genre, total_copies, available_copies)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (isbn, title, author, publisher, yr_of_publication, genre, total_copies, available_copies))
        mysql.connection.commit()
        cur.close()

        # Flash message after successful insertion
        flash('Book added successfully!')

        # Redirect to avoid form resubmission
        return redirect(url_for('books'))
    return render_template('books.html')


@app.route('/edit-book/<isbn>', methods=['GET', 'POST'])
def edit_book(isbn):
    if request.method == 'POST':
        # Update book details
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        yr_of_publication = request.form['yr_of_publication']
        genre = request.form['genre']
        total_copies = request.form['total_copies']
        available_copies = request.form['available_copies']

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE Books 
            SET title=%s, author=%s, publisher=%s, yr_of_publication=%s, genre=%s, total_copies=%s, available_copies=%s
            WHERE isbn=%s
        """, (title, author, publisher, yr_of_publication, genre, total_copies, available_copies, isbn))
        mysql.connection.commit()
        cur.close()

        flash('Book details updated successfully!')
        return redirect(url_for('books'))

    # Fetch current book details
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Books WHERE isbn=%s", (isbn,))
    book = cur.fetchone()
    cur.close()

    return render_template('edit_book.html', book=book)


@app.route('/delete-book/<isbn>', methods=['POST', 'GET'])
def delete_book(isbn):
    try:
        # Delete the book from the database
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM Books WHERE isbn=%s", (isbn,))
        mysql.connection.commit()
        cur.close()

        flash('Book deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting book: {e}', 'danger')
    
    return redirect(url_for('books'))


@app.route('/add-to-issue/<isbn>')
def add_to_issue(isbn):
    # Initialize session storage if not present
    if 'to_be_issued' not in session:
        session['to_be_issued'] = []
    
    # Check if the book is already in the list
    if isbn not in session['to_be_issued']:
        session['to_be_issued'].append(isbn)
        session.modified = True  # Mark session as modified for updates
        flash(f'Book with ISBN {isbn} added to issue list.', 'success')
    else:
        flash(f'Book with ISBN {isbn} is already in the issue list.', 'warning')
    
    return redirect(url_for('books'))

@app.route('/remove-from-issue/<isbn>')
def remove_from_issue(isbn):
    if 'to_be_issued' in session and isbn in session['to_be_issued']:
        session['to_be_issued'].remove(isbn)
        session.modified = True
        flash(f'Book with ISBN {isbn} removed from issue list.', 'success')
    else:
        flash(f'Book with ISBN {isbn} not found in issue list.', 'warning')
    return redirect(url_for('issue'))

@app.route('/issue-book-form/<isbn>')
def issue_book_form(isbn):
    return render_template('issue_form.html', isbn=isbn)


@app.route('/issue-book/<isbn>', methods=['POST'])
def issue_book(isbn):
    member_id = request.form['member_id']
    catalog_num = request.form['catalog_num']
    issue_date = request.form['issue_date']
    due_date = request.form['due_date']

    try:
        # Check if member exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM Member WHERE member_ID = %s", (member_id,))
        member_exists = cur.fetchone()[0]

        if member_exists == 0:
            flash(f'Member with ID {member_id} does not exist.', 'danger')
            return redirect(url_for('issue'))

        # Insert into Transactions table
        cur.execute("""
            INSERT INTO Transactions (member_ID, isbn, catalog_num, issue_date, due_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (member_id, isbn, catalog_num, issue_date, due_date))
        
        # Update available copies
        cur.execute("""
            UPDATE Books SET available_copies = available_copies - 1 WHERE isbn = %s
        """, (isbn,))
        
        mysql.connection.commit()
        cur.close()

        # Remove the book from session storage
        session['to_be_issued'].remove(isbn)
        session.modified = True

        flash(f'Book with ISBN {isbn} successfully issued to member ID {member_id}!', 'success')
    except Exception as e:
        flash(f'Error issuing book: {e}', 'danger')

    return redirect(url_for('issue'))




if __name__ == "__main__":
    app.run(debug=True)

