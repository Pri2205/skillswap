from flask import Flask, render_template, request, redirect

app = Flask(__name__, static_folder="Static")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/feedback", methods=["POST"])
def feedback():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")
    print("Feedback:", name, email, message)   # for now it only prints in the terminal
    return redirect("/?sent=1#site-feedback")


@app.route("/login", methods=["GET", "POST"])
def login():
    notice = None
    if request.method == "POST":
        # no database yet, so nobody can be signed in
        notice = "Sign in will work once the database is connected."
    return render_template("login.html", notice=notice)


@app.route("/register", methods=["GET", "POST"])
def register():
    notice = None
    if request.method == "POST":
        # no database yet, so the account is not saved
        notice = "Sign up will work once the database is connected."
    return render_template("register.html", notice=notice)


if __name__ == "__main__":
    app.run(debug=True)