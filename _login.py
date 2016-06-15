import six
import re
import logging
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
try:
    import urllib.parse as urllib
except ImportError:
    import urllib
try:
    from http.cookiejar import CookieJar
except ImportError:
    from cookielib import CookieJar
 
class Downloader(object):
    """
    Provides an object to easily log into Google.

    This code is modified from the original snippet by Greg Roberts at
    https://gist.github.com/gregroberts/11001277, discovered through the useful
    reddit post here http://www.reddit.com/r/Python/comments/233a0c/trying_to_download_google_trends_data/.
    """

    
    def __init__(self, username, password):
        """
        Sets various object parameters.
        """      
        self.login_params = {
            "continue": 'http://www.google.com/trends',
            "PersistentCookie": "yes",
            "Email": username,
            "Passwd": password,
        }
        self.headers = [("Referrer", "https://www.google.com/accounts/ServiceLoginBoxAuth"),
                        ("Content-type", "application/x-www-form-urlencoded"),
                        ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0 Safari/535.21'),
                        ("Accept", "text/plain")]
        self.url_ServiceLoginBoxAuth = 'https://accounts.google.com/ServiceLoginBoxAuth'
        self.url_Export = 'http://www.google.com/accounts/ServiceLoginBoxAuth'
        self.url_CookieCheck = 'https://www.google.com/accounts/CheckCookie?chtml=LoginDoneHtml'
        self.url_PrefCookie = 'http://www.google.com'
        self.header_dictionary = {}
        self._connect()
        
    def _connect(self):
        """
        Connects to Google Trends.
        """
        self.cj = CookieJar()
        cook = urllib2.HTTPCookieProcessor(self.cj)
        self.opener = urllib2.build_opener(cook)
        self.opener.addheaders = self.headers
        
        galx = re.compile('<input type="hidden"[\s]+name="GALX"[\s]+value="(?P<galx>[a-zA-Z0-9_-]+)">')
        resp = str(self.opener.open(self.url_ServiceLoginBoxAuth).read())
        resp = re.sub(r'\s\s+', ' ', resp)
        m = galx.search(resp)

        self.login_params['GALX'] = m.group('galx')
        params = urllib.urlencode(self.login_params).encode("utf-8")
        self.opener.open(self.url_ServiceLoginBoxAuth, params)
        self.opener.open(self.url_CookieCheck)
        self.opener.open(self.url_PrefCookie)
 
        
    def downloadReport(self, query):
        """
        Returns original raw csv file as a one large string.
        """
        data = self.opener.open(query).read()
        #This is because in Py3 data is returned as bytes, and we want str
        #This is an issue when in Py2 data is already an str, and doesn't
        #have the decode method.
        if not isinstance(data, six.string_types):
            data = data.decode()
        
        if data in ['You must be signed in to export data from Google Trends']:
            logging.error('You must be signed in to export data from Google Trends')
            raise Exception(data)

        return data 
