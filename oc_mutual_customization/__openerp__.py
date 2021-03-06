
# -*- coding: utf-8 -*-
#################################################################################
# Author      : Odoo Concepts. (<www.odooconcepts.com>)
# Copyright(c): 2019-Present Odoo Concepts.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'Mutual Customization',
    'author': 'Odoo Concepts',
    'summary': 'Add source document and invoice id on invoice tree view',
    'depends': ['base', 'account','sale','mutual_sales','mutual_reports','mutual_accounts_inventory'],
    'data': ['views/account_invoice_view.xml','reports/cp_report_temp.xml','reports/cp_report.xml'],
    'category': '',
    'website': "https//:www.odooconcepts.com",
    'installable': True,
    'auto_install': False,
}
