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
from zope.event import notify
from Products.PlonePAS.events import UserLoggedInEvent, UserInitialLoginInEvent


logger = logging.getLogger("mingtak.oauthlogin.browser.oauthLogin")

class OauthWorkFlow(object):
    prefixString = "mingtak.oauthlogin.oauth2login.IOauth2Setting."
    oauthServerName = ""

    def __init__(self, oauthServerName):
        self.oauthServerName = oauthServerName

    def getRegistryValue(self):
        prefixString, oauthServerName = self.prefixString, self.oauthServerName
        registry = getUtility(IRegistry)
        client_id = registry.get("%s%s%s" % (prefixString, oauthServerName, "AppId"))
        client_secret = registry.get("%s%s%s" % (prefixString, oauthServerName, "AppSecret"))
        scope = registry.get("%s%s%s" % (prefixString, oauthServerName, "Scope"))
        redirect_uri = registry.get("%s%s%s" % (prefixString, oauthServerName, "RedirectUri"))
        return client_id, client_secret, scope, redirect_uri

    def getUserInfo(self, oauth2Session, token_url, client_secret, code, getUrl):
        oauth2Session.fetch_token(token_url=token_url,
                                  client_secret=client_secret,
                                  code=code)
        getUser = oauth2Session.get(getUrl)
        return getUser

    def createUser(self, userid, email, properties):
        userObject = api.user.create(username=userid, email=email, properties=properties,)
        return userObject


class FacebookLogin(BrowserView):
    token_url = "https://graph.facebook.com/oauth/access_token"
    authorization_base_url = "https://www.facebook.com/dialog/oauth"
    getUrl = "https://graph.facebook.com/me?"

    def __call__(self):
        oauthWorkFlow = OauthWorkFlow(oauthServerName="facebook")
        client_id, client_secret, scope, redirect_uri = oauthWorkFlow.getRegistryValue()
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
        user = oauthWorkFlow.getUserInfo(facebook, self.token_url, client_secret, code, self.getUrl).json()


        # check has id, if True, is a relogin user, if False, is a new user


        userid = safe_unicode("fb%s") % user["id"]

#########
        userObject = api.user.get(userid=userid)
        if api.user.get(userid=userid) is not None:
            self.context.acl_users.session._setupSession(userid.encode("utf-8"), self.context.REQUEST.RESPONSE)
            self.request.RESPONSE.redirect("/")
#########
            notify(UserLoggedInEvent(userObject))
            return
        userInfo = dict(
            fullname=safe_unicode(user.get("name", "")),
            description=safe_unicode(user.get("about", "")),
            location=safe_unicode(user.get("locale", "")),
            fbGender=safe_unicode(user.get("gender", "")),
            home_page=safe_unicode(user.get("link", "")),
        )
        userObject = oauthWorkFlow.createUser(userid, safe_unicode((user.get("email", ""))), userInfo)
#        self.context.acl_users.session._setupSession(userid.encode("utf-8"), self.context.REQUEST.RESPONSE)
#        self.request.RESPONSE.redirect("/")
        notify(UserInitialLoginInEvent(userObject))
        return


class GoogleLogin(BrowserView):
    token_url = "https://accounts.google.com/o/oauth2/token"
    authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
    getUrl = "https://www.googleapis.com/oauth2/v1/userinfo"

    def __call__(self):
        oauthWorkFlow = OauthWorkFlow(oauthServerName="google")
        client_id, client_secret, scope, redirect_uri = oauthWorkFlow.getRegistryValue()
        scope = scope.split(',')
        code = getattr(self.request, 'code', None)
        google = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
        if code == None:
            if hasattr(self.request, 'error'):
                self.request.response.redirect("/")
                return
            authorization_url, state = google.authorization_url(self.authorization_base_url)
            self.request.response.redirect(authorization_url)
            return
        user = oauthWorkFlow.getUserInfo(google, self.token_url, client_secret, code, self.getUrl).json()
        # check has id, if True, is a relogin user, if False, is a new user
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
        oauthWorkFlow.createUser(userid, safe_unicode((user.get("email", ""))), userInfo)
        self.context.acl_users.session._setupSession(userid.encode("utf-8"), self.context.REQUEST.RESPONSE)
        self.request.RESPONSE.redirect("/")
        return
