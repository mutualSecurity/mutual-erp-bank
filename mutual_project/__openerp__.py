# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Issues and Tasks',
    'version': '1.1',
    'author':'Parkash and Hadi',
    'website': 'https://www.odoo.com/page/project-management',
    'category': 'Project Management',
    'sequence': 10,
    'summary': 'Projects, Tasks',
    'depends': [
        'base',
        'project_issue',
    ],
    'description': """
Track multi-level projects, tasks, work done on tasks
=====================================================

This application allows an operational project management system to organize your activities into tasks and plan the work you need to get the tasks completed.

Gantt diagrams will give you a graphical representation of your project plans, as well as resources availability and workload.

Dashboard / Reports for Project Management will include:
--------------------------------------------------------
* My Tasks
* Open Tasks
* Tasks Analysis
* Cumulative Flow
    """,
    'data': ['wizard/wizard_customer_inventory_view.xml',
             'wizard/wizard_technician_inventory_view.xml',
             'customer_inventory_report.xml',
             'technician_inventory_report.xml',
             'stock_return_view.xml',
             'faulty_devices_view.xml',
             'views/report_customer_inventory.xml',
             'views/report_technician_inventory.xml',
             'mutualprojects_view.xml',
             'views/project.xml',
             'data/scheduled_action_data.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
