from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:ok@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

from models import db, User, Blog

# TODO start make session definitive either email or user id
@app.before_request
def require_login():
    allowed_routes = ['index', 'login', 'signup']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')
# TODO end make session definitive either email or user id

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

# TODO start of validation pw needs to be aligned with words password and verification

@app.route("/signup", methods=['POST'])
def validate_fields():
    username = request.form["username"]
    password = request.form["password"]
    verify = request.form["verify"]
    email = request.form["email"]

    username_error = ''
    password_error = ''
    verify_error = ''
    pw_error = ''
    email_error = ''

    if len(username) < 3:
        username = ''
        username_error = 'Username must be more than 3 characters'
    elif len(username) > 20:
        username = ''
        username_error = 'Username must be less than 20 characters'
    else:
        username = username
    #https://www.infoworld.com/article/2655121/security/password-size-does-matter.html
    #https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/password
    if len(password) < 3:
        password = password
        password_error = 'Password must contain more than 3characters long, 20 max, minimum 14 recommended'

    if len(verify) < 3:
        verify = verify
        verify_error = 'Verification password must contain more than 3 characters long, 20 max, minimum 14 recommended' 

    if len(password) > 20:
        password = password
        password_error = 'Password is too long, 20 max, minimum 14 recommended'

    if len(verify) > 20:
        verify = verify
        verify_error = 'Verification password is too long, 20 max, minimum 14 recommended'    

    if password != verify:
        password = password
        verify = verify
        pw_error = 'Passwords do not match'

    #Criteria for email are that it has a single @, a single ., contains no spaces, and is between 3 and 20 characters long
    if len(email) > 0:
        if not(email.endswith('@') or email.startswith('@') or email.endswith('.') or email.startswith('.')) and email.count('@') == 1 and email.count('.') == 1:
            email=email
        else:
            email = ''
            email_error = 'Improperly formed email  -- it must contain an @ sign, only one period, and is between 3 and 20 characters long'
    else:
        email = ''

    if username == "":
        username_error = 'Username must be more than 3 characters but no more than 20'
    if password == "":
        password_error = 'Set a password, no fewer than 3 and no longer than 20 characters'
    if verify == "":
        verify_error = 'Enter a password to match the one above, no fewer than 3 and no longer than 20 characters'


    if not username_error and not password_error and not verify_error and not pw_error and not email_error:
        return render_template('hello_greeting.html', username = username)

    else:
        return render_template('hello_form.html', pw_error=pw_error, username_error=username_error, password_error=password_error, verify_error=verify_error, email_error=email_error,
        username=username, password=password, pw2=pw2, email=email)
# TODO end of validation pw needs to be aligned with words password and verification 

# TODO start check how sessions are defined and decide whether email or user id 
@app.route('/logout')
def logout():
    del session['email']
    #del session['user_id']
    return redirect('/')
# TODO end check on sessions to be defined as user id or email

@app.route('/blog', methods=['POST', 'GET'])
def blog_listing():

    if request.method == 'POST':
        blog_title = request.form['title']
        new_blog = Blog(blog_title)
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.all()
    return render_template('blog.html',title="Blog!", blogs=blogs)


@app.route('/signup', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.flush()   #from Adnan's example flush session to get id of inserted row
            db.session.commit()
            session['email'] = email
            #session['user_id'] = new_user.id
            return redirect('/')
        else:
            # TODO consider using flash("User already exists")
            return "<h1>This username is already in use -- choose another</h1>"

    return render_template('signup.html')            

@app.route('/blog', methods=['GET'])
def display_post():
    posts = Blog.query.all()
    if len(request.args) != 0:
        #writeup_id = request.args.get("id")
        #writeup = Blog.query.get(writeup_id)

        return render_template('writeup.html', writeup=writeup)

    return render_template('blog.html', posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if title == "" or body == "":
            if title == "":
                title_error = "Please enter a title"
            if body == "":
                body_error = "Please enter a post body"
            return render_template('/newpost.html', title=title, body=body, title_error=title_error, body_error=body_error)
        else:
            post = Blog(title, body)
            db.session.add(post)
            db.session.commit()

            body_id = str(post.id)
            return redirect("/blog?id=" + body_id)

    return render_template('/newpost.html')

@app.route('/newpost', methods=['POST', 'GET'])        


@app.route('/delete-blog', methods=['POST'])
def delete_blog():

    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    db.session.delete(blog)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()