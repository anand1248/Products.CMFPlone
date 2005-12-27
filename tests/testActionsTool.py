#
# ActionsTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from OFS.SimpleItem import Item
from Acquisition import Explicit
from traceback import format_exception
from sets import Set

class ExplicitItem(Item, Explicit):
    '''Item without implicit acquisition'''
    id = 'dummy'
    meta_type = 'Dummy Item'

expected_filtered_actions=Set(['site_actions', 'object', 'workflow', 'portal_tabs',
                               'global', 'object_buttons', 'document_actions',
                               'user', 'folder_buttons', 'folder'])


class TestActionsTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.actions = self.portal.portal_actions
        self.portal.acl_users._doAddUser('user1', 'secret', ['Member'], [])

    def fail_tb(self, msg):
        """ special fail for capturing errors """
        e, v, tb = sys.exc_info()
        tb = ''.join(format_exception(e, v, tb))
        self.fail("%s\n%s\n" % (msg, tb))

    def testAddAction(self):
        # addAction should work even though PloneTestCase patches _cloneActions
        action_infos = self.actions.listActions()
        length = len(action_infos)
        self.actions.addAction(id='foo',
                               name='foo_name',
                               action='foo_action',
                               condition='foo_condition',
                               permission='foo_permission',
                               category='foo_category',
                               visible=1)
        action_infos = self.actions.listActions()
        self.assertEqual(len(action_infos), length + 1)
        self.assertEqual(action_infos[-1].id, 'foo')
        self.assertEqual(action_infos[-1].title, 'foo_name')
        self.assertEqual(action_infos[-1].permissions, ('foo_permission',))
        self.assertEqual(action_infos[-1].category, 'foo_category')

    def testListFilteredActionsFor(self):
        self.assertEqual(Set(self.actions.listFilteredActionsFor(self.folder).keys()),
                         expected_filtered_actions)

    def testPortalRegistrationIsActionProvider(self):
        self.failUnless('portal_registration' in self.actions.listActionProviders())

    def testMissingActionProvider(self):
        self.portal._delObject('portal_registration')
        try:
            self.actions.listFilteredActionsFor(self.portal)
        except:
            self.fail_tb('Should not bomb out if a provider is missing')

    def testBrokenActionProvider(self):
        self.portal.portal_registration = None
        try:
            self.actions.listFilteredActionsFor(self.portal)
        except:
            self.fail_tb('Should not bomb out if a provider is broken')

    def testMissingListActions(self):
        self.portal.portal_registration = ExplicitItem()
        try:
            self.actions.listFilteredActionsFor(self.portal)
        except:
            self.fail_tb('Should not bomb out if a provider is broken')

    def testDocumentActionsPermissionBug(self):
        # Test to ensure that permissions for items categorized as
        # 'document_actions' have their permissions evaluated in the context
        # of the content object.
        self.actions.addAction(id='foo',
                               name='foo_name',
                               action='foo_action',
                               condition='',
                               permission='View',
                               category='document_actions',
                               visible=1)
        actions = self.actions.listFilteredActionsFor(self.folder)
        match = [a for a in actions['document_actions'] if a['id'] == 'foo']
        self.failUnless(match)
        self.portal.portal_workflow.doActionFor(self.folder, 'hide')
        self.login('user1')
        actions = self.actions.listFilteredActionsFor(self.folder)
        match = [a for a in actions.get('document_actions', []) if a['id'] == 'foo']
        self.failIf(match)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestActionsTool))
    return suite

if __name__ == '__main__':
    framework()
