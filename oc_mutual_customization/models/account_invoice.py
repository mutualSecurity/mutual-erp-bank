from openerp.osv import fields, osv


class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'is_foc': fields.boolean('Is a FOC?', default=False, help="Check if the sale order is FOC "),
    }

# class wizard_data_inherit(osv.osv):
#     _inherit = "account.invoice"
#
#     # _columns = {
#     #     'data_wizard':
#     # }
#
#     def get_data(self, cr, uid, ids, context=None):
#         # view_id = self.ref('mutual_reports.wiz_report_select')
#         ctx({'ntn': self.NTN})
#         return {
#             'name': ('wizard_open'),
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'wiz.report.selection',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#              'context': ctx,
#              },
