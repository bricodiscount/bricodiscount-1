# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class rhe_iuts_report(models.TransientModel):
    _name = "rhe.iuts.report"
    _description = "IUTS du mois"

    lot_id = fields.Many2one('hr.payslip.run', 'Période', required=True)
    date_cour = fields.Date('date impression', default=fields.Date.context_today)

    def _build_contexts(self, data):
        result = {}
        result['lot_id'] = data['form']['lot_id'] or False
        result['date_cour'] = data['form']['date_cour'] or False
        return result

    def _print_report(self, data):
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env.ref('rhextend.action_report_iuts').report_action(self, data=data)

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['lot_id', 'date_cour'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'fr_FR'))
        return self._print_report(data)

class rhe_cnss_report(models.TransientModel):
    _name = "rhe.cnss.report"
    _description = "cnss"

    lot_ids = fields.Many2many('hr.payslip.run', 'payslip_runc_rel', 'cnss_id', 'lot_id', 'Périodes', required=True)
    date_cour = fields.Date('date impression', default=fields.Date.context_today)

    def _build_contexts(self, data):
        result = {}
        result['lot_ids'] = data['form']['lot_ids'] or False
        result['date_cour'] = data['form']['date_cour'] or False
        return result

    def _print_report(self, data):
        records = self.env[data['model']].browse(data.get('ids', []))
        #return self.env['report'].with_context(landscape=False).get_action(records, 'rhe.report_cnss', data=data)
        return self.env.ref('rhextend.action_report_cnss').report_action(self, data=data, config=False)

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['lot_ids', 'date_cour'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'fr_FR'))
        return self._print_report(data)
class rhe_rubsal_report(models.TransientModel):
    _name = "rhe.rubsal.report"
    _description = "rubsal"

    lot_ids = fields.Many2many('hr.payslip.run', 'payslip_runr_rel', 'rubsal_id', 'lot_id', 'Périodes', required=True)
    date_cour = fields.Date('date impression', default=fields.Date.context_today)

    def _build_contexts(self, data):
        result = {}
        result['lot_ids'] = data['form']['lot_ids'] or False
        result['date_cour'] = data['form']['date_cour'] or False
        return result

    def _print_report(self, data):
        records = self.env[data['model']].browse(data.get('ids', []))
        #return self.env['report'].with_context(landscape=False).get_action(records, 'rhe.report_rubsal', data=data)
        return self.env.ref('rhextend.action_report_rubsal').with_context(landscape=True).report_action(self, data=data, config=False)

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['lot_ids', 'date_cour'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'fr_FR'))
        return self._print_report(data)

class rhe_virement_report(models.TransientModel):
    _name = "rhe.virement.report"
    _description = "virement du mois"

    dateordre = fields.Date('Date', default=fields.Date.context_today, required=True)
    lot_id = fields.Many2one('hr.payslip.run', 'Période', required=True)
    cbank = fields.Many2one('res.partner.bank','Compte Banque', required=True)
    date_cour = fields.Date('date impression', default=fields.Date.context_today)

    def _build_contexts(self, data):
        result = {}
        result['lot_id'] = data['form']['lot_id'] or False
        result['dateordre'] = data['form']['dateordre'] or False
        result['cbank'] = data['form']['cbank'] or False
        result['date_cour'] = data['form']['date_cour'] or False
        return result

    def _print_report(self, data):
        records = self.env[data['model']].browse(data.get('ids', []))
        #return self.env['report'].with_context(landscape=False).get_action(records, 'rhe.report_virement', data=data)
        return self.env.ref('rhextend.action_report_virement').report_action(self, data=data, config=False)

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['lot_id', 'date_cour', 'dateordre', 'cbank'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'fr_FR'))
        return self._print_report(data)