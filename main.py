from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:ok@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

from models import db, User, Blog

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


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

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')


@app.route('/delete-task', methods=['POST'])
def delete_task():

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()


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


@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        blog_title = request.form['title']
        new_blog = Blog(blog_title)
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.all()
    return render_template('blog.html',title="Blog!", blogs=blogs)


@app.route('/delete-blog', methods=['POST'])
def delete_blog():

    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    db.session.delete(blog)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()