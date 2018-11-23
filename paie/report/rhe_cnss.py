# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import time
from odoo import api, models

class Report_cnss(models.AbstractModel):
    _name = 'report.rhextend.report_cnss'

    def _etat_cnss(self,lot_ids):
        cr = self.env.cr
        res = tuple(lot_ids)
        requete = "WITH tcnss AS " \
                   "(SELECT p.employee_id as emp_id, round(sum(l.amount/0.055)) as basecnss " \
                   "FROM hr_payslip_run r, hr_payslip p, hr_payslip_line l " \
                   "WHERE l.slip_id = p.id " \
                   "AND p.payslip_run_id = r.id " \
                   "AND l.code = 'CNSS' " \
                   "AND r.id in %s " \
                   "GROUP BY p.employee_id), " \
                   "res AS " \
                   "(SELECT e.name as nom, e.identification_id as imat, c.basecnss " \
                   "FROM hr_employee e " \
                   "LEFT JOIN tcnss c " \
                   "ON e.id = c.emp_id " \
                   "WHERE c.basecnss is not null " \
                   "order by e.name) " \
                   "(SELECT row_number() over() as numordre, nom, imat, basecnss " \
                   "FROM res) "
        cr.execute(requete,(res,))
        clines = cr.dictfetchall()
        return clines
    def _etat_totcnss(self,lot_ids):
        cr = self.env.cr
        res = tuple(lot_ids)
        requete = "WITH tcnss AS " \
                   "(SELECT p.employee_id as emp_id, round(sum(l.amount/0.055)) as basecnss " \
                   "FROM hr_payslip_run r, hr_payslip p, hr_payslip_line l " \
                   "WHERE l.slip_id = p.id " \
                   "AND p.payslip_run_id = r.id " \
                   "AND l.code = 'CNSS' " \
                   "AND r.id in %s " \
                   "GROUP BY p.employee_id) " \
                   "SELECT sum(basecnss)as totbasecnss, round(sum(basecnss)*0.215) as totcnss " \
                   "FROM tcnss "
        cr.execute(requete,(res,))
        clines = cr.dictfetchall()
        return clines
    def _get_debut(self,lot_ids):
        cr = self.env.cr
        res = tuple(lot_ids)
        requete = "SELECT to_char(min(date_start),'dd-mm-yyyy')" \
                  "FROM hr_payslip_run " \
                  "WHERE id in %s "
        cr.execute(requete,(res,))
        debut = cr.fetchone()[0]
        if debut is not None:
            result = debut
        else:
            result=""
        return result
    def _get_fin(self,lot_ids):
        cr = self.env.cr
        res = tuple(lot_ids)
        requete = "SELECT to_char(max(date_end),'dd-mm-yyy')" \
                  "FROM hr_payslip_run " \
                  "WHERE id in %s "
        cr.execute(requete,(res,))
        fin = cr.fetchone()[0]
        if fin is not None:
            result = fin
        else:
            result=""
        return result
    @api.model
    def get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        clines = self._etat_cnss(data['form']['lot_ids'])
        tclines = self._etat_totcnss(data['form']['lot_ids'])
        debut = self._get_debut(data['form']['lot_ids'])
        fin = self._get_fin(data['form']['lot_ids'])
        return{
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'clines': clines,
            'tclines': tclines,
            'debut': debut,
            'fin': fin,
        }