from flask import render_template, request
from . import home

@home.route("/test")
def test():
    return "flask route works"


@home.route("/")
def homepage():
    """
    Render the homepage template on the / route
    """
    text = request.args.get('text', '')
    return render_template("page/home/index.html", title="Welcome", text=text)


@home.route("/dashboard")
def dashboard():
    """
    Render the dashboard template on the /dashboard route
    """
    return render_template("page/home/dashboard.html", title="Dashboard")
