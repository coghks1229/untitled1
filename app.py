import os
import tempfile
from werkzeug.utils import secure_filename
from flask import Flask, redirect, render_template, url_for, request, flash, session
from DB_handler import DBModule

app= Flask(__name__)
app.secret_key ="fhdusfdskfj#dfhj"
DB = DBModule()


@app.route("/")
def index():
    if "uid" in session:
        user= session["uid"]
    else:
        user="Login"
    return render_template("index.html", user=user)


@app.route("/list")
def post_list():
    post_list = DB.post_list()
    if post_list == None:
        length = 0
    else:
        length = len(post_list)
    return render_template("post_list.html", post_list=post_list.items(), length=length)


@app.route("/post/<string:pid>")
def post(pid):
    if "uid" in session:
        user = session["uid"]
    else:
        user = "Login"
    post,post_id = DB.post_detail(pid)
    image = DB.get_image(pid)
    return render_template(
        "post_detail.html", post=post, image=image, post_id=post_id, user=user
    )

@app.route("/logout")
def logout():
    if "uid" in session:
        session.pop("uid")
        return redirect((url_for("index")))
    else:
        return redirect((url_for("login")))



@app.route("/login")
def login():
    if "uid" in session:
        return redirect((url_for("index")))
    return render_template("login.html")



@app.route("/login_done", methods = ["get"])
def login_done():
    uid = request.args.get("id")
    pwd = request.args.get("pwd")
    if DB.login(uid, pwd):
        session["uid"] =uid
        return redirect(url_for("index"))
    else:
        flash("아이디가 없거나 비밀번호가 틀립니다.")
        return redirect(url_for("login"))


@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route("/signin_done", methods = ["get"])
def signin_done():
    email= request.args.get("email")
    uid=request.args.get("id")
    pwd=request.args.get("pwd")
    name=request.args.get("name")
    if DB.signin(email=email, _id_=uid, pwd=pwd, name=name):
        return redirect(url_for("index"))
    else:
        flash("이미 존재하는 아이디 입니다.")
        return redirect(url_for("signin"))


@app.route("/write")
def write():
    if "uid" in session:
        user = session["uid"]
        return render_template("write_post.html", user=user)
    else:
        return redirect(url_for("login"))


# @app.route("/write_done", methods=["GET","POST"])
# def write_done():
#     if request.method =='POST':
#         title = request.args.get("title")
#         contents = request.args.get("contents")
#         uid = session.get("uid")
#         file = request.args.get("file")
#
#     DB.write_post(title, contents,file, uid)
#     return redirect(url_for("index"))

# @app.route("/write_done", methods=["GET"])
# def write_done():
#     title = request.args.get("title")
#     contents = request.args.get("contents")
#     uid = session.get("uid")
#     DB.write_post(title, contents, uid)
#     return redirect(url_for("index"))

@app.route("/write_done", methods=["POST"])
def write_done():
    title = request.form.get("title")
    contents = request.form.get("contents")
    uid = session.get("uid")
    file = request.files["file"]
    temp = tempfile.NamedTemporaryFile(delete=False)
    file.save(temp.name)
    DB.write_post(title, contents, uid, temp.name)
    temp.close()
    os.remove(temp.name)
    return redirect(url_for("index"))


# @app.route("/write_done", methods=["POST"])
# def write_done():
#     title = request.form["title"]
#     contents = request.form["contents"]
#     uid = session.get("uid")
#     DB.write_post(title, contents, uid)
#     return redirect(url_for("index"))

@app.route("/user/<string:uid>")
def user_posts(uid):
    u_post = DB.get_user(uid)
    if u_post==None:
        length = 0
    else:
        length= len(u_post)

    return render_template("user_detail.html", post_list=u_post, length=length, uid=uid)

@app.route("/edit_post/<string:pid>")
def edit_post(pid):
    if "uid" in session:
        user = session["uid"]
    else:
        user = "Login"
    post, post_id= DB.post_detail(pid)
    if user == post["uid"]:
        return render_template("edit_post.html", post=post, post_id=post_id ,user=user)
    else:
        flash("수정 권한이 없습니다.")
        return redirect(url_for("post", pid=post_id))




@app.route("/edit_done/<string:pid>", methods=["POST"])
def edit_done(pid):
    title = request.form.get("title")
    contents = request.form.get("contents")
    file = request.files["file"]
    temp = tempfile.NamedTemporaryFile(delete=False)
    file.save(temp.name)
    file_name = (str(file)).split(" ")[1]
    print(file_name)
    print(temp.name)
    if file_name == "''":
        DB.edit_post(title, contents, pid)
    else:
        DB.edit_post_with_image(title, contents, pid, temp.name)
        temp.close()
        os.remove(temp.name)
    return redirect(url_for("post_list"))


@app.route("/delete_post/<string:pid>")
def delete_post(pid):
    post, post_id = DB.post_detail(pid)
    if session["uid"] == post["uid"]:
        DB.delete_post(pid)
        return redirect(url_for("post_list"))
    else:
        print("작성자가 아님")
        flash("삭제 권한이 없습니다.")
        return redirect(url_for("post", pid=pid))

if __name__ == "__main__":
    app.run(debug=True)


