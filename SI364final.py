# Import statements
import os
import requests
import json
import datetime
import random
from flask import Flask, render_template, session, redirect, request, url_for, flash
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from flask import jsonify #for AJAX
from wtforms import StringField, SubmitField, FileField, PasswordField, BooleanField, SelectMultipleField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from werkzeug.security import generate_password_hash, check_password_hash
from requests.exceptions import HTTPError
# Imports for login management
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from requests_oauthlib import OAuth2Session

#OAUTH CONFIG
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
basedir = os.path.abspath(os.path.dirname(__file__))

"""App Configuration"""
class Auth:
    """Google Project Credentials"""
    CLIENT_ID = ('1099272711939-e49s5l42rtvvcc0ivk181o9tmo3fi0s8.apps.googleusercontent.com')
    CLIENT_SECRET = 'M2VT2CHKZqmT1Xa-ceACptOi'
    REDIRECT_URI = 'http://localhost:5000/gCallback'
    # URIs determined by Google, below
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = ['profile', 'email'] # Could edit for more available scopes -- if reasonable, and possible without $$

class Config:
    """Base config"""
    APP_NAME = "Test Google Login"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "something secret"

class DevConfig(Config):
    """Dev config"""
    DEBUG = True
    USE_RELOADER = True
    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/364FinalProjectVINHBL" # TODO: Need to create this database or edit URL for your computer
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

class ProdConfig(Config):
    """Production config"""
    DEBUG = False
    USE_RELOADER = True
    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/364FinalProjectVINHBL" # If you were to run a different database in production, you would put that URI here. For now, have just given a different database name, which we aren't really using.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

# To set up different configurations for development of an application
config = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "default": DevConfig
}

# Application configurations
app = Flask(__name__)
app.debug = True
app.use_reloader = True
app.config['SECRET_KEY'] = 'hardtoguessstring'
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL') or "postgresql://localhost/364FinalProjectVINHBL" #project plan database URI
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['HEROKU_ON'] = os.environ.get('HEROKU')

# App addition setups
manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

# Login configurations setup
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app) # set up login manager


########################
######## Models ########
########################

#Association Tables
searched = db.Table('searched',db.Column('search_id',db.Integer, db.ForeignKey('searches.id')),db.Column('pokemon_id', db.Integer, db.ForeignKey('pokemon.id')))

user_team = db.Table('user_team', db.Column('user_id',db.Integer, db.ForeignKey('pokemon.id')),db.Column('team_id', db.Integer, db.ForeignKey('personalTeam.id')))

## IMPORTANT FUNCTION / MANAGEMENT
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


""" OAuth Session creation """
def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
            Auth.CLIENT_ID,
            state=state,
            redirect_uri=Auth.REDIRECT_URI)
    oauth = OAuth2Session(
        Auth.CLIENT_ID,
        redirect_uri=Auth.REDIRECT_URI,
        scope=Auth.SCOPE)
    return oauth

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(200))
    tokens = db.Column(db.Text)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    team = db.relationship('PersonalTeam', backref='User')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

# Model to store encountered/searched Pokemon
class Pokemon(db.Model):
    __tablename__ = "pokemon"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    ability = db.Column(db.String(128))
    sprite = db.Column(db.String(128))
    number = db.Column(db.Integer)
    imgURL = db.Column(db.String(256))

    # __repr__ method that shows the name, number, and ability of the Pokemon
    def __repr__(self):
        return "Name: {}, Number: {}, Ability: {}".format(self.name, self.number, self.ability)

# Model for users to create custom Pokemon teams
class PersonalTeam(db.Model):
    __tablename__ = "personalTeam"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id")) #one to many
    pokemon = db.relationship('Pokemon', secondary=user_team, backref=db.backref('personalTeam', lazy='dynamic'), lazy='dynamic') #many to many
# This model has a one-to-many relationship with the User model (one user, many personal Teams of Pokemon with different names. For example, 'Water Team', 'Psychic Team', etc.)

class SearchTerm(db.Model):
    __tablename__ = "searches"
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(64), unique=True)
    pokemon = db.relationship('Pokemon', secondary=searched, backref=db.backref('searches', lazy='dynamic'),lazy='dynamic')
# This model has a many to many relationship with pokemon (a search will generate many pokemon to save, and one pokemon could potentially appear in many searches)

    #repr method that returns term and type of search
    def __repr__(self):
        return "{} : {}".format(self.term, self.type)

########################
######## Forms #########
########################

#Registration form
class RegistrationForm(FlaskForm):
    email = StringField('Email:', validators=[Required(),Length(1,64),Email()])
    username = StringField('Username:',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password:',validators=[Required(),EqualTo('password2',message="Passwords must match")])
    password2 = PasswordField("Confirm Password:",validators=[Required()])
    submit = SubmitField('Register User')

    #Additional checking methods for the form
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            flash('The email provided has already been registered!')
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        if User.query.filter_by(name=field.data).first():
            flash('The username provided has already been taken!')
            raise ValidationError('Username already taken')

#Form for user to login if they already have an account
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

#Form that uses POST and sends data to the same page.
class PokemonSearchForm(FlaskForm):
    submit = SubmitField('Enter Tall Grass!')

#Another form that uses POST and sends data to the same page.
class PokemonFilterForm(FlaskForm):
    filter = StringField("Enter a pokemon name to filter by:", validators=[Required()])
    submit = SubmitField('Filter Encounters')

#Form that uses GET and sends data to a new page.
class PokemonTypeForm(FlaskForm):
    type = StringField('Enter a term to search for Pokemon', validators=[Required()])
    submit = SubmitField('Submit')

class CreateTeamForm(FlaskForm):
    name = StringField('Team Name',validators=[Required()])
    picks = SelectMultipleField('Pokemon to include')
    submit = SubmitField("Create Team")

    #Custom validator
    def validate_picks(self, field):
        if len(field.data) > 6:
            flash('Teams cannot be larger than 6 Pokemon!')
            raise ValidationError('Teams cannot be larger than 6 pokemon!')

        if len(field.data) == 0:
            flash('You must select at least 1 Pokemon!')
            raise ValidationError('You must select at least 1 Pokemon!')


#update form in case users want to change their teams' lineup
class UpdateTeamForm(FlaskForm):
    picks = SelectMultipleField('Pokemon to include')
    submit = SubmitField('Update')

    #Custom validator
    def validate_picks(self, field):
        if len(field.data) > 6:
            flash('Teams cannot be larger than 6 Pokemon!')
            raise ValidationError('Teams cannot be larger than 6 pokemon!')

        if len(field.data) == 0:
            flash('You must select at least 1 Pokemon!')
            raise ValidationError('You must select at least 1 Pokemon!')

#update button for updating pokemon teams.
class UpdateButtonForm(FlaskForm):
    submit = SubmitField("Update")

#Will allow users to delete pokemon from teams and delete teams altogether
class DeleteButton(FlaskForm):
    submit = SubmitField('Delete')


########################
### Helper functions ###
########################
baseurl = "http://pokeapi.co/api/v2/"
pokemon_search = "http://pokeapi.co/api/v2/pokemon/"
# type_url = "http://pokeapi.co/api/v2/type/" #if load times are slow, switch to uncomment this line and comment the one below.
type_url = 'http://pokeapi.salestock.net/api/v2/type/'
types = ['normal', 'fire', 'fighting', 'water', 'flying', 'grass', 'poison', 'electric', 'ground', 'psychic', 'rock', 'ice', 'bug', 'dragon', 'ghost', 'dark', 'steel', 'fairy']

#Additional helper method that gets pokemon from database by id
def get_pokemon_by_id(id):
    return Pokemon.query.filter_by(id=id).first()

def get_pokemon_from_api(param): #param is either a pokemon name or number since the API accepts both as a search query.
    url = pokemon_search + param.lower()
    response = requests.get(url).json()
    if response['forms'][0]['name']:
        name = response['forms'][0]['name']
        number = response['id']
        ability = response['abilities'][random.randint(0,len(response['abilities'])-1)]['ability']['name']#gets a random ability
        sprite = list(response['sprites'].keys())[random.randint(6,7)]#gets a random trait (shiny or not shiny)
        if 'shiny' in sprite:
            sprite = 'Shiny'
        else:
            sprite = 'Regular'
        imgURL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{}.png".format(number)
        pokemon = get_or_create_pokemon(name, ability, sprite, number, imgURL)
        return pokemon
    else:
        return flash('Error, no pokemon around!')
        return []

def get_or_create_pokemon(name, ability, sprite, number, imgURL): #identifier is either a pokemon name or number since the API accepts both as a search query.
    pokemon = db.session.query(Pokemon).filter_by(name=name, ability=ability, sprite=sprite).first()
    if pokemon:
        return pokemon
    else:
        pokemon = Pokemon(name=name, ability=ability, sprite=sprite, number=number, imgURL=imgURL)
        db.session.add(pokemon)
        db.session.commit()
    return pokemon

def get_or_create_search_term(term, pokemon_objs=[]):
    searchTerm = SearchTerm.query.filter_by(term=term).first()
    if searchTerm:
        flash('Search term was found. Added these encounters to the term.')
        for p in pokemon_objs:
            searchTerm.pokemon.append(p)
        return searchTerm
    else:
        searchTerm = SearchTerm(term=term)
        for p in pokemon_objs:
            poke = get_or_create_pokemon(name=p.name, ability=p.ability, sprite=p.sprite, number=p.number, imgURL=p.imgURL)
            searchTerm.pokemon.append(poke)
        db.session.add(searchTerm)
        db.session.commit()
        flash("Added new term")
        return searchTerm


def get_or_create_team(name, current_user, pokemon_list=[]):
    team = db.session.query(PersonalTeam).filter_by(name=name, user_id=current_user.id).first()
    if team:
        flash('Team already exists!')
        return team
    else:
        team = PersonalTeam(name=name, user_id=current_user.id, pokemon=[])
        for p in pokemon_list:
            team.pokemon.append(p)
        db.session.add(team)
        db.session.commit()
        return team

#gets 5 random pokemon of type and returns a list of pokemon objects
def get_pokemon_by_type(type):
    url = type_url + (type.lower())
    response = requests.get(url).json()
    pokemon = []
    if len(response.keys()) > 1:
        for i in range(3):
            p = response['pokemon'][random.randint(0, len(response['pokemon'])-1)]
            pokemon.append(get_pokemon_from_api(p['pokemon']['name']))
        return pokemon
    else:
        return pokemon

#Extra helper function to randomize pokemon traits
    response = requests.get(pokemon_search + pokemon).json()
    name = response['forms'][0]['name']
    ability = response['abilities'][random.randint(0,len(response['abilities'])-1)]['ability']['name']#gets a random ability
    sprite = list(response['sprites'].keys())[random.randint(6,7)]#gets a random trait (shiny or not shiny)
    return {'pokemon': name, 'ability': ability, 'trait': sprite}

########################
#### View functions ####
########################

# Error Handler. Redirects unknown urls to a 404.html page.
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Error Handler. Redirects server errors urls to a 500.html page.
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#Callback route for Google OAuth
@app.route('/gCallback')
def callback():
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    if 'error' in request.args: # Good Q: 'what are request.args here, why do they matter?'
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    # print(request.args, "ARGS")
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
                Auth.TOKEN_URI,
                client_secret=Auth.CLIENT_SECRET,
                authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            # print("SUCCESS 200") # For debugging/understanding
            user_data = resp.json()
            email = user_data['email']
            user = User.query.filter_by(email=email).first()
            if user is None:
                # print("No user...")
                user = User()
                user.email = email
            user.name = user_data['name']
            # print(token)
            user.tokens = json.dumps(token)
            user.avatar = user_data['picture']
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
        return 'Could not fetch your information.'

## Login-related routes
@app.route('/login',methods=["GET","POST"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html', auth_url=auth_url, form=form)
#Should render the login.html page which contains the LoginForm. On submission of the form, if the user is authenticated, they should be redirected to the index page where they can encounter pokemon. If not, flash the invalid credentials message.

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
#Only displayed if the user is loggedd in. If the user logs out then they will be redirected to the index.html page and a successful message will be flashed.

@app.route('/register',methods=["GET","POST"])
def register():
    defaultAvatar = 'https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg'
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,name=form.username.data,password=form.password.data, avatar=defaultAvatar)
        db.session.add(user)
        db.session.commit()
        flash('Successfully registered! You can now log in.')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)
#Displays the RegistrationForm to the user. If the user submits the form, the form will check to see if the user exists/create the user by calling get_or_create_user. The user will then be redirected to the login page and a message will be flashed indicating successful registration.

## Other routes
@app.route('/', methods=['GET', 'POST'])
def index():
    form = PokemonSearchForm()
    if form.validate_on_submit():
        number = random.randint(1, 802)
        pokemon = get_pokemon_from_api(str(number))
        img_url = pokemon.imgURL
        name=pokemon.name
        flash("{} encountered!".format((pokemon.name).upper()))
        flash('Ability: {}, Trait: {}'.format((pokemon.ability).upper(), (pokemon.sprite).upper()))
        return render_template('index.html', form=form, img_url=img_url, name=name)
    return render_template('index.html', form=form)
#This view function should display the PokemonSearchForm. Upon submission of the form, if validated, the function will invoke the get or create search term method and the get_pokemon_from_api method which will store pokemon results into the searches table. It will then redirect the user to the search_results route.

@app.route('/type_search', methods=['GET', 'POST'])
def type_search():
    form = PokemonTypeForm()
    return render_template('type_search.html', form=form)

@app.route('/search_results', methods=['GET', 'POST'])
def search_results():
    type = request.args['type']
    pokemon = get_pokemon_by_type(type)
    get_or_create_search_term(type, pokemon)
    return render_template('search_results.html', pokemon=pokemon, type=type)

@app.route('/specific_search/<search_term>')
def specific_search(search_term):
    term = SearchTerm.query.filter_by(term=search_term).first()
    pokemon = term.pokemon
    return render_template('specific_search.html', pokemon=pokemon, term=search_term)


#this function will query the search term created in the index function and return the pokemon stored. The searched_results.html page will be rendered displaying pokemon returned.
@app.route('/search_history')
def search_history():
    searches = SearchTerm.query.all()
    return render_template('search_history.html', searches=searches)
#This function queries the searches table and returns all the terms that have been entered by the user and sends this data to  searched_terms.html which the function then renders.

@app.route('/all_encountered', methods=["GET","POST"])
def all_encountered():
    form = PokemonFilterForm()
    pokemon = Pokemon.query.all()
    if form.validate_on_submit():
        filter = form.filter.data
        filter = '%' + filter + '%'
        pokemon = Pokemon.query.filter(Pokemon.name.like(filter)).all()
        print(pokemon)
        if not pokemon:
            flash('No matches! Try another filter.')
        return render_template('all_encountered.html', pokemon=pokemon, form=form)
    return render_template('all_encountered.html', pokemon=pokemon, form=form)
#This function queries the pokemon table and returns all the pokemon that have been encountered by the user and sends this data to all_pokemon.html which the function then renders.

#Creates a new team for the user. The form on this page is a POST form that redirects to a NEW page.
@app.route('/create_team',methods=["GET","POST"])
@login_required
def create_team():
    form = CreateTeamForm()
    pokemon = Pokemon.query.all()
    choices = [(str(p.id), ('Pokemon: ' + (p.name).upper() + ' Ability: ' + (p.ability).upper() + ' Trait: ' + (p.sprite).upper())) for p in pokemon]
    form.picks.choices = choices
    print('here')
    if form.validate_on_submit():
        poke_ids = [i for i in form.picks.data]
        pokemon_objs = [get_pokemon_by_id(id) for id in poke_ids]
        get_or_create_team(form.name.data, current_user, pokemon_objs)
        return redirect(url_for('teams', team=current_user.team))
    elif form.errors:
        flash("Error in form submission.")
    return render_template('create_team.html', form=form)
#THis route renders the create_team.html page which displays the CreateTeamForm. If the form validates on submit, the list of the pokemon ids that were selected from the form passed to the get pokemon by id function to create a list of Pokemon objects.  Then, this information is passed into the get_or_create_team method.
# If the form is not validated, this view function renders the create_team.html template and sends the form to the template.

@app.route('/teams',methods=["GET","POST"])
@login_required
def teams():
    form = DeleteButton()
    return render_template('teams.html', teams=current_user.team, form=form)
#This view function renders the teams.html template so that only the current user's personal teams are sent to the team.html template.

@app.route('/single_team/<id_num>')
def single_team(id_num):
    form = UpdateButtonForm()
    id_num = int(id_num)
    team = PersonalTeam.query.filter_by(id=id_num).first()
    pokemon = team.pokemon.all()
    return render_template('single_team.html', team=team, pokemon=pokemon, form=form)
#this function is invoked when the user clicks to view a specific team. The id of that team list is passed in and it queries the team's pokemon from the database. Then sends this info to the team.html page.

@app.route('/update/<i>',methods=["GET","POST"])
def update(i):
    form = UpdateTeamForm()
    pokemon = Pokemon.query.all()
    choices = [(str(p.id), ('Pokemon: ' + (p.name).upper() + ' Ability: ' + (p.ability).upper() + ' Trait: ' + (p.sprite).upper())) for p in pokemon]
    form.picks.choices = choices
    team = PersonalTeam.query.filter_by(id=i).first()
    if form.validate_on_submit():
        poke_ids = [i for i in form.picks.data]
        pokemon_objs = [get_pokemon_by_id(id) for id in poke_ids]
        team.pokemon = []
        for p in pokemon_objs:
            team.pokemon.append(p)
        flash("Updated team {}".format(team.name))
        return redirect(url_for('teams', team=current_user.team))
    return render_template('update_team.html', form=form)
# This function should be invoked when the UpdateButton form is submitted and allows users to update which pokemon are in their team. The updates from the form are gathered and the teams table is queried and new values are inserted. Once it is updated, it redirects them to the page showing all the teams created and flashes successfully updated team.

@app.route('/delete/<team_id>',methods=["GET","POST"])
def delete(team_id):
    if request.method == "POST":
        team = PersonalTeam.query.filter_by(id=team_id).first()
        if team:
            name = team.name
            db.session.delete(team)
            db.session.commit()
            flash('Successfully deleted {} team!'.format(name))
            return redirect(url_for('teams'))
#this function gathers the team id from the form and commits a delete.

#Some ajax to quickly show users what pokemon have been encountered without going in to their details.
@app.route('/ajax')
def all():
    names = jsonify({"pokemon" : [{'name' : p.name} for p in Pokemon.query.all()]})
    return names



if __name__ == '__main__':
    db.create_all()
    manager.run()
