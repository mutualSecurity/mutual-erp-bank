from openerp.osv import fields, osv
from openerp import api

class invoice_csnumber(osv.osv):
    _inherit = 'account.analytic.account'
    _columns = {
        'cs_number': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
        'branch_code': fields.related('partner_id','branch_code',type='char',string='Branch Code',readonly=True),
        'bank_code': fields.related('partner_id','bank_code',type='char',string='Bank Code',readonly=True),
        'address': fields.related('partner_id','street',type='char',string='Address',readonly=True),
        'city': fields.related('partner_id','city',type='char',string='City',readonly=True),
    }

