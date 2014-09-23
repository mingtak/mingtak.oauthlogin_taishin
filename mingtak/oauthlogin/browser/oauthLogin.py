# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
#from ..config import PAGE_ACCESS_LOG_FILE
#from DateTime import DateTime
import logging
#from Products.CMFPlone.utils import safe_unicode
#from plone import api
#import os
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
import urllib2
import os; os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from oauthlib.oauth2 import TokenExpiredError



class FacebookLogin(BrowserView):
    def __call__(self):
        code = getattr(self.request, 'code', None)
        facebook = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
        facebook = facebook_compliance_fix(facebook)
        if code == None:
            authorization_url, state = facebook.authorization_url(authorization_base_url)
            self.request.response.redirect(authorization_url)
            return
        facebook.fetch_token(token_url,
                             client_secret=client_secret,
                             code=code)
        r = facebook.get('https://graph.facebook.com/me?')
        return r.content
