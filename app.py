from flask import Flask, render_template, request, redirect

app = Flask(__name__, static_folder="Static")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/feedback", methods=["POST"])
def feedback():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")
    print("Feedback:", name, email, message)   # for now it only prints in the terminal
    return redirect("/?sent=1#site-feedback")

if __name__ == "__main__":
    app.run(debug=True)