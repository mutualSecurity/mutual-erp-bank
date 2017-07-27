from openerp import models,fields,api,_
from openerp.osv import fields,osv


class WizardMissingVisits(osv.TransientModel):
    _name = 'wiz.missing.visits'
    _description = 'Missing Visits Calculation'

    _columns = {
        'bank_code': fields.selection([('MBL','MBL'),
                                       ('SAMBA','SAMBA'),
                                       ('ABL','ABL'),
                                       ('UBL','UBL'),
                                       ('NBP','NBP'),
                                       ('HBL','HBL')],'Bank Code', required=True),
    }

    _defaults = {
        'bank_code': 'MBL'
    }

    @api.multi
    def createvisits(self):
        self.env.cr.execute(
            "select bank_code,branch_code,street,city,force_code,rf_id from res_partner where rf_id is not null and bank_code="+"'"+self.bank_code+"'"+" and rf_id not in (select card_no from mutual_guard_tracking where archive_signal is null and visit_time is not null)")
        missing_branches = self.env.cr.dictfetchall()

        self.env.cr.execute(
            "select visit_time,visit_time_two from mutual_guard_tracking where visit_time is null and visit_time_two is null and archive_signal is False and bank_code=" + "'" + self.bank_code + "'")
        missing_visits_created = self.env.cr.dictfetchall()

        print ">>>>>>>>>>>>>>>>>>>Missing Visits>>>>>>>>>>>>>>>>>>>>>"
        print len(missing_visits_created)
        if(len(missing_branches)>0):
            if(len(missing_visits_created)==0):
                for branch in missing_branches:
                    self.env['mutual.guard.tracking'].create({
                        'bank_code': branch['bank_code'],
                        'branch_code': branch['branch_code'],
                        'address': branch['street'],
                        'city': branch['city'],
                        'force_code': branch['force_code'],
                        'card_no': branch['rf_id']
                    })
            else:
                raise osv.except_osv('Alert.......', 'Missing visits has been already created')

        else:
            raise osv.except_osv('Alert.......', 'All branches have been first visited')
