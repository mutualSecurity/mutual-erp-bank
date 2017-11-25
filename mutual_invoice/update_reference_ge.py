from openerp.osv import fields, osv
from openerp import models
from openerp import fields as field
from openerp import api,_
from datetime import date, timedelta,datetime
import re
import calendar
import time
from dateutil.relativedelta import *
from openerp.tools import amount_to_text_en
from openerp.exceptions import except_orm, Warning, RedirectWarning


class generalEntryCreate(osv.osv):
    _inherit = "account.move"
    _columns = {
        'count': fields.integer('Cancel Count', store=True),
    }

    _defaults = {
        'count': 0
    }

    def button_cancel(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        obj.count = obj.count +1
        for line in self.browse(cr, uid, ids, context=context):
            if not line.journal_id.update_posted:
                raise osv.except_osv(_('Error!'), _(
                    'You cannot modify a posted entry of this journal.\nFirst you should set the journal to allow cancelling entries.'))
        if ids:
            cr.execute('UPDATE account_move ' \
                       'SET state=%s ' \
                       'WHERE id IN %s', ('draft', tuple(ids),))
            self.invalidate_cache(cr, uid, context=context)
        return True

    def button_validate(self, cursor, user, ids, context=None):
        obj = self.browse(cursor, user, ids[0], context=context)
        if str(obj.period_id.name).split('/')[0] == str(obj.date).split('-')[1] or str(obj.period_id.code).split('/')[0] == '00':
            if(obj.count>0):
                cursor.execute('UPDATE account_move_line SET ref =' + "'" + str(obj.ref) + "'" + 'WHERE move_id =' + str(obj.id))
            for move in self.browse(cursor, user, ids, context=context):
                # check that all accounts have the same topmost ancestor
                top_common = None
                for line in move.line_id:
                    account = line.account_id
                    top_account = account
                    while top_account.parent_id:
                        top_account = top_account.parent_id
                    if not top_common:
                        top_common = top_account
                    elif top_account.id != top_common.id:
                        raise osv.except_osv(_('Error!'),
                                             _(
                                                 'You cannot validate this journal entry because account "%s" does not belong to chart of accounts "%s".') % (
                                             account.name, top_common.name))
            return self.post(cursor, user, ids, context=context)
        else:
            raise osv.except_osv(_('Error!'), _(
                'Accounting period and posting date must belong to the same month.'))
