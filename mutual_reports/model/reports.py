from openerp.osv import fields, osv
# import xlwt
#
# class report_additional_invoice(osv.osv_abstract):
#     _name='report.mutual_reports.custom_additional_invoice_xls'
#
#     @api.multi
#     def additional_excel_report(self,cr, uid, context=None):
#         workbook = xlwt.Workbook( 'additional invoice.xls', {'in_memory': True})
#         format_h = workbook.add.format({'font_size':14, 'align':'vcenter', 'bold':True})
#         worksheet = workbook.add_worksheet()
#         row = 0
#         col = 0
#         worksheet.write(row, col,'Additional Invoice',format_h)
#         for rec in self:
#             worksheet.write(row+1,col+1,self.NTN)
#
#
#         workbook.close()
#
class account_inh(osv.osv):
    _inherit = "account.invoice"
    _columns = {
        'is_cust_hf': fields.boolean('For Header', default=False, help="Check if for custom header footer "),
    }
