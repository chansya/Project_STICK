""" Models for habit building app. """

from datetime import date, timedelta
from flask_sqlalchemy import SQLAlchemy
import pendulum

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
        """Return a specific user object."""
        return cls.query.get(user_id)

    @classmethod
    def get_by_email(cls, email):
        """Return a user object with specific email."""
        return cls.query.filter(User.email == email).first()

    @classmethod
    def all_users(cls):
        """Return list of all users."""
        return cls.query.all()


class Habit(db.Model):
    """A habit."""

    __tablename__ = "habits"

    habit_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    habit_name = db.Column(db.String, nullable=False)
    frequency = db.Column(db.Integer, nullable=False)
    time_period = db.Column(db.String, nullable=False)
    current_streak = db.Column(db.Integer, nullable=False, default=0)
    max_streak = db.Column(db.Integer, nullable=False, default=0)
    start_date = db.Column(db.Date, nullable=False)
    # end_date = db.Column(db.Date, nullable=True)

    # The user to which a habit belongs
    user = db.relationship("User", back_populates="habits")
    # A ist of records for this habit
    records = db.relationship("Record", back_populates="habit")

    def __repr__(self):
        return f"<Habit habit_id={self.habit_id} habit_name={self.habit_name}>"

    @classmethod
    def create(cls, user_id, habit_name, frequency, time_period,
                 current_streak, max_streak, start_date):
        """Create and return a new habit."""

        return cls(user_id=user_id,
                   habit_name=habit_name,
                   frequency=frequency,
                   time_period=time_period,
                   current_streak=current_streak,
                   max_streak=max_streak,
                   start_date=start_date)
        #   end_date=end_date)

    @classmethod
    def get_by_id(cls, habit_id):
        """Return a single habit object."""
        return cls.query.get(habit_id)

    @classmethod
    def get_by_user(cls, user_id):
        """Return list of all habits for a specific user."""
        return cls.query.filter(Habit.user_id == user_id).all()

    @classmethod
    def all_habits(cls):
        """Return list of all habits."""
        return cls.query.all()

    @classmethod
    def update_curr_streak(cls, habit_id):
        habit = cls.query.get(habit_id)
        
        today = date.today()

        # For daily goal
        if habit.time_period == "daily":
            # start from today and count streak going back one day at a time
            habit.current_streak = 0
            # if goal is reached today, update curr streak to 1
            rec_today = Record.query.filter(Record.habit_id==habit_id, Record.record_date==today).all()
            if len(rec_today) >= habit.frequency:
                habit.current_streak = 1
            
            yesterday = today - timedelta(days=1)
            rec_ytd = Record.query.filter(Record.habit_id==habit_id, Record.record_date==yesterday).all()
            
            while rec_ytd != None:
                yesterday = today - timedelta(days=1)
                rec_ytd = Record.query.filter(Record.habit_id==habit_id, Record.record_date==yesterday).all()

                # if total record from yesterday meets the frequency set:
                if len(rec_ytd) >= habit.frequency:
                    # increase current streak by 1
                    habit.current_streak += 1
                # if goal not met, stop the streak count
                else:
                    break
                today = yesterday


        # For weekly goal
        elif habit.time_period == "weekly":
             # start from current week and count streak going back one week at a time
            habit.current_streak = 0

            curr_week_start = today - timedelta(days=today.weekday())
            curr_week_end = curr_week_start + timedelta(days=6)

            # determine number of records within current week:
            rec_curr_week = Record.query.filter(Record.habit_id==habit_id, 
                                                Record.record_date>=curr_week_start,
                                                Record.record_date<=curr_week_end).all()
            
            # if goal is reached this week, update curr streak to 1
            if len(rec_curr_week) >= habit.frequency:
                habit.current_streak = 1
            
            # while loop to check past weeks for streak
            while rec_curr_week != None:
                last_week_start = curr_week_start - timedelta(days=7)
                last_week_end = curr_week_end - timedelta(days=7)
                # determine number of records within last week:
                rec_last_week = Record.query.filter(Record.habit_id==habit_id, 
                                                    Record.record_date>=last_week_start,
                                                    Record.record_date<=last_week_end).all()

                # if total record from last week meets the frequency set:
                if len(rec_last_week) >= habit.frequency:
                    # increase current streak by 1
                    habit.current_streak += 1
                # if goal not met, stop the streak count
                else:
                    break
                curr_week_start = last_week_start
                curr_week_end = last_week_end


         # For monthly goal
        elif habit.time_period == "monthly":
             # start from current month and count streak going back, one month at a time
            habit.current_streak = 0
            today = pendulum.today()
            curr_month_start = today.start_of("month").date()
            curr_month_end = today.end_of("month").date()
            
            # determine number of records within current month:
            rec_curr_month = Record.query.filter(Record.habit_id==habit_id, 
                                                Record.record_date>=curr_month_start,                                             Record.record_date<=curr_month_end).all()
            # if goal is reached this week, update curr streak to 1
            if len(rec_curr_month) >= habit.frequency:
                habit.current_streak = 1
            
            # while loop to check past months for streak
            while rec_curr_month != None:
                
                last_month_end = curr_month_start - timedelta(days=1)
                last_month_start = last_month_end.start_of("month")

                # determine number of records within last week:
                rec_last_month = Record.query.filter(Record.habit_id==habit_id, 
                                                    Record.record_date>=last_month_start,
                                                    Record.record_date<=last_month_end).all()

                # if total record from last week meets the frequency set:
                if len(rec_last_month) >= habit.frequency:
                    # increase current streak by 1
                    habit.current_streak += 1
                # if goal not met, stop the streak count
                else:
                    break
                curr_month_start = last_month_start
                curr_month_end = last_month_end


    @classmethod
    def update_max_streak(cls, habit_id):
        """ Update the highest streak. """
        habit = cls.query.get(habit_id)
        if habit.current_streak > habit.max_streak:
            habit.max_streak = habit.current_streak

    @classmethod
    def count_habit_by_user(cls, user_id):
        """Return the count of habits for a specific user."""
        return cls.query.filter(Habit.user_id == user_id).count()


class Record(db.Model):
    """A record for a habit."""

    __tablename__ = "records"

    record_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey("habits.habit_id"))
    finished = db.Column(db.Boolean, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    img_url = db.Column(db.String, nullable=True)
    record_date = db.Column(db.Date, nullable=False)

    # The habit to which a record belongs
    habit = db.relationship("Habit", back_populates="records")

    def __repr__(self):
        return f"<Record record_id={self.record_id} finished={self.finished}>"

    @classmethod
    def create(cls, habit_id, finished, notes, img_url, record_date):
        """Create and return a new record."""
        return cls(habit_id=habit_id, finished=finished, 
                    notes=notes, img_url=img_url, record_date=record_date)

    @classmethod
    def get_by_id(cls, record_id):
        """ Return a single record object. """
        return cls.query.get(record_id)

    @classmethod
    def get_by_habit(cls, habit_id):
        """ Rreturn list of records for a specific habit. """
        return cls.query.filter(Record.habit_id == habit_id).all()

    @classmethod
    def all_records(cls):
        """ Return all records for all habits. """
        return cls.query.all()

    @classmethod
    def count_records_by_habit(cls, habit_id):
        """ Return the count of records for a specific habit."""
        return cls.query.filter(Record.habit_id==habit_id).count()


class Badge(db.Model):
    """A badge."""

    __tablename__ = "badges"

    badge_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    img_url = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    message = db.Column(db.String, nullable=False)

    # The user to which a badge belongs
    user = db.relationship("User", back_populates="badges")

    def __repr__(self):
        return f"<Badge badge_id={self.badge_id} img_url={self.img_url}>"

    @classmethod
    def create(cls, user_id, img_url, name, message):
        """Create and return a new badge object."""
        return cls(user_id=user_id, img_url=img_url, name=name, message=message)

    @classmethod
    def get_by_id(cls, badge_id):
        """Return a single badge object."""
        return cls.query.get(badge_id)

    @classmethod
    def get_by_user(cls, user_id):
        """Return a list of badge object for a specific user."""
        return cls.query.filter(Badge.user_id == user_id).all()

    @classmethod
    def all_badges(cls):
        """ Return all badge objects."""
        return cls.query.all()

    @classmethod
    def count_badge_by_user(cls, user_id):
        """Return the count of badges for a specific user."""
        return cls.query.filter(Badge.user_id == user_id).count()


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
