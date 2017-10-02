from openerp import models,fields,api,_
from openerp.osv import fields,osv
from datetime import datetime, timedelta


class WizardCustomerInventory(osv.TransientModel):
    _name = 'wiz.customer.inventory'
    _description = 'Generate Report for Customer Inventory'

    _columns = {
        'partner_id': fields.many2one('res.partner','Customer',required=True),
    }

    def fetch_record(self):
        self.env.cr.execute("SELECT stock_picking.origin,stock_picking.date,stock_picking.status,"
                            "stock_move.product_qty,stock_move.name FROM stock_picking "
                            "INNER JOIN stock_move ON stock_picking.id = stock_move.picking_id "
                            "where stock_picking.state = 'done' and stock_picking.partner_id = "+str(self.partner_id.id)+
                            "order by stock_picking.origin asc")
        products = self.env.cr.dictfetchall()
        return products

    def print_report(self, cr, uid, ids, data, context=None):
        return {
            'type': 'ir.actions.report.xml',
            'name': 'mutual_project.report_customer_inventory',
            'report_name': 'mutual_project.report_customer_inventory'
        }

