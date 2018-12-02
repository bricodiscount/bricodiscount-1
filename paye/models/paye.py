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
from datetime import timedelta




class hr_contract(models.Model):
    _name = 'hr.contract'
    _description = 'Contract'
    _inherit = "hr.contract"

    sursal = fields.Float("Sursalaire")
    pcaisse = fields.Float("Prime de caisse")
    pex = fields.Float("Prime exceptionelle")
    pnuit = fields.Float("Prime de nuit")
    pres = fields.Float("Prime de responsabilité")
    pex = fields.Float("Prime exceptionelle")
    aprime = fields.Float("Autre prime")
    indfor = fields.Float("Indemnité forfaitaire")

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

    def brouillon(self):
        self.write({'state': "draft"})

    @api.depends('date_to','contract_id.date_start')
    def get_anc(self):
        for record in self:
            if record.contract_id and record.date_to:
                #debut = datetime.strptime(record.contract_id.date_start+' 00:00','%Y-%m-%d %H:%M')
                #fin = datetime.strptime(record.date_to+' 00:00','%Y-%m-%d %H:%M')
                debut = record.contract_id.date_start
                fin = record.date_to
                record.ancannee = relativedelta(fin,debut).years
                record.ancmois = relativedelta(fin,debut).months
    @api.depends('line_ids.total','worked_days_line_ids.number_of_days','input_line_ids.amount')
    def get_rub(self):
        for record in self:
            netp = 0
            for recordfil in record.line_ids:
                if recordfil.code == 'SBRUT':
                   record.brutp = recordfil.total
                if recordfil.code == 'NETI':
                   netp = netp+recordfil.total
                if recordfil.code == 'COTSAL':
                   record.chargesalp = recordfil.total
                if recordfil.code == 'COTPAT':
                   record.chargepatp = recordfil.total
                if recordfil.code == 'SITS':
                   record.itsp = recordfil.total
                if recordfil.code == 'NET':
                   record.snetp = recordfil.total
            record.netp = netp
            for recordfill in record.worked_days_line_ids:
                if recordfill.code == 'WORK100':
                   record.heuretp = recordfill.number_of_hours
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
            #bula = self.env['hr.payslip'].search([('date_to','ilike',record.date_to[0:4]),('employee_id','=',record.employee_id.id)])
            bula = self.env['hr.payslip'].search([('date_to','ilike',record.date_to.year),('employee_id','=',record.employee_id.id)])
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
    snetp = fields.Float('Net', compute='get_rub', store = True)
    chargesalp = fields.Float('Charge salariale', compute='get_rub', store = True)
    chargepatp = fields.Float('Charge patronale', compute='get_rub', store = True)
    itsp = fields.Float('Impot traitement', compute='get_rub', store = True)
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



class Employee(models.Model):
    _name = "hr.employee"
    _description = "Employee"
    _inherit = "hr.employee"

    categorie = fields.Char('Catégorie')
    echelon = fields.Char('Echelon')
    secsoc = fields.Char('N° Sécurité sociale')

class hr_payslip_run(models.Model):
    _name = "hr.payslip.run"
    _description = "Lot de bulletin"
    _inherit = "hr.payslip.run"

    @api.depends('slip_ids.line_ids.total')
    def centralise(self):
        rd1 = 0
        rd2 = 0
        rdn = 0
        indf = 0
        cotsal = 0
        cotpat = 0
        src = 0
        sits = 0
        srm = 0
        sav = 0
        for record in self:
            for recordfil in record.slip_ids:
                for recordfill in recordfil.line_ids:
                    if recordfill.code in ['BSB','BSS','NHA','BHS','BCP']:
                       rd1 = rd1 + round(recordfill.total,0)
                for recordfill in recordfil.line_ids:
                    if recordfill.code in ['BPANC','BPC','BPN','BPRA','BPA','BPE']:
                       rd2 = rd2 + round(recordfill.total,0)
                for recordfill in recordfil.line_ids:
                    if recordfill.code in ['SINF']:
                       indf = indf + recordfill.total
                for recordfill in recordfil.line_ids:
                    if recordfill.code in ['COTSAL']:
                       cotsal = cotsal + round(recordfill.total,0)
                for recordfill in recordfil.line_ids:
                    if recordfill.code in ['COTPAT']:
                       cotpat = round(cotpat + recordfill.total,0)
                for recordfill in recordfil.line_ids:
                    if recordfill.code in ['SRC']:
                       src = src + round(recordfill.total,0)
                for recordfill in recordfil.line_ids:
                    if recordfill.code in ['SITS']:
                       sits = sits + round(recordfill.total,0)
                for recordfill in recordfil.line_ids:
                    if recordfill.code in ['SRM']:
                       srm = srm + round(recordfill.total,0)
                for recordfill in recordfil.line_ids:
                    if recordfill.code in ['SAV']:
                       sav = sav + round(recordfill.total,0)
                for recordfill in recordfil.line_ids:
                    if recordfill.code in ['NET']:
                       rdn = rdn + (round(recordfill.total/5,0))*5
            rdc = rd1+rd2+indf
            cnsss = cotsal
            cnssp = cotpat
            itsc = sits
            rdd = src + srm + sav
            record.rd1 = rd1
            record.rd2 = rd2
            record.indf = indf
            record.cotsal = cotsal
            record.cotpat = cotpat
            record.src = src
            record.sits = sits
            record.srm = srm
            record.sav = sav
            record.rdc = rdc
            record.rdd = rdd
            record.rdn = rdn
    def comptabiliser(self):
        am = self.env['account.move']
        aml = []
        company = self.env.user.company_id
        vals1 = {
                'account_id':company.salap.id,
                'name' : 'Salaires, Appointements',
                'debit': round(self.rdn+self.cotsal+self.sits+self.src+self.srm+self.sav-self.rd2-self.indf,0),
                'credit': 0,
                }
        aml.append((0, False, vals1))
        vals2 = {
                'account_id':company.prime.id,
                'name' : 'Primes et gratifications',
                'debit': round(self.rd2,0),
                'credit': 0,
                }
        aml.append((0, False, vals2))
        vals3 = {
                'account_id':company.ind.id,
                'name' : 'Indemintés et avantages divers',
                'debit': round(self.indf,0),
                'credit': 0,
                }
        aml.append((0, False, vals3))
        vals4 = {
                'account_id':company.cnsspat.id,
                'name' : 'Cotisation CNSS / Part patronale',
                'debit': round(self.cotpat,0),
                'credit': 0,
                }
        aml.append((0, False, vals4))
        vals5 = {
                'account_id':company.remdu.id,
                'name' : 'Remunération dûe / A verser',
                'debit': 0,
                'credit': round(self.rdn,0),
                }
        aml.append((0, False, vals5))
        vals6 = {
                'account_id':company.cnsssal.id,
                'name' : 'Cotisation CNSS / Part salariale',
                'debit': 0,
                'credit': round(self.cotsal,0),
                }
        aml.append((0, False, vals6))
        vals7 = {
                'account_id':company.cnsspatc.id,
                'name' : 'Cotisation CNSS / Part patronale',
                'debit': 0,
                'credit': round(self.cotpat,0),
                }
        aml.append((0, False, vals7))
        vals8 = {
                'account_id':company.impot.id,
                'name' : 'Impôts, Traitements et salaires',
                'debit': 0,
                'credit': round(self.sits,0),
                }
        aml.append((0, False, vals8))
        vals9 = {
                'account_id':company.retc.id,
                'name' : 'Retenue Cimetière',
                'debit': 0,
                'credit': round(self.src,0),
                }
        aml.append((0, False, vals9))
        vals10 = {
                'account_id':company.retachat.id,
                'name' : 'Retenue Achat Brico Discount',
                'debit': 0,
                'credit': round(self.srm,0),
                }
        aml.append((0, False, vals10))
        vals11 = {
                'account_id':company.avance.id,
                'name' : 'Avance et acompte',
                'debit': 0,
                'credit': round(self.sav,0),
                }
        aml.append((0, False, vals11))


        amc = am.create({'journal_id':company.journalpaie.id,'date':self.date_end,'ref':self.name})
        for record in amc:
            record.write({'line_ids':aml})
            #record.post()
        self.write({'compta':True})
        self.write({'move_id': amc.id})
        return True
    compta = fields.Boolean("Comptabilisé", default = False)
    move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True, copy=False)
    rd1 = fields.Float('Remunération base', compute='centralise', store=True)
    rd2 = fields.Float('Primes et gratifications', compute='centralise', store=True)
    indf = fields.Float('Indemnité forfaitaire', compute='centralise', store=True)
    cotsal = fields.Float('Cotisations salariales', compute='centralise', store=True)
    cotpat = fields.Float('Cotisations patronales', compute='centralise', store=True)
    src = fields.Float('Retenue CM', compute='centralise', store=True)
    sits = fields.Float('Impots traitement', compute='centralise', store=True)
    srm = fields.Float('Retenue Achat', compute='centralise', store=True)
    sav = fields.Float('Avance et acompte', compute='centralise', store=True)
    rdc = fields.Float('Remunération directe crediteur', compute='centralise', store=True)
    rdd = fields.Float('Remunération directe debiteur', compute='centralise', store=True)
    rdn = fields.Float('Remunération nette', compute='centralise', store=True)

class ResourceMixin(models.AbstractModel):
    _name = "resource.mixin"
    _description = 'Resource Mixin'
    _inherit = "resource.mixin"

    def get_work_days_data(self, from_datetime, to_datetime, calendar=None):
        #days_count = 0.0
        #total_work_time = timedelta()
        #calendar = calendar or self.resource_calendar_id
        #for day_intervals in calendar._iter_work_intervals(
        #        from_datetime, to_datetime, self.resource_id.id,
        #        compute_leaves=True):
        #    theoric_hours = self.get_day_work_hours_count(day_intervals[0][0].date(), calendar=calendar)
        #    work_time = sum((interval[1] - interval[0] for interval in day_intervals), timedelta())
        #    total_work_time += work_time
        #    if theoric_hours:
        #        days_count += float_utils.round((work_time.total_seconds() / 3600 / theoric_hours) * 4) / 4
        return {
            #'days': days_count,
            #'hours': total_work_time.total_seconds() / 3600,
            'days':30,
            'hours':208,
        }

class Company(models.Model):
    _name = "res.company"
    _description = 'Companies'
    _inherit = "res.company"

    journalpaie = fields.Many2one('account.journal',string='Journal des salaires')
    salap = fields.Many2one('account.account',string='Salaire et appointement')
    prime = fields.Many2one('account.account',string='Primes et gratifications')
    ind = fields.Many2one('account.account',string='Indemnités et avantages')
    cnsspat = fields.Many2one('account.account',string='CNSS Patronale Débit')
    cnsssal = fields.Many2one('account.account',string='CNSS Salariale')
    remdu = fields.Many2one('account.account',string='Rémunération dûe')
    cnsspatc = fields.Many2one('account.account',string='CNSS Patronale Crédit')
    impot = fields.Many2one('account.account',string='Impôts et traitements')
    retc = fields.Many2one('account.account',string='Retenue cimetière')
    retachat = fields.Many2one('account.account',string='Retenue achat')
    avance = fields.Many2one('account.account',string='Avances et acomptes')
