from openerp.osv import fields, osv
import xlwt
from xlwt import *
from openerp import api
import cStringIO
import xlsxwriter
import base64


class ReportSelection(osv.TransientModel):
    _name = 'wiz.report.selection'
    _description = 'for excel report selection'


    _columns = {
        'select': fields.selection(
            [
                ('additional', 'Additional Invoice Report'),
                ('monitoring', 'Monitoring Report'),
                ('tax_break', 'Tax Break-Up Invoice'), ], required="1"),
        'report': fields.binary('report data', readonly=True),
        'report_name': fields.char('file name', store=True, readonly=True),
        # 'data_invoice': fields.many2one('account.invoice', string="Invoice Ref",),
    }

    @api.multi
    def select_report_type(self):
        if self.select == 'additional':
            return self.additional_excel_report()
        elif self.select == 'monitoring':
            return self.monitoring_invoive()
        elif self.select == 'tax_break':
            return self.tax_break_inv()
        else:
            raise ValueError('No Report Type Selected')

    # additional report function excel report
    @api.multi
    def additional_excel_report(self):
        active_id = self.env.context.get('active_id', False)
        records =self.env['account.invoice'].search(([('id', '=', active_id)]))
# header format
        borders_header = Borders()
        borders_header.left = 3
        borders_header.right = 3
        borders_header.top = 3
        borders_header.bottom = 3

        fnt_header = Font()
        fnt_header.name = 'Arial'
        fnt_header.colour_index = 4
        fnt_header.bold = True

        a_header = Alignment()
        a_header.horz = Alignment.HORZ_CENTER
        a_header.vert = Alignment.VERT_CENTER
# --------
        #         total amount formating
        a = Alignment()
        a.horz = Alignment.HORZ_RIGHT

        b = Borders()
        b.top = 1

        total_format = XFStyle()
        total_format.borders = b
        total_format.alignment = a
# -----------------
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Additional')
        ws.protect = True
        fp = cStringIO.StringIO()

        row = 10
        col = 0

        header_style = XFStyle()
        header_style.font = fnt_header
        header_style.borders = borders_header
        header_style.alignment = a_header

        sub_header_style = xlwt.easyxf("font: name Calibri size 13 px, bold on, height 200;")
        value_style = xlwt.easyxf("font: name Calibri size 15 px, height 200 ;")


        ws.write_merge(0, 0, 0, 10, 'Additional Invoice', header_style)
        ws.write(2, 1,records.partner_id.name, sub_header_style)
        ws.write(5, 5, 'STN', sub_header_style)
        ws.write(5, 6, '17-00-3764-757-19', sub_header_style)
        ws.write(5, 1, 'NTN', sub_header_style)
        ws.write(5, 2,records.NTN,value_style )
        ws.write(7, 1,'INVOICE REF #', sub_header_style)
        ws.write(7, 4,records.id, value_style)

        ws.write(9, 0, 'Description', sub_header_style)
        ws.write(9, 6, 'Quantity', sub_header_style)
        ws.write(9, 8, 'Unit Price', sub_header_style)
        ws.write(9, 10, 'Amount', sub_header_style)

        for data in records.invoice_line:
            if data:
                ws.write(row, 0, data.name, value_style)
                ws.write(row, 6, data.quantity, value_style)
                ws.write(row, 8, data.price_unit, value_style)
                ws.write(row, 10, data.price_subtotal, value_style)
                row+=1

        ws.write(24, 8, 'Total', sub_header_style)
        ws.write(24, 10, round(records.amount_total), total_format )


        wb.save(fp)
        out = base64.encodestring(fp.getvalue())
        self.write({'report': out, 'report_name': 'additional.xls'})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wiz.report.selection',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],

        }
# monitoring excel report funtion
    @api.multi
    def monitoring_invoive(self):

        active_id = self.env.context.get('active_id', False)
        records = self.env['account.invoice'].search(([('id', '=', active_id)]))
# header format
        borders_header = Borders()
        borders_header.left = 1
        borders_header.right = 1
        borders_header.top = 1
        borders_header.bottom = 1


        fnt_header = Font()
        fnt_header.name = 'Arial'
        fnt_header.colour_index = 4
        fnt_header.bold = True

        a_header = Alignment()
        a_header.horz = Alignment.HORZ_CENTER
        a_header.vert = Alignment.VERT_CENTER
# --------
        #         total amount formating
        a = Alignment()
        a.horz = Alignment.HORZ_RIGHT

        b = Borders()
        b.top = 1

        total_format = XFStyle()
        total_format.borders = b
        total_format.alignment = a
        # -----------------

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Monitoring')
        ws.protect = True
        fp = cStringIO.StringIO()

        row = 10
        col = 0

        header_style = XFStyle()
        header_style.font = fnt_header
        header_style.borders = borders_header
        header_style.alignment = a_header

        sub_header_style = xlwt.easyxf("font: name Calibri size 13 px, bold on, height 200;")
        value_style = xlwt.easyxf("font: name Calibri size 15 px, height 200 ;")

        ws.write_merge(0, 0, 0, 8, 'Monitoring Invoice', header_style)
        ws.write(2, 1, records.partner_id.name, sub_header_style)
        ws.write(5, 1, 'NTN', sub_header_style)
        ws.write(5, 2,records.NTN,value_style )
        ws.write(7, 1, 'INVOICE REF #', sub_header_style)
        ws.write(7, 3, records.id, value_style)

        # one to many field data
        ws.write(9, 0, 'Description', sub_header_style)
        ws.write(9, 6, 'Billing Period', sub_header_style)
        ws.write(9, 8, 'Amount', sub_header_style)

# For cond on Description

        for line in records.invoice_line:
            if line.product_id.name == 'Monitoring charges' and records.partner_id.name == 'National Bank of Pakistan':
                ws.write(row, 0, 'Monitoring charges Including Provincial Sales Tax', value_style)
                row +=1
            elif line.product_id.name == 'Monitoring charges' and records.partner_id.name == 'National Bank of Pakistan':
                ws.write(row, 0, 'Monitoring charges Including Provincial Sales Tax', value_style)
                row = +1
# for condition on billing period
        for line in records.invoice_line:
            if line.product_id.name == 'Monitoring charges':
                ws.write(row, 6, records.to, value_style)
                ws.write(row, 7, records.to , value_style)
                row += 1

        ws.write(24, 6, 'Total', sub_header_style)
        ws.write(24, 8, round(records.amount_total), total_format )


        wb.save(fp)

        out = base64.encodestring(fp.getvalue())
        self.write({'report': out, 'report_name': 'monitoring invoice.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wiz.report.selection',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],

        }

# tax excel report funtion
    @api.multi
    def tax_break_inv(self):
        active_id = self.env.context.get('active_id', False)
        records = self.env['account.invoice'].search(([('id', '=', active_id)]))

# header format
        borders_header = Borders()
        borders_header.left = 1
        borders_header.right = 1
        borders_header.top = 1
        borders_header.bottom = 1


        fnt_header = Font()
        fnt_header.name = 'Arial'
        fnt_header.colour_index = 4
        fnt_header.bold = True

        a_header = Alignment()
        a_header.horz = Alignment.HORZ_CENTER
        a_header.vert = Alignment.VERT_CENTER

        header_style = XFStyle()
        header_style.font = fnt_header
        header_style.borders = borders_header
        header_style.alignment = a_header

        # --------
#         total amount formating
        a = Alignment()
        a.horz = Alignment.HORZ_RIGHT

        b = Borders()
        b.top = 1

        total_format = XFStyle()
        total_format.borders = b
        total_format.alignment = a



        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Tax Break-Up')
        ws.protect = True
        fp = cStringIO.StringIO()

        row = 10
        col = 0

        sub_header_style = xlwt.easyxf("font: name Calibri size 13 px, bold on, height 200;")
        value_style = xlwt.easyxf("font: name Calibri size 15 px, height 200 ;")

        ws.write_merge(0, 0, 0, 14, 'Tax Break-UP Invoice', header_style)
        ws.write(2, 1, records.partner_id.name, sub_header_style)
        ws.write(5, 1, 'NTN', sub_header_style)
        ws.write(5, 2,records.NTN, value_style)
        ws.write(7, 1, 'INVOICE REF #', sub_header_style)
        ws.write(7, 4, records.id, value_style)

        # one to many field data
        ws.write(9, 0, 'Description', sub_header_style)
        ws.write(9, 6, 'Quantity', sub_header_style)
        ws.write(9, 8, 'Unit Price', sub_header_style)
        ws.write(9, 10, 'Tax Rate', sub_header_style)
        ws.write(9, 12, 'Tax Amount', sub_header_style)
        ws.write(9, 14, 'Amount', sub_header_style)

        coline = 0
        for data in records.invoice_line:
            if data:
                ws.write(row, 0, data.name, value_style)
                ws.write(row, 6, data.quantity, value_style)
                ws.write(row, 8, data.price_unit, value_style)
                ws.write(row, 10, data.invoice_line_tax_id.name, value_style)
                ws.write(row, 12, data.quantity * data.price_unit * data.invoice_line_tax_id.amount, value_style)
                ws.write(row, 14, data.price_subtotal + data.tax_amount, value_style)
                row += 1
        ws.write(20, 10, 'Total Without Tax', sub_header_style)
        ws.write(20, 12, round(records.amount_untaxed), total_format)
        ws.write(22, 10, 'Taxes', sub_header_style)
        ws.write(22, 12, round(records.amount_tax), total_format)
        ws.write(24, 10, 'Total', sub_header_style)
        ws.write(24, 12, round(records.amount_total), total_format)



        wb.save(fp)
        out = base64.encodestring(fp.getvalue())
        self.write({'report': out, 'report_name': 'Tax Break-Up Invoice.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wiz.report.selection',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
        }