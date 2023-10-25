from odoo import api, fields, models
from odoo.exceptions import ValidationError
import logging

class CrmLead(models.Model):
    _inherit='crm.lead'

    #Many2many

    category_id = fields.Many2many('res.partner.category', string='Etiquetas',related='partner_id.category_id',readonly=False)


    #Boolean
    
    spo_shipment_date_risks_evaluation = fields.Date(string='Fecha de Envío a Evaluación en Comité de Riesgos')

    spo_result_date_risks_evaluation = fields.Date(string='Fecha de Resultado de Evaluación en Comité de Riesgos')
    
    spo_spo_risk_motive_aptos_bool = fields.Boolean(string='Motivo de Riesgo?')


    #Date
    spo_personal_interview_date = fields.Date(string='Fecha de Entrevista Personal')
    
    spo_evaluation_state = fields.Boolean(string='Estado de Evaluación Crediticia')

    spo_socioeconomic_evaluation_state = fields.Boolean(string='Estado de Evaluación Socioeconómica')
    
    spo_delivery_date_aditional_document = fields.Date(string='Fecha de Entrega de Documentos Adicionales')
    
    #Many2one
    
    l10n_pe_district = fields.Many2one(
        'l10n_pe.res.city.district', string='Distrito',
        help='Districts are part of a province or city.')

    spo_risk_motive_aptos_1_ids= fields.Many2one('spo.risk.motive.info', string='Motivo de Riesgo para Aptos en Comité 1')
    
    spo_risk_motive_aptos_2_ids= fields.Many2one('spo.risk.motive.info', string='Motivo de Riesgo para Aptos en Comité 2')
    
    spo_risk_motive_aptos_3_ids= fields.Many2one('spo.risk.motive.info', string='Motivo de Riesgo para Aptos en Comité 3')
    
    

    spo_state_1_id = fields.Many2one(comodel_name='spo.state.1.info', string='Estado De Entrevista Personal', )

    spo_state_2_id = fields.Many2one(comodel_name='spo.state.2.info', string='Estado De Entrega De Documentos Adicionales',)

    spo_state_3_id = fields.Many2one(comodel_name='spo.state.3.info', string='Estado De Evaluación Aptitudinal', )

    spo_state_4_id = fields.Many2one(comodel_name='spo.state.4.info', string='Resultado Preliminar Del Postulante',)
    
    spo_state_5_id = fields.Many2one(comodel_name='spo.state.5.info', string='Resultado Del Postulante Luego Del Comité',)

    spo_state_6_id = fields.Many2one(comodel_name='spo.state.6.info', string='Resultado Final De La Evaluación',)
    
    

