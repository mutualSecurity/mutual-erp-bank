#The file name of this file must match the filename name which we import in __init__.py file
# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp import api
from datetime import date,time

class mutual_requisition(osv.osv):
    _name = "mutual.requisition"
    _columns = {
        'title': fields.char('Title',store=True),
        'date':fields.date('Date',store=True),
        # 'receipt_no': fields.char('Reciept No',store=True),
        'products': fields.one2many('products.req','product_tb','Products',store=True),
        'req_type':fields.selection([('New Installation','New Installation'),('Faulty','Faulty'),('Additional','Additional'),('none',' ')],'Requsition Type')
    }
    _defaults={
        'req_type':'none',
    }

class products(osv.osv):
    _name = 'products.req'
    _columns = {
        'product_tb': fields.many2one('product.template','Products',store=True,required=True),
        'product_name': fields.many2one('product.template', 'Name', store=True,required=True),
        'quantity':fields.float('Quantity',store=True,required=True),
        'type': fields.selection([('For Technician', 'For Technician'), ('For Customer', 'For Customer')], 'Type', store=True),
        'customer':fields.many2one('res.partner','Customer',store=True),
        'ref_to':fields.char('Reference',store=True)
    }