from openerp.osv import fields, osv
from openerp import api
from datetime import date, timedelta, datetime


class smsLogs(osv.osv):
    _name = "sms.logs"
    _order = "sys_date desc"
    _columns = {
        'device_id':fields.char('Device ID',store=True),
        'card_id': fields.char('Card ID',store=True),
        'date': fields.char('Date',store=True),
        'time': fields.char('Time',store=True),
        'sys_date': fields.char('System Time',store=True),
    }


class mutual_guard_tracking(osv.osv):
    _name = "mutual.guard.tracking"
    _columns = {
        'bank_code': fields.char('Bank Code', store=True, readonly=True),
        'branch_code': fields.char('Branch Code', store=True, readonly=True),
        'address': fields.char('Address', store=True, readonly=True),
        'city': fields.char('City', store=True, readonly=True),
        'visit_time': fields.char('First Visit', store=True),
        'visit_time_two': fields.char('Second Visit', store=True),
        'visit_date': fields.date('Visit Date I', store=True),
        'visit_date_two': fields.date('Visit Date II', store=True),
        'card_no': fields.char('RF_ID', store=True),
        'device_no': fields.char('Device#', store=True),
        'force_code': fields.char('Force Code', store=True, readonly=True),
        'remarks': fields.char('Remarks', store=True),
        'archive_signal': fields.boolean('Status', store=True),
        'bank': fields.many2one('res.partner', 'Customer', store=True),
    }

    _defaults = {
        'visit_date': datetime.today(),
        'visit_date_two': datetime.today()
    }

    @api.one
    @api.depends('bank')
    def fetch_details(self):
        self.branch_code = self.bank.branch_code
        self.bank_code = self.bank.bank_code
        self.address = self.bank.street
        self.city = self.bank.city
        self.force_code = self.bank.force_code


class mutual_device_tracking(osv.osv):
    _name = "mutual.device.tracking"
    _columns = {
        'scanner_id': fields.char('Scanner ID', store=True),
        'force_id': fields.char('Force ID', store=True),
    }