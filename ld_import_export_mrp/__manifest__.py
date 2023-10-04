# -*- coding: utf-8 -*-
{
    'name': "MRP Yield Calculation",
    'summary': "MRP Yield Calculation",
    'description': "MRP Yield Calculation",
    'author': "Live digital marketing solutions pvt ltd",
    'website' : "https://www.ldtech.in/",
    'category': 'MRP',
    'version': '16.0.1',
    'depends': ['base','mrp', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/mrp_view.xml',
        'views/yield_report.xml',
        'views/batch_yield_report.xml',
        'views/mrp_batch_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
