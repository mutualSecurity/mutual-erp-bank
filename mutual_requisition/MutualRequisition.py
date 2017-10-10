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
        'products': fields.one2many('basic.package.items', 'req_slip', 'Products',store=True, states={'confirmed': [('readonly', True)]}),
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
    def confrm_date(self, curr_req_slip_date):
        # print curr_req_slip_date
        self.env.cr.execute("select * from mutual_requisition where date ='"+str(curr_req_slip_date)+"'")
        chk_lst = self.env.cr.dictfetchall()
        if len(chk_lst) == 0 and self.counter != 8:
            self.counter += 1
            res = self.confrm_date(curr_req_slip_date-timedelta(days=1))
            return res
        else:
            return curr_req_slip_date

    @api.multi
    def validate(self):
        if not self.allow_req:
            alrt = ''
            rec_date = datetime.strptime(self.date, '%Y-%m-%d').date()
            date_list = [rec_date-timedelta(days=1), rec_date]
            self.counter=1
            date_list = [self.confrm_date(date_list[0]), date_list[1]]
            print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>MY DATE"
            print date_list
            all_req = self.get_reqslp_data(date_list)
            pattern1, pattern2 = '', ''
            for index, item in enumerate(all_req):
                # print item
                for item2 in all_req[index+1:]:
                    if item["id"] != item2["id"] and item["cs"] == item2["cs"] and item["cs"] is not None and item2["cs"] is not None and item["quantity"] == item2["quantity"] and item["name"] == item2["name"]:
                        if item["req_code"] is not None and item2["req_code"] is not None:
                            pattern1 = "(" + str(item["req_code"]) + "," + str(item2["req_code"]) + "),"
                            pattern2 = "(" + str(item2["req_code"]) + "," + str(item["req_code"]) + "),"
                        elif item["req_code"] is None and item2["req_code"] is not None:
                            pattern1 = "(" + str(item["id"]) + "," + str(item2["req_code"]) + "),"
                            pattern2 = "(" + str(item2["req_code"]) + "," + str(item["id"]) + "),"
                        elif item["req_code"] is not None and item2["req_code"] is None:
                            pattern1 = "(" + str(item2["id"]) + "," + str(item["req_code"]) + "),"
                            pattern2 = "(" + str(item["req_code"]) + "," + str(item2["id"]) + "),"
                        else:
                            pattern1 = "(" + str(item["id"]) + "," + str(item2["id"]) + "),"
                            pattern2 = "(" + str(item2["id"]) + "," + str(item["id"]) + "),"
                        if pattern1 not in alrt and pattern2 not in alrt:
                            alrt += pattern1
                        print pattern2,pattern1
                    elif item["id"] != item2["id"] and item["cs"] is None and item2["cs"] is None and item["quantity"] == item2["quantity"] and item["name"] == item2["name"] and item["partner_name"] == item2["partner_name"]:
                        if item["req_code"] is not None and item2["req_code"] is not None:
                            pattern1 = "(" + str(item["req_code"]) + "," + str(item2["req_code"]) + "),"
                            pattern2 = "(" + str(item2["req_code"]) + "," + str(item["req_code"]) + "),"
                        elif item["req_code"] is None and item2["req_code"] is not None:
                            pattern1 = "(" + str(item["id"]) + "," + str(item2["req_code"]) + "),"
                            pattern2 = "(" + str(item2["req_code"]) + "," + str(item["id"]) + "),"
                        elif item["req_code"] is not None and item2["req_code"] is None:
                            pattern1 = "(" + str(item2["id"]) + "," + str(item["req_code"]) + "),"
                            pattern2 = "(" + str(item["req_code"]) + "," + str(item2["id"]) + "),"
                        else:
                            pattern1 = "(" + str(item["id"]) + "," + str(item2["id"]) + "),"
                            pattern2 = "(" + str(item2["id"]) + "," + str(item["id"]) + "),"
                        if pattern1 not in alrt and pattern2 not in alrt:
                            alrt += pattern1
                        print pattern2,pattern1
            print pattern2 , pattern1
            for ind,item in enumerate(self.products):
                for item1 in self.products[ind+1:]:
                    if item.courier_sheet_products.name == item1.courier_sheet_products.name and item.quantity ==item1.quantity and item.cs_number ==item1.cs_number:
                        raise osv.except_osv(('Error'), ('Multiple entries in this requsition'))


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
        self.env.cr.execute("""select mr.id as id,mr.req_code as req_code,mr.allow_req as allow_req ,bp.quantity as quantity,bp.cs_number as cs,rp.name as partner_name,pi.name as name 
                                       from mutual_requisition mr
                                       inner join basic_package_items bp on mr.id=bp.req_slip
                                       inner join product_items pi on bp.courier_sheet_products=pi.id
                                       inner join res_partner rp on rp.id=bp.customer
                                       where mr.date in (""" + dv + ")")
        return self.env.cr.dictfetchall()
