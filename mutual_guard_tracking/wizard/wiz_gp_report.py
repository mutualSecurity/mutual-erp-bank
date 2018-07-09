from openerp.osv import fields, osv
from openerp import api
from datetime import date, timedelta, datetime


class WizardReportPdf(osv.TransientModel):
    _name = 'wiz.gp.report.pdf'
    _description = 'Compute Report'

    _columns = {
        'date_from': fields.date('From'),
        'date_to': fields.date('To')
    }

    _defaults = {
        'date_from': datetime.today(),
        'date_to': datetime.today()
    }
    
    def generate_report(self):
        self.env.cr.execute("""select * from mutual_guard_tracking where archive_signal=False""")
        return self.env.cr.dictfetchall()
    
    @api.multi
    def print_report(self):
        return {
            'type': 'ir.actions.report.xml',
            'name': 'mutual_guard_tracking.wiz_patrolling_report_pdf',
            'report_name': 'mutual_guard_tracking.wiz_patrolling_report_pdf'
        }
