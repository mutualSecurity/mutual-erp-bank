# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from openerp.osv import fields, osv


class error_message_wizard(osv.TransientModel):
    _name = 'error.message.wizard'
    _description = 'Message wizard to display warnings, alert ,success messages'

    _columns = {
        'name': fields.text(string='Message'),
    }

    def get_default(self):
        if self.env.context.get("message", False):
            return self.env.context.get("message")
        return False

    _defaults = {
        'name': get_default,
    }

