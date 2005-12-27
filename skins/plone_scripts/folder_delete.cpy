## Controller Python Script "folder_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Delete objects from a folder
##

from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError
paths=context.REQUEST.get('paths', [])
titles=[]
titles_and_paths=[]
failed = {}

portal = context.portal_url.getPortalObject()
status='failure'
message=_(u'Please select one or more items to delete.')

for path in paths:
    # Skip and note any errors
    try:
        obj = portal.restrictedTraverse(path)
        obj_parent = obj.aq_inner.aq_parent
        obj_parent.manage_delObjects([obj.getId()])
        titles.append(obj.title_or_id())
        titles_and_paths.append('%s (%s)' % (obj.title_or_id(), path))
    except ConflictError:
        raise
    except Exception, e:
        failed[path]= e

if titles:
    status='success'
    message = _(u'Item(s) deleted.')

    transaction_note('Deleted %s' % (', '.join(titles_and_paths)))

if failed:
    message = _(u'${items} could not be deleted.', mapping={u'items' : ', '.join(failed.keys())})

context.plone_utils.addPortalMessage(message)
return state.set(status=status)

