import pyrebase
import json
import uuid
from datetime import datetime

class DBModule:
    def __init__(self):
        with open("./auth/firebaseAuth.json") as f:
            config = json.load(f)

        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()
        self.storage = firebase.storage()

    def login(self, uid, pwd):
        users = self.db.child("users").get().val()
        try:
            userinfo =users[uid]
            if userinfo["pwd"] ==pwd:
                return True
            else:
                return False
        except:
            return False


    def signin_verification(self, uid):
        users = self.db.child("users").get().val()
        for i in users:
            if uid == i:
                return False
        return True


    def signin(self, _id_, pwd, name, email):
        information ={
            "pwd": pwd,
            "uname": name,
            "email": email
        }
        if self.signin_verification(_id_):
            self.db.child("users").child(_id_).set(information)
            return True
        else:
            return False

    # def write_post(self, title, contents, uid, file):
    #     pid = str(uuid.uuid4())[:12]
    #     posting_time = str(datetime.now())[:19]
    #     information = {
    #         "title": title,
    #         "contents": contents,
    #         "uid": uid,
    #         "time": posting_time,
    #     }
    #     self.db.child("posts").child(pid).set(information)
    #     self.storage.child(pid).put(file)

    def write_post(self, title, contents, uid, file):
        pid = str(uuid.uuid4())[:12]
        posting_time = str(datetime.now())[:19]
        information = {
            "title": title,
            "contents": contents,
            "uid": uid,
            "time": posting_time,
        }
        self.db.child("posts").child(pid).set(information)
        self.storage.child(pid).put(file)


    def edit_post(self, title, contents, pid):
        changed_info = {"title": title, "contents": contents}
        self.db.child("posts").child(pid).update(changed_info)

    def edit_post_with_image(self, title, contents, pid, file):
        changed_info = {"title": title, "contents": contents}
        self.db.child("posts").child(pid).update(changed_info)
        self.storage.child(pid).put(file)

    # def write_post(self, title, contents,  uid):
    #     pid = str(uuid.uuid4())[:12]
    #     information = {
    #         "title": title,
    #         "contents": contents,
    #
    #         "uid": uid
    #     }
    #     self.db.child("posts").child(pid).set(information)

    def post_list(self):
        post_lists = self.db.child("posts").get().val()
        temp = sorted(
            list(post_lists.items()), key=lambda x: x[1]["time"], reverse=True
        )
        post_lists.clear()
        post_lists.update(temp)
        return post_lists


    def post_detail(self, pid):
        post = self.db.child("posts").get().val()[pid]
        post_id = pid
        return post, post_id

    def get_image(self, pid):
        image = self.storage.child(pid).get_url(None)
        return image

    def delete_post(self, pid):
        self.db.child("posts").child(pid).set({})


    def get_user(self, uid):
        post_list = []
        users_post = self.db.child("posts").get().val()
        temp = sorted(
            list(users_post.items()), key=lambda x: x[1]["time"], reverse=True
        )
        users_post.clear()
        users_post.update(temp)
        for post in users_post.items():
            if post[1]["uid"] == uid:
                post_list.append(post)
        return post_list

