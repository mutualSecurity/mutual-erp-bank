{

    'name'  :   'Mutual Reporting',
    'summery'   :  'Custom Module for the all Reports',
    'description': """""",
    'author': "Team Emotive Labs",
    'category': '["mutual","Account", "projects"]',
    'website': "www.emotivelabs.ca",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Mutual',
    'version': '0.1',
    # any module necessary for this one to work correctly

    'depends':   [
        'sale',
        'account',
        'mutual_sale_discount_total',
        'mutual_sales',
        'mutual_project',
        'mutual_invoice'
    ],
    'data': [
            'mutual_reports_reports.xml',
            'views/mutual_header_footer.xml',
            'views/tax_break_up_invoice.xml',
            'views/wiz_recovery_report.xml',
            'views/custom_sales_tax_invoice_pdf.xml',
            'views/custom_report_mutual_stock_return_pdf.xml',
            'views/custom_courier_sheet_report.xml',
            'views/custom_report_mutual_req_pdf.xml',
            'views/custom_layouts.xml',
            'views/report_acknowledgment_receipt.xml',
            'views/report_issue_pdf.xml',
            'views/report_task_pdf.xml',
            'views/report_history_pdf.xml',
            'views/summary_sheet_pdf.xml',
            'views/technician_info_pdf.xml',
            'views/customer_biodata_pdf.xml',
            'views/custom_additional_invoice_pdf.xml',
            'views/custom_monitoring_invoice_pdf.xml',
            'wizard/wiz_recovery_report_view.xml',
            'wizard/wizard_invoices_writeoff_view.xml',
            'wiz_report_menuitem.xml',
            'wizard/wiz_report_selection.xml'

    ]
}