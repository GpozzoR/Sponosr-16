from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging
from datetime import datetime, date
import base64

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    spo_nro_cuota = fields.Integer(string='Nro')
    spo_nro_cuota_ident = fields.Char(string='Cuota')
    spo_semerter_cuota = fields.Char(string='Semestre')
    spo_emision_date = fields.Date(string='Fecha. Emisión')
    spo_final_date = fields.Date(string='Vencimiento')
    spo_desembolso = fields.Float(string='Desemb.')
    spo_capital = fields.Float(string='Capital')
    spo_interes = fields.Float(string='Interes')
    spo_amortizacion = fields.Float(string='Amort.')
    spo_costo_gestion = fields.Float(string='C. Gestion')
    spo_desgravamen = fields.Float(string='Desgr.')
    cuota_total = fields.Float(string='Total')
    spo_type_cuota = fields.Selection(string='Tipo. Cuota', selection=[('student', 'Estudiante'), ('graduate', 'Graduado'),('no', 'No Aplica')])
    payment_state = fields.Selection(string='Estado de Pago', selection=[('not_paid', 'No pagado'), ('create_pay','Pago Creado'),('paid', 'Pagado'),('late','Retrasado')])
    spo_import = fields.Float(string='Importe')
    spo_currency = fields.Selection(string='Moneda', selection=[('usd', 'USD'), ('pen', 'PEN'),], default='pen')
    spo_paid_date = fields.Date(string='Pagado')
    spo_memo = fields.Char(string='Memo')
    spo_diary = fields.Many2one(comodel_name='account.journal', string='Diario')
    spo_bancary_account = fields.Many2one(comodel_name='account.account', string='Cuenta Bancaria')
    def _get_cuota_related(self):
        for rec in self:
            if rec.order_id and rec.spo_nro_cuota_ident:
                rec.spo_cuota_related =f'{rec.order_id.name} - {rec.spo_nro_cuota_ident}'
            else:rec.spo_cuota_related =''
    spo_cuota_related = fields.Char(string='Cuota Relacionada', compute='_get_cuota_related')
    
    def open_payments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Recibos',
            'res_model': 'account.payment',
            'domain': [('spo_cuota_id','=',self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }
    spo_payments = fields.Integer(string="recibos")
    def open_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facturas',
            'res_model': 'account.move.line',
            'domain': [('spo_cuota_id','=',self.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }
    spo_count_recibo = fields.Integer(string='')
    spo_invoces = fields.Integer(string='Facturas')
    def open_diario(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Asiento de Diarios',
            'res_model': 'account.journal',
            'domain': [('id','=',self.spo_diary.id)],
            'view_mode': 'tree,form',
            'target': 'current',
        }
    
    def search_group(self):
        for rec in self:
            user = rec.env['res.users'].browse(rec._uid)
            desired_user_gr = user.has_group('sponsor_educative_credit.group_no_create_edit')
            if desired_user_gr:rec.groups = 'True'
            elif not desired_user_gr:rec.groups = 'False'
    groups = fields.Char(string='grupo',compute='search_group')


    """
        Método que busca los diferentes cuotas
    """
    def search_cuotas(self):
        #Busca todas las cutos del día de hoy 
        cuotasNotPaid = self.env['sale.order.line'].search([('spo_final_date','<=',str(date.today())),('payment_state','=','not_paid')])
        #Busca todas las cuotas pasadas de hoy
        cuotasCreatePaid = self.env['sale.order.line'].search([('spo_final_date','<',str(date.today())),('payment_state','=','create_pay')])
        #Busca todas las cuotas pagadas
        cuotasPaidError = self.env['sale.order.line'].search([('payment_state','=','paid')])
        return cuotasNotPaid, cuotasCreatePaid, cuotasPaidError
    """
        Metodo que cambia los estados de las cuetas
    """
    def change_state_cuota(self):
        payment = self.env['account.payment']
        cuotasNotPaid , cuotasCreatePaid, cuotasPaidError = self.search_cuotas()
        #Cambio de Estado si por error la pago es confirmado
        if cuotasPaidError:
            for cuotasValues in cuotasPaidError:
                #Validacion si existe un pago con esa cuota relacionada y que el pago esté en estado borrador
                validationPayment = payment.search([('spo_cuota_id','=',cuotasValues.id),('state','=','draft')])
                if validationPayment:
                    cuotasValues.write({'payment_state':'create_pay'})
                    if cuotasValues.spo_final_date < date.today():
                        cuotasValues.write({'payment_state':'late'})

        #Cambio de Estado de "Pago creado" a "Retrasado"
        if cuotasCreatePaid:
            for cuotasValues in cuotasCreatePaid:
                cuotasValues.write({'payment_state':'late'})
        
        #Cambio de Estado de "Pendiente" a "Pago creado"
        if cuotasNotPaid:
            for cuotasValues in cuotasNotPaid:
                validationPayment = payment.search([('spo_cuota_id','=',cuotasValues.id)])
                #Si existe
                if validationPayment:
                    cuotasValues.write({'payment_state':'create_pay'})
                    if cuotasValues.spo_final_date < date.today():
                        cuotasValues.write({'payment_state':'late'})
    """
        Método que crea los pago, envía lo recibos de pago a lo clientes y cambia el estado de las cuotas
    """
    def create_payment_cuota_and_send_email(self):
        payment = self.env['account.payment']
        #Busca todas las cutos del día de hoy 
        cuotasNotPaid , cuotasCreatePaid, cuotasPaidError = self.search_cuotas()
        #les crea un pago y le envía un reporte por mail
        if cuotasNotPaid:
            for cuotasValues in cuotasNotPaid:
                #Validacion si existe un pago con esa cuota relacionada
                validationPayment = payment.search([('spo_cuota_id','=',cuotasValues.id)])
                #Si no existe
                if not validationPayment:
                    #creacion del pago
                    payment_create =payment.create({
                        'state':'draft',
                        'amount':cuotasValues.cuota_total,
                        'date':date.today(),
                        'payment_type':'inbound',
                        'partner_id':cuotasValues.order_partner_id.id,
                        'spo_cuota_id':cuotasValues.id
                    })
                    #Renderizacion del report qweb
                    invoice_report = self.env.ref('sponsor_educative_credit.report_cuota_mail')
                    data_record = base64.b64encode(self.env['ir.actions.report'].sudo()._render_qweb_pdf(invoice_report, [cuotasValues.id], data=None)[0])
                    ir_values = {
                        'name': 'Recibo de Pago PDF' ,
                        'type': 'binary',
                        'datas': data_record,
                        'store_fname': data_record,
                        'mimetype': 'application/pdf',
                        'res_model': 'sale.order.line',
                    }
                    #Creacion del pdf a adjuntar
                    report_attachment_id = self.env['ir.attachment'].sudo().create(ir_values)
                    if report_attachment_id:
                        email_template = self.env.ref('sponsor_educative_credit.spo_mail_payment_template')
                        #Envío del mail con el pdf adjunto
                        email_template.attachment_ids = [(4, report_attachment_id.id)]
                        email_template.send_mail(cuotasValues.id, force_send=True)
                        email_template.attachment_ids = [(5, 0, 0)]
        self.change_state_cuota()

