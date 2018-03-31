import json
import time
import logging
from sql_alchemy.models import DbUser, DbDetails


class User:

    def __init__(self, request):
        self._request = request
        self.form = dict(request.form)
        self._user_agent_string = request.headers.get('User-Agent')
        self.form["user_agent_string"] = self._user_agent_string

    def create_user_file(self):
        if self._request.form is not None:
            with open(str(int(time.time())) + '.json', 'w') as outfile:
                json.dump(self.form, outfile)
        else:
            logging.error("could not write to file")

    def add_user_to_db(self, ps_database):

        user = DbUser()

        user_details = DbDetails()
        if self.form['email'] is not None:
            user_details.email = self.form['email'][0]
        else:
            logging.error("user class, did not find email in form")
            return

        if 'password' in self.form:
            user_details.password = self.form['password'][0]
        elif 'pass' in self.form:
            user_details.password = self.form['pass'][0]
        else:
            logging.error("user class, did not find password in form")
            return
        user_details.user = user
        ps_database.session.add(user)
        print( self.form['pass'][0])
        print(self.form['email'][0])
        ps_database.session.add(user_details)
        ps_database.session.commit()
