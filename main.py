  
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

    blog_id = request.args.get("id")
    if request.method == "GET" and blog_id:
        
        blog = Blog.query.filter_by(id=blog_id).first()

        return render_template("singleblog.html", blog=blog)


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

        blog = Blog.query.filter_by(title=new_blog.title, body=new_blog.body).first()

        return render_template("singleblog.html", blog=blog)

    blogs = Blog.query.all()

    return render_template('blog.html',title="Blog Post", 
        blogs=blogs)

@app.route("/newblog", methods=["POST" , "GET"])
def newblog():
    
    errors_dict = {"empty_body": False, "empty_title": False}
    return render_template("newblog.html" , errors =errors_dict)

@app.route("/blog" , methods=["POST" , "GET"])
def single_blog():
    print(request.args.get("title"))
    return 

if __name__ == '__main__':
    app.run()