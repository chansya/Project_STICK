""" Models for habit building app. """

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """A user."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(15), nullable=False)

    # A list of habits objects
    habits = db.relationship("Habit", back_populates="user")
    # A list of badge objects
    badges = db.relationship("Badge", back_populates="user")

    def __repr__(self):
        return f"<User user_id={self.user_id} email={self.email}>"

    @classmethod
    def create(cls, name, email, password):
       """Create and return a new user."""

       return cls(name=name, email=email, password=password)

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.get(user_id)

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter(User.email == email).first()

    @classmethod
    def all_users(cls):
        return cls.query.all()


class Habit(db.Model):
    """A habit."""

    __tablename__ = "habits"

    habit_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    habit_name = db.Column(db.String, nullable=False)
    frequency = db.Column(db.Integer, nullable= False)
    time_period = db.Column(db.String, nullable=False)
    current_streak = db.Column(db.Integer, nullable=False, default=0)
    max_streak = db.Column(db.Integer, nullable=False, default=0)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    
    # user_id, habit_name,frequency,time_period,current_streak,max_streak
    # The user to which a habit belongs
    user = db.relationship("User", back_populates="habits")
    # A ist of records for this habit
    records = db.relationship("Record", back_populates="habit")

    def __repr__(self):
        return f"<Habit habit_id={self.habit_id} habit_name={self.habit_name}>"

    @classmethod
    def create(cls, user_id, habit_name,frequency,time_period,current_streak,max_streak, start_date, end_date):
       """Create and return a new habit."""

       return cls(user_id=user_id, 
                  habit_name=habit_name, 
                  frequency=frequency,
                  time_period=time_period,
                  current_streak=current_streak,
                  max_streak=max_streak, 
                  start_date=start_date, 
                  end_date=end_date)

    @classmethod
    def get_by_id(cls, habit_id):
        return cls.query.get(habit_id)

    @classmethod
    def get_by_user(cls, user_id):
        return cls.query.filter(Habit.user_id==user_id).all()

    @classmethod
    def all_habits(cls):
        return cls.query.all()


class Record(db.Model):
    """A record for a habit."""

    __tablename__ = "records"

    record_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey("habits.habit_id"))
    finished = db.Column(db.Boolean, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    record_date = db.Column(db.Date, nullable=False)
    
    # The habit to which a record belongs
    habit = db.relationship("Habit", back_populates="records")

    def __repr__(self):
        return f"<Record record_id={self.record_id} finished={self.finished}>"

    @classmethod
    def create(cls, habit_id, finished, notes, record_date):
       """Create and return a new record."""

       return cls(habit_id=habit_id, finished=finished, notes=notes, record_date=record_date)

    @classmethod
    def get_by_id(cls, record_id):
        return cls.query.get(record_id)

    @classmethod
    def get_by_habit(cls, habit_id):
        return cls.query.filter(Record.habit_id==habit_id).all()

    @classmethod
    def all_records(cls):
        return cls.query.all()



class Badge(db.Model):
    """A badge."""

    __tablename__ = "badges"

    badge_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    img_url = db.Column(db.String, nullable=False)
    
    # The user to which a badge belongs
    user = db.relationship("User", back_populates="badges")

    def __repr__(self):
        return f"<Badge badge_id={self.badge_id} img_url={self.img_url}>"

    @classmethod
    def create(cls, user_id, img_url):
       """Create and return a new badge."""

       return cls(user_id=user_id, img_url=img_url)

    @classmethod
    def get_by_id(cls, badge_id):
        return cls.query.get(badge_id)

    @classmethod
    def get_by_user(cls, user_id):
        return cls.query.filter(Badge.user_id==user_id).all()

    @classmethod
    def all_badges(cls):
        return cls.query.all()


def connect_to_db(app, db_uri="postgresql:///habits", echo=True):
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_ECHO"] = echo
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = app
    db.init_app(app)

    print("Connected to the db!")


if __name__ == "__main__":

    from server import app

    connect_to_db(app)
   