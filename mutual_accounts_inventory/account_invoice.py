from openerp.osv import fields, osv
from openerp import models
from openerp import fields as field
from openerp import api
from datetime import date, timedelta,datetime
import re
import calendar
import time
from dateutil.relativedelta import *
from openerp.tools import amount_to_text_en



class mutual_account_invoice(osv.osv):
    _inherit = 'account.invoice'

    _columns = {
        'cancel': fields.char('cancel',store=True,compute='delete_inventory_logs'),
    }

    def createLogs(self,line,customer,supplier):
        salecount=line.quantity if customer else 0.0
        purchasecount=line.quantity if supplier else 0.0
        self.env['inventory.logs'].create({
            'item_code': line.product_id.id,
            'item_name': line.product_id.name,
            'sale_count': salecount,
            'purchase_return': 0.0,
            'sale_return': 0.0,
            'purchase_count': purchasecount,
            'date': self.date_invoice,
            'inv_id': self.id,
        })

    def checkNeg(self,line):
        sale_rec=0
        open_rec=0
        self.env.cr.execute("select sum(sale_count) sales from inventory_logs where item_code =" + "'" + str(line.product_id.id) + "'")
        product_stock = self.env.cr.dictfetchall()
        if any(d['sales'] == None for d in product_stock):
            sale_rec=0
        else:
            for item in product_stock:
                sale_rec=item["sales"]
        self.env.cr.execute("select opening_count from inventory_opening where item_code=" + "'" + str(line.product_id.id) + "'" )
        opening_stock=self.env.cr.dictfetchall()
        for item in opening_stock:
            open_rec=item["opening_count"]
        remain_count=open_rec-(sale_rec+line.quantity)
        if(remain_count>=0):
            return 0
        else:
            return 1

    @api.multi
    def invoice_validate(self):
        for line in self.invoice_line:
            if(line.product_id.type != 'service'):
                if(self.partner_id.customer and self.checkNeg(line)==0):
                    self.createLogs(line,self.partner_id.customer,self.partner_id.supplier)
                elif(self.checkNeg(line)==0):
                    self.createLogs(line,self.partner_id.customer,self.partner_id.supplier)
                else:
                    raise osv.except_osv('Error....', 'product count might go into exceeding to negative')
        return self.write({'state': 'open'})

    @api.depends('state')
    def delete_inventory_logs(self):
        self.cancel = self.state
        if self.state == 'cancel':
            self.env.cr.execute("select * from inventory_logs where inv_id ="+ "'" + str(self.id)+"'")
            stock_moves = self.env.cr.dictfetchall()
            if(len(stock_moves)>0):
                self.env.cr.execute('Delete from inventory_logs WHERE inv_id='+ "'" + str(self.id)+"'")
