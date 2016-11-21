from openerp.osv import fields, osv
from openerp import api

class invoice_csnumber(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'courier': fields.boolean('Couriered', store=True),
        'payment_received': fields.boolean('Payment Received', store=True),
        'bank_cs_invoice': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number',readonly=True),
        'bank_code_invoice': fields.related('partner_id','bank_code',type='char', size=12,string='Bank code',readonly=True),
        'branch_code_invoice': fields.related('partner_id', 'branch_code', type='char', size=12, string='Branch code',readonly=True),
        # 'phone': fields.related('partner_id','phone',type='char', size=12,string='Phone',readonly=True),
        # 'mobile': fields.related('partner_id','mobile',type='char', size=12,string='Mobile',readonly=True),
        # 'ntn_num': fields.related('partner_id','ntn_num',type='char', size=12,string='NTN',readonly=True),
        # 'gst_num': fields.related('partner_id','gst_num',type='char', size=12,string='GST',readonly=True),
        # 'uplink_date': fields.related('partner_id','uplink_date',type='char', size=20,string='Uplink Date',readonly=True),
    }
invoice_csnumber()