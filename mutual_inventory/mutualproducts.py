#The file name of this file must match the filename name which we import in __init__.py file
from datetime import date, datetime
from dateutil import relativedelta
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv
from openerp.tools.float_utils import float_round, float_compare
from openerp import api
from openerp import SUPERUSER_ID, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class mutual_stock_quants(osv.osv):

    _inherit = "stock.quant"

    def quants_reserve(self, cr, uid, quants, move, link=False, context=None):

        '''This function reserves quants for the given move (and optionally given link). If the total of quantity reserved is enough, the move's state
        is also set to 'assigned'

        :param quants: list of tuple(quant browse record or None, qty to reserve). If None is given as first tuple element, the item will be ignored. Negative quants should not be received as argument
        :param move: browse record
        :param link: browse record (stock.move.operation.link)
        '''
        toreserve = []
        reserved_availability = move.reserved_availability
        #split quants if needed
        for quant, qty in quants:
            if qty <= 0.0 or (quant and quant.qty <= 0.0):
                raise osv.except_osv(_('Error!'), _('You can not reserve a negative quantity or a negative quant.'))
            if not quant:
                continue
            self._quant_split(cr, uid, quant, qty, context=context)
            toreserve.append(quant.id)
            reserved_availability += quant.qty
        #reserve quants
        if toreserve:
            self.write(cr, SUPERUSER_ID, toreserve, {'reservation_id': move.id, 'in_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
            #if move has a picking_id, write on that picking that pack_operation might have changed and need to be recomputed
            if move.picking_id:
                self.pool.get('stock.picking').write(cr, uid, [move.picking_id.id], {'recompute_pack_op': True}, context=context)
        #check if move'state needs to be set as 'assigned'
        rounding = move.product_id.uom_id.rounding
        if float_compare(reserved_availability, move.product_qty, precision_rounding=rounding) == 0 and move.state in ('confirmed', 'waiting')  :
            self.pool.get('stock.move').write(cr, uid, [move.id], {'state': 'assigned'}, context=context)
        elif float_compare(reserved_availability, 0, precision_rounding=rounding) > 0 and not move.partially_available:
            self.pool.get('stock.move').write(cr, uid, [move.id], {'partially_available': True}, context=context)


class mutual_products(osv.osv):
    _inherit = "product.product"
    _columns = {
        'default_code': fields.char('', select=True),
        'acc_inv_check': fields.boolean('In Accounts Inventory', store=True),


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
    values = [('Stock Returned from Customer To Warehouse', 'Stock Returned from Customer To Warehouse'),
              ('Stock Returned from Customer To Technician', 'Stock Returned from Customer To Technician'),
              ('Stock Returned from Technician To Warehouse', 'Stock Returned from Technician  To Warehouse'),
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