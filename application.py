#Imports
from flask import Flask, render_template, request, redirect, url_for, send_from_directory #import Flask, Jinja2 rendering
from flask_bootstrap import Bootstrap #import bootstrap - don't forget to pip install flask-bootstrap first
from flask_script import Manager #import flask-script
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash
import os
from flask import jsonify
#import sys
from flask_wtf import Form
from datetime import datetime
from wtforms import StringField, SubmitField, SelectField, BooleanField, PasswordField,validators
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sslify import SSLify
from flask import json
#############################
##          Config         ##
#############################
#reload(sys)
#sys.setdefaultencoding('latin-1')
basedir = os.path.abspath(os.path.dirname(__file__))
application = app = Flask(__name__) #Pass the __name__ argument to the Flask application constructor
manager = Manager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SECRET_KEY'] = 'you_should_really_have_this_be_an_environment_variable'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'

#Video Upload Config
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

#############################
## Route Definitions Below ##
#############################



#Form we use for logging in
class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

#Form for creating a new user
class RegistrationForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                           Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[
        Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email taken')

#login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

#logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))

#Route for registering a new user. Note - no password in model. Model will hash it.
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#Landing Page, Playback Multiple Videos
@app.route('/')
def index():
    projects=Project.query.order_by(Project.project_date.desc()).all()
    videos= Video.query.order_by(Video.date.desc()).all()
    return render_template('index.html',videos=videos,projects=projects)
#Project Page
@app.route('/project/<project_name>')
def project(project_name):
    project=Project.query.filter_by(name=project_name).one()
    videos= Video.query.order_by(Video.date.desc()).all()
    return render_template('project.html',project=project,videos=videos)

@app.route('/search', methods=['POST'])
def search():
    searchcontent = request.form['searchcontent']
    projects=Project.query.filter(Project.name.contains(searchcontent)).all()
    if len(projects)==0:
        return render_template('noresult.html')
    return render_template('result.html',projects=projects)

#Create Project Page
@app.route('/create')
@login_required
def create():
    return render_template('create.html')

#Upload Video Page
@app.route('/upload')
@login_required
def upload():
    return render_template('upload.html')

#Create Database
# @app.route('/create_db')
# def create_db():
#     db.drop_all()
#     db.create_all()
#     return '<h1>Database Created</h1>'
#Create Project -- Post
@app.route('/createproject', methods=['POST'])
def createproject():
    name=request.form['name']
    project_description=request.form['project_description']
    #Image Upload Store File
    target = os.path.join(APP_ROOT, 'static/img/')
    for file in request.files.getlist("file"):
        image_file=file.filename
        destination = "/".join([target, image_file])
        file.save(destination)
    project=Project(picture_name=image_file,name=name,project_description=project_description,user_id=current_user.id,project_date=datetime.now())
    db.session.add(project)
    db.session.commit()
    videos= Video.query.order_by(Video.date.desc()).all()
    return render_template('project.html', project=project,videos=videos)
    # for file in request.files.getlist("file"):
    #     file.seek(0, os.SEEK_END)
    #     if not file.tell() == 0:
    #         image_file=file.filename
    #         destination = "/".join([target, image_file])
    #         file.save(destination)
    #         project=Project(picture_name=image_file,name=name,project_description=project_description,user_id=current_user.id)
    #         db.session.add(project)
    #         db.session.commit()
    #         videos= Video.query.order_by(Video.date.desc()).all()
    #         return render_template('project.html', project=project,videos=videos)
    #     else:
    #         flash('No selected file')
    #         return redirect('create')


#Video Page
@app.route('/video/<video_title>')
def video(video_title):
    video= Video.query.filter_by(title=video_title).one()
    date=video.date.strftime('%B %d, %Y ')
    videos= Video.query.order_by(Video.date.desc()).all()
    # userid = current_user.id
    return render_template('video.html',video=video,date=date,videos=videos)

#Upload Video -- Post
@app.route('/uploadvideo', methods=['POST'])
def uploadvideo():
    #Video Upload Store File
    target = os.path.join(APP_ROOT, 'static/vid/')
    for file in request.files.getlist("file"):
        video_file=file.filename
        destination = "/".join([target, video_file])
        file.save(destination)

    title=request.form['title']
    feedback=request.form['feedback']
    description=request.form['description']
    project_id_this = request.form['selected-project']
    if len(project_id_this)==0:
        flash('Please select a project')
        return render_template('upload.html')
    else:
        video = Video(vid_name=video_file,title=title,description=description,feedback=feedback,date=datetime.now(),user_id=current_user.id,project_id=project_id_this)
        db.session.add(video)
        db.session.commit()
        return render_template('video.html', video=video)
#add comment by ajax
@app.route('/api/addcomment', methods=['POST'])
@login_required
def apiaddcomment():
    data = request.data
    dataDict = json.loads(data)
    videoname = dataDict["videoname"]
    videoid = dataDict["videoid"]
    content = dataDict["comment"]
    commenttime = dataDict["timestamp"]
    video= Video.query.filter_by(title=videoname).one()
    date=video.date.strftime('%B %d, %Y ')
    if len(content)==0:
        response = app.response_class(
            status = 400,
            mimetype='application/json'
        )
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'}
    else:
        print(current_user.id)
        comment = Comment(content=content,user_id=current_user.id,video_id=videoid,time=commenttime)
        db.session.add(comment)
        db.session.commit()
        response = app.response_class(
            status = 200,
            mimetype='application/json'
        )
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


# add comment
@app.route('/addcomment', methods=['POST'])
@login_required
def addcomment():
    # content=request.args.get('cmt_content')
    # videoid=request.args.get('videoid')
    # videoname = request.args.get('videoname')
    content=request.form['btn-input']
    videoid=request.form['videoid']
    videoname = request.form['videoname']
    commenttime = request.form['timestamp']
    video= Video.query.filter_by(title=videoname).one()
    date=video.date.strftime('%B %d, %Y ')
    videos= Video.query.order_by(Video.date.desc()).all()
    if len(content)==0:
        flash('must fill in something')
        return render_template('video.html',video=video,date=date,videos=videos)
    else:
        comment = Comment(content=content,user_id=current_user.id,video_id=videoid,time=commenttime)
        db.session.add(comment)
        db.session.commit()
        return render_template('video.html',video=video,date=date,videos=videos)
#Playback Single Video
# @app.route('/../static/vid/<filename>')
# def send_vid(filename):
#     return send_from_directory("vid", filename)

#############################
## Model Definitions Below ##
#############################
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    video_id = db.Column(db.Integer,db.ForeignKey('videos.id'),nullable=False)
    content = db.Column(db.String(64))
    time = db.Column(db.String(64))

class Video(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False) # how to connect the foreign key of user???
    project_id = db.Column(db.Integer,db.ForeignKey('projects.id'),nullable=False)
    title = db.Column(db.String(64))
    comments = db.Column(db.String(64), unique=True, index=True)
    description = db.Column(db.String(120), nullable=True)
    likes = db.Column(db.Integer)
    vid_name = db.Column(db.String, default=None, nullable=True)
    date = db.Column(db.DateTime) # not in scope right now
    feedback=db.Column(db.String(120),nullable=True)
    comment_list = db.relationship('Comment',
                               foreign_keys=[Comment.video_id],
                               backref=db.backref('video', lazy='joined'),
                               lazy='dynamic')
class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    name = db.Column(db.String(64))
    project_date = db.Column(db.DateTime)
    genre = db.Column(db.String(64)) ##or should we use Integer
    project_description = db.Column(db.String(120))
    #picture = db.Column(db.LargeBinary)
    picture_name= db.Column(db.String, default=None, nullable=True)
    video_list = db.relationship('Video',
                               foreign_keys=[Video.project_id],
                               backref=db.backref('project', lazy='joined'),
                               lazy='dynamic')

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    project_list = db.relationship('Project',
                               foreign_keys=[Project.user_id],
                               backref=db.backref('author_project', lazy='joined'),
                               lazy='dynamic')
    video_list = db.relationship('Video',
                               foreign_keys=[Video.user_id],
                               backref=db.backref('author_video', lazy='joined'),
                               lazy='dynamic')
    comment_list = db.relationship('Comment',
                               foreign_keys=[Comment.user_id],
                               backref=db.backref('author_comment', lazy='joined'),
                               lazy='dynamic')
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)





#user loader for login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

###########################################
## Run the Flask Webserver in debut mode ##
###########################################
if __name__=='__main__':
    app.config['TEMPLATES_AUTO_RELOAD']=True
    app.run(debug=True,threaded=True)
