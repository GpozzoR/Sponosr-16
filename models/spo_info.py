from odoo import api, fields, models
from odoo.exceptions import ValidationError


# #######Beneficent
class SpoBeneficent(models.Model):
    _name = 'spo.beneficent.info'

    #char
    name = fields.Char(string='Nombre')

class SpoAcademicProgram(models.Model):
    _name = 'spo.academic.program.info'
    # Char
    name = fields.Char(string='Nombre')
    #Integer
    spo_credits_saved = fields.Integer(string='Créditos Acumulados')
    spo_credits_saved_exeption = fields.Integer(string='Exepción')
    #Float
    @api.constrains('spo_average_saved','spo_average_saved_exception')
    def validationAverage(self):
        if self.spo_average_saved > 20 or self.spo_average_saved_exception > 20:raise ValidationError('El promedio no puede ser mayor a 20')
        elif self.spo_average_saved < 0 or self.spo_average_saved_exception < 0:raise ValidationError('El promedio no puede ser menor a 0')
    spo_average_saved = fields.Float(string='Promedio Ponderado Acumulado')
    spo_average_saved_exception = fields.Float(string='Exepción')
    #Many2many
    spo_university_ids = fields.Many2many('spo.university.info', string='Universidades')

class SpoAcademicProgramUniversity(models.Model):
    _name = 'spo.academic.program.uni.info'
    _rec_name='program'
    program = fields.Char(string='Programa')
    name = fields.Many2one(comodel_name='spo.academic.program.info', string='Programa')
    #Integer
    spo_credits_saved = fields.Integer(string='Parámetro (CA)')
    spo_credits_saved_exeption = fields.Integer(string='Parámetro (CA) Exepción')
    #Float
    @api.constrains('spo_average_saved','spo_average_saved_exception')
    def validationAverage(self):
        if self.spo_average_saved > 20 or self.spo_average_saved_exception > 20:raise ValidationError('El promedio no puede ser mayor a 20')
        elif self.spo_average_saved < 0 or self.spo_average_saved_exception < 0:raise ValidationError('El promedio no puede ser menor a 0')
    spo_average_saved = fields.Float(string='Parámetro (PPA)')
    spo_average_saved_exception = fields.Float(string='Parámetro (PPA) Exepción')

    #Many2many
    spo_university_id = fields.Many2one('spo.university.info', string='Universidad')

class SpoCareers(models.Model):
    _name = 'spo.careers.info'

    #Char
    name = fields.Char(string='Nombre')

    #Many2one
    spo_type_AP_id = fields.Many2one('spo.academic.program.info', string='Tipo')
    
    spo_type_career = fields.Selection([
        ('prim', 'Principal'),
        ('secu', 'Secundaríia')
    ], string='Tipo de Carrera')

    spo_university_ids = fields.Many2many('spo.university.info', string='Universidades')
    
class SpoCareersMixed(models.Model):
    _name = 'spo.careers.mixed'
    _rec_name='display_name'
    spo_university_id = fields.Many2one('spo.university.info', string='Universidad')
    spo_academic_program_id = fields.Many2one('spo.academic.program.info', string='Programa Academico')
    spo_academic_program_uni_id = fields.Many2one('spo.academic.program.uni.info', string='Programa Académico')
    spo_principal_career_id = fields.Many2one('spo.careers.info', string='Carrera Primaria')
    spo_principal_career = fields.Char(string='Carrera Primaria')
    spo_second_career_id = fields.Many2one('spo.careers.info', string='Carrera Secundaria')
    spo_second_career = fields.Char(string='Carrera Secundaria')

    @api.depends('spo_principal_career','spo_second_career')
    def _getName(self):
        for rec in self:
            if rec.spo_principal_career and not rec.spo_second_career:rec.display_name = f'{rec.spo_principal_career} / Ninguna'
            elif not rec.spo_principal_career and rec.spo_second_career:rec.display_name = ''
            elif rec.spo_principal_career and rec.spo_second_career:rec.display_name = f'{rec.spo_principal_career} / {rec.spo_second_career}'
            else:rec.display_name  = ''
    display_name = fields.Char(string='Carrera',compute='_getName')
    spo_total_credits = fields.Integer(string='Créditos Totales')
    spo_credits_semester = fields.Integer(string='Créditos por Semestre')
    spo_CCU = fields.Float(string='Costo del Crédito Universitario', related='spo_university_id.spo_CCU')
    spo_CM = fields.Float(string='Costo de Mensualidad',related='spo_university_id.spo_CM')

class SpoUniversity(models.Model):
    _name= 'spo.university.info'
    _rec_name = 'short_name'
    name = fields.Many2one('res.partner',string='Nombre')
    short_name = fields.Char(string='Nombre Corto')
    spo_email = fields.Char(string='Correo')

    def _spo_CGS_value(self):
        val1= self.env['ir.config_parameter'].search([('key','=','sponsor_educative_credit.spo_CGS_value')])
        value = None
        if val1:
            for vals in val1:value = vals.value
        return value
    spo_CGS = fields.Float(string='Costo de Gestión en Soles', digits=(2, 2), default=_spo_CGS_value)

    def _spo_TD_value(self):
        val2= self.env['ir.config_parameter'].search([('key','=','sponsor_educative_credit.spo_TD_value')])
        value = None
        if val2:
            for vals in val2:value = vals.value
        return value
    spo_TD = fields.Float(string='Tasa de Seguro de Desgravamen %', digits=(2, 3), default=_spo_TD_value)

    def _spo_TIA_value(self):
        val3= self.env['ir.config_parameter'].search([('key','=','sponsor_educative_credit.spo_TIA_value')])
        value = None
        if val3:
            for vals in val3:value = vals.value
        return value
    spo_TIA = fields.Float(string='Tasa de Interes Anual %', digits=(2, 2),default=_spo_TIA_value)
    spo_CCU = fields.Float(string='Costo del Crédito Universitario')
    spo_CM = fields.Float(string='Costo de Mensualidad')
# ############ credit oportunities
class SpoState1(models.Model):

    _name ='spo.state.1.info'

    name = fields.Char(string='Nombre del Estado')

class SpoState2(models.Model):

    _name ='spo.state.2.info'

    name = fields.Char(string='Nombre del Estado')
    
class SpoState3(models.Model):

    _name ='spo.state.3.info'

    name = fields.Char(string='Nombre del Estado')

class SpoState4(models.Model):

    _name ='spo.state.4.info'


    name = fields.Char(string='Nombre del Resultado')
    
class SpoState5(models.Model):

    _name ='spo.state.5.info'

    name = fields.Char(string='Nombre del Resultado')
    
class SpoState6(models.Model):

    _name ='spo.state.6.info'

    name = fields.Char(string='Nombre del Resultado')
    
class SpoRiskMotive(models.Model):
    _name='spo.risk.motive.info'

    name = fields.Char(string='Nombre del Motivo de Riesgo')

class SpoContractStates(models.Model):
    _name='spo.contract.states.info'

    name = fields.Char(string='Nombre')

    type_state = fields.Selection(selection=[('1', '1'), ('2', '2'),('3', '3'),('4', '4'),])

class SpoCreditsSemester(models.Model):
    _name='spo.credits.semester.info'

    _rec_name = 'value'
    
    academic_program_id = fields.Many2one(comodel_name='spo.academic.program.info', string='Programa Académico')

    second_career = fields.Boolean(string='Segunda Carrera')

    value = fields.Integer(string='Valor')
    
scription = fields.Char(string='Descripción de Semestre')
    
class SpoMissSemester(models.Model):
    _name='spo.miss.semester'

    _rec_name='number'

    number = fields.Integer(string='Numero de Semestre Faltante')

class SpoCuotas(models.Model):
    _name='spo.cuotas.info'

    name  = fields.Integer(string='Valor')
    
    spo_Type_installment = fields.Selection(string='tipo de Cuota', selection=[('student', 'Estudiante'), ('graduate', 'Graduado')])
    
    spo_academic_program_id = fields.Many2one('spo.academic.program.info', string='Programa Academico')

    spo_miss_semester = fields.Many2one(comodel_name='spo.miss.semester',string='Semestres Pendientes')
    
    
class SpoSemesterInf(models.Model):
    _name = 'spo.semester.info'