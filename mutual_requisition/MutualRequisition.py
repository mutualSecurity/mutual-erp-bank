#The file name of this file must match the filename name which we import in __init__.py file
# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp import api
from datetime import datetime,date,time,timedelta

class mutual_requisition(osv.osv):
    _name = "mutual.requisition"
    _columns = {
        'counter': fields.integer('Counter'),
        'allow_req':fields.boolean('Allow Requistion To Pass',store=True),
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
        'allow_req':False,
        'counter':0
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
    def cancel(self):
        return self.write({'state': 'draft'})

    # confirm the dates
    # def confrm_date(self, dt_list):
    #     dates = dt_list
    #     self.env.cr.execute("select * from mutual_requisition where date ='"+str(dates[0])+"'")
    #     chk_lst = self.env.cr.dictfetchall()
    #     print chk_lst
    #     dates = [dates[0], dates[1]]
    #     print dates
    #     if len(chk_lst) == 0:
    #         dates = [dates[0] - timedelta(days=1), dates[1]]
    #         self.counter += 1
    #         # print dates
    #         self.confrm_date(dates)
    #         return dates

    @api.multi
    def validate(self):
        if not self.allow_req:
            alrt = ''
            rec_date = datetime.strptime(self.date, '%Y-%m-%d').date()
            date_list = [rec_date-timedelta(days=1), rec_date]
            self.counter=1
            my_date = self.confrm_date(date_list)
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>MY DATE"
            print my_date
            all_req = self.get_reqslp_data(date_list)
            for index, item in enumerate(all_req):
                for item2 in all_req[index+1:]:
                    if item["id"] != item2["id"] and item["cs"] == item2["cs"] and item["cs"] is not None and item2["cs"] is not None:
                        pattern = "(" + str(item["id"]) + "," + str(item2["id"]) + ")"
                        print pattern
                        if pattern not in alrt:
                            alrt += "(" + str(item["id"]) + "," + str(item2["id"]) + "),"
            if alrt != '':
                alrt = alrt[:-1]
                raise osv.except_osv(('Error'), ('Duplicate entries exist at id' + alrt))
            else:
                return self.write({'state': 'confirmed'})
        else:
            return self.write({'state': 'confirmed'})


    # get all req using dates
    def get_reqslp_data(self, dt_lst):
        dv = ''
        for dt in dt_lst:
            dv += "'" + str(dt) + "'" + ','
        dv = dv[:-1]
        # print dv
        self.env.cr.execute("""select mr.id as id,bp.quantity as quantity,bp.cs_number as cs,pi.name as name from mutual_requisition mr
                                       inner join basic_package_items bp on mr.id=bp.req_slip
                                       inner join product_items pi on bp.courier_sheet_products=pi.id
                                       where mr.date in (""" + dv + ")")
        return self.env.cr.dictfetchall()
