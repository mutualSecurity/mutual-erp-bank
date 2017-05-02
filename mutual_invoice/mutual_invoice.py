from openerp.osv import fields, osv
from openerp import api
from datetime import date, timedelta,datetime
import re
class invoice_line_(osv.osv):
    _inherit = 'account.invoice.line'
    _columns = {
        'from': fields.date('From', store=True),
        'to': fields.date('To', store=True),
    }


class invoice_csnumber(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'show_tax': fields.boolean('Show Tax', store=True, compute='select_auto_tax'),
        'NTN': fields.char('NTN', store=True, default="3764757-1",readonly=True),
        'sales_tax_no': fields.char('STN', store=True,default="17-00-3764-757-19",readonly=True),
        'courier': fields.boolean('Couriered', store=True),
        'payment_received': fields.boolean('Payment Received', store=True),
        'bank_cs_invoice': fields.related('partner_id', 'cs_number', type='char', size=12, string='CS Number',readonly=True),
        'bank_code_invoice': fields.related('partner_id','bank_code',type='char', size=12,string='Bank code',readonly=True),
        'branch_code_invoice': fields.related('partner_id', 'branch_code', type='char', size=12, string='Branch code',readonly=True),
        'remarks': fields.text('Follow Up', store=True),
        'po_dd':fields.selection([('PO','PO'),('DD','DD')], 'PO/DD', store=True, track_visibility='onchange'),
        'cheque_date': fields.date('Cheque Received Date', store=True, track_visibility='onchange'),
        'cheque_no':fields.char('Cheque no.',store=True,track_visibility='onchange'),
        'cheque_date_customer': fields.date('Cheque Date', store=True, track_visibility='onchange'),
        'actual_amount': fields.float('Actual received amount',store=True,track_visibility='onchange'),
        'from': fields.date('From',store=True),
        'to': fields.date('To',store=True),
        'pay_remarks':fields.char('Payment Remarks',store=True,track_visibility='onchange'),
        'invoice_date': fields.date('Invoice Date', store=True, track_visibility='onchange'),
    }

    @api.one
    @api.depends('invoice_line.invoice_line_tax_id')
    def select_auto_tax(self):
        for line in self.invoice_line:
            if line.invoice_line_tax_id != False:
                self.show_tax = True

    @api.onchange('remarks')
    def followup_date(self):
        if self.remarks!=False:
            if len(re.findall(str(datetime.now().date()), self.remarks))==0:
                self.remarks = self.remarks+"\n"+str(datetime.now().date())

    @api.multi
    def compute_roundoff(self):
        print 'Round off amount >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'+str(round(self.amount_total))
        self.amount_total = round(self.amount_total)


class summary_sheet(osv.osv):
    _name = 'summary_sheet'
    _columns = {
        'customer': fields.many2one('res.partner', 'Customer', required=True, domain="[('customer','=',True)]"),
        'name': fields.char('Name', store=True),
        'summary_sheet': fields.one2many('billing_period', 'dummy', 'Summary Sheets', store=True),
        'sale_tax': fields.boolean('Sales Tax',store=True),
        'maintenance_charges': fields.boolean('Maintenance Charges', store=True),
        'total': fields.float('Total Amount', store=True, compute='_compute_total_ss')
    }

    @api.one
    @api.depends('summary_sheet.total_amount_with_sales_tax')
    def _compute_total_ss(self):
        total = sum(round(float(line.total_amount_with_sales_tax),2) for line in self.summary_sheet)
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Amount :"+str(total)+">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        self.total = round(total)

class billing_period(osv.osv):
    _name = 'billing_period'
    _columns = {
        'dummy': fields.char('dummy', store=True),
        'cs_number': fields.char('CS Number', store=True),
        'branch_code': fields.char('Branch Code', store=True),
        'address1': fields.char('Address 1', store=True),
        'address2': fields.char('Address 2', store=True),
        'from': fields.date('From', store=True),
        'to': fields.date('To', store=True),
        'service_period': fields.integer('Service Period', store=True),
        'sales_tax': fields.float('Sales Tax in %', store=True),
        'sales_tax_amount': fields.float('Sales Tax in amount', store=True, compute='total_in_sales_tax'),
        'basic_amount': fields.float('Monitoring Amount per month', store=True),
        'maintenance_basic_amount': fields.float('Maintenance Amount per month', store=True),
        'total_moni': fields.float('Total Monitoring', store=True, compute='total_in_sales_tax'),
        'total_ment': fields.float('Total Maintenance', store=True,compute='total_in_sales_tax'),
        'total_amount_ex_sales_tax': fields.float('Total billing amount excluding sales tax', store=True, compute='total_in_sales_tax'),
        'total_amount_with_sales_tax': fields.float('Total billing amount including sales tax', store=True, compute='total_in_sales_tax'),
    }

    @api.one
    @api.depends('service_period', 'basic_amount', 'sales_tax', 'maintenance_basic_amount')
    def total_in_sales_tax(self):
        tax = (self.sales_tax * self.basic_amount)/100
        self.sales_tax_amount = self.service_period * tax
        self.total_ment = round(self.service_period * self.maintenance_basic_amount)
        self.total_moni = round(self.service_period * self.basic_amount)
        if self.maintenance_basic_amount > 0.0:
            self.total_amount_ex_sales_tax = round((self.service_period * self.basic_amount) + (self.service_period * self.maintenance_basic_amount))
            self.total_amount_with_sales_tax = round((self.service_period * self.basic_amount)+(self.service_period*tax) + self.total_ment)
        else:
            self.total_amount_ex_sales_tax = round(self.service_period * self.basic_amount)
            self.total_amount_with_sales_tax = float(self.total_amount_ex_sales_tax) + float(self.sales_tax_amount)




