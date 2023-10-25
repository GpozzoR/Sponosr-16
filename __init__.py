# -*- coding: utf-8 -*-
import logging
from . import controllers
from . import models
from . import wizards
# from . import reports
from odoo import api, SUPERUSER_ID


def value_params(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    val1= env['ir.config_parameter'].search([('key','=','sponsor_educative_credit.spo_CGS_value')])
    if val1:
        val1.write({
            'value': 40.00,
        })
    else:
        env['ir.config_parameter'].create({
            'key':'sponsor_educative_credit.spo_CGS_value',
            'value': 40.00,
        })
    val2= env['ir.config_parameter'].search([('key','=','sponsor_educative_credit.spo_TD_value')])
    if val2:
        val2.write({
            'value': 0.018,
        })
    else:
        env['ir.config_parameter'].create({
            'key':'sponsor_educative_credit.spo_TD_value',
            'value': 0.018,
        })
    val3= env['ir.config_parameter'].search([('key','=','sponsor_educative_credit.spo_TIA_value')])
    if val3:
        val3.write({
            'value': 15.90,
        })
    else:
        env['ir.config_parameter'].create({
            'key':'sponsor_educative_credit.spo_TIA_value',
            'value': 15.90,
        })



