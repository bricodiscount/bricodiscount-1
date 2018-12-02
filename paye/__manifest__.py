# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'paye',
    'version' : '1.1',
    'summary': 'Permet de gérer la paie',
    'sequence': 180,
    'description': """
Gestion de la paie
====================
    """,
    'license': 'OPL-1',
    'author': 'HSN Consult',
    'category': 'Ressources humaines',
    'website': 'http://www.hsnconsult.com',
    'depends': ['hr','hr_contract','hr_payroll','resource','account'],
    'data': [
        'views/paye_view.xml',
        'views/paye_report.xml',
        'views/report_bulletin.xml',
        'views/report_rubrique.xml',
        'views/report_cnss.xml',
        'views/report_its.xml',
        'views/report_salarie.xml',
        'views/report_fiche.xml',
        ],
    'installable': True,
    'application': True,
    'auto_install': False
}
