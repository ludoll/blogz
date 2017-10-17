from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from cgi import escape

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blog_id = db.relationship('blog_id', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
       
    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
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
            flash('Successfully logged in!')            
            return redirect('/')
        else:
            flash('Either your password is wrong or you are not real','error')

    return render_template('login.html')

@app.route('/register', methods=['POST','GET'])
def register():
    password = request.form['password']
    verify = request.form['verify']
    email = request.form['email']

    password = escape(password) 
    verify = escape(verify)
    email = escape(email)

    password_error = ""
    verify_error = ""
    email_error = ""

    if password == "" or " " in password or len(password) < 3 or len(password) > 20:
        password_error = "Your password isn't good enough, friend"
    if verify == "" or verify != password:
        verify_error = "Your passwords don't match"
    if "@" not in email or "." not in email or " " in email or len(email) < 3 or len(email) > 30:
        email_error = "This can't be a real email address."
        

    if email_error == "" and verify_error == "" and password_error == "":
        return render_template("welcome.html")
    else:
        return render_template("index.html", password_error = password_error
                                           , verify_error = verify_error
                                           , email_error = email_error
                                           , username = username
                                           , email = email

@app.route('/newpost', methods=['GET', 'POST'])
def add_blog():
    if request.method == 'GET':
        return render_template('newpost.html')

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        title_error = ''
        body_error = ''

    if len(blog_body) < 1:
        title_error = 'You have to name your blog'

    if len(blog_body) < 1:
        body_error = "Blog can't be blank"

    if not title_error and not body_error:
        new_blog = Blog(blog_title, blog_body)
        db.session.add(new_blog)
        db.session.commit()
        new_url = "/blog?id=" + str(new_blog.id)
        return redirect(new_url)

    else:
        return render_template('newpost.html', title='New Blog', title_error=title_error, body_error=body_error)

@app.route('/blog', methods=['POST','GET'])
def index():
    if request.args:
        blog_id = request.args.get("id")
        blog = Blog.query.get(blog_id)

        return render_template('blogentry.html', blog=blog)

    else:
        all_blogs = Blog.query.all()
        return render_template('blog.html', all_blogs=all_blogs)

    
if __name__ == '__main__':
    app.run()
    