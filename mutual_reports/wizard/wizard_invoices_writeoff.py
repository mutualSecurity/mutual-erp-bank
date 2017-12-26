from openerp import models,fields,api
from openerp.osv import fields,osv
from datetime import date, timedelta,datetime


class WizardReports(osv.TransientModel):
    _name = 'wiz.invoices.writeoff'
    _description = 'PDF Reports for showing all disconnection,reconnection'

    _columns = {
        'date': fields.date('Invoice Date', required=True),
        'cheque_no': fields.char('Cheque No', required=True),
        'bank_code': fields.selection([('FBL', 'FBL'),
                                       ('JSBL', 'JSBL'),], required=True, string='Bank Code'),
        'invoice_amount': fields.float('Invoice Amount', required=True),
        'received_amount': fields.float('Received Amount', required=True)

    }

    def inv_status_changed(self,central,south,north,main):
        self.env.cr.execute("UPDATE account_invoice "
                            "SET state='cancel', payment_received=True,courier=True"
                            +",cheque_no='"+str(self.cheque_no)+"'"
                            +",comment='Payment has been received against parent invoice therefore user cancelled this invoice' "
                            "FROM res_partner WHERE account_invoice.partner_id = res_partner.id and account_invoice.state='draft' "
                            +"and res_partner.bank_code='"+str(self.bank_code)+"'"
                            +"and account_invoice.invoice_date='" + str(self.date) + "'"
                            +"and account_invoice.amount_total='"+str(self.invoice_amount)+"'"
                            +"and account_invoice.partner_id!='"+str(central)+"'"+ "and account_invoice.partner_id != '"+str(south)+"'"
                            +"and account_invoice.partner_id !='"+str(north)+"'"+"and account_invoice.partner_id !="+str(main))
        return True

    @api.one
    def inv_status_change_request(self):
        if self.bank_code == 'FBL':
            fbl_central = 9464
            fbl_south = 9522
            fbl_north = 9450
            fbl_main = 9572
            result = self.inv_status_changed(fbl_central,fbl_south,fbl_north,fbl_main)
            return result

        if self.bank_code == 'JSBL':
            jsbl_central = 11056
            jsbl_south = 11057
            jsbl_north = 11058
            jsbl_main = 3349
            result = self.inv_status_changed(jsbl_central,jsbl_south,jsbl_north,jsbl_main)
            return result

        raise osv.except_osv("Done........", "Records have been successfully updated")

