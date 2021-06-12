from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import api
import re
import urllib
import urllib2
from xml.dom.minidom import parseString
import requests


class smsIntegration(osv.osv):
    _name = 'sms.integration'
    _rec_name = 'number'
    _columns = {
        'state': fields.selection([('draft', 'Not Confirmed'),
                ('done', 'Confirmed')], default='draft'),
        'customer_id': fields.char('Customer ID', required=True),
        'password': fields.char('Password', required=True),
        'mask': fields.char('Mask', required=True),
        'message': fields.text('Message', default='Hello World....!'),
        'number': fields.char('Number'),
        'message_type': fields.selection([('Transactional','Transactional'), ('Nontransactional','Non-Transactional')], string='Message Type')
    }

    def error_message(self, message):
        context = dict(self._context or {})
        context['message'] = message
        view_id = self.env['ir.model.data'].get_object_reference(
            'oc_ufone_sms_api_integration',
            'error_message_wizard')[1]

        return {
            'name': _('Message'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'error.message.wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }


    @api.multi
    def sent_message(self):
        ''' Sends post request to get session Id against username & password '''
        customer_id = urllib.unquote(self.customer_id).encode('utf8')
        number = urllib.unquote(self.number).encode('utf8')
        password = urllib.unquote(self.password).encode('utf8')
        message = urllib.unquote(self.message).encode('utf8')
        mask = urllib.unquote(self.mask).encode('utf8')
        message_type = urllib.unquote(self.message_type).encode('utf8')
        url = ("https://bsms.ufone.com/bsms_v8_api/sendapi-0.3.jsp?id=%s&message=%s&shortcode=%s&lang=English&mobilenum=%s&password=%s&groupname=&messagetype=%s"%(customer_id,message,mask,number,password,message_type))
        repsonse = requests.get(url,verify=False)
        result = parseString(repsonse.content).getElementsByTagName('response_text')[0].childNodes[0].data
        if 'Successful' in result:
            self.write({'state':'done'})
        return result


class SmsMain(osv.osv):
    _name = 'sms'
    _rec_name = 'message_body'

    _columns = {
        'state': fields.selection(
            [('sending', 'Sending'),
             ('fail', 'Failed'),('sent', 'Sent')],string='State', default='sending'),
        'mobile_no': fields.char('Mobile Number'),
        'message_body': fields.text('Message'),
        'sender_list': fields.many2many('res.partner', string='Sender List'),
        'reason': fields.char('Reason')
    }

    @api.multi
    def testMessage(self):
        sms_config = self.env['sms.integration'].search([])[0]
        ''' Sends post request to get session Id against username & password '''
        customer_id = urllib.unquote(sms_config.customer_id).encode('utf8')
        number = urllib.unquote(self.mobile_no).encode('utf8')
        password = urllib.unquote(sms_config.password).encode('utf8')
        message = urllib.unquote(self.message_body).encode('utf8')
        mask = urllib.unquote(sms_config.mask).encode('utf8')
        message_type = urllib.unquote(sms_config.message_type).encode('utf8')
        url = ("https://bsms.ufone.com/bsms_v8_api/sendapi-0.3.jsp?id=%s&message=%s&shortcode=%s&lang=English&mobilenum=%s&password=%s&groupname=&messagetype=%s" % (
                customer_id, message, mask, number, password, message_type))
        repsonse = requests.get(url, verify=False)
        result = parseString(repsonse.content).getElementsByTagName('response_text')[0].childNodes[0].data
        if 'Successful' in result:
            self.write({'state': 'sent', 'reason': result})
        else:
            self.write({'state': 'fail', 'reason': result})
        return result

    @api.multi
    def sendMessage(self,number,message):
        print(">>>>>>>>>>>>>>>>>>>>>>> SMS Service >>>>>>>>>>>>>>>>>>>>>>>>>")
        sms_config = self.env['sms.integration'].search([])[0]
        ''' Sends post request to get session Id against username & password '''
        customer_id = urllib.unquote(sms_config.customer_id).encode('utf8')
        number = urllib.unquote(number).encode('utf8')
        password = urllib.unquote(sms_config.password).encode('utf8')
        message = urllib.unquote(message).encode('utf8')
        mask = urllib.unquote(sms_config.mask).encode('utf8')
        message_type = urllib.unquote(sms_config.message_type).encode('utf8')
        url = ("https://bsms.ufone.com/bsms_v8_api/sendapi-0.3.jsp?id=%s&message=%s&shortcode=%s&lang=English&mobilenum=%s&password=%s&groupname=&messagetype=%s" % (
            customer_id, message, mask, number, password, message_type))
        repsonse = requests.get(url, verify=False)
        result = parseString(repsonse.content).getElementsByTagName('response_text')[0].childNodes[0].data
        if 'Successful' in result:
            self.write({'state': 'sent', 'reason':result})
            self.env.cr.commit()
            print(">>>>>>>>>>>>>>>>>>>>>>> Message Sent >>>>>>>>>>>>>>>>>>>>>>>>>")
        else:
            self.write({'state': 'fail', 'reason':result})
            self.env.cr.commit()
        return result

    def auto_send_message(self, cr, uid, context=None):
        messages = self.search(cr, uid, [('state','=', 'sending')])
        for message in self.browse(cr, uid, messages, context=context):
            print(">>>>>>>>>>>>>>>>>>>>>>> Sending Message >>>>>>>>>>>>>>>>>>>>>>>>>")
            message.sendMessage(message.mobile_no,message.message_body)
