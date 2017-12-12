from openerp import models,fields,api
from openerp.osv import fields,osv
from datetime import date, timedelta,datetime


class WizardReports(osv.TransientModel):
    _name = 'wiz.reports'
    _description = 'PDF Reports for showing all disconnection,reconnection'

    _columns = {

    }

    def pending_invoices(self):
        self.env.cr.execute(
            "select bank_code,sum(amount_total) amount_total, count(amount_total) invoices_total from account_invoice "
            "INNER JOIN res_partner ON account_invoice.partner_id = res_partner.id where account_invoice.courier = True "
            "and account_invoice.payment_received = False "
            "and account_invoice.state != 'cancel' and account_invoice.state != 'paid' and account_invoice.state != 'open' "
            "group by bank_code")

        pendings = self.env.cr.dictfetchall()
        return pendings

    def received_invoices(self):
        self.env.cr.execute(
            "select bank_code,sum(amount_total) amount_total, count(amount_total) invoices_total from account_invoice INNER JOIN res_partner ON account_invoice.partner_id = res_partner.id where account_invoice.payment_received = True "
            "and account_invoice.state != 'cancel' "
            "group by bank_code")
        received = self.env.cr.dictfetchall()
        return received

    def print_report(self, cr, uid, ids, data, context=None):
        return {
                'type': 'ir.actions.report.xml',
                'name': 'mutual_reports.wiz_recovery_report',
                'report_name': 'mutual_reports.wiz_recovery_report'
            }
