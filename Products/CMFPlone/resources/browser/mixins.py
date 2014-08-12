from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner
from Products.PythonScripts.standard import url_quote
from zope.component import getUtility
from zope.component import getMultiAdapter
from urlparse import urlparse


from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.interfaces import IResourceRegistry

lessconfig = """
 window.less = {
    env: "development",
    logLevel: 2,
    async: false,
    fileAsync: false,
    errorReporting: 'console',
    poll: 1000,
    functions: {},
    dumpLineNumbers: "comments",
    globalVars: {
      %s
    },
  };
"""


class LessConfiguration(BrowserView):
    """
    Browser view that gets the definition of less variables on plone
    """

    def registry(self):
        registryUtility = getUtility(IRegistry)
        return registryUtility.records['Products.CMFPlone.lessvariables'].value

    def resource_registry(self):
        registryUtility = getUtility(IRegistry)
        return registryUtility.collectionOfInterface(IResourceRegistry, prefix="Products.CMFPlone.resources")

    def __call__(self):
        registry = self.registry()
        portal_state = getMultiAdapter((self.context, self.request),
            name=u'plone_portal_state')
        site_url = portal_state.portal_url()
        result = ""
        result += "sitePath: '\"%s\"',\n" % site_url
        result += "isPlone: 'true',\n"
        result += "isMockup: 'false',\n"

        less_vars_params = {
            'site_url': site_url,
        }
        for name, value in registry.items():
            t = value.format(**less_vars_params)
            result += "'%s': '\"%s\"',\n" % (name, t)

        for name, value in self.resource_registry().items():
            for css in value.css:

                url = urlparse(css)
                if url.netloc == '':
                    # Local
                    src = "%s/%s" % (site_url, css)
                else:
                    src = "%s" % (css)
                # less vars can't have dots on it
                result += "'%s': '\"%s\"',\n" % (name.replace('.','_'), src)

        self.request.response.setHeader("Content-Type", "application/javascript")

        return lessconfig % result

class LessDependency(BrowserView):
    """
    Browser view that returns the less/css on less format for specific resource
    """

    def registry(self):
        registryUtility = getUtility(IRegistry)
        return registryUtility.collectionOfInterface(IResourceRegistry, prefix="Products.CMFPlone.resources")

    def __call__(self):
        portal_state = getMultiAdapter((self.context, self.request),
                        name=u'plone_portal_state')
        site_url = portal_state.portal_url()

        registry = self.registry()
        resource = self.request.get('resource', None)
        result = ""
        if resource:
            if resource in registry:
                for css in registry[resource].css:
                    url = urlparse(css)
                    if url.netloc == '':
                        # Local
                        src = "%s/%s" % (site_url, css)
                    else:
                        src = "%s" % (css)

                    result += "@import url('%s');\n" % css

        self.request.response.setHeader("Content-Type", "stylesheet/less")

        return result
