#Imports
from flask import Flask, render_template #import Flask, Jinja2 rendering
from flask_bootstrap import Bootstrap #import bootstrap - don't forget to pip install flask-bootstrap first
from flask_script import Manager #import flask-script
from flask_sqlalchemy import SQLAlchemy
import os
from flask_wtf import Form
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Required

#############################
##          Config         ##
#############################

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__) #Pass the __name__ argument to the Flask application constructor
manager = Manager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SECRET_KEY'] = 'you_should_really_have_this_be_an_environment_variable'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

#############################
## Form Definitions Below ##
#############################

class NameForm(Form):
    name = StringField('What would you like me to call you?', validators=[Required()])
    ready = SelectField("Are you ready for class?",choices=[('ready', 'So. Ready.'), ('sleeping', 'So. Tired.'), ('busy', 'So. Busy.')])
    submit = SubmitField('Submit')

#############################
## Route Definitions Below ##
#############################

@app.route('/', methods=['GET', 'POST']) #define the route for <server>/
def index(): #index function
    name = None
    form = NameForm()
    if form.validate_on_submit():
        existinguser=User.query.filter_by(username=form.name.data).first()
        if existinguser is None:
            name=form.name.data
            user=User(username=form.name.data, ready=form.ready.data)
            db.session.add(user)
        else:
            existinguser.username=form.name.data
            existinguser.ready=form.ready.data
            name=form.name.data
            db.session.commit()
    return render_template('index.html', form=form, name=name)

@app.route('/<name>')
def user(name):
    existinguser=User.query.filter_by(username=name).first()
    if existinguser is None:
        return 'I do not know who this is.'
    else:
        return 'This user is %s' % existinguser.ready

@app.route('/create_db')
def create_db():
    db.create_all()
    return '<h1>Database Created</h1>'

#############################
## Model Definitions Below ##
#############################
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    ready = db.Column(db.String(64), nullable=True)

###########################################
## Run the Flask Webserver in debut mode ##
###########################################
if __name__=='__main__': #only do the following if the script is executed directly skip if imported
    app.run(debug=True) #start the integrated flask webserver
