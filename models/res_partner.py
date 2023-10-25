from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date

class ResPartner(models.Model):
    _inherit='res.partner'
# #     #Many2one
    spo_beneficent_ids = fields.Many2many('spo.beneficent.info', string='Tipo de Cliente')
    spo_academic_program_id = fields.Many2one('spo.academic.program.info', string='Programa Academico')
    spo_academic_program_uni_id = fields.Many2one('spo.academic.program.uni.info', string='Programa Academico')
    spo_career_id = fields.Many2one('spo.careers.info', string='Carrera Principal',related='spo_career_mixed_id.spo_principal_career_id',store=True )
    spo_second_career_id = fields.Many2one('spo.careers.info', string='Segunda Carrera',related='spo_career_mixed_id.spo_second_career_id',store=True)
    spo_career_mixed_id = fields.Many2one('spo.careers.mixed', string='Carrera')
    country_id = fields.Many2one(
        'res.country',
        ondelete='restrict',
        help=u"País",
        default=lambda self: self.env['res.country'].search(
            [('code', '=', 'PE')]
        )
    )
    spo_country_id = fields.Many2one(
        'res.country', 
        ondelete='restrict',
        string='Nacionalidad',
        default=lambda self: self.env['res.country'].search(
            [('code', '=', 'PE')])
        )
    spo_university_id = fields.Many2one('spo.university.info', string='Universidad')
    spo_representative_id= fields.Many2one('res.partner', string='Representante Legal')
    spo_fiador_id= fields.Many2one('res.partner', string='Fiador Solidario(Aval)')
    spo_exption = fields.Many2one(comodel_name='res.users', string='Excepción')
    l10n_latam_identification_type_id = fields.Many2one('l10n_latam.identification.type',
        string="Identification Type", index='btree_not_null', auto_join=True,
        default=lambda self: self.env['l10n_latam.identification.type'].search([('name','=','DNI')]),
        help="The type of identification")
    # Selecction
    spo_sex_type = fields.Selection(string='Sexo', selection=[('fe', 'FEMENINO'), ('ma', 'MASCULINO'),])
    spo_modality_career = fields.Selection(string='Modalidad de Carrera', selection=[('PRE', 'PRESENCIAL'), ('SEMI', 'SEMIPRESENCIAL'),('VIR', 'VIRTUAL')],default='PRE')
    spo_study_place = fields.Selection(string='Sede de Carrera', selection=[('MOL', 'LA MOLINA'), ('LIM', 'LIMA NORTE'),('MAG','MAGDALENA')], default='LIM')
    spo_requisit = fields.Selection(string='Cumple Requisito Mínimo de PPA/CA', selection=[('apto', 'Apto'), ('noapto', 'No apto'),('excep', 'Excepsión')])
    #Char
    def _signal_requisist_PPA(self):
        for rec in self:
            if rec.spo_average_saved < rec.spo_academic_program_uni_id.spo_average_saved:rec.spo_signal_requisist_PPA = 'No cumple'
            elif rec.spo_average_saved >= rec.spo_academic_program_uni_id.spo_average_saved:rec.spo_signal_requisist_PPA = 'Cumple'
    spo_signal_requisist_PPA = fields.Char(compute='_signal_requisist_PPA')
    def _signal_requisist_PPA_excep(self):
        for rec in self:
            if rec.spo_average_saved < rec.spo_academic_program_uni_id.spo_average_saved_exception:rec.spo_signal_requisist_PPA_excep = 'No cumple Excep'
            if rec.spo_average_saved >= rec.spo_academic_program_uni_id.spo_average_saved_exception:rec.spo_signal_requisist_PPA_excep = 'Cumple Excep'
    spo_signal_requisist_PPA_excep = fields.Char(compute='_signal_requisist_PPA_excep')

    def _signal_requisist_CA(self):
        for rec in self:
            if rec.spo_credits_saved < rec.spo_academic_program_uni_id.spo_credits_saved:rec.spo_signal_requisist_CA = 'No cumple'
            elif rec.spo_credits_saved >= rec.spo_academic_program_uni_id.spo_credits_saved:rec.spo_signal_requisist_CA = 'Cumple'
    spo_signal_requisist_CA = fields.Char(compute='_signal_requisist_CA')
    def _signal_requisist_CA_excep(self):
        for rec in self:
            if rec.spo_credits_saved < rec.spo_academic_program_uni_id.spo_credits_saved_exeption:rec.spo_signal_requisist_CA_excep = 'No cumple Excep'
            if rec.spo_credits_saved >= rec.spo_academic_program_uni_id.spo_credits_saved_exeption:rec.spo_signal_requisist_CA_excep = 'Cumple Excep'
    spo_signal_requisist_CA_excep = fields.Char(compute='_signal_requisist_CA_excep')
    spo_work_email = fields.Char(string='Correo de Trabajo')
    spo_uni_email = fields.Char(string='Correo de Universidad')
    spo_work_mobile = fields.Char(string='Móvil de Trabajo')
    @api.depends('spo_age')
    def _spo_display_age(self):
        for rec in self:
            if rec.spo_age:rec.spo_display_age = f'{rec.spo_age} Años'
            else:rec.spo_display_age = ''
    spo_display_age = fields.Char(string='Edad', compute='_spo_display_age')
    @api.depends('vat','l10n_latam_identification_type_id')
    def _spo_display_doc(self):
        for rec in self:
            if rec.vat and rec.l10n_latam_identification_type_id.name:rec.spo_display_doc = f'{rec.l10n_latam_identification_type_id.name}-{rec.vat}'
            elif rec.l10n_latam_identification_type_id.name and not rec.vat:rec.spo_display_doc = f'{rec.l10n_latam_identification_type_id.name}-'
            elif rec.vat and not rec.l10n_latam_identification_type_id.name :rec.spo_display_doc = f'-{rec.vat}'
            else:rec.spo_display_doc = f''
    spo_display_doc  = fields.Char(string='Documento', compute='_spo_display_doc')
    spo_street_born = fields.Char(string='Lugar de Nacimiento')
    spo_RUC = fields.Char(string='RUC')
    
    #Integer
    @api.depends("spo_birthdate_date")
    def _compute_age(self):
        for record in self:
            age = 0
            if record.spo_birthdate_date:age = relativedelta(fields.Date.today(), record.spo_birthdate_date).years
            record.spo_age = age
    spo_age = fields.Integer(readonly=True, compute="_compute_age", string='Edad', store=True)
    spo_credits_saved = fields.Integer(string='Créditos Acumulados(CA)')
    #Float
    @api.constrains('spo_average_saved')
    def validationAverage(self):
        if self.spo_average_saved > 20:raise ValidationError('El promedio no puede ser mayor a 20')
        elif self.spo_average_saved < 0:raise ValidationError('El promedio no puede ser menor a 0')
    spo_average_saved = fields.Float(string='Promedio Ponderado Acumulado(PPA)')
    #Date
    @api.constrains('spo_birthdate_date','spo_beneficent_ids')
    def min_age(self):
        for rec in self:
            if rec.spo_beneficent_ids:
                for types in rec.spo_beneficent_ids.ids:
                    if types in [2,3]:
                        if  rec.spo_age == 0 and rec.spo_birthdate_date : raise ValidationError('La Edad no puede ser Cero')
                        elif rec.spo_age < 18 and rec.spo_birthdate_date : raise ValidationError('No puede ser menor de edad')
    spo_birthdate_date = fields.Date("Fecha de Nacimento")
#     #Boolean
    @api.depends('spo_second_career_id')
    def _checkSecondCareer(self):
        for rec in self:
            if rec.spo_second_career_id:
                rec.spo_doble_career = True
            else:
                rec.spo_doble_career = False
    spo_doble_career = fields.Boolean(string='Financiar Doble Grado?', compute='_checkSecondCareer')
