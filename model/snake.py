""" database dependencies to support sqliteDB examples """
# randrage used for creating test users
from random import randrange

# datetime type for date of birth and date game played
from datetime import date

# used to load json data
import json

# database orm api
# desc and asc used to order returned data in descending and ascending order
from sqlalchemy import desc, asc

# IntegrityError is used in create calls
from sqlalchemy.exc import IntegrityError

# password hash generation and password checking
# used in saving user accounts and login requests
from werkzeug.security import generate_password_hash, check_password_hash

# app and db objects are created in teh __init__ file
from __init__ import app, db

# Define the Score class to manage actions in 'scores' table,  with a relationship to 'users' table
class Score(db.Model):
    # table name - scores
    __tablename__ = 'scores'

    # Define the Scores schema
    # id column
    id = db.Column(db.Integer, primary_key=True)
    
    # gamers' score
    score = db.Column(db.Integer, unique=False, nullable=False)

    # date the game was played and score posted
    dateplayed = db.Column(db.Date, unique=False)
    
    # userID is teh gamers table primary key
    # many-to-one (many scores to one gamer)
    userID = db.Column(db.Integer, db.ForeignKey('gamers.id'))

    # Constructor of a Scores object, initializes of instance variables within object
    def __init__(self, id, score):
        self.userID = id
        self.score = score
        # date set to today
        self.dateplayed = date.today()

    # Returns a string representation of the Scores object, similar to java toString()
    # returns string
    def __repr__(self):
        return "Scores(" + str(self.id) + "," + str(self.score) + "," + str(self.userID) + "," + self.dateplayed.strftime('%Y-%m-%d')+ ")"

    # CRUD create, adds a new record to the Scores table
    # returns the object added or None in case of an error
    def create(self):
        try:
            # creates a Scores object from Scores(db.Model) class, passes initializers
            db.session.add(self)  # add prepares to persist person object to Scores table
            db.session.commit()  # SqlAlchemy "unit of work pattern" requires a manual commit
            return self
        except IntegrityError:
            db.session.remove()
            return None

    # CRUD read, returns dictionary representation of Scores object
    # returns dictionary
    def read(self):        
        return {
            "id": self.id,
            "userID": self.userID,
            "score": self.score,
            "dateplayed": self.dateplayed.strftime('%Y-%m-%d')
        }

    # returns the scores for the user identified by userID
    # scores are sorted by descending order of the score and ascending order of the date game was played
    # oldest highest score is shown frst
    def getScoresForUser(userID):
        print("User UID: " + userID)
        return db.session.query(Score).filter(Score.userID == userID).order_by(desc(Score.score)).order_by(asc(Score.dateplayed))
    
    # clears user's scores
    def deleteUserScores(userID):
        db.session.query(Score).filter(Score.userID==userID).delete()
        db.session.commit()

# Define the User class to manage actions in the 'users' table
# -- Object Relational Mapping (ORM) is the key concept of SQLAlchemy
# -- a.) db.Model is like an inner layer of the onion in ORM
# -- b.) User represents data we want to store, something that is built on db.Model
# -- c.) SQLAlchemy ORM is layer on top of SQLAlchemy Core, then SQLAlchemy engine, SQL
class User(db.Model):
    __tablename__ = 'gamers'  # table name is plural, class name is singular

    # Define the User schema
    # unique id as primary key
    id = db.Column(db.Integer, primary_key=True)
    # user name - not unique
    _name = db.Column(db.String(255), unique=False, nullable=False)
    # user login id - unique
    _uid = db.Column(db.String(255), unique=True, nullable=False)
    # user password
    _password = db.Column(db.String(255), unique=False, nullable=False)
    # user date of birth 
    _dob = db.Column(db.Date)
    # user's level Integer. Track's difficulty levels
    # 0 - Beginner
    # 1 - Easy
    # 2 - Medium
    # 3 - Hard
    # 4 - Master
    # 5 - God
    _level = db.Column(db.Integer, unique=False, nullable=False)

    # Defines a relationship between User record and Scores table, one-to-many (one user to many scores)
    scores = db.relationship("Score", cascade='all, delete', backref='gamers', lazy=True)

    # constructor of a User object, initializes the instance variables within object (self)
    # password defaults to 123querty
    # level defaults = 1 (Easy)
    def __init__(self, name, uid, level=1, password="123qwerty", dob=date.today()):
        self._name = name
        self._uid = uid
        self.set_password(password)
        self._dob = dob
        self._level = level

    # a name getter method, extracts name from object
    @property
    def name(self):
        return self._name
    
    # a setter function, allows name to be updated after initial object creation
    @name.setter
    def name(self, name):
        self._name = name
    
    # a name getter method, extracts name from object
    @property
    def level(self):
        return self._level
    
    # a setter function, allows name to be updated after initial object creation
    @level.setter
    def level(self, level):
        self._level = level
    
    # a getter method, extracts email from object
    @property
    def uid(self):
        return self._uid
    
    # a setter function, allows name to be updated after initial object creation
    @uid.setter
    def uid(self, uid):
        self._uid = uid
        
    # check if uid parameter matches user id in object, return boolean
    def is_uid(self, uid):
        return self._uid == uid
    
    @property
    def password(self):
        return self._password[0:10] + "..." # because of security only show 1st characters

    # update password, this is conventional setter
    def set_password(self, password):
        """Create a hashed password."""
        self._password = generate_password_hash(password, method='sha256')

    # check password parameter versus stored/encrypted password
    def is_password(self, password):
        """Check against hashed password."""
        result = check_password_hash(self._password, password)
        return result
    
    # dob property is returned as string, to avoid unfriendly outcomes
    @property
    def dob(self):
        dob_string = self._dob
        return dob_string
    
    # dob should be have verification for type date
    @dob.setter
    def dob(self, dob):
        self._dob = dob
    
    @property
    def age(self):
        today = date.today()
        return today.year - self._dob.year - ((today.month, today.day) < (self._dob.month, self._dob.day))
    
    # output content using str(object) in human readable form, uses getter
    # output content using json dumps, this is ready for API response
    def __str__(self):
        return json.dumps(self.read())

    # CRUD create/add a new record to the table
    # returns self or None on error
    def create(self):
        try:
            # creates a person object from User(db.Model) class, passes initializers
            db.session.add(self)  # add prepares to persist person object to Users table
            db.session.commit()  # SqlAlchemy "unit of work pattern" requires a manual commit
            return self
        except IntegrityError:
            db.session.remove()
            return None

    # CRUD read converts self to dictionary
    # returns dictionary
    def read(self):
        return {
            "id": self.id,
            "name": self.name,
            "uid": self.uid,
            "dob": self.dob.strftime('%Y-%m-%d'),
            "age": self.age,
            "level": self.level,
            "scores": [score.read() for score in self.scores]
        }

    # CRUD update: updates user name, password, phone
    # returns self
    def update(self, name="", uid="", level=1, password=""):
        """only updates values with length"""
        if len(name) > 0:
            self.name = name
        if len(uid) > 0:
            self.uid = uid
        if len(password) > 0:
            self.set_password(password)
        self.level = level
        db.session.commit()
        return self
    
    # CRUD update: updates user name, password, phone
    # returns self
    def update(self):
        db.session.commit()
        return self

    # CRUD delete: remove self
    # None
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None
    
    # finds the matching user by the primary key id
    def getUserById(userid):
        return db.session.query(User).filter(User.id == userid).first()
    
    # finds the user by the login id: _uid
    def getUserByUserId(loginid):
        print("Login ID: " + loginid)
        return db.session.query(User).filter(User._uid == loginid).first()

    # validates user's password for login
    def validateUserPassword(gamer, password):
        if (gamer is None):
            return False
        return User.is_password(gamer, password)
    
    # returns all scores
    # order in descending order of score and ascending order of date played
    # top 50 scores are returned to avoid reading the entire table, if the table has more records
    def getAllScores():
        return  db.session.query(User, Score).filter(User.id == Score.userID).order_by(desc(Score.score)).order_by(asc(Score.dateplayed)).limit(50)

    # returns the user's highest scroe
    def getHighScore(id):
        return  db.session.query(Score).filter(Score.userID == id).order_by(desc(Score.score)).first()

# administrative user account table - 
# this is used to delete user accounts from the user interface
# prevents non-admin account holders and public from viewing and deleting user accounts
class AdminUser(db.Model):
    __tablename__ = 'admin_users'  # table name is plural, class name is singular

    # Define the AdminUser schema 
    # primary key - id
    id = db.Column(db.Integer, primary_key=True)
    # admin user name
    _name = db.Column(db.String(255), unique=False, nullable=False)
    # admin user login id
    _uid = db.Column(db.String(255), unique=True, nullable=False)
    # admin user password
    _password = db.Column(db.String(255), unique=False, nullable=False)
    
    # constructor of Admin User object, initializes the instance variables within object (self)
    def __init__(self, name, uid,  password="123qwerty"):
        self._name = name    # variables with self prefix become part of the object, 
        self._uid = uid
        self.set_password(password)
        
    # a name getter method, extracts name from object
    @property
    def name(self):
        return self._name
    
    # a setter function, allows name to be updated after initial object creation
    @name.setter
    def name(self, name):
        self._name = name
    
    # a getter method, extracts email from object
    @property
    def uid(self):
        return self._uid
    
    # a setter function, allows name to be updated after initial object creation
    @uid.setter
    def uid(self, uid):
        self._uid = uid
        
    # check if uid parameter matches user id in object, return boolean
    def is_uid(self, uid):
        return self._uid == uid
    
    @property
    def password(self):
        return self._password[0:10] + "..." # because of security only show 1st characters

    # update password, this is conventional setter
    def set_password(self, password):
        """Create a hashed password."""
        self._password = generate_password_hash(password, method='sha256')

    # check password parameter versus stored/encrypted password
    def is_password(self, password):
        """Check against hashed password."""
        result = check_password_hash(self._password, password)
        return result
    
    # output content using str(object) in human readable form, uses getter
    # output content using json dumps, this is ready for API response
    def __str__(self):
        return json.dumps(self.read())

    # CRUD create/add a new record to the table
    # returns self or None on error
    def create(self):
        try:
            # creates a person object from User(db.Model) class, passes initializers
            db.session.add(self)  # add prepares to persist person object to Users table
            db.session.commit()  # SqlAlchemy "unit of work pattern" requires a manual commit
            return self
        except IntegrityError:
            db.session.remove()
            return None

    # CRUD read converts self to dictionary
    # returns dictionary
    def read(self):
        return {
            "id": self.id,
            "name": self.name,
            "uid": self.uid
        }

    # CRUD update: updates user name, password, phone
    # returns self
    def update(self, name="", uid="", password=""):
        """only updates values with length"""
        if len(name) > 0:
            self.name = name
        if len(uid) > 0:
            self.uid = uid
        if len(password) > 0:
            self.set_password(password)
        db.session.commit()
        return self
    
    # CRUD update: updates user name, password, phone
    # returns self
    def update(self):
        db.session.commit()
        return self

    # CRUD delete: remove self
    # None
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None
    
    # get admin user by id - primary key
    def getAdminUserById(userid):
        return db.session.query(AdminUser).filter(AdminUser.id == userid).first()
    
    # get admin user by login id
    def getAdminUserByLoginId(loginid):
        print("Login ID: " + loginid)
        return db.session.query(AdminUser).filter(AdminUser._uid == loginid).first()

    # validate admin user pasword for login
    def validateUserPassword(adminUser, password):
        if (adminUser is None):
            return False
        
        return AdminUser.is_password(adminUser, password)

"""Database Creation and Testing """
# Builds working data for testing
def initGamers():
    """Create database and tables"""
    app.app_context().push()
    db.create_all()
    """Tester data for table"""
    u1 = User(name='Thomas Edison', uid='toby', level=1, password='123toby', dob=date(1847, 2, 11))
    u2 = User(name='Nicholas Tesla', uid='niko',level=1,  password='123niko')
    u3 = User(name='Alexander Graham Bell', level=1, uid='lex', password='123lex')
    u4 = User(name='Eli Whitney', uid='whit',level=1,  password='123whit')
    u5 = User(name='John Mortensen', uid='jm1021', level=1, dob=date(1959, 10, 21))

    users = [u1, u2, u3, u4, u5]

    """Builds sample user/score(s) data"""
    for user in users:
        try:
            '''add a few 1 to 4 scores per user'''
            for num in range(randrange(1, 4)):
                score = str(num)
                user.scores.append(Score(id=user.id, score=score))
            '''add user/score data to table'''
            user.create()
            print(user.name + " created")
        except IntegrityError:
            '''fails with bad or duplicate data'''
            db.session.remove()
            print(f"Records exist, duplicate email, or error: {user.uid}")

def initAdminUsers():
    """Create database and tables"""
    app.app_context().push()
    db.create_all()
    """Tester data for table"""
    u1 = AdminUser(name='Administrator', uid='admin', password='passsword')
    
    """Builds sample user/score(s) data"""
    try:
        u1.create()
        print(u1.name + " created")
    except IntegrityError:
        '''fails with bad or duplicate data'''
        db.session.remove()
        print(f"Records exist, duplicate email, or error: {u1.uid}")
#initGamers()
#initAdminUsers()