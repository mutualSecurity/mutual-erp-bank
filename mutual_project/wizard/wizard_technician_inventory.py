from openerp import models,fields,api,_
from openerp.osv import fields,osv
from datetime import datetime, timedelta


class WizardTechnicianInventory(osv.TransientModel):
    _name = 'wiz.technician.inventory'
    _description = 'Generate Report for Technician Inventory'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Technician'),
        'all_rec': fields.boolean('Choose all Technician')
    }
    _default = {
        'all_rec': False,
    }

    def fetch_record(self):
        self.env.cr.execute("""select id from res_partner where is_technician=True""")
        all_part = self.env.cr.dictfetchall()
        all_id = ''
        for a in all_part:
            all_id += str(a["id"])+ ','

        if self.all_rec is False:
            self.env.cr.execute("""select sw.code,sw.partner_id,sq.product_id,pp.name_template,sum(sq.qty) as qty from stock_quant sq 
                                           inner join stock_location sl on sq.location_id=sl.id 
                                           inner join stock_warehouse sw on sl.id=sw.lot_stock_id
                                           inner join product_product pp on sq.product_id=pp.id
                                           where sq.qty>0 and sw.partner_id=""" + str(self.partner_id.id) + " group by sw.code,sw.partner_id,sq.product_id,pp.name_template")
            products = self.env.cr.dictfetchall()
            return self.create_prod_list(products, 1)
        else:
            self.env.cr.execute("""select sw.code,sw.partner_id,sq.product_id,pp.name_template,sum(sq.qty) as qty from stock_quant sq
                                           inner join stock_location sl on sq.location_id=sl.id
                                           inner join stock_warehouse sw on sl.id=sw.lot_stock_id
                                           inner join product_product pp on sq.product_id=pp.id
                                           where sq.qty>0 and sw.partner_id in (""" + all_id[:-1] + ")"+ " group by sw.code,sw.partner_id,sq.product_id,pp.name_template")
            products = self.env.cr.dictfetchall()
            return self.create_prod_list(products, 2)



    def create_prod_list(self,product,all_or_one):

        new_sort_list = sorted(product, key=lambda k: (k['partner_id'], k['product_id']))
        # for n in new_sort_list:
        tech_name = str(new_sort_list[0]['code'])
        tech_id = str(new_sort_list[0]['partner_id'])
        # print tech_name
        prodlist=[]
        return_list=[]
        # count = 1
        if all_or_one == 2:
            for index, prod1 in enumerate(new_sort_list):
                if len(prodlist) == 0:
                    prodlist.append(prod1)
                for prod2 in new_sort_list[index+1:]:
                    if tech_name == str(prod2["code"]) and prod2 not in prodlist:
                        # print "if name not equal"
                        prodlist.append(prod2)
                if tech_name != str(prod1['code']):
                    # count += 1
                    # print ">>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<"
                    # print tech_name
                    # print prodlist
                    # print ">>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<"
                    list = self.env['res.partner'].search([['id', '=', tech_id], ])
                    # print list.name,list.id
                    dict1 = {'name': list.name, 'designation':list.function, 'city':list.city, 'address':list.street, 'items': prodlist}
                    return_list.append(dict1)
                    tech_name = prod1['code']
                    tech_id=prod1['partner_id']
                    prodlist = []
                    # print ">>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<"
                    # print dict1
                    # print ">>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<"
            return return_list
            prodlist=[]
        elif all_or_one == 1:
            for item in new_sort_list:
                prodlist.append(item)
            list = self.env['res.partner'].search([['id', '=', tech_id], ])
            # print list.name,list.id
            dict1 = {'name': list.name, 'designation': list.function, 'city': list.city, 'address': list.street,
                     'items': prodlist}
            return_list.append(dict1)
            tech_name = item['code']
            tech_id = item['partner_id']
            return return_list


    def print_report(self, cr, uid, ids, data, context=None):
        return {
            'type': 'ir.actions.report.xml',
            'name': 'mutual_project.report_technician_inventory',
            'report_name': 'mutual_project.report_technician_inventory'
        }

