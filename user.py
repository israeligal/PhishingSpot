import json
import time
import logging


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
