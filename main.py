from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.String(1000))
       
    def __init__(self, title, body):
        self.title = title
        self.body= body

@app.route('/newpost', methods=['GET', 'POST'])
def add_blog():
    if request.method == 'GET':
        return render_template('newpost.html', title='Add a Blog Entry')


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
    