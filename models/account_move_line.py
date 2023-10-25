from odoo import _, api, fields, models
from odoo.exceptions import ValidationError



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    spo_cuota_id  = fields.Many2one(comodel_name='sale.order.line', string='Cuota Relacionada')



