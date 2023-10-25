from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging
import datetime
from datetime import date, datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    #Many2one
    spo_academic_program_id = fields.Many2one(comodel_name='spo.academic.program.info', related='partner_id.spo_academic_program_uni_id.name', store=True)
    final_result_evaluation = fields.Many2one(comodel_name='spo.contract.states.info', string='Resultado Final se la Evaluación')
    contract_state = fields.Many2one(comodel_name='spo.contract.states.info', string='Estado del Contrato')
    sending_state_CCE = fields.Many2one(comodel_name='spo.contract.states.info', string='Estado de Envío del CCE')
    signature_state_CEE = fields.Many2one(comodel_name='spo.contract.states.info', string='Estado de Firma del CCE ')
    #One2many
    desembolso_ids = fields.One2many(comodel_name='sale.order.line.desembolso', inverse_name='relation_sale_order', string='Desembolsos')
    #Selection
    beginning_semester = fields.Selection(string='Semestre de Inicio del Financiamiento Sponsor', selection=[('1', '1er Semestre del Año'), ('2', '2do Semestre del Año'),])
    state = fields.Selection(
        selection=[
            ('draft', "Cronograma"),
            ('sent', "Cronograma Enviado"),
            ('sale', "Confirmado"),
            ('done', "Bloqueado"),
            ('cancel', "Cancelado"),
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')
    month_start = fields.Selection(string='Mes', selection=[('1', '01'), ('2', '02'),('3', '03'), ('4', '04'),('5', '05'), ('6', '06'),('7', '07'), ('8', '08'),('9', '09'), ('10', '10'),('11', '11'), ('12', '12'),])
    def year():
        today = date.today()
        year = 1999
        days = today.year - 1999 
        years_list = []
        for years in range(days):
            year= year + 1
            years_list.append((str(year),str(year)))
        return years_list
    year_start = fields.Selection(string='Año',selection=year())
    #Date
    final_result_date = fields.Date(string='Fecha de Resultado Final')
    sendig_date_simulation_IPFE = fields.Date(string='Fecha de Envío de Simulación a IPFE')
    sendig_date_simulation_postulant = fields.Date(string='Fecha de Envío de Simulación a Postulante')
    beginnig_date_contract = fields.Date(string='Fecha de Inicio de Contrato')
    sending_date_CCE = fields.Date(string='Fecha de Envío del CCE')
    start_date = fields.Date(string='Fecha de Inicio de Incio del Sponsor')
    #FLoat
    def _total_prestamo(self):
        values = []
        for rec in self:
            if rec.desembolso_ids:
                for lines in rec.desembolso_ids:
                    values.append(lines.total_desembolso)
            rec.total_prestamo = sum(values)
    total_prestamo = fields.Float(string='Préstamo', compute='_total_prestamo')
    total_capital = fields.Float(string='Total Capital Pagado')
    def _total_entregado(self):
        values = []
        for rec in self:
            if rec.desembolso_ids:
                for lines in rec.desembolso_ids:
                    if lines.spo_state_desembolso == 'paid':
                        values.append(lines.total_desembolso)
            rec.total_entregado = sum(values)
    total_entregado = fields.Float(string='Entregado', compute='_total_entregado')
    def _total_per_entregado(self):
        values = []
        for rec in self:
            if rec.desembolso_ids:
                for lines in rec.desembolso_ids:
                    if lines.spo_state_desembolso == 'not_paid':
                        values.append(lines.total_desembolso)
            rec.total_per_entregado = sum(values)
    total_per_entregado = fields.Float(string='Por Entregar', compute='_total_per_entregado')
    def _total_interes(self):
        values = []
        for rec in self:
            if rec.order_line:
                for lines in rec.order_line:
                    values.append(lines.spo_interes)
            rec.total_interes = sum(values)
    total_interes = fields.Float(string='Total Interés Pagado', compute='_total_interes')
    total_moras = fields.Float(string='Total Moras', compute='')
    def _total_gestion(self):
        values = []
        for rec in self:
            if rec.order_line:
                for lines in rec.order_line:
                    values.append(lines.spo_costo_gestion)
            rec.total_other = sum(values)
    total_other = fields.Float(string='Total Otros Gastos', compute='_total_gestion')
    
    def _total_paid(self):
        values = []
        for rec in self:
            if rec.order_line:
                for lines in rec.order_line:
                    if lines.payment_state == 'paid':
                        values.append(lines.cuota_total)
            rec.total_paid = sum(values)
    total_paid  = fields.Float(string='Total Pagado', compute='_total_paid')
    
    def _total_late(self):
        values = []
        for rec in self:
            if rec.order_line:
                for lines in rec.order_line:
                    if lines.payment_state == 'late':
                        values.append(lines.cuota_total)
            rec.total_late = sum(values)
    total_late  = fields.Float(string='Total Adeudado', compute='_total_late')
    #Char
    Total_time_credit = fields.Char(string='Plazo Total del Crédito', compute='')
    def search_group(self):
        for rec in self:
            user = rec.env['res.users'].browse(rec._uid)
            desired_user_gr = user.has_group('sponsor_educative_credit.group_no_create_edit')
            if desired_user_gr:rec.groups = 'True'
            elif not desired_user_gr:rec.groups = 'False'
    groups = fields.Char(string='grupo',compute='search_group')
    #bool
    spo_doble_career = fields.Boolean(related='partner_id.spo_doble_career', store=True)
    #params
    spo_cost_gestion = fields.Float(related='partner_id.spo_university_id.spo_CGS', store=True)
    spo_rate_interes_anual  = fields.Float(related='partner_id.spo_university_id.spo_TIA', store=True)
    spo_rate_seguro_desgravamen = fields.Float(related='partner_id.spo_university_id.spo_TD', store=True)
    spo_rate_desgravamen  = fields.Float(default= lambda self: self.env.ref('l10n_pe.1_sale_tax_igv_18').amount)
    spo_parameter_CA = fields.Integer(related='partner_id.spo_academic_program_uni_id.spo_credits_saved', store=True)
    spo_parameter_CA_exepcion = fields.Integer(related='partner_id.spo_academic_program_uni_id.spo_credits_saved_exeption', store=True)
    spo_parameter_PPA = fields.Float(related='partner_id.spo_academic_program_uni_id.spo_average_saved', store=True)
    spo_parameter_PPA_exepcion = fields.Float(related='partner_id.spo_academic_program_uni_id.spo_average_saved_exception', store=True)
    @api.onchange('partner_id')
    def _loadCredits(self):
        order = self.env['sale.order'].browse(self.id)
        order.write({
            'spo_credits_career':self.partner_id.spo_career_mixed_id.spo_total_credits
        })
    spo_credits_career = fields.Integer(string='Nro de Créditos de Carrera', related='partner_id.spo_career_mixed_id.spo_total_credits')
    spo_credits_studied = fields.Integer(string='Nro de Créditos Estudiados')
    def _missCredits(self):
        for rec in self: 
            if rec.spo_credits_career - rec.spo_credits_studied < 0:
                rec.spo_credits_miss = 0
            else:rec.spo_credits_miss = rec.spo_credits_career - rec.spo_credits_studied 
    spo_credits_miss = fields.Integer(string='Créditos Faltantes', compute='_missCredits')
    spo_cuota_student = fields.Integer(string='Cuota de Estudiante')
    spo_cuota_graduate = fields.Integer(string='Cuota de Graduado')

    
    




    """
        Este metodo contiene todas las condiciones necesarias para poder realizar el calculo del desembolso.ñ
        Es decir datos obligatorios.
    """
    def ValidationDesembolso(self,line ,dobleCarrera = False, tipoCambio = False):
        # if  not line.deuda_soles and \
        #     not line.cuota_matricula_soles and \
        #     not line.cuota_pension_soles   and \
        #     not line.Nro_credits : 
        #     raise ValidationError(
        #         """
        #             Para Cálcular el desembolso son obligatiorios los siguientes campos ('N° De Créditos' , 'Matricula' ,'Pensión', 'Deuda').
        #         """
        #     )
        if  tipoCambio == 0:
            raise ValidationError(
                """
                    El tipo de campo no esta definido ,debe agregar una tasa.
                """
            )

        if not self.partner_id.spo_academic_program_uni_id:
            raise ValidationError('Beneficiario seleccionado NO posee un tipo de programa académico.')
        if not self.partner_id.spo_career_mixed_id:
            raise ValidationError('Beneficiario seleccionado NO posee una carrera.')
        if self.spo_credits_miss == 0:
            raise ValidationError('El Nro de créditos faltantes no puede ser igual a 0')
        if self.partner_id.spo_career_mixed_id.spo_credits_semester == 0:
            raise ValidationError('El Nro de créditos por semestre no puede ser igual a 0')
    """
        Este metodo Funciona para obtener los credito franccionados por cantidad de semetes
        EJM CREDIT = 55  RESULTADO = [20,20,15] serian 3 semestres.
    """
    def _getSemesterForCredit(self,TotalCredi,credit): #20 21 entre otros
        creditos_por_semestre = []
        while TotalCredi > 0:
            unidades_por_semestre = min(TotalCredi, credit)
            creditos_por_semestre.append(unidades_por_semestre)
            TotalCredi -= unidades_por_semestre
            miss_semester_id= self.env['spo.miss.semester'].search([('number','=',len(creditos_por_semestre))])
        return creditos_por_semestre

    """
        Este metodo Permite obtener la tasa del dia contra los Soles.
        
    """
    def getRate(self):
        res_currency_id = self.env['res.currency'].search([
            ('name','=','USD'),
            ('active','=',True)
            ], limit=1)
        if res_currency_id and res_currency_id.rate_ids:
            rate_day = res_currency_id.rate_ids.sorted('name', reverse=True)[:1]
            return rate_day.inverse_company_rate 
        else :return 0

    def _calculate_desembolso(self,desebolso):
        tipoCambio = self.getRate()
        #Numero de creditos por semestre
        nro_seme = self.partner_id.spo_career_mixed_id.spo_credits_semester
        self.ValidationDesembolso(desebolso,False,tipoCambio)
        semestres = self._getSemesterForCredit(self.spo_credits_miss,nro_seme)
        TotalDesembolsoXSemestre = 0
        lisTotalDesembolsoXSemestre = []
        # Calcular el total de desembolso para cada semestre
        for sem in range(1,len(semestres) + 1 ):
            if  desebolso.spo_academic_program_id.id == self.env.ref('sponsor_educative_credit.spo_academic_program_1').id or \
                desebolso.spo_academic_program_id.id == self.env.ref('sponsor_educative_credit.spo_academic_program_2').id:
                if sem == 1:#calculo para el Primer Semestre
                    TotalDesembolsoXSemestre = ((desebolso.deuda_soles) + (desebolso.cuota_matricula_soles) + ((5)*(desebolso.cuota_pension_soles)))+((tipoCambio)*((desebolso.deuda_usd)+(desebolso.cuota_matricula_usd) + ((5)*(desebolso.cuota_pension_usd))))
                elif sem == len(semestres) and semestres[sem - 1 ] < nro_seme:#Calculo para el ultimo semestre 
                    TotalDesembolsoXSemestre = ((desebolso.cuota_matricula_soles) + ((5)*(desebolso.cuota_pension_soles)/(13)*(semestres[sem - 1 ])))+((tipoCambio)*((desebolso.cuota_matricula_usd) + ((5)*(desebolso.cuota_pension_usd))))
                else:#Calculo que aplicar en los semestres != al primero y el ultimo
                    if desebolso.spo_doble_career: #Si es doble carrera cambia un poco el calculo a los semestres distinto al 1 y el ultimo.
                        TotalDesembolsoXSemestre = (desebolso.cuota_matricula_soles) + ((5) * (desebolso.cuota_pension_soles)) + ((tipoCambio) * ((desebolso.cuota_matricula_usd) + ((5) * desebolso.cuota_pension_usd)))
                    else:
                        TotalDesembolsoXSemestre = ((desebolso.cuota_matricula_soles) + ((5)*(desebolso.cuota_pension_soles)))+((tipoCambio)*((desebolso.cuota_matricula_usd) + ((5)*(desebolso.deuda_usd))))
            elif desebolso.spo_academic_program_id.id == self.env.ref('sponsor_educative_credit.spo_academic_program_3').id:
                if sem == 1:#calculo para el Primer Semestre CPEL
                    TotalDesembolsoXSemestre = ((desebolso.deuda_soles) + (desebolso.cuota_matricula_soles) + ((semestres[sem - 1])/(5)*(desebolso.cuota_pension_soles)))
                else:#calculo para el el resto del semestre cPEL
                    TotalDesembolsoXSemestre = ((desebolso.cuota_matricula_soles) + ((semestres[sem - 1])/(5)*(desebolso.cuota_pension_soles)))
            lisTotalDesembolsoXSemestre.append({
                'semestre':sem,
                'desenbolso':TotalDesembolsoXSemestre,
                'creditos':semestres[sem - 1]
            })
            logging.info(lisTotalDesembolsoXSemestre)
        return  [i.get('desenbolso') for i in lisTotalDesembolsoXSemestre]  if not desebolso.sponsor_promotion else TotalDesembolsoXSemestre - (desebolso.sponsor_promotion * TotalDesembolsoXSemestre) / 100 , lisTotalDesembolsoXSemestre, (5)*(desebolso.cuota_pension_soles),(5)*(desebolso.cuota_pension_usd)

    def calculate_desembolso(self):
        order = self.env['sale.order'].browse(self.id)
        for line in self:
            for rec in line.desembolso_ids:
                totalDesembolso , lisTotalDesembol, baseAmountPen,baseAmountUsd = self._calculate_desembolso(rec)
                nro_desembolso = 1
                if len(line.desembolso_ids) <= 1:
                    rec.total_desembolso = lisTotalDesembol[0].get('desenbolso')
                    rec.Nro_credits = lisTotalDesembol[0].get('creditos')
                    rec.sale_order_id = line.id
                    rec.spo_state_desembolso = 'not_paid'
                    rec.spo_base_amount_pen = baseAmountPen
                    rec.spo_base_amount_usd = baseAmountUsd
                    rec.spo_nro_desem = f'D{nro_desembolso}'
                    student_value =line.env['spo.cuotas.info'].search([('spo_Type_installment','=','student'),('spo_academic_program_id','=',line.spo_academic_program_id.id),('spo_miss_semester','=',len(lisTotalDesembol))]).name
                    graduate_value =line.env['spo.cuotas.info'].search([('spo_Type_installment','=','graduate'),('spo_academic_program_id','=',line.spo_academic_program_id.id),('spo_miss_semester','=',len(lisTotalDesembol))]).name
                    #Al momento de cargar el desembolso se obtene y carga en el valor de la cuota(Estudiante o Graduado)
                    if student_value:order.write({'spo_cuota_student':student_value})
                    if graduate_value:order.write({'spo_cuota_graduate': graduate_value})
                    #Disección del desembolso el la tabla de desembolsos 9560, 7800, 7800, ...
                    for i in lisTotalDesembol:
                        if nro_desembolso > 1:
                            order.write({
                                'desembolso_ids':[(0, None,{
                                    'spo_academic_program_id':rec.spo_academic_program_id.id,
                                    'spo_nro_desem':f'D{nro_desembolso}',
                                    'spo_base_amount_pen':baseAmountPen,
                                    'spo_base_amount_usd':baseAmountUsd,
                                    'sponsor_promotion': 0,
                                    'deuda_soles':0,
                                    'deuda_usd':0,
                                    'cuota_matricula_soles':rec.cuota_matricula_soles,
                                    'cuota_matricula_usd':rec.cuota_matricula_usd,
                                    'cuota_pension_soles':rec.cuota_pension_soles,
                                    'cuota_pension_usd':rec.cuota_pension_usd,
                                    'total_desembolso': i.get('desenbolso'),
                                    'Nro_credits': i.get('creditos'),
                                    'sale_order_id':line.id,
                                    'spo_state_desembolso':'not_paid',
                                    'spo_doble_career':rec.spo_doble_career
                                    })]
                                })
                        nro_desembolso +=1 


    def validationCuotas(self, university, dateStart):
        if not university:raise ValidationError('El Beneficiario seleccionado NO posee una univerdiad.')
        elif university:
            if not dateStart:raise ValidationError('Es necesario la fecha de inicio del Sponsor.')
    
    def _getYearBisiest(self,year):
        if year % 4 != 0: 
            return 0
        elif year % 4 == 0 and year % 100 != 0: #divisible entre 4 y no entre 100 o 400
            return 1
        elif year % 4 == 0 and year % 100 == 0 and year % 400 != 0: #divisible entre 4 y 10 y no entre 400
            return 0
        elif year % 4 == 0 and year % 100 == 0 and year % 400 == 0: #divisible entre 4, 100 y 400
            return 1
    
    def _getInfoLine(self,**kwargs):
        monthYear = {
            1:31, 2:[28,29], 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31
        }
        cuota =kwargs.get('cuota')
        semester_count =kwargs.get('semester')
        spo_year = kwargs.get('year') 
        spo_month = kwargs.get('month')
        final_date = None
        ListDesembolso =  kwargs.get('ListDesembol')
        cuotaDesem = kwargs.get('cuotaDesem')
        if cuota ==0:
            if spo_month == 1 or spo_month > 2: final_date = date(spo_year,spo_month, monthYear.get(spo_month))#
            elif spo_month == 2:final_date = date(spo_year,spo_month,monthYear.get(spo_month)[self._getYearBisiest(spo_year)])
            spo_desembolso = ListDesembolso.get('desembolso')[0]#
            return spo_year,spo_month,spo_desembolso,final_date,cuotaDesem
        if cuota >= 1:
            spo_desembolso = 0.0
            spo_month = spo_month + 1
            if spo_month in [13,7]:
                semester_count = semester_count + 1
                try:
                    spo_desembolso = ListDesembolso.get('desembolso')[semester_count]
                    cuotaDesem += 1
                except IndexError:spo_desembolso = 0.0
            if spo_month == 13:
                spo_month =  1
                spo_year = spo_year + 1
            if spo_month == 1 or spo_month > 2:final_date = date(spo_year,spo_month, monthYear.get(spo_month))#
            elif spo_month == 2:final_date = date(spo_year,spo_month,monthYear.get(spo_month)[self._getYearBisiest(spo_year)])
            return spo_year,spo_month,spo_desembolso,final_date,semester_count,cuotaDesem
    def _calculateInteresDegravamen(self,**kwargs):
        if kwargs:
            plazo = kwargs.get('finalDate', 0) - kwargs.get('interesDate')[0]
            intereses =  kwargs.get('capital', 0) * kwargs.get('tasaDiaria',0) * int(plazo.days)
            intereses = round(intereses, 2)
            val1 =(kwargs.get('capital',0)*kwargs.get('seguroDesgra',0))/100
            val2 = (val1*kwargs.get('tasaDesgra',0))/100
            desgravamen = val1 + val2
            return intereses, desgravamen
    def createCuota(self,**kwargs):
        order = self.env['sale.order'].browse(self.id)
        order.write({
            'order_line':[(0, None,{
                'product_id':kwargs.get('product').id,
                'name':str(round(kwargs.get('amount', 0.0),2)),
                'spo_nro_cuota_ident':kwargs.get('cuota'),
                'spo_emision_date':kwargs.get('emisionDate'),
                'spo_final_date':str(kwargs.get('finalDate')),
                'spo_desembolso':kwargs.get('desembolso'),
                'spo_capital':kwargs.get('capital',0.0),
                'spo_interes':kwargs.get('interes', 0.0),
                'spo_amortizacion':kwargs.get('amort',0.0),
                'spo_costo_gestion':kwargs.get('costoGest',0.0),
                'spo_desgravamen':kwargs.get('desgra',0.0),
                'cuota_total':kwargs.get('total',0.0),
                'spo_type_cuota': kwargs.get('typeCuota','no'),
                'payment_state':kwargs.get('state',False)
                })]
            })
    def load_cuotas(self):
        for line in self:
            if line.desembolso_ids:
                self.validationCuotas(line.partner_id.spo_university_id,line.start_date)
                listaDesembolso ={'desembolso':[ i.total_desembolso for i in line.desembolso_ids]}
                logging.info(listaDesembolso)
                product_id = line.env.ref('sponsor_educative_credit.spo_product_cuota')
                product_product = self.env['product.product'].search([('name','=',product_id.name)])
                spo_month_start = int(line.start_date.strftime('%m'))
                spo_year_start = int(line.start_date.strftime('%Y'))
                spo_emision_date = date.today()
                final_date =  None
                spo_capital = 0.0
                tasa_interes= line.spo_rate_interes_anual /100
                spo_date_interes = []
                spo_amortizacion = 0.0
                intereses = 0.0
                spo_costo_gestion = line.spo_cost_gestion
                spo_seguro_desgravamen = line.spo_rate_seguro_desgravamen
                spo_desgravamen = line.spo_rate_desgravamen
                desgravamen = None
                semester_count = 0
                cuota_total = 0.0
                spo_year = None
                spo_month = None
                spo_desembolso = None
                amount = 0.0
                cuota = 0
                cuotaDesem = 0
                cuotaName = None
                cuotaVal = None
                amount = None
                cuotaDesemVali = []
                if cuota == 0:	
                    cuotaDesem += 1
                    cuotaDesemVali.append(cuotaDesem)
                    cuotaVal = f'D{cuotaDesem}'
                    dictLineValues = dict(cuotaDesem=cuotaDesem,cuota=cuota, year=spo_year_start,month=spo_month_start,semester=semester_count,ListDesembol=listaDesembolso)
                    spo_year,spo_month,spo_desembolso,final_date,cuotaDesem = self._getInfoLine(**dictLineValues)
                    spo_capital= spo_desembolso + spo_capital
                    dictCreateCuota = dict(product=product_product,cuota=cuotaVal,emisionDate=spo_emision_date,finalDate=final_date,desembolso=spo_desembolso,capital=spo_capital)
                    self.createCuota(**dictCreateCuota)
                    spo_date_interes.append(final_date)
                while spo_capital > spo_amortizacion:
                    cuota += 1
                    if cuota >= 1:
                        dictLineValues = dict(cuotaDesem=cuotaDesem,cuota=cuota, year=spo_year,month=spo_month,semester=semester_count,ListDesembol=listaDesembolso)
                        spo_year,spo_month,spo_desembolso,final_date,semester_count,cuotaDesem = self._getInfoLine(**dictLineValues)
                        if spo_desembolso > 0.0:spo_capital = spo_desembolso + spo_capital
                        if semester_count <= len(listaDesembolso.get('desembolso')):
                            amount = line.spo_cuota_student
                            spo_type_cuota = 'student'
                            cuotaName = 'E'
                        elif semester_count > len(listaDesembolso.get('desembolso')):
                            amount = line.spo_cuota_graduate
                            spo_type_cuota = 'graduate'
                            cuotaName = 'G'
                        cuotaVal = f'{cuotaName}{cuota}' 
                        if cuotaDesem != cuotaDesemVali[0] :
                            cuotaDesemVali.pop()
                            cuotaDesemVali.append(cuotaDesem)
                            cuotaVal = f'D{cuotaDesem} / {cuotaName}{cuota}'
                        dictCalculateIntDes = dict(finalDate=final_date,interesDate=spo_date_interes,capital=spo_capital,tasaDiaria=((1+tasa_interes)**(1/360)) - 1,seguroDesgra=spo_seguro_desgravamen,tasaDesgra=spo_desgravamen)
                        intereses, desgravamen = self._calculateInteresDegravamen(**dictCalculateIntDes)
                        spo_amortizacion = amount - intereses
                        spo_capital = spo_capital - spo_amortizacion
                        cuota_total = amount + desgravamen + spo_costo_gestion
                        dictCreateCuota = dict(product=product_product,amount=amount,cuota=cuotaVal,emisionDate=spo_emision_date,finalDate=final_date,desembolso=spo_desembolso,capital=spo_capital,interes=intereses,amort=spo_amortizacion,costoGest=spo_costo_gestion,desgra=desgravamen,total=cuota_total,typeCuota=spo_type_cuota,state='not_paid')
                        if amount > spo_capital:
                            amount = spo_capital + intereses
                            spo_amortizacion = spo_capital
                            cuota_total = amount + desgravamen + spo_costo_gestion
                            dictCreateCuota = dict(product=product_product,amount=amount,cuota=cuotaVal,emisionDate=spo_emision_date,finalDate=final_date,desembolso=spo_desembolso,capital=spo_capital,interes=intereses,amort=spo_amortizacion,costoGest=spo_costo_gestion,desgra=desgravamen,total=cuota_total,typeCuota=spo_type_cuota,state='not_paid')
                            self.createCuota(**dictCreateCuota)
                            spo_date_interes.pop()
                            spo_date_interes.append(final_date)
                            break
                        self.createCuota(**dictCreateCuota)
                        spo_date_interes.pop()
                        spo_date_interes.append(final_date)
    def delete_cuotas(self):
        for lines in self.order_line:
            if lines.payment_state != 'paid':
                lines.unlink()

    def wizard_cuota_report(self):
        view_id = self.env.ref('sponsor_educative_credit.spo_report_cuota_view_form').id
        return {
            'name': 'Reporte de Cuota',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'spo.report.cuota',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }