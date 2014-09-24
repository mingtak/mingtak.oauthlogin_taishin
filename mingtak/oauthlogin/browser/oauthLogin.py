from Products.Five.browser import BrowserView
import logging
from plone import api
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
import urllib2
from zope.component import getUtility, queryUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.utils import safe_unicode
from oauthlib.oauth2 import TokenExpiredError
import os; os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

logger = logging.getLogger("mingtak.oauthlogin.browser.oauthLogin")


#class OauthWorkFlow(object):




class FacebookLogin(BrowserView):
    token_url = 'https://graph.facebook.com/oauth/access_token'
    authorization_base_url = 'https://www.facebook.com/dialog/oauth'

    def __call__(self):
        registry = getUtility(IRegistry)
        client_id = registry.get('mingtak.oauthlogin.oauth2login.IOauth2Setting.facebookAppId')
        client_secret = registry.get('mingtak.oauthlogin.oauth2login.IOauth2Setting.facebookAppSecret')
        scope = registry.get('mingtak.oauthlogin.oauth2login.IOauth2Setting.facebookScope')
        redirect_uri = registry.get('mingtak.oauthlogin.oauth2login.IOauth2Setting.facebookRedirectUri')
        code = getattr(self.request, 'code', None)
        facebook = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
        facebook = facebook_compliance_fix(facebook)
        if code == None:
            if hasattr(self.request, 'error'):
                self.request.response.redirect("/")
                return
            authorization_url, state = facebook.authorization_url(self.authorization_base_url)
            self.request.response.redirect(authorization_url)
            return
        facebook.fetch_token(self.token_url,
                             client_secret=client_secret,
                             code=code)
        getUser = facebook.get('https://graph.facebook.com/me?')
        user = getUser.json()

        # check has id, if True, login
        userid = safe_unicode("fb%s") % user["id"]
        if api.user.get(userid=userid) is not None:
            self.context.acl_users.session._setupSession(userid.encode("utf-8"), self.context.REQUEST.RESPONSE)
            self.request.RESPONSE.redirect("/")
            return

        userInfo = dict(
            fullname=safe_unicode(user.get("name", "")),
            description=safe_unicode(user.get("about", "")),
            location=safe_unicode(user.get("locale", "")),
            fbGender=safe_unicode(user.get("gender", "")),
            home_page=safe_unicode(user.get("link", "")),
        )
        api.user.create(
            username=safe_unicode("fb%s") % user["id"],
            email=safe_unicode((user.get("email", ""))),
            properties=userInfo,
        )
# relogin or newuser???
#        info = ""
      
#        for i in user.json().viewitems():
#            info += "%s : %s\n" % (i[0], i[1])
        self.context.acl_users.session._setupSession(userid.encode("utf-8"), self.context.REQUEST.RESPONSE)
        self.request.RESPONSE.redirect("/")
        self.request.response.redirect("/")
        return




class GoogleLogin(BrowserView):
    token_url = 'https://accounts.google.com/o/oauth2/token'
    authorization_base_url = 'https://accounts.google.com/o/oauth2/auth'

    def __call__(self):
        registry = getUtility(IRegistry)
        client_id = registry.get('mingtak.oauthlogin.oauth2login.IOauth2Setting.googleAppId')
        client_secret = registry.get('mingtak.oauthlogin.oauth2login.IOauth2Setting.googleAppSecret')
        scope = registry.get('mingtak.oauthlogin.oauth2login.IOauth2Setting.googleScope').split(',')
        redirect_uri = registry.get('mingtak.oauthlogin.oauth2login.IOauth2Setting.googleRedirectUri')
        code = getattr(self.request, 'code', None)
        google = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
        if code == None:
            if hasattr(self.request, 'error'):
                self.request.response.redirect("/")
                return
            authorization_url, state = google.authorization_url(self.authorization_base_url)
            self.request.response.redirect(authorization_url)
            return
        google.fetch_token(token_url=self.token_url,
                           client_secret=client_secret,
                           code=code,)
        getUser = google.get('https://www.googleapis.com/oauth2/v1/userinfo')
        user = getUser.json()
        """
        userinfo = ''
        for i in user.viewitems():
            userinfo += '%s : %s\n' % (i[0], i[1])
        return userinfo
        """
        # check has id, if True, login
        userid = safe_unicode("gg%s") % user["id"]
        if api.user.get(userid=userid) is not None:
            self.context.acl_users.session._setupSession(userid.encode("utf-8"), self.context.REQUEST.RESPONSE)
            self.request.RESPONSE.redirect("/")
            return

        userInfo = dict(
            fullname=safe_unicode(user.get("name", "")),
            location=safe_unicode(user.get("locale", "")),
            fbGender=safe_unicode(user.get("gender", "")),
            home_page=safe_unicode(user.get("link", "")),
        )
        api.user.create(
            username=userid,
            email=safe_unicode((user.get("email", ""))),
            properties=userInfo,
        )
# relogin or newuser???
#        info = ""
      
#        for i in user.json().viewitems():
#            info += "%s : %s\n" % (i[0], i[1])
        self.context.acl_users.session._setupSession(userid.encode("utf-8"), self.context.REQUEST.RESPONSE)
        self.request.RESPONSE.redirect("/")
        self.request.response.redirect("/")
        return





