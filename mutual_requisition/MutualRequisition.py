#The file name of this file must match the filename name which we import in __init__.py file
# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp import api
from datetime import date,time

class mutual_requisition(osv.osv):
    _name = "mutual.requisition"
    _columns = {
        'req_code': fields.char('Serial No.', readonly=True, store=True),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], 'State', store=True, default='draft'),
        'title': fields.char('Title',store=True),
        'date': fields.date('Date',store=True),
        'products': fields.one2many('basic.package.items','req_slip','Products',store=True),
        'devices':fields.char('Devices',store=True, defaults=' ', compute='devices_details'),
        'qty':fields.char('Qty',store=True, defaults=' ', compute='devices_details'),
        'ref': fields.char('Ref', store=True, defaults=' ', compute='devices_details',readonly=True),
        'req_type': fields.selection([('New Installation','New Installation'),('Additional','Additional'),('none',' ')],'Requisition Type')

    }
    _defaults={
        'req_type':'none',
    }

    def create(self, cr, uid, vals, context=None):
        if vals['req_type'] == 'New Installation':
            vals['req_code'] = self.pool.get('ir.sequence').get(cr, uid, 'mutual.ni.requisition')
        elif vals['req_type'] == 'Additional':
            vals['req_code'] = self.pool.get('ir.sequence').get(cr, uid, 'mutual.ad.requisition')
        return super(mutual_requisition, self).create(cr, uid, vals, context=context)



    @api.depends('products.courier_sheet_products', 'products.quantity')
    def devices_details(self):
        print ">>>>>>>>>>>>>>>>>>>>>>>SingleTOn>>>>>>>>>>>>."
        for line in self.products:
            print ">>>>>>>>>>>>for singlton>>>>>>>>>>>>>>>>>"
            self.devices = str(self.devices) + str(line.courier_sheet_products.name) + ","
            self.devices = self.devices.replace('False', ' ')
            self.qty = str(self.qty) + str(line.quantity) + ","
            self.qty = self.qty.replace('False', ' ')
            self.ref=str(self.ref)+str(line.cs_number)+","
            self.ref = self.ref.replace('False', ' ')

    @api.multi
    def validate(self):
        return self.write({'state': 'confirmed'})

    @api.multi
    def cancel(self):
        return self.write({'state': 'draft'})


# class products(osv.osv):
#     _name = 'products.req'
#     _columns = {
#         'product_tb': fields.many2one('mutual.requisition','Products',store=True,required=True),
#         'product_name': fields.many2one('product.template', 'Name', store=True,required=True),
#         'quantity': fields.float('Quantity',store=True,required=True),
#         'type': fields.selection([('For Technician', 'For Technician'), ('For Customer', 'For Customer')], 'Type', store=True),
#         'customer': fields.many2one('res.partner','Customer',store=True),
#         'ref_to': fields.char('Reference',store=True)
#     }