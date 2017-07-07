from openerp.osv import fields, osv


class mutual_guard_tracking(osv.osv):
    _name = "mutual.guard.tracking"
    _columns = {
        'bank_code': fields.char('Bank Code', store=True, readonly=True),
        'branch_code': fields.char('Branch Code', store=True, readonly=True),
        'address': fields.char('Address', store=True, readonly=True),
        'city': fields.char('City', store=True),
        'visit_time': fields.char('Visit Time', store=True, readonly=True),
        'visit_date': fields.date('Visit Date', store=True, readonly=True),
        'card_no': fields.char('RF_ID', store=True),
        'device_no': fields.char('Device#', store=True),
        'force_code': fields.char('Force Code',store=True),
        'remarks': fields.char('Remarks',store=True),
        'archive_signal': fields.boolean('Status',store=True),

    }


class mutual_device_tracking(osv.osv):
    _name = "mutual.device.tracking"
    _columns = {
        'scanner_id': fields.char('Scanner ID', store=True),
        'force_id': fields.char('Force ID', store=True),
    }