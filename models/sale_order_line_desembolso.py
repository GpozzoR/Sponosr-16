from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging
from datetime import date

class SaleOrderLineDesembolso(models.Model):
    _name = 'sale.order.line.desembolso'

    #Char
    spo_nro_desem = fields.Char(string='Nro')
    #Many2one
    sale_order_id = fields.Many2one('sale.order', string='Cronograma')
    relation_sale_order = fields.Many2one(comodel_name='sale.order', string='Orden de Venta')
    spo_doble_career = fields.Boolean(string='Doble Carrera')
    spo_academic_program_id = fields.Many2one(comodel_name='spo.academic.program.info', string='Programa Académico')
    #Selection
    spo_type_currency  = fields.Selection([
        ('pen', 'PEN'),('usd', 'USD')
    ], string='Moneda', default='pen')

    def getRate(self):
        res_currency_id = self.env['res.currency'].search([
            ('name','=','USD'),
            ('active','=',True)
            ], limit=1)
        if res_currency_id and res_currency_id.rate_ids:
            rate_day = res_currency_id.rate_ids.sorted('name', reverse=True)[:1]
            return rate_day.inverse_company_rate 
        else :return 0
    def chage_state(self):
        for rec in self:
            if rec.total_desembolso > 0:
                if rec.spo_currency == 'pen':
                    if rec.spo_import >= rec.total_desembolso:rec.spo_state_desembolso = 'paid'
                    elif rec.spo_date_give: 
                        if rec.spo_date_give < date.today():rec.spo_state_desembolso='late'
                        else:rec.spo_state_desembolso='not_paid'
                    else:rec.spo_state_desembolso='not_paid'
                elif rec.spo_currency == 'usd':
                    tipoCambio = self.getRate()
                    if (rec.spo_import *tipoCambio) >= rec.total_desembolso:rec.spo_state_desembolso = 'paid'
                    elif rec.spo_date_give: 
                        if rec.spo_date_give < date.today():rec.spo_state_desembolso='late'
                        else:rec.spo_state_desembolso='not_paid'
                    else:rec.spo_state_desembolso='not_paid'
                elif not rec.spo_currency:
                    if rec.spo_date_give: 
                        if rec.spo_date_give < date.today():rec.spo_state_desembolso='late'
                        else:rec.spo_state_desembolso='not_paid'
                    else:rec.spo_state_desembolso='not_paid'
            else:rec.spo_state_desembolso='not_paid'
    spo_state_desembolso = fields.Selection(string='Estado', selection=[('paid', 'Realizado'), ('late', 'Retrasado'),('not_paid','En Espera')], compute='chage_state')
    #Integer
    sponsor_promotion = fields.Integer(string='Promoción Sponsor %')
    @api.onchange('sponsor_promotion')
    def validation_length(self):
        list_vals=[]
        for rec in self:
            for vals in str(rec.sponsor_promotion):
                list_vals.append(vals)
            if len(list_vals) > 3:
                raise ValidationError('Error no puede ser mayor de tres dígitos')
    @api.depends('sponsor_promotion')
    def _display_promo(self):
        for rec in self:
            if rec.sponsor_promotion:rec.spo_display_promo = f'{rec.sponsor_promotion}-%'
            elif not rec.sponsor_promotion:rec.spo_display_promo = f' -%'
    spo_display_promo = fields.Char(string='Promoción', compute='_display_promo')
    Nro_credits = fields.Integer(string='Nro de Créditos Faltantes')
    #Float
    deuda_soles = fields.Float(string='Deuda en Soles')
    deuda_usd = fields.Float(string='Deuda en Dolares')
    cuota_matricula_soles = fields.Float(string='Cuota de Matrícula en soles')
    cuota_matricula_usd = fields.Float(string='Cuota de Matrícula en Dolares')
    cuota_pension_soles = fields.Float(string='Cuota de Pensión en Soles')
    cuota_pension_usd = fields.Float(string='Cuota de Pensión en Dolares')
    total_desembolso = fields.Float(string='Total Desembolso')
    spo_base_amount_pen = fields.Float(string='Monto Base Soles')
    spo_base_amount_usd = fields.Float(string='Monto Base Dolares')
    def _getVauesByCurrency(self):
        for rec in self:
            if rec.spo_type_currency == 'pen':
                rec.deuda = rec.deuda_soles
                rec.matri = rec.cuota_matricula_soles
                rec.pension = rec.cuota_pension_soles
                rec.base_amount = rec.spo_base_amount_pen
            elif rec.spo_type_currency == 'usd':
                rec.deuda = rec.deuda_usd
                rec.matri = rec.cuota_matricula_usd
                rec.pension = rec.cuota_pension_usd
                rec.base_amount = rec.spo_base_amount_usd
            else:
                rec.deuda = 0
                rec.matri = 0
                rec.pension = 0
                rec.base_amount = 0
    deuda  = fields.Float(string='Deuda',compute='_getVauesByCurrency')
    matri = fields.Float(string='Matrícula',compute='_getVauesByCurrency')
    pension = fields.Float(string='Pensión',compute='_getVauesByCurrency')
    base_amount = fields.Float(string='Monto Base',compute='_getVauesByCurrency')

    spo_import = fields.Float(string='Importe')
    spo_currency = fields.Selection(string='Moneda', selection=[('usd', 'USD'), ('pen', 'PEN'),], default='pen')
    spo_paid_date = fields.Date(string='Pagado')
    spo_memo = fields.Char(string='Memo')
    spo_diary = fields.Many2one(comodel_name='account.journal', string='Diario')
    spo_bancary_account = fields.Many2one(comodel_name='account.account', string='Cuenta Bancaria')
    def open_diario(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Asiento de Diarios',
            'res_model': 'account.journal',
            'domain': [('id','=',self.spo_diary.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }
    
    

    
    spo_date_give = fields.Date(string='Fecha de Entrega')
    @api.constrains('Nro_credits','deuda_soles','cuota_matricula_soles','cuota_pension_soles','deuda_usd','cuota_matricula_usd','cuota_pension_usd')
    def validate_desembolso(self):
        for record in self:
            if not record.spo_doble_career:
                if record.Nro_credits == 0.0 and record.deuda_soles == 0.0 and record.cuota_matricula_soles == 0.0 and record.cuota_pension_soles == 0.0 :
                    raise ValidationError('No se puede guardar el desembolso, Todos los campos se encunetran en cero.')
            elif record.spo_doble_career:
                if record.Nro_credits == 0.0 and record.deuda_soles == 0.0 and record.cuota_matricula_soles == 0.0 and record.cuota_pension_soles == 0.0 and record.deuda_usd == 0.0 and record.cuota_matricula_usd == 0.0 and record.cuota_pension_usd == 0.0 :
                    raise ValidationError('No se puede guardar el desembolso, Todos los campos se encuentran en cero.')
    
    # def change_state_desembolso(self):
    #     spo_final_date = None
    #     desembolso_ids = self.env['sale.order.line.desembolso'].search([])
    #     for desembolsos in desembolso_ids:
    #         cuota = self.env['sale.order.line'].search([('spo_final_date','<',str(date.today())),('order_id','=',desembolsos.sale_order_id.id),('spo_desembolso','=',desembolsos.total_desembolso)])
    #         logging.info(cuota)
    #         if cuota:
    #             logging.info('entró')
    #             desembolsos.write({'spo_state_desembolso':'late'})

