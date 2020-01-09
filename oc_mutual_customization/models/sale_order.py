from openerp.osv import fields, osv


class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'is_foc': fields.boolean('Is a FOC?', default=False, help="Check if the sale order is FOC "),
    }