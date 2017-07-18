from openerp.osv import fields, osv
from openerp import api


class mutual_guard_tracking(osv.osv):
    _name = "mutual.guard.tracking"
    _columns = {
        'bank_code': fields.char('Bank Code', store=True, readonly=True,compute='fetch_details'),
        'branch_code': fields.char('Branch Code', store=True, readonly=True,compute='fetch_details'),
        'address': fields.char('Address', store=True, readonly=True,compute='fetch_details'),
        'city': fields.char('City', store=True, readonly=True,compute='fetch_details'),
        'visit_time': fields.char('Visit Time', store=True),
        'visit_date': fields.date('Visit Date', store=True),
        'card_no': fields.char('RF_ID', store=True),
        'device_no': fields.char('Device#', store=True),
        'force_code': fields.char('Force Code', store=True, readonly=True,compute='fetch_details'),
        'remarks': fields.char('Remarks', store=True),
        'archive_signal': fields.boolean('Status', store=True),
        'bank': fields.many2one('res.partner', 'Customer', store=True),
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