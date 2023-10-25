from odoo import _, api, fields, models

class ProductAttributeValue(models.Model):
    _inherit='product.attribute.value'

    spo_miss_semester = fields.Many2many(comodel_name='spo.miss.semester',string='Semestres Pendientes')
