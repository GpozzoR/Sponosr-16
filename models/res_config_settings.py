from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    
    spo_CGS_value = fields.Float(string='COSTO DE GESTION EN SOLES', digits=(2, 2),)

    spo_TD_value = fields.Float(string='TASA DE SEGURO DE DESGRAVAMEN %', digits=(2, 3),)

    spo_TIA_value = fields.Float(string='TASA DE INTERES ANUAL %', digits=(2, 2),)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            spo_CGS_value = self.env['ir.config_parameter'].sudo().get_param('sponsor_educative_credit.spo_CGS_value'),
            spo_TD_value = self.env['ir.config_parameter'].sudo().get_param('sponsor_educative_credit.spo_TD_value'),
            spo_TIA_value = self.env['ir.config_parameter'].sudo().get_param('sponsor_educative_credit.spo_TIA_value'),

        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        spo_CGS_value_s = self.spo_CGS_value and self.spo_CGS_value or False
        spo_TD_value_s = self.spo_TD_value and self.spo_TD_value or False
        spo_TIA_value_s = self.spo_TIA_value and self.spo_TIA_value or False
        

        param.set_param('sponsor_educative_credit.spo_CGS_value', spo_CGS_value_s)
        param.set_param('sponsor_educative_credit.spo_TD_value', spo_TD_value_s)
        param.set_param('sponsor_educative_credit.spo_TIA_value', spo_TIA_value_s)


