from odoo import _, api, fields, models
from datetime import date

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    spo_cuota_id  = fields.Many2one(comodel_name='sale.order.line', string='Cuota Relacionada')
    
    def action_post(self):
        res = super(AccountPayment, self).action_post()
        #Cambia el estado de la cuota de 'Pendiente' a 'Pago Creado'
        cuotas = self.env['sale.order.line'].search([('id','=',self.spo_cuota_id.id)])
        cuotas.write({'payment_state':'paid'})
        return res