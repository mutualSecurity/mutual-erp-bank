#The file name of this file must match the filename name which we import in __init__.py file
from dateutil.relativedelta import relativedelta
from datetime import datetime as datetime
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
class mutual_procurements(osv.osv):
    _inherit = "procurement.order"
    def _run_move_create(self, cr, uid, procurement, context=None):
        ''' Returns a dictionary of values that will be used to create a stock move from a procurement.
        This function assumes that the given procurement has a rule (action == 'move') set on it.

        :param procurement: browse record
        :rtype: dictionary
        '''
        newdate = (datetime.strptime(procurement.date_planned, '%Y-%m-%d %H:%M:%S') - relativedelta(days=procurement.rule_id.delay or 0)).strftime('%Y-%m-%d %H:%M:%S')
        group_id = False
        if procurement.rule_id.group_propagation_option == 'propagate':
            group_id = procurement.group_id and procurement.group_id.id or False
        elif procurement.rule_id.group_propagation_option == 'fixed':
            group_id = procurement.rule_id.group_id and procurement.rule_id.group_id.id or False
        #it is possible that we've already got some move done, so check for the done qty and create
        #a new move with the correct qty
        already_done_qty = 0
        already_done_qty_uos = 0
        for move in procurement.move_ids:
            already_done_qty += move.product_uom_qty if move.state == 'done' else 0
            already_done_qty_uos += move.product_uos_qty if move.state == 'done' else 0
        qty_left = max(procurement.product_qty - already_done_qty, 0)
        qty_uos_left = max(procurement.product_uos_qty - already_done_qty_uos, 0)
        # new implementation added on inherited function on 7-11-2017
        vals = {
            'name': procurement.name,
            'company_id': procurement.rule_id.company_id.id or procurement.rule_id.location_src_id.company_id.id or procurement.rule_id.location_id.company_id.id or procurement.company_id.id,
            'product_id': procurement.product_id.id,
            'product_uom': procurement.product_uom.id,
            'product_uom_qty': qty_left,
            'product_uos_qty': (procurement.product_uos and qty_uos_left) or qty_left,
            'product_uos': (procurement.product_uos and procurement.product_uos.id) or procurement.product_uom.id,
            'partner_id': procurement.rule_id.partner_address_id.id or (procurement.group_id and procurement.group_id.partner_id.id) or False,
            'location_id': procurement.rule_id.location_src_id.id,
            'location_dest_id': procurement.location_id.id,
            'move_dest_id': procurement.move_dest_id and procurement.move_dest_id.id or False,
            'procurement_id': procurement.id,
            'rule_id': procurement.rule_id.id,
            'procure_method': procurement.rule_id.procure_method,
            'origin': procurement.origin,
            'picking_type_id': procurement.rule_id.picking_type_id.id,
            'group_id': group_id,
            'route_ids': [(4, x.id) for x in procurement.route_ids],
            'warehouse_id': procurement.rule_id.propagate_warehouse_id.id or procurement.rule_id.warehouse_id.id,
            'date': newdate,
            'date_expected': newdate,
            'propagate': procurement.rule_id.propagate,
            'priority': procurement.priority,
        }
        if vals['partner_id'] in self.pool.get('res.partner').search(cr, uid, [('is_technician', '=', True)]):
            print self.pool.get('res.partner').search(cr, uid, [('is_technician', '=', True)])
            print vals['partner_id']
            cond = self.pool.get('stock.warehouse').search(cr, uid, [('partner_id', '=', vals['partner_id'])])
            if len(cond) > 0:
                data = self.pool.get('stock.warehouse').browse(cr, uid, cond[0], context=None)
                vals['location_dest_id'] = data.lot_stock_id.id

        return vals

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