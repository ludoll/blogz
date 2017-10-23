from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from cgi import escape

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = '3l33t5UzP3B'

db = SQLAlchemy(app)

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blog_id = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
       
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup',]
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = User.query.filter_by(email=email)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['email'] = user.email
                flash('welcome back, '+user.email)
                return redirect("/")
        flash('You may not be in the database')
        return render_template("login.html", email=email)

@app.route('/logout')
def logout():
    del session['email']
    flash ('See you soon!')
    return redirect('/blog')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if "@" not in email or "." not in email or " " in email or len(email) < 3 or len(email) > 20:
            flash('It seems that you have entered an email that has the incorrect format')
            return redirect('/signup')
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('User email is already spoken for, chief.')
        if password != verify:
            flash('passwords did not match')
            return redirect('/signup')
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session['email'] = user.email
        return redirect("/")
    else:
        return render_template('signup.html')


@app.route('/')
def index():
    all_users = User.query.all()
    return render_template('index.html', all_users=all_users)

@app.route('/blog/newpost', methods=['GET','POST'])
def new_blog():
    if request.method == 'GET':
        return render_template('newpost.html')

    if request.method == 'POST':
        owner = User.query.filter_by(email=session['email']).first()
        blog_title = request.form['title']
        blog_body = request.form['body']
        title_error = ''
        body_error = ''

    if len(blog_body) < 1:
        title_error = 'You have to name your blog'

    if len(blog_body) < 1:
        body_error = "Blog can't be blank"

    if not title_error and not body_error:
        new_entry = Blog(blog_title, blog_body, owner)
        db.session.add(new_entry)
        db.session.commit()
        new_url = "/blog?id=" + str(new_entry.id)
        return redirect(new_url)

    else:
        return render_template('newpost.html', title_error=title_error, body_error=body_error)

@app.route('/blog', methods=['POST','GET'])
def blog():
    id = request.args.get('id')
    email = request.args.get('email')
    blog_title = Blog.query.get('title')
    blog_body = Blog.query.get('body')    
    # if id = '':
    #     return 
        
    # if email = '':
    #     return: 
    return render_template('blog.html', blog_title=blog_title
                                      , blog_body=blog_body)

    
if __name__ == '__main__':
    app.run()
    