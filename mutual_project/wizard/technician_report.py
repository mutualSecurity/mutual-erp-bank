from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class technicianReport(models.TransientModel):
    _name = 'technician.report'
    _description = 'Generate Report of Technician TimeIn/Out'

    technician_id = fields.Many2many('hr.employee', string='Technician')
    date_start = fields.Datetime('From')
    date_end = fields.Datetime('To')

    @api.multi
    def get_details(self):
        tech_activities=[]
        for tech in self.technician_id:
            complaints = self.env['tech.activities.issues'].search([('date_start', '>=', self.date_start),('date_end', '<=', self.date_end),('technician_name','=',tech.id)])
            if len(complaints)>0:
                tech_activities.append({'technician':tech.name, 'complaints':complaints})
        return tech_activities

    @api.multi
    def print_report(self):
        return {
            'type': 'ir.actions.report.xml',
            'name': 'mutual_project.technician_report_pdf',
            'report_name': 'mutual_project.technician_report_pdf'
        }
