# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import time
from odoo import api, models

class Report_rubsal(models.AbstractModel):
    _name = 'report.rhextend.report_rubsal'

    def _etat_rubsal(self,lot_ids):
        cr = self.env.cr
        res = tuple(lot_ids)
        requete = "WITH base AS " \
                   "(SELECT p.employee_id as emp_id, sum(l.amount) as base " \
                   "FROM hr_payslip_run r, hr_payslip p, hr_payslip_line l " \
                   "WHERE l.slip_id = p.id " \
                   "AND p.payslip_run_id = r.id " \
                   "AND l.code = 'SBASE' " \
                   "AND r.id in %s " \
                   "GROUP BY p.employee_id), " \
                   "transport AS " \
                   "(SELECT p.employee_id as emp_id, sum(l.amount) as transport " \
                   "FROM hr_payslip_run r, hr_payslip p, hr_payslip_line l " \
                   "WHERE l.slip_id = p.id " \
                   "AND p.payslip_run_id = r.id " \
                   "AND l.code = 'ITRANS' " \
                   "AND r.id in %s " \
                   "GROUP BY p.employee_id), " \
                   "fonction AS " \
                   "(SELECT p.employee_id as emp_id, sum(l.amount) as fonction " \
                   "FROM hr_payslip_run r, hr_payslip p, hr_payslip_line l " \
                   "WHERE l.slip_id = p.id " \
                   "AND p.payslip_run_id = r.id " \
                   "AND l.code = 'IFONC' " \
                   "AND r.id in %s " \
                   "GROUP BY p.employee_id), " \
                   "logement AS " \
                   "(SELECT p.employee_id as emp_id, sum(l.amount) as logement " \
                   "FROM hr_payslip_run r, hr_payslip p, hr_payslip_line l " \
                   "WHERE l.slip_id = p.id " \
                   "AND p.payslip_run_id = r.id " \
                   "AND l.code = 'ILOG' " \
                   "AND r.id in %s " \
                   "GROUP BY p.employee_id), " \
                   "brut AS " \
                   "(SELECT p.employee_id as emp_id, sum(l.amount) as brut " \
                   "FROM hr_payslip_run r, hr_payslip p, hr_payslip_line l " \
                   "WHERE l.slip_id = p.id " \
                   "AND p.payslip_run_id = r.id " \
                   "AND l.code = 'SBRUT' " \
                   "AND r.id in %s " \
                   "GROUP BY p.employee_id), " \
                   "cnss AS " \
                   "(SELECT p.employee_id as emp_id, sum(l.amount) as cnss " \
                   "FROM hr_payslip_run r, hr_payslip p, hr_payslip_line l " \
                   "WHERE l.slip_id = p.id " \
                   "AND p.payslip_run_id = r.id " \
                   "AND l.code = 'CNSS' " \
                   "AND r.id in %s " \
                   "GROUP BY p.employee_id), " \
                   "iuts AS " \
                   "(SELECT p.employee_id as emp_id, sum(l.amount) as iuts " \
                   "FROM hr_payslip_run r, hr_payslip p, hr_payslip_line l " \
                   "WHERE l.slip_id = p.id " \
                   "AND p.payslip_run_id = r.id " \
                   "AND l.code = 'NIUTS' " \
                   "AND r.id in %s " \
                   "GROUP BY p.employee_id), " \
                   "remb AS " \
                   "(SELECT p.employee_id as emp_id, sum(l.amount) as remb " \
                   "FROM hr_payslip_run r, hr_payslip p, hr_payslip_line l " \
                   "WHERE l.slip_id = p.id " \
                   "AND p.payslip_run_id = r.id " \
                   "AND l.code = 'REMB' " \
                   "AND r.id in %s " \
                   "GROUP BY p.employee_id), " \
                   "net AS " \
                   "(SELECT p.employee_id as emp_id, sum(l.amount) as snet " \
                   "FROM hr_payslip_run r, hr_payslip p, hr_payslip_line l " \
                   "WHERE l.slip_id = p.id " \
                   "AND p.payslip_run_id = r.id " \
                   "AND l.code = 'SNET' " \
                   "AND r.id in %s " \
                   "GROUP BY p.employee_id), " \
                   "sursal as " \
                   "(SELECT n.emp_id, n.snet-b.base as sursal " \
                   "FROM net n, base b " \
                   "WHERE n.emp_id = b.emp_id), " \
                   "cnssemp as " \
                   "(SELECT emp_id, round(cnss*0.16/0.055) as cnsse " \
                   "FROM cnss), " \
                   "res AS " \
                   "(SELECT e.name as nom, b.base, t.transport, f.fonction, l.logement, s.sursal, sb.brut, c.cnss, ce.cnsse, i.iuts, r.remb, n.snet " \
                   "FROM hr_employee e " \
                   "JOIN base b " \
                   "ON e.id = b.emp_id " \
                   "LEFT JOIN transport t " \
                   "ON e.id = t.emp_id " \
                   "LEFT JOIN fonction f " \
                   "ON e.id = f.emp_id " \
                   "LEFT JOIN logement l " \
                   "ON e.id = l.emp_id " \
                   "LEFT JOIN sursal s " \
                   "ON e.id = s.emp_id " \
                   "LEFT JOIN brut sb " \
                   "ON e.id = sb.emp_id " \
                   "LEFT JOIN cnss c " \
                   "ON e.id = c.emp_id " \
                   "LEFT JOIN cnssemp ce " \
                   "ON e.id = ce.emp_id " \
                   "LEFT JOIN iuts i " \
                   "ON e.id = i.emp_id " \
                   "LEFT JOIN remb r " \
                   "ON e.id = r.emp_id " \
                   "LEFT JOIN net n " \
                   "ON e.id = n.emp_id) " \
                   "(SELECT nom, base, transport, fonction, logement, sursal, brut, cnss, cnsse, iuts, remb, snet " \
                   "FROM res) " \
                   "UNION ALL " \
                   "(SELECT 'TOTAL', sum(base), sum(transport), sum(fonction), sum(logement), sum(sursal), sum(brut), sum(cnss), sum(cnsse), sum(iuts), sum(remb), sum(snet) " \
                   "FROM res)"
        cr.execute(requete,(res,res,res,res,res,res,res,res,res,))
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
        clines = self._etat_rubsal(data['form']['lot_ids'])
        debut = self._get_debut(data['form']['lot_ids'])
        fin = self._get_fin(data['form']['lot_ids'])
        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'clines': clines,
            'debut': debut,
            'fin': fin,
        }