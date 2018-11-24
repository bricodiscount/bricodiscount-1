# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'paie',
    'version' : '1.1',
    'summary': 'Permet de gérer la paie',
    'sequence': 180,
    'description': """
Gestion de la paie
====================
    """,
    'category': 'Ressources humaines',
    'website': 'http://www.hsnconsult.com',
    'depends': ['hr','hr_contract','hr_payroll',],
    'data': [
        'views/paie_view.xml',
        'views/paie_report.xml',
        'views/report_bulletin.xml',
        ],
    'installable': True,
    'application': True,
    'auto_install': False
}
