  
from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:admin@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = "lolarules"
db = SQLAlchemy(app)

#####################################################################
####################### Models ######################################
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner_id):
        self.title = title
        self.body = body
        self.owner_id = owner_id

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(5000))
    blogs = db.relationship("Blog", backref="blog")

    def __init__(self, username, password):

        self.username = username
        self.password = password


###############################################################################
######################## Helpers ##############################################

class SignupInfo():

    def __init__(self, my_info):

        self.user_name = my_info["username"]#[1]
        self.password = my_info["password"]#[1]
        self.veri_password = my_info["veripassword"]#[1]
        # self.email = my_info["email"]#[1]
        error_dict = {}
        self.is_verified = False
        if self.password == self.veri_password:
            self.is_verified = True

        for data in my_info:
            
            if data != "email":
                if len(my_info[data]) == 0 :
                    error_dict.update({str(data)+ "_is_empty" : True })
                    print({str(data)+ "_is_empty" : True})


                if (len(my_info[data]) < 3 ) and len(my_info[data]) > 0:
                    error_dict.update({str(data)+ "_bad_length" : True})
            
        # if my_info["email"].count("@") != 1 and my_info["email"].count(".") != 1 and my_info["email"].count(" ") != 1:
        #     error_dict.update({"email_invalid_char" : True})
        #     print({"email_invalid_char" : True})

        self.errors= error_dict.copy()
        self.has_data = True
        self.redirect = False
        print("there are {0} errors".format(len(self.errors)))
        if len(self.errors) == 0:

            self.redirect = True

    def print_all(self):
        print("""username: {0}
        password: {1}
        verify password: {2}
        """.format(self.user_name,self.password, self.veri_password))

#################################################################################
######################## Controlers ############################################

@app.before_request
def required_login():

    if not "username" in session and (request.endpoint == "newblog"):
        return redirect("login")

    pass

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    new_signup = ""

    if request.method == "POST":

        user = User.query.filter_by(username=request.form["username"]).all()

        new_signup = SignupInfo(request.form)
        
        if len(user) == 1:
            new_signup.errors.update({"user_exists": True})
            new_signup.redirect = False
            

        if new_signup.redirect:
            
            new_user = User(new_signup.user_name, new_signup.password)
            db.session.add(new_user)
            db.session.commit()
            print("made it here")
            new_user = User.query.filter_by(username=new_signup.user_name).first()
            session["username"] = new_user.username
            # print("this is the user id:" + str(new_user.id ))

            return render_template("/single_user.html", session=session, name= new_user, user=new_user)

        print("made it there")
        return render_template("signup.html", tittle = "Signup", new_signup = new_signup)

    if request.method == "GET":
        new_signup = None
        return render_template("signup.html", tittle = "Signup", is_verified = True)
    # return None

@app.route('/login', methods=['POST', 'GET'])
def login():
    
    if request.method == "POST":

        user = User.query.filter_by(username=request.form["username"]).first()
        new_login = request.form

        if user == None:

            return render_template("login.html", tittle = "Signup", is_verified = False, new_login=new_login, new_login_user = False)

        if user.username == request.form["username"] and user.password == request.form["password"]:
            
            # user = User.query.filter_by(username=request.form["username"]).first()
            session["username"] = request.form["username"]
            return redirect("/newblog")
        
        else:
            return render_template("login.html", tittle = "Signup", is_verified = False, new_login=new_login, new_login_user = True, bad_user_pass = True)


    return render_template("login.html", tittle = "Signup", is_verified = True)

@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop("username")
    return redirect("/blog")

@app.route('/single-user', methods=['POST', 'GET'])
def single_user():

    user = User.query.filter_by(username=session["username"]).first()
    blogs = Blog.query.filter_by(id=user.id).all()
    return render_template("single_user.html", blogs = blogs)

@app.route('/', methods=['POST', 'GET'])
def index():

    owner_id = request.args.get("id")
    if request.method == "GET" and owner_id:
        print("-----made it to get------")
        blogs = Blog.query.filter_by(owner_id=owner_id).all()
        users = User.query.filter_by(id=owner_id).all()
        return render_template("blog.html", blogs=blogs, users=users)
    # blogs = Blog.query.all()
    users = User.query.all()
    # return render_template('blog.html',title="Blog Post", 
    #     blogs=blogs)

    # return render_template("login.html", tittle = "Signup", is_verified = True)
    return render_template("index.html", users=users)

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    blog_id = request.args.get("id")
    owner_id = request.args.get("owner_id")

    if request.method == "GET" and blog_id:

        blog = Blog.query.filter_by(id=blog_id).first()
        user = User.query.filter_by(id=blog.owner_id).first()
        return render_template("singleblog.html", blog=blog, user=user)

    if request.method == "GET" and owner_id:
        print("====here====")
        blogs = Blog.query.filter_by(owner_id=owner_id).all()
        user = User.query.filter_by(id=owner_id).first()
        return render_template("single_user.html", blogs=blogs, user=user)


    if request.method == 'POST':
        
        blog_title = request.form['title']
        blog_body = request.form['body']
        blog_owner_id = User.query.filter_by(username=session["username"]).first().id
        error_dict = {}
        if blog_title == "" :
            error_dict.update( {"empty_title":True})
        if blog_body == "":
            error_dict.update( {"empty_body": True})
        if len(error_dict)>0:
            return render_template("newblog.html", errors = error_dict)

        new_blog = Blog(blog_title, blog_body, blog_owner_id)
        db.session.add(new_blog)
        db.session.commit()

        # blog = Blog.query.filter_by(title=new_blog.title, body=new_blog.body).first()

        # return render_template("singleblog.html", blog=blog)
        # print("-----------hereeee------------  " + str(blog_owner_id))
        blog = Blog.query.filter_by(title=blog_title).first()
        user = User.query.filter_by(id=blog_owner_id).first()
        # print(blogs)
        return render_template("singleblog.html", blog=blog, user=user)


    blogs = Blog.query.all()
    users = User.query.all()
    # print(users)

    return render_template('blog.html',title="Blog Post", 
        blogs=blogs, users=users)

@app.route("/newblog", methods=["POST" , "GET"])
def newblog():
    
    errors_dict = {"empty_body": False, "empty_title": False}
    return render_template("newblog.html" , session = session, errors =errors_dict)

# @app.route("/blog" , methods=["POST" , "GET"])
# def single_blog():
#     print(request.args.get("title"))
#     return 

if __name__ == '__main__':
    app.run()