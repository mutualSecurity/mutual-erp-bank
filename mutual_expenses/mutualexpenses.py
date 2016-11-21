from openerp.osv import fields, osv

class mutual_expenses(osv.osv):
    _inherit = "hr.expense.expense",
    _columns = {
        'partner_id_expense': fields.many2one('res.partner', 'Customer', required=True),
        'test': fields.char('test')
    }

mutual_expenses()



