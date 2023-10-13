# -*- coding: utf-8 -*

from flask import (
    Flask,
    render_template,
    request,
    make_response,
    g,
    jsonify,
    redirect,
    url_for,
)
from redis import Redis
import os
import socket
import random
import json
import uuid
import sys
import importlib

importlib.reload(sys)


option_a = os.getenv("OPTION_A", "空气滤芯")
option_b = os.getenv("OPTION_B", "汽车电瓶")
option_c = os.getenv("OPTION_C", "刹车片")
option_d = os.getenv("OPTION_D", "汽油滤芯")
option_e = os.getenv("OPTION_E", "电瓶搭火线")
option_f = os.getenv("OPTION_F", "刹车钳")


hostname = socket.gethostname()

app = Flask(__name__, static_folder="assets")


def get_redis():
    if not hasattr(g, "redis"):
        g.redis = Redis(host="redis", db=0, socket_timeout=5)
    return g.redis


@app.route("/", methods=["POST", "GET"])
def hello():
    voter_id = str(uuid.uuid4())
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    vote = None

    if request.method == "POST":
        redis = get_redis()
        vote = request.form["vote"]
        data = json.dumps({"voter_id": voter_id, "vote": vote})
        redis.rpush("votes", data)
    username = request.args.get("username")
    if username == None:
        username = "登录"

    resp = make_response(
        render_template(
            "index.html",
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            option_e=option_e,
            option_f=option_f,
            hostname=hostname,
            username=username,
            vote=vote,
        )
    )
    resp.set_cookie("voter_id", voter_id)
    return resp


# 登陆转发
@app.route("/login", methods=["GET"])
def login_fowrd():
    return render_template("login.html")


@app.route("/api/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if password == "123456" and username == "张三":
            return redirect(url_for("hello", username=username))
        else:
            dict_new = "not passwod and word"
            return render_template("login.html", dict_new=dict_new)

    if request.method == "GET":
        dict_new = {"message": "tean"}
        return jsonify(dict_new)
    else:
        return jsonify(dict_new)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8088, debug=True, threaded=True)
