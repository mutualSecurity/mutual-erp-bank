#The file name of this file must match the filename name which we import in __init__.py file
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv
from openerp.tools.float_utils import float_round, float_compare
from openerp import api




class mutual_products(osv.osv):
    _inherit = "product.product"
    _columns = {
        'default_code': fields.char('', select=True),

    }

class mutual_stockwarhouse(osv.osv):
    _inherit = "stock.warehouse"
    _columns = {
        'code': fields.char('Short Name', size=100, store=True, required=True, select=True),
    }

class mutual_templates(osv.osv):
    _inherit = "product.template"
    _columns = {
        'type': fields.selection([('product', 'Stockable Product'), ('consu', 'Consumable'), ('service', 'Service')],
                                 'Product Type', required=True,
                                 help="Consumable: Will not imply stock management for this product. \nStockable product: Will imply stock management for this product."),
        'list_price': fields.float('Sale Price', digits_compute=dp.get_precision('Product Price'),
                                   help="Base price to compute the customer price. Sometimes called the catalog price."),
        'standard_price': fields.property(type='float', digits_compute=dp.get_precision('Product Price'),
                                          help="Cost price of the product template used for standard stock valuation in accounting and used as a base price on purchase orders. "
                                               "Expressed in the default unit of measure of the product.",string="Cost Price"),
    }

class mutual_stock(osv.osv):
    _inherit = "stock.picking"
    values = [('Stock Returned from Customer', 'Stock Returned from Customer'),
              ('Stock Returned from Technician', 'Stock Returned from Technician'),
              ('Stock Returned from Bank Warehouse', 'Stock Returned from Bank Warehouse'), ('None', 'None'),
               ]
    _columns = {

        'cs_number': fields.related('partner_id', 'cs_number',type='char', size=12, string='CS Number',readonly=True),
        'approve': fields.boolean('Approved',store=True, compute='approval', read=['stock.group_stock_user'], write=['stock.group_stock_manager']),
        'status': fields.selection(values, 'Status')
    }

    _defaults = {
        'status': 'None',
    }


    @api.one
    @api.depends('partner_id')
    def approval(self):
        if self.partner_id:
            self.approve = True