from odoo import models, fields, api, _
import xlwt
import base64
import cStringIO


class FincaReport(models.TransientModel):
    _rec_name = 'report_name'
    _name = 'finca.report'

    report_name = fields.Char('File Name')
    report = fields.Binary('CSV File', filters='.csv', readonly=True)
    type = fields.Selection([('monitoring','Monitoring Invoice'),
                             ('additional','Additional Invoice'),
                             ('tax_breakup_invoice','Tax Break-Up Invoice')])

    @api.multi
    def get_width(self,num_characters,constant=300):
        return int((1 + num_characters) * constant)

    @api.multi
    def get_payslip_components(self, payslip_id, emp_id):
        employees = self.env['hr.employee'].search([('id', '=', emp_id)])
        self.env.cr.execute(
            """select sum(psl.total) as total,fc.id as finca_category_id from hr_payslip_line as psl 
            inner join hr_salary_rule as hsl on psl.salary_rule_id=hsl.id
            inner join finca_categories as fc on hsl.finca_category_id = fc.id
            where psl.slip_id=%s group by fc.id order by fc.sequence""" % (payslip_id))
        res = self.env.cr.dictfetchall()
        for emp in employees:
            res.insert(0, {'cnic': emp.identification_id or '', 'finca_category_id': -1})
            res.insert(0, {'mobile': emp.mobile_phone or '', 'finca_category_id': -1})
            res.insert(0, {'name': emp.name_related or '', 'finca_category_id': -1})
        return res

    @api.multi
    def get_data(self):
        res = []
        self.env.cr.execute(
            """select id,employee_id from hr_payslip where payslip_run_id=%s""" % (self.payslip_batch.id))
        records = self.env.cr.dictfetchall()
        for rec in records:
            res.append(self.get_payslip_components(rec['id'], rec['employee_id']))
        return res

    @api.multi
    def get_finca_categories(self):
        self.env.cr.execute("""select * from finca_categories where appears_on_finca_report='%s' order by sequence asc"""%(True))
        res = self.env.cr.dictfetchall()
        return res

    @api.multi
    def generate_xls_report(self):
        self.ensure_one()
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Payslip Details')
        ws.protect = True
        fp = cStringIO.StringIO()

        sub_header_style = xlwt.easyxf("font: name Calibri size 11 px, height 200;")

        first_row = 0
        ws.row(first_row).height = 500
        categories = self.get_finca_categories()
        category_ids = []

        for i in range(len(self.get_finca_categories())):
            ws.col(i).width = self.get_width(len(categories[i]['name']))
            ws.write(first_row, i, categories[i]['name'], sub_header_style)
            category_ids.append(categories[i]['id'])

        data = self.get_data()

        second_row = 1

        for record in range(len(data)):
            for rec in range(len(data[record])):
                if data[record][rec]['finca_category_id'] in category_ids:
                    ws.col(rec).width = self.get_width(len(str(data[record][rec]['total'])))
                    categ_pos = category_ids.index(data[record][rec]['finca_category_id'])
                    ws.write(second_row, categ_pos, data[record][rec]['total'], sub_header_style)

                elif data[record][rec]['finca_category_id'] == -1 and 'name' in data[record][rec]:
                    ws.col(rec).width = self.get_width(len(data[record][rec]['name']),350)
                    ws.write(second_row, 0, data[record][rec]['name'], sub_header_style)

                elif data[record][rec]['finca_category_id'] == -1 and 'mobile' in data[record][rec]:
                    ws.col(rec).width = self.get_width(len(data[record][rec]['mobile']))
                    ws.write(second_row, 1, data[record][rec]['mobile'], sub_header_style)

                elif data[record][rec]['finca_category_id'] == -1 and 'cnic' in data[record][rec]:
                    ws.col(rec).width = self.get_width(len(data[record][rec]['cnic']))
                    ws.write(second_row, 2, data[record][rec]['cnic'], sub_header_style)
            second_row += 1

        wb.save(fp)
        out = base64.encodestring(fp.getvalue())
        self.write({'report': out, 'report_name': 'finca_report.csv'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'finca.report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],

        }
