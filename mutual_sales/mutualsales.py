from openerp.osv import fields, osv
from openerp import api


class mutual_sales(osv.osv):
    _inherit = "res.partner"
    _name = "res.partner"
    _columns = {
        'is_rider': fields.boolean('Is a Rider?',help="Check if the contact is a company, otherwise it is a person"),
        'is_technician': fields.boolean('Is a Technician?',help="Check if the contact is a company, otherwise it is a person"),
        'customer_branch_det': fields.one2many('customer.branch.details','customer_branch_details','Branch Details'),
        'customer_relatives': fields.one2many('customer.relatives','customer_r','Relative'),
        'cs_number': fields.char('Cs Number', size=10,select=True, store=True),
        'branch_code':fields.char('Branch Code',size=10,select=True, store=True),
        'bank_code':fields.char('Bank Code',size=10,select=True, store=True),
        'uplink_date': fields.date('Uplink Date', select=True, store=True),
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

    }

mutual_sales()



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


class customer_branch_details(osv.osv):
    _name = "mutual.res.users"
    _inherit = "res.users"


class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'complaint_reference': fields.char('Complaint reference',store=True, on_change='auto_select()'),
        'cs_number': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number', readonly=True),
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




