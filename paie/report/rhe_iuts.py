# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError

class Report_iuts(models.AbstractModel):
    _name = 'report.rhextend.report_iuts'

    def _etat_iuts(self,lot_id):
        cr = self.env.cr
        idlot = lot_id[0]
        requete = "WITH ttotgain AS " \
                   "(SELECT p.employee_id as emp_id, l.amount as totgain " \
                   "FROM hr_payslip_run r, hr_payslip p, hr_payslip_line l " \
                   "WHERE l.slip_id = p.id " \
                   "AND p.payslip_run_id = r.id " \
                   "AND l.code = 'SBRUT' " \
                   "AND r.id = '"+str(idlot)+"'), " \
                   "tbi AS " \
                   "(SELECT p.employee_id as emp_id, l.amount as bi " \
                   "FROM hr_payslip_run r, hr_payslip p, hr_payslip_line l " \
                   "WHERE l.slip_id = p.id " \
                   "AND p.payslip_run_id = r.id " \
                   "AND l.code = 'BIUTS' " \
                   "AND r.id = '"+str(idlot)+"'), " \
                   "tiuts AS " \
                   "(SELECT p.employee_id as emp_id, l.amount as iuts " \
                   "FROM hr_payslip_run r, hr_payslip p, hr_payslip_line l " \
                   "WHERE l.slip_id = p.id " \
                   "AND p.payslip_run_id = r.id " \
                   "AND l.code = 'NIUTS' " \
                   "AND r.id = '"+str(idlot)+"'), " \
                   "res AS " \
                   "(SELECT e.name as nom, t.totgain as salbrut, b.bi, e.charges, i.iuts " \
                   "FROM hr_employee e " \
                   "LEFT JOIN ttotgain t " \
                   "ON e.id = t.emp_id " \
                   "LEFT JOIN tbi b " \
                   "ON e.id = b.emp_id " \
                   "LEFT JOIN tiuts i " \
                   "ON e.id = i.emp_id " \
                   "WHERE i.iuts is not null " \
                   "order by e.name) " \
                   "(SELECT row_number() over() as numordre, nom, salbrut, bi, charges, iuts " \
                   "FROM res) " \
                   "UNION " \
                   "(SELECT null, 'TOTAUX', sum(salbrut), sum(bi), sum(charges), sum(iuts) " \
                   "FROM res) " \
                   "ORDER BY numordre "
        cr.execute(requete)
        ilines = cr.dictfetchall()
        return ilines
    
    @api.model
    def get_report_values(self, docids, data=None):
        
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        
        ilines = self._etat_iuts(data['form']['lot_id'])
        
        return {
            'doc_ids': docids,
            'doc_model': self.model,
            'data': data,
            'docs': docs,
            'time': time,
            'ilines': ilines,
            'lot': data['form'].get('lot_nom'),
        }
        