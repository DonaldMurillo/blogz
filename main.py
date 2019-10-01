  
from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:admin@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/', methods=['POST', 'GET'])
def index():

    blogs = Blog.query.all()

    return render_template('blog.html',title="Blog Post", 
        blogs=blogs)

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    if request.method == 'POST':
        
        blog_title = request.form['title']
        blog_body = request.form['body']
        error_dict = {}
        if blog_title == "" :
            error_dict.update( {"empty_title":True})
        if blog_body == "":
            error_dict.update( {"empty_body": True})
        if len(error_dict)>0:
            return render_template("newblog.html", errors = error_dict)

        new_blog = Blog(blog_title, blog_body)
        db.session.add(new_blog)
        db.session.commit()

    blogs = Blog.query.all()

    return render_template('blog.html',title="Blog Post", 
        blogs=blogs)

@app.route("/newblog", methods=["POST" , "GET"])
def newblog():
    
    errors_dict = {"empty_body": False, "empty_title": False}
    return render_template("newblog.html" , errors =errors_dict)



if __name__ == '__main__':
    app.run()