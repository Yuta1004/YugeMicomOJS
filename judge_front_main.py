from flask import Flask, render_template, request, session, redirect, url_for
from flask_bootstrap import Bootstrap
from login_process import register, login
from user import get_user_data, update_user_data, change_password
from problem import get_all_problem, get_submission_data
from contest import get_3type_divided_contest

# Flask
app = Flask(__name__)
app.config.from_pyfile("config.cfg")
bootstrap = Bootstrap(app)

# Other
base_url = "/yuge_micom_ojs"

#Routes
@app.before_request
def before_request():
    if "user_id" not in session.keys():
        session["user_id"] = None

    if ("/login" not in request.url) and ("/register" not in request.url) and session["user_id"] is None:
        return redirect(base_url + "/login")


@app.route(base_url + "/")
def index():
    return render_template("index.html",
                           session=session["user_id"])


@app.route(base_url + "/register", methods=["GET", "POST"])
def register_user():
    if request.method == "GET":
        return render_template("register.html",
                               session=session["user_id"])

    user_id = request.form["user_id"]
    user_name = request.form["user_name"]
    password = request.form["password"]
    password_conf = request.form["password_conf"]

    # ユーザ登録
    if register(user_id, user_name, password, password_conf):
        session["user_id"] = user_id
        return redirect("/yuge_micom_ojs")
    else:
        return render_template("register.html",
                               inp_failed="Failed",
                               session=session["user_id"])


@app.route(base_url + "/login", methods=["GET", "POST"])
def login_user():
    if request.method == "GET":
        return render_template("login.html",
                               session=session["user_id"])

    user_id = request.form["user_id"]
    password = request.form["password"]

    # 認証
    if login(user_id, password):
        session["user_id"] = user_id
        return redirect(base_url)
    else:
        return render_template("login.html",
                               login_failed="Failed",
                               session=session["user_id"])


@app.route(base_url + "/logout")
def logout_user():
    session["user_id"] = None
    return redirect(base_url)


@app.route(base_url + "/user_settings", methods=["POST", "GET"])
def user_settings():
    if session["user_id"] is None:
        return redirect(base_url)

    update_succeeded = None

    # データ更新(POST)
    if request.method == "POST":
        user_name = request.form["name"]
        open_code = int(request.form["open_code"])
        update_succeeded = update_user_data(session["user_id"], user_name, open_code)

    # 設定ページに必要な情報取得
    user_info = get_user_data(session["user_id"])
    if user_info is None:
        return redirect(base_url)

    return render_template("user_settings.html",
                           user=user_info,
                           update_succeeded=update_succeeded,
                           session=session["user_id"])


@app.route(base_url + "/change_password", methods=["POST", "GET"])
def change_password_route():
    if session["user_id"] is None:
        return redirect(base_url)

    change_succeeded = None

    # パスワード更新
    if request.method == "POST":
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        new_password_conf = request.form["new_password_conf"]
        change_succeeded = change_password(session["user_id"],
                                           old_password,
                                           new_password,
                                           new_password_conf)

    return render_template("change_password.html",
                           session=session["user_id"],
                           change_succeeded=change_succeeded)

@app.route(base_url + "/contest_list")
def contest_list_view():
    now_page = request.args.get("page", 1, type=int)
    past_contest, now_contest, future_contest = get_3type_divided_contest()

    return render_template("contest_list.html",
                            session=session["user_id"],
                            past_contest=past_contest,
                            now_contest=now_contest,
                            now_page=now_page,
                            future_contest=future_contest)


@app.route(base_url + "/contest/<path:contest_id>")
def contest_view(contest_id):
    return contest_id


@app.route(base_url + "/problem_list")
def problem_list_view():
    now_page = request.args.get("page", 1, type=int)

    return render_template("problem_list.html",
                            session=session["user_id"],
                            now_page=now_page,
                            problem_list=get_all_problem())


@app.route(base_url + "/problem/<path:problem_id>")
def problem_view(problem_id):
    return render_template("problem.html",
                           session=session["user_id"])


@app.route(base_url + "/submission_list/<path:user_id>")
def submission_view(user_id):
    now_page = request.args.get("page", 1, type=int)

    return render_template("submission_list.html",
                           session=session["user_id"],
                           now_page=now_page,
                           submission_data=get_submission_data(user_id, "all"))


if __name__ == '__main__':
    app.run(port=11000)
