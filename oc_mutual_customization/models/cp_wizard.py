from openerp import models,fields,api
from openerp.osv import fields,osv
from datetime import datetime, timedelta



class WizardCustomerPer(osv.TransientModel):
    _name = 'wiz.customer.performance'
    _description = 'Generate Report for Customer Performance'

    _columns = {
        'start_date': fields.date('Start Date', required=True),
        'end_date': fields.date('End Date', required=True),
        'partner_id': fields.many2many('res.partner', string='Customer', required=True),
        'journal': fields.many2many('account.journal', string='Bank')
    }
    def fetch_record(self, journal_id):
        self.env.cr.execute("""SELECT aml.partner_id,rp.name,SUM(credit) AS amount FROM account_move_line as aml
                                INNER JOIN  res_partner as rp ON  aml.partner_id=rp.id
                                where  journal_id = %s and partner_id in %s and aml.date between '%s' AND '%s'
                                group by aml.partner_id,rp.name order by rp.name""" %(journal_id,tuple(self.partner_id.ids) if len(self.partner_id.ids)>1 else "("+str(self.partner_id.ids[0])+")",self.start_date,self.end_date))
        products = self.env.cr.dictfetchall()
        return products

    def get_partner_name(self,partner_id):
        partner_name = self.env['res.partner'].search(([('id', '=', partner_id)]))
        return partner_name[0].name
    #
    # def get_journal_name(self,journal):
    #     journal_name = self.env['account.journal'].search(([('id', '=', journal)]))
    #     return journal_name[0].name


    def print_report(self, cr, uid, ids, data, context=None):
        return {
            'type': 'ir.actions.report.xml',
            'name': 'oc_mutual_customization.report_customer_recov_template',
            'report_name': 'oc_mutual_customization.report_customer_recov_template'
        }