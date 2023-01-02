from flask import *
from flask_login import login_required, logout_user, current_user, login_user, UserMixin, current_user
from datetime import datetime, timedelta
from flask_sqlalchemy import *
from werkzeug.security import *
from flask_login import LoginManager
from flask_admin import *
from flask_admin.contrib.sqla import ModelView
import random
import string
from flask_migrate import Migrate
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
import requests
import subprocess
import os
import re
from subprocess import Popen, PIPE
from threading import Timer

# ASH SUBSCRIBERS
ash=["volcano", "riolku"]

upload_profile = "./static/images/profile"
app = Flask(__name__, static_folder='./static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['UPLOAD_PROFILE'] = upload_profile
app.config['SECRET_KEY'] = open('secret_key.txt', 'r').read()
login_manager = LoginManager()
login_manager.init_app(app)
db=SQLAlchemy(app)
migrate = Migrate(app, db)

class news(db.Model):
    __tablename__="News"
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String, default="volcano's Next Post")
    body=db.Column(db.String)
    authors=db.Column(db.String, default="N/A")
    date=db.Column(db.DateTime, default=datetime.now)

class problems(db.Model):
    __tablename__="Problem"
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String, default="volcano's Next Problem")
    body=db.Column(db.String)
    testcase=db.Column(db.Text)
    output=db.Column(db.Text)
    timelimit=db.Column(db.Integer)
    authors=db.Column(db.String, default="N/A")
    samplein=db.Column(db.String, default="N/A")
    sampleout=db.Column(db.String, default="N/A")
    sampleex=db.Column(db.String, default="N/A")
    code=db.Column(db.String)
    points=db.Column(db.Integer)
    contestfor=db.Column(db.String, default="None")

class contests(db.Model):
    __tablename__="Contest"
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String, default="volcano's Next Contest")
    about=db.Column(db.Text)
    problemcount=db.Column(db.Integer)
    timelimit=db.Column(db.Integer)
    setter=db.Column(db.String, default="N/A")
    date=db.Column(db.DateTime, default=datetime.now)
    end_date=db.Column(db.String)
    code=db.Column(db.String)
    rated=db.Column(db.Integer, default=0)
    p1=db.Column(db.String, default="None")
    p2=db.Column(db.String, default="None")
    p3=db.Column(db.String, default="None")
    p4=db.Column(db.String, default="None")
    p5=db.Column(db.String, default="None")
    registered=db.Column(db.String, default=" ")
    problems=db.Column(db.String, default=" ")

class comments(db.Model):
    __tablename__="Comment"
    id=db.Column(db.Integer, primary_key=True)
    body=db.Column(db.Text)
    author=db.Column(db.String)
    username=db.Column(db.String)
    problem=db.Column(db.String)
    date=db.Column(db.DateTime, default=datetime.now)
    votes=db.Column(db.Integer, default=0)
    voted=db.Column(db.String, default=" ")

class User(db.Model, UserMixin):
    __tablename__="Login"
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String, unique=True)
    password=db.Column(db.String)
    email=db.Column(db.String, unique=True)
    org = db.Column(db.String(140), default="None")
    profile_pic = db.Column(db.String, default="/static/images/profile/404.jpg")
    isverified = db.Column(db.Integer, default = 0)
    rating = db.Column(db.Integer, default=0)
    maxrating = db.Column(db.Integer, default=0)
    contestsauthored = db.Column(db.Integer, default=0)
    totalpoints = db.Column(db.Integer, default=0)
    completedproblems = db.Column(db.String, default=" ")
    darkmode=db.Column(db.Integer, default=0)
    bio=db.Column(db.String, default="This user seems to be quite boring.")
    incontest=db.Column(db.Integer, default=0)
    currcontest=db.Column(db.String, default="None")
    currscore=db.Column(db.Integer, default=-1)
    timestarted=db.Column(db.DateTime, default=datetime.now())
    colour=db.Column(db.String, default="#525252")


    def __repr__(self):
        return "Registered User " + str(self.id)
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Submission(db.Model):
    __tablename__ = "submission"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey("Login.id"))
    prob = db.Column(db.Integer, db.ForeignKey("Problem.id"))


@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)
    return None


@app.route("/")
def start():
    problemcount=problems.query.count()
    contestcount=contests.query.count()
    if current_user.is_authenticated:
        p=problems.query.order_by(problems.title.desc()).all()
        c=comments.query.order_by(comments.date.desc()).all()
        c=c[:4]
        news1=news.query.order_by(news.date.desc()).all()
        return render_template("index.html", User=User, comments=c, prob=p, news=news1[:3], problemcount=problemcount, contestcount=contestcount, contests=contests.query.order_by(contests.date))
    else:
        return render_template("index_no.html", problemcount=problemcount, contestcount=contestcount, totalcontests=0)

@app.route("/signup", methods=["GET","POST"])
def register():
    global passmsg
    username = request.form['username']
    email = request.form["email"]
    password = request.form["password"]
    org = request.form["org"]
    existing_user = User.query.filter_by(email=email).first()
    existing_user1 = User.query.filter_by(username=username).first()
    if existing_user is None:
        if existing_user1 is None:
            user=User(email=email, username=username, org=org)
            user.set_password(password)
            if re.fullmatch("[0-9A-Za-z_]{1,16}", user.username) is None or re.fullmatch("[0-9A-Za-z_ ]{1,100}", user.org) is None or re.fullmatch("[0-9A-Za-z_.]+@[0-9A-Za-z-.]+\\.[A-Za-z]+", user.email) is None or "volcano" in user.username.lower() or "volcano" in user.org.lower():
                return redirect(request.referrer)
            else:
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect("/")
        else:
            return redirect(request.referrer)
    else:
        return redirect(request.referrer)

@app.route("/edit-profile")
@login_required
def edit_profile1():
    problemcount=problems.query.count()
    contestcount=contests.query.count()
    return render_template("edit_profile.html", problemcount=problemcount, contestcount=contestcount, totalcontests=0)

@app.route("/edit-profile-admin")
@login_required
def edit_profile_admin1():
    if current_user.username=="volcano":
        problemcount=problems.query.count()
        contestcount=contests.query.count()
        return render_template("edit_profile_admin.html", problemcount=problemcount, contestcount=contestcount, totalcontests=0)

@app.route("/edit-profile/submit", methods=["GET", "POST"])
@login_required
def edit_profile2():
    org = request.form['in1']
    bio = request.form['in2']
    if current_user.org!="Volcano Judge" and "Volcano" not in org and "volcano" not in org and len(org)<17 and "<" not in org and ">" not in org:
        current_user.org=org
    if "script" not in bio and "$" not in bio and "%" not in bio and "<" not in bio and ">" not in bio:
        current_user.bio=bio
    db.session.commit()
    return redirect(request.referrer)

@app.route("/edit-profile-admin/submit", methods=["GET", "POST"])
@login_required
def edit_profile_admin2():
    if current_user.username=="volcano":
        username = org = request.form['in3']
        user=User.query.filter_by(username=username).first()
        org = request.form['in1']
        bio = request.form['in2']
        user.org=org
        user.bio=bio
        db.session.commit()
        return redirect(request.referrer)

@app.route("/comment/<id>/delete", methods=['GET', 'POST'])
@login_required
def delete_comment_1(id):
    if current_user.username=="volcano":
        comm=comments.query.filter_by(id=id).first()
        db.session.delete(comm)
        db.session.commit()
        return "success"
    else:
        abort(403)

@app.errorhandler(401)
def page_not_found(e):
    return render_template('401.html'), 401

@app.errorhandler(403)
def page_not_found(e):
    return render_template('401.html'), 403


@app.route("/comment/<id>/upvote", methods=['GET', 'POST'])
@login_required
def comment_upvote(id):
    comm=comments.query.filter_by(id=id).first()
    if (current_user.username in comm.voted or current_user.username==comm.username) and current_user.username!="volcano":
        return redirect(request.referrer)
    else:
        comm.votes+=1
        if current_user.username!="volcano":
            comm.voted=comm.voted+current_user.username+" "
        db.session.commit()
        return redirect(request.referrer)

@app.route("/comment/<id>/downvote", methods=['GET', 'POST'])
@login_required
def comment_downvote(id):
    comm=comments.query.filter_by(id=id).first()
    if (current_user.username in comm.voted or current_user.username==comm.username) and current_user.username!="volcano":
        return redirect(request.referrer)
    else:
        comm.votes-=1
        if current_user.username!="volcano":
            comm.voted=comm.voted+current_user.username+" "
        if comm.votes<-12:
            db.session.delete(comm)
        db.session.commit()
        return redirect(request.referrer)

@app.route("/delete-account")
@login_required
def delete_account():
    if current_user.username=="volcano":
        return render_template("delete_account.html")
    else:
        abort(403)

@app.route("/delete-account/result", methods=['GET', 'POST'])
@login_required
def delete_account_1():
    if current_user.username=="volcano":
        username=request.form["in1"]
        user=User.query.filter_by(username=username).first()
        comm=comments.query.filter_by(username=username).all()
        for c in comm:
            db.session.delete(c)
        db.session.delete(user)
        db.session.commit()
        return "success"
    else:
        abort(403)

@app.route("/login",methods=['GET','POST'])
def login1():
    msg = ''
    if current_user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        user1 = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=user1).first()
        if user and user1!="":
            if user.check_password(password):
                login_user(user)
                next = request.args.get('next')
                return redirect(next or "/")
        else:
            return redirect(request.referrer)
        try:
            return redirect(request.referrer)
        except:
            return redirect("/")
    return redirect("/")

@app.route("/login_page")
def login_p():
    if current_user.is_authenticated:
        return redirect("/")
    problemcount=problems.query.count()
    contestcount=contests.query.count()
    return render_template("login.html", problemcount=problemcount, contestcount=contestcount, totalcontests=0)

@app.route("/logout")
@login_required
def logout_page():
    logout_user()
    return redirect("/")

@app.route("/create-contest")
@login_required
def create_contest():
    return render_template("create_contest.html")

@app.route("/user/<username>/edit")
@login_required
def edit_user_admin(username):
    if current_user.username=="volcano":
        return render_template("edit_user_admin.html", username=username)

@app.route("/user/<username>/edit/result", methods=["GET", "POST"])
@login_required
def edit_user_admin_result(username):
    if current_user.username=="volcano":
        user1=User.query.filter_by(username=username).first()
        rating=request.form["rating"]
        maxrating=request.form["maxrating"]
        user1.rating=rating
        user1.maxrating=maxrating
        colour="black"
        new=int(rating)
        if new==0:
            colour="#525252"
        elif new>0 and new<100:
            colour="#99a199"
        elif new<300:
            colour="#95f59d"
        elif new<500:
            colour="#738cde"
        elif new<800:
            colour="#f7c728"
        elif new<1200:
            colour="#fc5347"
        else:
            colour="#800000"
        user1.colour=colour
        db.session.commit()
        return "success"

@app.route("/user/<username>")
def user_profile(username):
    problemcount=problems.query.count()
    contestcount=contests.query.count()
    actual=username
    try:
        user=User.query.filter_by(username=username).first()
        colour="black"
        if user.rating==0:
            username=username+" [unrated]"
            colour="#525252"
        elif user.rating>0 and user.rating<100:
            username=username+" [beginner]"
            colour="#99a199"
        elif user.rating<300:
            username=username+" [good]"
            colour="#95f59d"
        elif user.rating<500:
            username=username+" [expert]"
            colour="#738cde"
        elif user.rating<800:
            username=username+" [ruler]"
            colour="#f7c728"
        elif user.rating<1200:
            username=username+" [crazy]"
            colour="#fc5347"
        else:
            username=username+" [god]"
            colour="#800000"
        colour2="black"
        if user.maxrating==0:
            colour2="#525252"
        elif user.maxrating>0 and user.maxrating<100:
            colour2="#99a199"
        elif user.maxrating<300:
            colour2="#95f59d"
        elif user.maxrating<500:
            colour2="#738cde"
        elif user.maxrating<800:
            colour2="#f7c728"
        elif user.maxrating<1200:
            colour2="#fc5347"
        else:
            colour2="#800000"
        return render_template("user.html", is_ash=(actual in ash), user=user, colour2=colour2, problemcount=problemcount, contestcount=contestcount, totalcontests=0, points=user.totalpoints, username=username, rating=user.rating, max_rating=user.maxrating, contests_authored=user.contestsauthored, colour=colour)
    except:
        return "This username couldn't be found"

@app.route("/rankings")
def rankings():
    problemcount=problems.query.count()
    contestcount=contests.query.count()
    a=0
    users=User.query.order_by(User.totalpoints.desc()).all()
    return render_template("rankings.html", users=users, a=a, problemcount=problemcount, contestcount=contestcount, totalcontests=0)

@app.route("/dark-mode")
@login_required
def dark_mode():
    if current_user.darkmode==0:
        current_user.darkmode=1
        db.session.commit()
    else:
        current_user.darkmode=0
        db.session.commit()
    return redirect(request.referrer)

@app.route("/contest/<code>")
@login_required
def contest_page(code):
    problemcount=problems.query.count()
    contestcount=contests.query.count()
    try:
        time_up=False
        contest=contests.query.filter_by(code=code).first()
        seconds_in_day = 24 * 60 * 60
        difference = datetime.now() - current_user.timestarted
        time=divmod(difference.days * seconds_in_day + difference.seconds, 60)
        if current_user.currcontest==code and time[0]>=contest.timelimit:
            time_up=True
        is_rated=""
        if contest.rated==1:
            is_rated="Yes"
        else:
            is_rated="No"
        p1=contest.p1
        p2=contest.p2
        p3=contest.p3
        p4=contest.p4
        p5=contest.p5
        a=str(contest.date)
        for i in range(16):
            a=a[:-1]
        left=300-len(contest.registered.split())
        return render_template("contest.html", timeup=time_up, registered=contest.registered.split(), problemcount=problemcount, contestcount=contestcount, totalcontests=0, left=left, contest=contest, date=a, code=code, rated=is_rated, title=contest.title, organizers=contest.setter, time_allowed=contest.timelimit)
    except:
        return "This contest couldn't be found"

@app.route("/contest/<code>/close")
@login_required
def close_contest(code):
    if current_user.username=="volcano":
        contest=contests.query.filter_by(code=code).first()
        db.session.delete(contest)
        prob=problems.query.filter_by(contestfor=code).all()
        user_=User.query.filter_by(currcontest=code).all()
        for p in prob:
            p.contestfor="None"
        if contest.rated==1:
            user=User.query.filter_by(currcontest=code).all()
            username_list=[]
            score_list=[]
            for u in user:
                username_list.append(u.username)
                score_list.append(u.currscore)
            scores, usernames = zip(*sorted(zip(score_list, username_list), reverse=True))
            ratings=[]
            for i in usernames:
                u1=User.query.filter_by(username=i).first()
                ratings.append(u1.rating)
            for i in range(len(usernames)):
                user1=User.query.filter_by(username=usernames[i]).first()
                if user1.rating!=0:
                    user1.rating=(ratings[i]+(3*len(usernames)*(len(usernames)-i+1)))//2
                    new=(ratings[i]+(3*len(usernames)*(len(usernames)-i+1)))//2
                    user1.maxrating=max(user1.maxrating, new)
                    colour="black"
                    if new==0:
                        colour="#525252"
                    elif new>0 and new<100:
                        colour="#99a199"
                    elif new<300:
                        colour="#95f59d"
                    elif new<500:
                        colour="#738cde"
                    elif new<800:
                        colour="#f7c728"
                    elif new<1200:
                        colour="#fc5347"
                    else:
                        colour="#800000"
                    user1.colour=colour
                else:
                    user1.rating=(3*len(usernames)*(len(usernames)-i+1))
                    new=(3*len(usernames)*(len(usernames)-i+1))
                    user1.maxrating=max(user1.maxrating, new)
                    colour="black"
                    if new==0:
                        colour="#525252"
                    elif new>0 and new<100:
                        colour="#99a199"
                    elif new<300:
                        colour="#95f59d"
                    elif new<500:
                        colour="#738cde"
                    elif new<800:
                        colour="#f7c728"
                    elif new<1200:
                        colour="#fc5347"
                    else:
                        colour="#800000"
                    user1.colour=colour
        for u in user_:
            u.currcontest="None"
        db.session.commit()
        return "Contest closed permanently."
    else:
        return "unauthorized"

@app.route("/contest/<code>/register")
@login_required
def contest_register(code):
    problemcount=problems.query.count()
    contestcount=contests.query.count()
    try:
        contest=contests.query.filter_by(code=code).first()
        is_rated=""
        if contest.rated==1:
            is_rated="Yes"
        else:
            is_rated="No"
        p1=contest.p1
        p2=contest.p2
        p3=contest.p3
        p4=contest.p4
        p5=contest.p5
        a=str(contest.date)
        for i in range(16):
            a=a[:-1]
        left=300-len(contest.registered.split())
        return render_template("register_contest.html", problemcount=problemcount, contestcount=contestcount, totalcontests=0, left=left, contest=contest, date=a, code=code, rated=is_rated, title=contest.title, organizers=contest.setter, time_allowed=contest.timelimit)
    except:
        return "This contest couldn't be found"

@app.route("/contest-rules")
def contest_rules():
    return render_template("contest_rules.html")

@app.route("/about")
def about_page():
    problemcount=problems.query.count()
    contestcount=contests.query.count()
    return render_template("about.html", problemcount=problemcount, contestcount=contestcount, totalcontests=0, User=User)

@app.route("/contact")
def contact_page():
    problemcount=problems.query.count()
    contestcount=contests.query.count()
    return render_template("contact.html", problemcount=problemcount, contestcount=contestcount, totalcontests=0, User=User)

@app.route("/contest/<code>/register/submit")
@login_required
def contest_register_submit(code):
    contest=contests.query.filter_by(code=code).first()
    if len(contest.registered.split())<300 and current_user.username not in contest.registered.split():
        contest.registered=contest.registered+" "+current_user.username
        current_user.incontest=1
        current_user.currscore=0
        current_user.currcontest=code
        current_user.timestarted=datetime.now()
        db.session.commit()
        return redirect("/contest/"+code)
    else:
        return "Something happened while trying to register you. Either you have already registered or the max limit has been reached. Stop trying."

@app.route("/contest/change-score")
@login_required
def change_contest_scoreboard():
    if current_user.username=="contestbot":
        return render_template("change_scoreboard.html")
    else:
        abort(403)

@app.route("/contest/change-score/submit", methods=['GET', 'POST'])
@login_required
def change_contest_scoreboard_submit():
    if current_user.username=="contestbot":
        username=request.form["in1"]
        score=request.form["in2"]
        user1=User.query.filter_by(username=username).first()
        user1.currscore=score
        db.session.commit()
        return "success"
    else:
        abort(403)

@app.route("/contest/<code>/scoreboard")
@login_required
def contest_scoreboard(code):
    try:
        problemcount=problems.query.count()
        contestcount=contests.query.count()
        contest=contests.query.filter_by(code=code).first()
        user=User.query.filter_by(currcontest=code).all()
        username_list=[]
        score_list=[]
        for u in user:
            username_list.append(u.username)
            score_list.append(u.currscore)
        scores, usernames = zip(*sorted(zip(score_list, username_list), reverse=True))
        ratings=[]
        for i in usernames:
            u1=User.query.filter_by(username=i).first()
            ratings.append(u1.rating)
        return render_template("contest_scoreboard.html", ratings=ratings, length=len(usernames), rated=contest.rated, title=contest.title, contest=contest, scores=scores, usernames=usernames, problemcount=problemcount, contestcount=contestcount, totalcontests=0)
    except:
        return "Nobody has started yet!"

@app.route("/publish-contest")
@login_required
def publish_contest():
    if current_user.username!="volcano":
        abort(403)
    else:
        return render_template("publish.html")

@app.route("/publish-problem")
@login_required
def publish_problem():
    if current_user.username!="volcano":
        abort(403)
    else:
        return render_template("publish_prob.html")


@app.route("/publish-news")
@login_required
def publish_news():
    if current_user.username!="volcano":
        abort(403)
    else:
        return render_template("publish_news.html")

@app.route("/p-prob",methods=['GET','POST'])
@login_required
def p_prob():
    title = request.form['title']
    code = request.form['code']
    authors = request.form['authors']
    tl = request.form['tl']
    tc = request.form['tc']
    o = request.form['o']
    body = request.form['body']
    samplein = request.form['si']
    sampleout = request.form['so']
    sampleex = request.form['se']
    points = request.form['p']
    contest = request.form['contest']
    if current_user.username=="volcano":
        problem=problems(contestfor=contest, title=title, points=points, code=code, authors=authors, timelimit=tl, body=body, testcase=tc, output=o, samplein=samplein, sampleout=sampleout, sampleex=sampleex)
        db.session.add(problem)
        db.session.commit()
        return "Problem Published!"
    else:
        abort(403)

@app.route("/p-cont",methods=['GET','POST'])
@login_required
def p_cont():
    title = request.form['title']
    code = request.form['code']
    organizers = request.form['organizers']
    tl = request.form['tl']
    rated = request.form['rat']
    p1 = request.form['p1l']
    p2 = request.form['p2l']
    p3 = request.form['p3l']
    p4 = request.form['p4l']
    p5 = request.form['p5l']
    end = request.form['end']
    pcount = request.form['pcount']
    about = request.form['body']
    rated1=0
    if rated=="yes":
        rated1=1
    if current_user.username=="volcano":
        contest=contests(problemcount=pcount, title=title, about=about, code=code, setter=organizers, timelimit=tl, rated=rated1, p1=p1, p2=p2, p3=p3, p4=p4, p5=p5, end_date=end)
        db.session.add(contest)
        db.session.commit()
        return "Contest Published!"
    else:
        abort(403)

@app.route("/problem/<code>")
def problem_page(code):
    problemcount=problems.query.count()
    contestcount=contests.query.count()
    problem=problems.query.filter_by(code=code).first()
    p=str(problem.body)
    comm=comments.query.filter_by(problem=code).all()
    comm.reverse()
    if not problem.contestfor or current_user.currcontest==problem.contestfor:
        return render_template("problem.html", User=User, problem=problem, comm=comm, points=problem.points, problemcount=problemcount, contestcount=contestcount, totalcontests=0, code=code, body=p, testcase=problem.testcase, output=problem.output, authors=problem.authors, timelimit=problem.timelimit, title=problem.title, samplein=problem.samplein, sampleout=problem.sampleout, sampleex=problem.sampleex)
    else:
        return "This problem couldn't be found. You may be writing a contest, this problem may not exist, or you might not be logged in."

@app.route("/problem/<code>/edit")
@login_required
def problem_page_edit(code):
    if current_user.username=="volcano" or current_user.username=="contestbot":
        problemcount=problems.query.count()
        contestcount=contests.query.count()
        problem=problems.query.filter_by(code=code).first()
        p=str(problem.body)
        comm=comments.query.filter_by(problem=code).all()
        if current_user.currcontest==problem.contestfor:
            return render_template("edit_problem.html", User=User, problem=problem, comm=comm, points=problem.points, problemcount=problemcount, contestcount=contestcount, totalcontests=0, code=code, body=p, testcase=problem.testcase, output=problem.output, authors=problem.authors, timelimit=problem.timelimit, title=problem.title, samplein=problem.samplein, sampleout=problem.sampleout, sampleex=problem.sampleex)
        else:
            return "This problem couldn't be found"
    else:
        abort(403)

@app.route("/problem/<code>/edit/result", methods=['GET', 'POST'])
@login_required
def problem_page_edit_result(code):
    if current_user.username=="volcano" or current_user.username=="contestbot":
        body=request.form["in1"]
        sampleex=request.form["in2"]
        input=request.form["in3"]
        output=request.form["in4"]
        samplein=request.form["in5"]
        sampleout=request.form["in6"]
        problem=problems.query.filter_by(code=code).first()
        problem.body=body
        problem.sampleex=sampleex
        problem.testcase=input
        problem.output=output
        problem.samplein=samplein
        problem.sampleout=sampleout
        db.session.commit()
        return "success"
    else:
        abort(403)

@app.route("/problems")
def redir_problems():
    return redirect("/problems/alpha")

@app.route("/problems/<order>")
def problems_page(order):
    problemcount=problems.query.count()
    contestcount=contests.query.count()
    try:
        if (order=="alpha"):
            p=problems.query.order_by(problems.title.asc()).all()
            return render_template("problems.html", prob=p, problemcount=problemcount, contestcount=contestcount, totalcontests=0)
        elif (order=="high-points"):
            p=problems.query.order_by(problems.points.desc()).all()
            return render_template("problems.html", prob=p, problemcount=problemcount, contestcount=contestcount, totalcontests=0)
        elif (order=="low-points"):
            p=problems.query.order_by(problems.points.asc()).all()
            return render_template("problems.html", prob=p, problemcount=problemcount, contestcount=contestcount, totalcontests=0)
        else:
            return "Format must be 'problems/[order]' Where [order] must be replaced with one of the following:<br>alpha, high-points, low-points"
    except:
        return "There seems to be an issue with loading problems right now"


@app.route("/contests")
def contests_page():
    problemcount=problems.query.count()
    contestcount=contests.query.count()
    try:
        p=contests.query.order_by(contests.date.desc()).all()
        return render_template("contests.html", prob=p, problemcount=problemcount, contestcount=contestcount, totalcontests=0)
    except:
        return "There seems to be an issue with loading contests right now"


@app.route("/announcement/<id>/delete", methods=['GET', 'POST'])
@login_required
def delete_news(id):
    if current_user.username=="volcano":
        new=news.query.filter_by(id=id).first()
        db.session.delete(new)
        db.session.commit()
        return "success"

@app.route("/comment/<code>", methods=['GET', 'POST'])
@login_required
def comment_problem(code):
    body=request.form['body']
    username=current_user.username
    user=current_user
    problem=code
    if current_user.currcontest=="None" and "<" not in body and "$" not in body and len(body)>2 and "DROP" not in body:
        comment=comments(body=body, author=username, problem=problem, username=current_user.username)
        db.session.add(comment)
        db.session.commit()
    return redirect(request.referrer)

@app.route("/problem/<code>/submit")
@login_required
def submit_page(code):
    problemcount=problems.query.count()
    contestcount=contests.query.count()
    try:
        problem=problems.query.filter_by(code=code).first()
        return render_template("problem_submit.html", code=code, title=problem.title)
    except:
        return "This problem couldn't be found"

@app.route("/problem/<code>/submit/python3")
@login_required
def submit_page_py3(code):
    return "No"
    problemcount=problems.query.count()
    contestcount=contests.query.count()
    try:
        problem=problems.query.filter_by(code=code).first()
        if current_user.currcontest==problem.contestfor:
            if current_user.darkmode==0:
                return render_template("problem_submit_py3_light.html", problemcount=problemcount, contestcount=contestcount, totalcontests=0, code=code, title=problem.title, body=problem.body, samplein=problem.samplein, sampleout=problem.sampleout, sampleex=problem.sampleex)
            else:
                return render_template("problem_submit_py3_dark.html", problemcount=problemcount, contestcount=contestcount, totalcontests=0, code=code, title=problem.title, body=problem.body, samplein=problem.samplein, sampleout=problem.sampleout, sampleex=problem.sampleex)
        else:
            return "This problem couldn't be found"
    except:
        return "This problem couldn't be found"

@app.route("/problem/<code>/submit/python3/result",methods=['GET','POST'])
@login_required
def submit_page_py3_send(code):
        return "No"
        problemcount=problems.query.count()
        contestcount=contests.query.count()
        problem1=problems.query.filter_by(code=code).first()
        if current_user.currcontest!=problem1.contestfor:
            return "Some error occurred."
        prog = request.form['program']
        if "_" in prog:
            return "Something happened. Ensure your variable names don't contain special characters please, since the judge can't handle them at the moment."
        s=open("try_python.py", "w")
        s.write("from sandbox import Sandbox\n")
        s.write("s=Sandbox()\n")
        s.write(prog)
        s.close()
        problem=problems.query.filter_by(code=code).first()
        s=open("python_input.txt", "w")
        s.write(problem.testcase)
        s.close()
        c=open("python_input.txt", "r")
        lines=c.readlines()
        with open("python_input.txt", "w") as f:
            for line in lines:
                if line != "\n":
                    f.write(line)
        s=open("python_output.txt", "w")
        s.write(problem.output+"\n")
        s.close()
        c=open("python_output.txt", "r")
        lines=c.readlines()
        with open("python_output.txt", "w") as f:
            for line in lines:
                if line != "\n":
                    f.write(line)
        try:
            r=open("python_input.txt", "r")
            py_output = subprocess.check_output(['python', 'try_python.py'], stdin=r, timeout=problem.timelimit)
        except subprocess.TimeoutExpired as t:
            return render_template("problem_timeout.html", problem=problem1, problemcount=problemcount, contestcount=contestcount, totalcontests=0)
        except subprocess.CalledProcessError as e:
            return render_template("problem_invalid_return.html", problem=problem1, problemcount=problemcount, contestcount=contestcount, totalcontests=0)
        output=str(py_output)
        output=output[2:]
        output=output[:-3]
        output=output+"\n"
        f=open("python_output.txt", "r")
        a=bytes(f.read(), 'utf-8')
        output=bytes(output, 'utf-8')
        a=str(a)
        output=str(output)
        output=str(output).replace("\\n", "n")
        output=output[:-2]
        a=a[:-3]
        if a==output:
            if problem.code not in current_user.completedproblems.split():
                current_user.totalpoints+=problem.points
                current_user.completedproblems=current_user.completedproblems+" "+problem.code
                seconds_in_day = 24 * 60 * 60
                difference = datetime.now() - current_user.timestarted
                time=divmod(difference.days * seconds_in_day + difference.seconds, 60)
                if current_user.currcontest!="None":
                    contest=contests.query.filter_by(code=current_user.currcontest).first()
                    if problem.contestfor!="None" and current_user.currcontest==problem.contestfor and time[0]<contest.timelimit:
                        current_user.currscore+=1
            seconds_in_day = 24 * 60 * 60
            difference = datetime.now() - current_user.timestarted
            time=divmod(difference.days * seconds_in_day + difference.seconds, 60)
            if current_user.currcontest!="None":
                contest=contests.query.filter_by(code=current_user.currcontest).first()
                if problem.contestfor!="None" and current_user.currcontest==problem.contestfor and time[0]>=contest.timelimit:
                    current_user.totalpoints+=problem.points
                    current_user.completedproblems=current_user.completedproblems+" "+problem.code
                    contest=contests.query.filter_by(code=problem.contestfor).first()
                    return render_template("problem_correct_time_up.html", problem=problem1, problemcount=problemcount, contestcount=contestcount, totalcontests=0)
            db.session.commit()
            return render_template("problem_correct.html", problem=problem1, problemcount=problemcount, contestcount=contestcount, totalcontests=0)
        else:
            return render_template("problem_wrong.html", problem=problem1, problemcount=problemcount, contestcount=contestcount, totalcontests=0)
        w=open("python_output.txt", "w")
        w.close()


@app.route("/problem/<code>/submit/cpp20")
@login_required
def submit_page_cpp20(code):
    try:
        problem=problems.query.filter_by(code=code).first()
        return render_template("problem_submit_cpp20.html", code=code, title=problem.title)
    except:
        return "This problem couldn't be found"

@app.route("/problem/<code>/submit/cpp20/result",methods=['GET','POST'])
@login_required
def submit_page_cpp_send(code):
    problem=problems.query.filter_by(code=code).first()
    if problem.contestfor and current_user.currcontest!=problem.contestfor:
        return "Some error occurred."
    prog = request.form['program']
    if len(prog) == 0 or len(prog) > 32768:
        return "Size matters (min size = 1 char, max size = 32768 chars)"
    sub = Submission(user=current_user.id, prob=problem.id)
    db.session.add(sub)
    db.session.commit()
    sid = sub.id
    with open(f"{sid}.cpp", "w") as sub_f:
        sub_f.write(prog)
    input_data = problem.testcase.replace("\r", "")
    if input_data[-1:] != '\n':
        input_data += '\n'
    with open(f"{sid}.in", "w") as in_f:
        in_f.write(input_data)
    expected_out = problem.output.replace("\r", "")
    if expected_out[-1:] != '\n':
        expected_out += '\n'
    # Compile
    p = None
    try:
        p = subprocess.run(['g++', '-O2', 'csandbox.c', f'{sid}.cpp', '-lseccomp', '-o', f'{sid}.o'], timeout=2)
        if p.returncode != 0:
            os.remove(f"{sid}.in")
            return "Compile Error noob did you not test your code beforehand"
    except subprocess.TimeoutExpired:
        p.kill()
        os.remove(f"{sid}.in")
        return "Time Limit Exceeded."
    # Run
    in_f = open(f"{sid}.in", "r")
    try:
        p = subprocess.run([f'./{sid}.o'], text=True, capture_output=True, stdin=in_f, timeout=problem.timelimit)
        if p.returncode == -31:
            return "Bad syscall (killed)"
        elif p.returncode != 0:
            return "Invalid Return (nonzero error code)"
        output_data = p.stdout.replace("\r", "")
        if output_data == expected_out:
           return "Correct Answer but I'm too lazy to give you points"
        else:
           return "Wrong Answer"
    except subprocess.TimeoutExpired:
        p.kill()
        return "Time Limit Exceeded."
    finally:
        in_f.close()
        os.remove(f'{sid}.o')
        os.remove(f"{sid}.in")

@app.route("/basalt-license")
def basalt_license():
    return render_template("basalt.html")

@app.route("/p-news",methods=['GET','POST'])
@login_required
def p_news():
    title = request.form['title']
    authors = request.form['authors']
    body = request.form['body']
    if current_user.username=="volcano":
        n=news(title=title, body=body, authors=authors)
        db.session.add(n)
        total_news=news.query.order_by(news.date.desc()).all()
        if len(total_news)==9:
            db.session.delete(total_news[-1])
        db.session.commit()
        return "News Published!"
    else:
        abort(403)

with app.app_context():
  db.create_all()
