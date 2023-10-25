from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # spo_academic_program_id = fields.Many2one('spo.academic.program.info', string='Programa Academico')
    # spo_Type_installment = fields.Selection(string='tipo de Cuota', selection=[('student', 'Estudiante'), ('graduate', 'Graduado'),('no', 'No Aplica')])
    
    