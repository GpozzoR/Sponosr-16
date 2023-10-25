from datetime import date, datetime
import datetime
from odoo import _, api, fields, models
import logging


class SpoReportCuota(models.TransientModel):
    _name = 'spo.report.cuota'

    cuota_id = fields.Many2one('sale.order.line', string='Cuota')
    order_id  = fields.Many2one(comodel_name='sale.order', string='Contrato', related='cuota_id.order_id')
    order_partner_id = fields.Many2one(comodel_name='res.partner', string='Cliente', related='cuota_id.order_partner_id')
    
    """
        Funcion para imprimir pdf
    """
    
    def print_cuota_report(self):
        data = {
            'model': 'spo.report.cuota',
            'id': self.cuota_id.id ,
            'order':self.order_id.id,
            'customer':self.order_partner_id.id
        }
        return self.env.ref('sponsor_educative_credit.report_cuota_wizard').report_action(self, data=data)
    


class ReportCuota(models.AbstractModel):
    _name = 'report.sponsor_educative_credit.report_cuota_wizard_template'

    """
        obtenemos lo los valores del reporte y returnamos un diccionario con la llave 'data' el cual nos trae todo la informacion al reporte 
    """
    @api.model
    def _get_report_values(self, docids, data=None):
        cuota = self.env['sale.order.line'].sudo().browse(data.get('id'))
        order = self.env['sale.order'].sudo().browse(data.get('order'))
        customer = self.env['res.partner'].sudo().browse(data.get('customer'))
        company_external_id = self.env.ref('base.main_partner').id
        company = self.env['res.partner'].sudo().browse(company_external_id)
        cuota_list = []
        for info_cuota in cuota:
            #Diccionario de Valores adicionales
            vals = {
                'order':order.name,
                'customer':customer.name,
                'customer_vat':customer.spo_display_doc,
                'customer_phone':customer.phone,
                'customer_email':customer.email,
                'company':company.name,
                'company_vat':company.spo_display_doc,
                'company_phone':company.phone,
                'company_email':company.email,
                'spo_nro_cuota_ident': info_cuota.spo_nro_cuota_ident,
                'emision_date': info_cuota.spo_emision_date,
                'cuota_value': info_cuota.name,
                'gestion_cost': round(info_cuota.spo_costo_gestion, 2),
                'desgravamen': round(info_cuota.spo_desgravamen, 2),
                'cuota_value_total':round( info_cuota.cuota_total, 2),
                'final_date': info_cuota.spo_final_date,
            }
            cuota_list.append(vals)
        return {
            'doc_ids' : docids,
            'doc_model' : self.env['sale.order.line'],
            'data' : cuota_list,
            'docs': self.env['sale.order.line'].sudo().browse(data.get('id'))
        }