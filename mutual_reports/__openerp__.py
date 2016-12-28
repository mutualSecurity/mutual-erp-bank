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
        'account',
        'mutual_sales',
        'mutual_project'
    ],
    'data': [
            'mutual_reports_reports.xml',
            'views/custom_layouts.xml',
            'views/report_acknowledgment_receipt.xml',
            'views/report_issue_pdf.xml',
            'views/report_task_pdf.xml',
            'views/report_history_pdf.xml',
            'views/summary_sheet_pdf.xml',
    ]

}