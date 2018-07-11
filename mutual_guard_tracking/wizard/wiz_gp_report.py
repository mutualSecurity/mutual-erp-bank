from openerp.osv import fields, osv
from openerp import api
from datetime import date, timedelta, datetime


class WizardReportPdf(osv.TransientModel):
    _name = 'wiz.gp.report.pdf'
    _description = 'Compute Report'

    _columns = {
        'date_from': fields.date('From'),
        'date_to': fields.date('To'),
        'bank_code': fields.selection([('ABL','ABL'), ('MBL','MBL'), ('DIB','DIB'),
                                       ('UBL', 'UBL'), ('HBL','HBL'), ('TMBL','TMBL'),
                                       ('JSBL','JSBL'), ('SAMBA','SAMBA'), ('NBP','NBP')], 'Bank Code')
    }

    _defaults = {
        'date_from': datetime.today(),
        'date_to': datetime.today()
    }
    
    def generate_report(self):
        self.env.cr.execute("""select * from mutual_guard_tracking where archive_signal=False and bank_code='%s'"""%(self.bank_code))
        res = self.env.cr.dictfetchall()
        if len(res)>0:
            return res
        else:
            raise osv.except_osv(('Error'), ('Active signals are not found of this bank'))

    @api.multi
    def print_report(self):
        if self.date_to > fields.date.today() or self.date_from > fields.date.today():
            raise osv.except_osv(('Error'), ('Date must be less than today'))
        return {
            'type': 'ir.actions.report.xml',
            'name': 'mutual_guard_tracking.wiz_patrolling_report_pdf',
            'report_name': 'mutual_guard_tracking.wiz_patrolling_report_pdf'
        }
