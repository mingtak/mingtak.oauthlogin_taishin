from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.dexterity.content import Container
from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder


from mingtak.oauthlogin import MessageFactory as _


# Interface class; used to define content-type schema.

class IOauth2Setting(form.Schema, IImageScaleTraversable):
    """
    Oauth2 login method
    """
    testField = schema.TextLine(
        title=_(u"Test Field"),
        required=False,
    )

    textField = schema.Text(
        title=_(u"Text Field"),
        required=False,
    )


class Oauth2Login(Container):
    grok.implements(IOauth2Setting)


class SampleView(grok.View):
    """ sample view class """

    grok.context(IOauth2Setting)
    grok.require('zope2.View')
    grok.name('view')
