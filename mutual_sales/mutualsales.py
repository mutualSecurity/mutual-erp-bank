from openerp.osv import fields, osv
from openerp import api
import requests


class mutual_sales(osv.osv):
    _inherit = "res.partner"
    _name = "res.partner"
    _columns = {
        'is_employee': fields.boolean('Is a Employee?', store=True),
        'is_rider': fields.boolean('Is a Rider?',help="Check if the contact is a company, otherwise it is a person"),
        'is_technician': fields.boolean('Is a Technician?',help="Check if the contact is a company, otherwise it is a person"),
        'customer_branch_det': fields.one2many('customer.branch.details','customer_branch_details','Branch Details'),
        'customer_relatives': fields.one2many('customer.relatives','customer_r','Relative'),
        'cs_number': fields.char('Cs Number', size=10,select=True, store=True,track_visibility='onchange'),
        'branch_code':fields.char('Branch Code',size=10,select=True, store=True,track_visibility='onchange'),
        'bank_code':fields.char('Bank Code',size=10,select=True, store=True,track_visibility='onchange'),
        'uplink_date': fields.date('Uplink Date', select=True, store=True,track_visibility='onchange'),
        'c_street': fields.char('Corresponding Street',select=True, store=True),
        'office': fields.char('Office Number',select=True, store=True),
        'c_street2': fields.char('Corresponding Street2',select=True, store=True),
        'c_zip': fields.char('Zip', change_default=True, size=24,select=True, store=True),
        'c_city': fields.char('City'),
        'c_state_id': fields.many2one("res.country.state", 'State'),
        'c_country_id': fields.many2one('res.country', 'Country'),
        'guard_less_branch': fields.selection([('Yes', 'Yes'), ('No', 'No')], 'Guard Less Branch', store=True, default='No'),
        'locker_available': fields.selection([('Yes', 'Yes'), ('No', 'No')], 'Locker Available', store=True),
        'saturday_open': fields.selection([('Yes', 'Yes'), ('No', 'No')], 'Saturday Open', store=True),
        'rf_id': fields.char('RF_ID', select=True, store=True),
        'force_code': fields.char('Force Code', select=True, store=True),
        'parent':fields.boolean('Parent',store=True),
        'customer_visit': fields.boolean('Force Visit Required', store=True),
        'cus_ntn_no': fields.char('NTN',store=True),
        'cus_strn_no': fields.char('STRN', store=True),
    }

    @api.onchange('customer_visit')
    def new_visit(self):
        if self.customer_visit == True:
            r = requests.post("http://localhost:2020/createcustomer",
                              data={
                                  'name': self.name,
                                  'cs': self.cs_number,
                                  'bank_code': self.bank_code,
                                  'branch_code': self.branch_code,
                                  'street1': self.street,
                                  'street2': self.street2,
                                  'city': self.city
                              })


class customer_relatives(osv.osv):
    _name="customer.relatives"
    _columns = {
        # 'sequence': fields.char('ID', store=True),
        'customer_r': fields.many2one('res.partner','Customer'),
        'other': fields.char('Name', size=64,store=True),
        'relationship': fields.char('Position',size=100,store=True),
        'contact_1':fields.char('Contact#1',size=64,store=True),
        'contact_2': fields.char('Contact#2', size=64, store=True),
        'sms_alert': fields.boolean('SMS alert',store=True),
    }

class customer_branch_details(osv.osv):
    _name = "customer.branch.details"
    _columns = {
        'customer_branch_details': fields.many2one('res.partner', 'Customer'),
        'guardname': fields.char('Guard Name', size=64,store=True),
        'number': fields.char('Number',size=100,store=True),
        'securityco': fields.char('Security Co',size=64,store=True),
    }


class branch_details(osv.osv):
    _name = "res.users"
    _inherit = "res.users"
    _columns = {
        'signature_image': fields.binary('Signature', store=True),
    }


class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'so_status': fields.selection([('None', 'None'),
                                       ('All Items Installed', 'All Items Installed'),
                                       ('Some Items Left', 'Some Items Left'),
                                       ('Additional Items Installed', 'Additional Items Installed')], 'SO Status', store=True, default='None'),
        'details': fields.many2one('stock.picking', store=True, string='Internal Move'),
        'installation_date': fields.date('Installation Date', store=True),
        'complaint_reference': fields.char('Complaint reference',store=True, on_change='auto_select()'),
        'cs_number': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
        'tcs_receipt': fields.char('TCS/Receipt No.',store=True),
        'tcs_delivery_status': fields.char('TCS Delivery Status', store=True),
        'dispatch_sheet_date': fields.date('Dispatched Date', store=True),
        'branch_code': fields.related('partner_id', 'branch_code', type='char', size=12, string='Branch Code', readonly=True),
        'customer_name': fields.related('partner_id', 'name', type='char', string='Name', readonly=True),
        'bank_code': fields.related('partner_id', 'bank_code', type='char', size=12, string='Bank Code', readonly=True),
        'region': fields.related('partner_id', 'city', type='char', size=12, string='Region', readonly=True),
        'remarks': fields.text('Remarks', store=True),
        'is_tech': fields.related('partner_id', 'is_technician', type='boolean', string='Technician', readonly=True),
        'warehouse_name': fields.related('warehouse_id', 'code', type='char', string='WH Name', readonly=True),
        'req_ref': fields.many2one('mutual.requisition', store=True, string='Requisition Ref'),
        'time_in_out_remarks': fields.char('TI/TO Remarks', store=True),
    }

    defaults = {
        'currency_id_invoices': 'auto_select()',
    }

    @api.one
    @api.onchange('complaint_reference')
    def auto_select(self, context=None):
        if self.complaint_reference:
            res = {'value': {'amenities': False}}
            self.env.cr.execute('select id from res_partner where id = any(select partner_id from project_issue where id ='+self.complaint_reference+')')
            customer = self.env.cr.dictfetchall()
            list=self.env['res.partner'].search([['id', '=', customer[0]['id']], ])
            # customers = self.pool.get('res.partner')
            # res = customers.search(self.env.cr, self.env.uid, [('name', '=', 'Allied Bank')],context=context)
            self.partner_id = list


class mutual_order_lines(osv.osv):
    _inherit = 'sale.order.line'

    _columns = {
        'order_cs_number': fields.related('order_partner_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
        'order_bank_code': fields.related('order_partner_id', 'bank_code', type='char', size=12, string='Bank Code',readonly=True),
    }

