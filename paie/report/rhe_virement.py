# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import time
from odoo import tools
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from odoo.osv import osv
from odoo.tools.enlettres import convlettres

class Report_virement(models.AbstractModel):
    _name = 'report.rhextend.report_virement'

    def _etat_virement(self,lot_id):
        cr = self.env.cr
        idlot = lot_id[0]
        requete = "WITH virements as " \
                  "(SELECT e.name as employe, c.codeg as cgui, b.name as banque, c.acc_number, c.rib, l.amount " \
                  "FROM hr_payslip_run r " \
                  "LEFT JOIN hr_payslip p " \
                  "ON p.payslip_run_id = r.id " \
                  "LEFT JOIN hr_payslip_line l " \
                  "ON l.slip_id = p.id " \
                  "LEFT JOIN hr_employee e " \
                  "ON p.employee_id = e.id " \
                  "LEFT JOIN res_partner_bank c " \
                  "ON c.id = e.cbank " \
                  "LEFT JOIN res_bank b " \
                  "ON b.id = c.bank_id " \
                  "WHERE r.id = "+str(idlot)+" " \
                  "AND l.code = 'NETPRET') " \
                  "(SELECT employe, cgui, banque, acc_number, rib, amount " \
                  "FROM virements " \
                  "ORDER BY employe) " \
                  "UNION ALL " \
                  "(SELECT 'TOTAL', null, null, null, null, sum(amount) " \
                  "FROM virements)"
        cr.execute(requete)
        vlines = cr.dictfetchall()
        return vlines

    def _etat_virementtot(self,lot_id):
        cr = self.env.cr
        idlot = lot_id[0]
        requete = "WITH virements as " \
                  "(SELECT e.name as employe, c.codeg as cgui, b.name as banque, c.acc_number, c.rib, l.amount " \
                  "FROM hr_payslip_run r " \
                  "LEFT JOIN hr_payslip p " \
                  "ON p.payslip_run_id = r.id " \
                  "LEFT JOIN hr_payslip_line l " \
                  "ON l.slip_id = p.id " \
                  "LEFT JOIN hr_employee e " \
                  "ON p.employee_id = e.id " \
                  "LEFT JOIN res_partner_bank c " \
                  "ON c.id = e.cbank " \
                  "LEFT JOIN res_bank b " \
                  "ON b.id = c.bank_id " \
                  "WHERE r.id = "+str(idlot)+" " \
                  "AND l.code = 'NETPRET') " \
                  "SELECT sum(amount) as totmontant FROM virements"
        cr.execute(requete)
        vtot = cr.fetchone()[0]
        #raise osv.except_osv(('Incoherence'), (vtot))
        return vtot
    def _get_banque(self,cbank):
        cr = self.env.cr
        requete = "SELECT b.name as banque " \
                  "FROM res_partner_bank p, res_bank b " \
                  "WHERE p.bank_id = b.id " \
                  "AND p.id = "+str(cbank)+""                 
        cr.execute(requete)
        banque = cr.fetchone()[0]
        return banque
    def _get_compte(self,cbank):
        cr = self.env.cr
        requete = "SELECT p.codeg||' '||p.acc_number||' '||p.rib as compte " \
                  "FROM res_partner_bank p " \
                  "WHERE p.id = "+str(cbank)+""                 
        cr.execute(requete)
        compte = cr.fetchone()[0]
        return compte
    @api.model
    def get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        vlines = self._etat_virement(data['form']['lot_id'])
        vtot = self._etat_virementtot(data['form']['lot_id'])
        vtotlettre = convlettres(vtot)
        banque = self._get_banque(data['form']['cbank'][0])
        compte = self._get_compte(data['form']['cbank'][0])
        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'vlines': vlines,
            'vtot': vtot,
            'vtotlettre' : vtotlettre,
            'banque' : banque,
            'compte' : compte,
        }