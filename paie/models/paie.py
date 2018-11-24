# -*- coding: utf-8 -*-
import time
import math
from datetime import datetime
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta




class hr_contract(models.Model):
    _name = 'hr.contract'
    _description = 'Contract'
    _inherit = "hr.contract"

    cat_id = fields.Many2one('hr.employee.category', 'Catégorie')
    sursal = fields.Integer("Sursalaire")
    indlog = fields.Integer("Indemnité de logement")
    indfonc = fields.Integer("Indemnité de fonction")
    indtrans = fields.Integer("Indeminté de transport")
    indcai = fields.Integer("Indeminité de caisse")
    indpou = fields.Integer("Indeminité de poussière")
    indsuj = fields.Integer("Indeminité de sujetion")
    indresp = fields.Integer("Indeminité de responsabilité")
    indsal = fields.Integer("Indeminité de salissure")
    indfor = fields.Integer("Indeminité forfaitaire")
    indast = fields.Integer("Indeminité d\'astreinte")
    bruti = fields.Float("Brut initial")
    neti = fields.Float("Net imposable initial")
    chargesali = fields.Float("Charge sal. initial")
    chargepati = fields.Float("Charge pat. initial")
    heureti = fields.Float("Heures travaillés initial")
    heuresupi = fields.Float("Heures sup initial")
    congeaci = fields.Float("Congés acquis initial")
    congepi = fields.Float("Congés pris initial")


class hr_payslip_input(models.Model):
    _name = 'hr.payslip.input'
    _description = 'Inputs'
    _inherit = "hr.payslip.input"

    @api.onchange('codeav')
    def get_descentree(self):
        for record in self:
            record.name = record.codeav.name
            record.code = record.codeav.code


    codeav = fields.Many2one('hr.contract.advantage.template', 'Entrée', required=True)

class HrSalaryRule(models.Model):
    _name = 'hr.salary.rule'
    _description = 'Salary rule'
    _inherit = "hr.salary.rule"

    ref = fields.Char('Référence')

class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _description = 'Pay Slip'
    _inherit = "hr.payslip"

    @api.depends('date_to','contract_id.date_start')
    def get_anc(self):
        for record in self:
            if record.contract_id and record.date_to:
                debut = datetime.strptime(record.contract_id.date_start+' 00:00','%Y-%m-%d %H:%M')
                fin = datetime.strptime(record.date_to+' 00:00','%Y-%m-%d %H:%M')
                record.ancannee = relativedelta(fin,debut).years
                record.ancmois = relativedelta(fin,debut).months
    @api.depends('line_ids.total','worked_days_line_ids.number_of_days','input_line_ids.amount')
    def get_rub(self):
        for record in self:
            netp = 0
            for recordfil in record.line_ids:
                if recordfil.code == 'SBRUT':
                   record.brutp = recordfil.total
                if recordfil.code == 'BIUTS' or recordfil.code == 'BIUTSC':
                   netp = netp+recordfil.total
                if recordfil.code == 'CHARGESAL':
                   record.chargesalp = recordfil.total
                if recordfil.code == 'CHARGEPAT':
                   record.chargepatp = recordfil.total
            record.netp = netp
            for recordfill in record.worked_days_line_ids:
                if recordfill.code == 'WORK100':
                   record.heuretp = recordfill.number_of_days*173.33/30
            tothsup = 0
            for recordfilll in record.input_line_ids:
                if 'HSUP' in recordfilll.code:
                   tothsup = tothsup + recordfilll.amount
                if recordfilll.code == 'CONGEP':
                   record.congepp = recordfilll.amount 
                record.heuresupp = tothsup
            record.congeacp = 2.5
            record.congerestp = 0

    @api.depends('brutp','netp','chargesalp','chargepatp','heuretp','heuresupp','congeacp','congepp','congerestp')
    def get_ruba(self):
        for record in self:
            bula = self.env['hr.payslip'].search([('date_to','ilike',record.date_to[0:4]),('employee_id','=',record.employee_id.id)])
            bruta = record.contract_id.bruti
            neta = record.contract_id.neti
            chargesala = record.contract_id.chargesali
            chargepata = record.contract_id.chargepati
            heureta = record.contract_id.heureti
            heuresupa = record.contract_id.heuresupi
            congeaca = record.contract_id.congeaci
            congepa = record.contract_id.congepi
            congeresta = 0
            for recordf in bula:
                bruta = bruta+recordf.brutp
                neta = neta+recordf.netp
                chargesala = chargesala+recordf.chargesalp
                chargepata = chargepata+recordf.chargepatp
                heureta = heureta+recordf.heuretp
                heuresupa = heuresupa+recordf.heuresupp
                congeaca = congeaca+recordf.congeacp
                congepa = congepa+recordf.congepp
                congeresta = congeaca - congepa
                if congeresta < 0:
                   congeresta = 0 
            record.bruta = bruta
            record.neta = neta
            record.chargesala = chargesala
            record.chargepata = chargepata
            record.heureta = heureta
            record.heuresupa = heuresupa
            record.congeaca = congeaca
            record.congepa = congepa
            record.congeresta = congeresta
    ancannee = fields.Integer('Ancienneté années', compute='get_anc', store = True)
    ancmois = fields.Integer('Ancienneté mois', compute='get_anc', store = True)
    brutp = fields.Float('Brut Période', compute='get_rub', store = True)
    netp = fields.Float('Net imposable', compute='get_rub', store = True)
    chargesalp = fields.Float('Charge salariale', compute='get_rub', store = True)
    chargepatp = fields.Float('Charge patronale', compute='get_rub', store = True)
    heuretp = fields.Float('Heures travaillées', compute='get_rub', store = True)
    heuresupp = fields.Float('Heures sup', compute='get_rub', store = True)
    congeacp = fields.Float('Congés acquis', compute='get_rub', store = True)
    congepp = fields.Float('Congés pris', compute='get_rub', store = True)
    congerestp = fields.Float('Congés restant', compute='get_rub', store = True)
    bruta = fields.Float('Brut Année', compute='get_ruba', store = True)
    neta = fields.Float('Net imposable', compute='get_ruba', store = True)
    chargesala = fields.Float('Charge salariale', compute='get_ruba', store = True)
    chargepata = fields.Float('Charge patronale', compute='get_ruba', store = True)
    heureta = fields.Float('Heures travaillées', compute='get_ruba', store = True)
    heuresupa = fields.Float('Heures sup', compute='get_ruba', store = True)
    congeaca = fields.Float('Congés acquis', compute='get_ruba', store = True)
    congepa = fields.Float('Congés pris', compute='get_ruba', store = True)
    congeresta = fields.Float('Congés restant', compute='get_ruba', store = True)
    modep = fields.Selection([('Chèque','Chèque'),('Virement','Virement'),('Espèces','Espèces')],string='Mode de paiement', default='Chèque')
    datep = fields.Date('Date paiement')


class HrPayrollStructure(models.Model):
    _name = 'hr.payroll.structure'
    _description = 'Salary Structure'
    _inherit = "hr.payroll.structure"


    tauxa = fields.Selection([('25%','25%'),('20%','20%')], string = 'Taux abattement IUTS')

class Employee(models.Model):
    _name = "hr.employee"
    _description = "Employee"
    _inherit = "hr.employee"

    categorie = fields.Char('Catégorie')
    echelon = fields.Char('Echelon')
    secsoc = fields.Char('N° Sécurité sociale')
