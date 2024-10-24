# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo import _, api, fields, models


class LimsAnalysisParameter(models.Model):
    _name = "lims.analysis.parameter"
    _description = "Parameter LIMS"

    analysis_ids = fields.Many2many(
        "lims.analysis",
        "lims_analysis_lims_analysis_parameter_rel",
        "parameter_id",
        "analysis_id",
        "Analysis lims",
    )

    limits_ids = fields.One2many(
        "lims.analysis.limit",
        "parameter_ids",
        string="Límits",
    )

    analytical_method_price_ids = fields.Many2many(
        comodel_name="analytical.method.price",
        relation="parameter_analytical_method_price_rel",
        string="Methods",
    )

    default_code = fields.Char("Reference", index=True)
    name = fields.Char(string="Name", store=True)
    description = fields.Text()
    type_tags = fields.Many2one(
        "lims.analysis.parameter.type.tags", string="Type tags"
    )
    parameter_uom = fields.Many2many("uom.uom", string="Unidad de medida de parámetro")
    required_comment = fields.Boolean(string="Required Commentary", store=True)
    show_potency = fields.Boolean(string="Mostrar en potencia", store=True)
    change_value_for_comment = fields.Boolean(string="Cambiar valor por comentario", store=True)
    show_description = fields.Boolean(string="Mostrar descripción", store=True)
    max_samples_number = fields.Integer(string="Número de muestras usado", store=True)
    max_samples_permitted = fields.Integer(string="Número de muestras permitidas", store=True)
    limit_value_char = fields.Char(string="Valor limite texto", store=True)
    decimal_precision = fields.Integer(string="Número de decimales", store=True)
    active = fields.Boolean(default=True, string="Active")

    def _is_code_in_use(self, code):
        parameter = self.env['lims.analysis.parameter'].search(
            [
                ("default_code", "=", code),
            ], )
        if parameter:
            return True
        return False

    def write(self, vals):
        print("*"*50)
        print("vals", vals)
        print("vals.get('active')", vals.get('active'))
        #Comprobamos si se esta archivando
        if 'active' in vals:
            paremeter_method = self.env['analytical.method.price'].search(
                [
                    ('parameter_id', 'in', self.ids),
                ]
            )
            print("paremeter_method", paremeter_method)
            if paremeter_method:
                if vals.get('active'):
                    paremeter_method_price_uom =self.env['parameter.analytical.method.price.uom'].search(
                        [
                            ('analytical_method_id', 'in', paremeter_method.ids),
                            ('is_active', '=', False),
                        ]
                    )
                else:
                    paremeter_method_price_uom = self.env['parameter.analytical.method.price.uom'].search(
                        [
                            ('analytical_method_id', 'in', paremeter_method.ids),
                        ]
                    )
                if paremeter_method_price_uom:
                    print("paremeter_method_price_uom", paremeter_method_price_uom)
                    for parameter_price in paremeter_method_price_uom:
                        print("parameter_price", parameter_price.name)
                        if vals.get('active') == False:
                            print("Se esta archivando")
                            parameter_price.write(
                                {
                                    'is_active': False,
                                }
                            )
                        else:
                            print("Se esta desarchivando")
                            parameter_price.write(
                                {
                                    'is_active': True,
                                }
                            )
        #Comprobamos si el codigo esta en uso, si lo esta y no es el mismo que el que ya tenia, lanzamos error
        if vals.get('default_code'):
            if vals['default_code']:
                parameter = self.env['lims.analysis.parameter'].search(
                    [
                        ("default_code", "=", vals['default_code']),
                        ("id", "!=", self.id),
                    ], )
                if parameter:
                    raise UserError(_("La referencia debe ser única por parámetro"))
        #Si se cambia el nombre, actualizamos el nombre de los metodos
        if vals.get('name'):
            for method in self.analytical_method_price_ids:
                method.write(
                    {
                        'name': vals['name'] + " - " + method.analytical_method_id.name,
                        'display_name': vals['name'] + " - " + method.analytical_method_id.name,
                    }
                )
        if vals.get('parameter_uom'):
            udm_vals = vals.get('parameter_uom')[0][2]
            udm_actuals = self.parameter_uom.ids
            for udm_actual in udm_actuals:
                if udm_actual not in udm_vals:
                    if self.analytical_method_price_ids:
                        for method in self.analytical_method_price_ids:
                            udm_to_delete = self.env['parameter.analytical.method.price.uom'].search([
                                ('uom_id', '=', udm_actual),
                                ('analytical_method_id', '=', method.id),
                            ])
                            udm_to_delete.unlink()

        if vals.get('analytical_method_price_ids'):
            #si se eliminan metodos:
            method_vals = vals.get('analytical_method_price_ids')[0][2]
            method_actuals = self.analytical_method_price_ids
            if method_vals != 0:
                for method_actual in method_actuals:
                    if method_actual.id not in method_vals:
                        method_to_delete = self.env['analytical.method.price'].search([
                            ('id', '=', method_actual.id)
                        ])
                        method_to_delete.unlink()
                        method_price_to_delete = self.env['parameter.analytical.method.price.uom'].search([
                            ('analytical_method_id', '=', method_actual.id),
                        ])
                        method_price_to_delete.unlink()
                #añadir metodos
                methods = self.env['analytical.method.price'].search(
                    [
                        ('id', 'in', vals.get('analytical_method_price_ids')[0][2]),
                    ]
                )
                for method in methods:
                    if self.parameter_uom:
                        for udm in self.parameter_uom:
                            method_exist = self.env['parameter.analytical.method.price.uom'].search(
                                [
                                    ('analytical_method_id', '=', method.id),
                                    ('uom_id', '=', udm.id),
                                ]
                            )
                            if len(method_exist) == 0:
                                self.env['parameter.analytical.method.price.uom'].create(
                                    {
                                        'analytical_method_id': method.id,
                                        'uom_id': udm.id,
                                        'parent_id': None,
                                    }
                                )
                    else:
                        method_exist = self.env['parameter.analytical.method.price.uom'].search(
                            [
                                ('analytical_method_id', '=', method.id),
                                ('uom_id', '=', False)
                            ]
                        )
                        if len(method_exist) == 0:
                            self.env['parameter.analytical.method.price.uom'].create(
                                {
                                    'analytical_method_id': method.id,
                                    'uom_id': None,
                                    'parent_id': None,
                                }
                            )
        print("*"*50)
        return super(LimsAnalysisParameter, self).write(vals)

    @api.model
    def create(self, vals):
        #Comprobamos si el codigo esta en uso, si lo esta y no es el mismo que el que ya tenia, lanzamos error
        if vals['default_code'] and vals['default_code'] != '':
            is_in_use = self._is_code_in_use(vals['default_code'])
            if is_in_use:
                if not self.default_code:
                    raise UserError(_("La referencia debe ser única por parámetro"))
                else:
                    vals['default_code'] = ''
        #Creación del parámetro
        res = super(LimsAnalysisParameter, self).create(vals)
        #si hay límites, los creamos
        if res and (self.limits_ids or res['limits_ids']):
            for limit in self.limits_ids:
                limit_to_create = self.env['lims.analysis.limit'].create(
                    {
                        'parameter_ids': res.id,
                        'type': limit.type,
                        'uom_id': limit.uom_id.id,
                        'parameter_uom': limit.parameter_uom,
                        'limit_result_line_ids': None,
                    }
                )
                #si hay líneas de límites, las creamos
                for limit_line in limit.limit_result_line_ids:
                    self.env['lims.analysis.limit.result.line'].create(
                        {
                            'parent_id': limit_to_create.id,
                            'operator_from': limit_line.operator_from,
                            'limit_value_from': limit_line.limit_value_from,
                            'operator_to': limit_line.operator_to,
                            'parameter_ids': res.id,
                            'limit_value_to': limit_line.limit_value_to,
                            'is_correct': limit_line.is_correct,
                            'is_present': limit_line.is_present,
                            'required_comment': limit_line.required_comment,
                            'type': limit_line.type,
                            'state': limit_line.state,
                            'message': limit_line.message,
                        }
                    )
        #si hay métodos, borramos los que tenemos en res y creamos los nuevos
        if res and (self.analytical_method_price_ids or res['analytical_method_price_ids']):
            methods = res['analytical_method_price_ids']
            #Eliminamos los métodos que ya teníamos
            res['analytical_method_price_ids'] = [(5, 0, 0)]
            method_ids = ()
            for method in methods:
                #Creamos el method
                new_method = self.env['analytical.method.price'].create(
                    {
                        'analytical_method_id': method.analytical_method_id.id,
                        'parameter_id': res.id,
                        'name': res.name + " - " + method.analytical_method_id.name,
                        'display_name': res.name + " - " + method.analytical_method_id.name,
                        'price': method.price,
                        'cost': method.cost,
                        'external_lab': method.external_lab.id,
                        'company_id': method.company_id.id,
                    }
                )
                res['analytical_method_price_ids'] = new_method
                method_ids = method_ids + (new_method.id,)
                #Por cada UDM, creamos un registo en parameter.analytical.method.price.uom, si no hay, genereamos uno si no existe
                if not self.parameter_uom and not res['parameter_uom']:
                    method_udm = self.env['parameter.analytical.method.price.uom'].search(
                        [("analytical_method_id", "=", new_method.id), ('uom_id', '=', False)])
                    if not method_udm:
                        self.env['parameter.analytical.method.price.uom'].create(
                            {
                                'analytical_method_id': new_method.id,
                                'uom_id': None,
                                'parent_id': None,
                            }
                        )
                else:
                    if res['parameter_uom']:
                        udms = res['parameter_uom']
                    else:
                        udms = self.parameter_uom
                    for udm in udms:
                        method_udm = self.env['parameter.analytical.method.price.uom'].search(
                            [("analytical_method_id", "=", new_method.id), ('uom_id', '=', udm.id)])
                        if not method_udm:
                            self.env['parameter.analytical.method.price.uom'].create(
                                {
                                    'analytical_method_id': new_method.id,
                                    'uom_id': udm.id,
                                    'parent_id': None,
                                }
                            )
            new_methods = self.env['analytical.method.price'].search([("id", "in", method_ids)])
            res['analytical_method_price_ids'] = new_methods
        else:
            for method in res['analytical_method_price_ids']:
                method.write(
                    {
                        'parameter_id': res.id,
                        'name': res.name + " - " + method.analytical_method_id.name,
                        'display_name': res.name + " - " + method.analytical_method_id.name,
                    }
                )
                if not self.parameter_uom:
                    method_udm = self.env['parameter.analytical.method.price.uom'].search(
                        [("analytical_method_id", "=", method.id), ('uom_id', '=', False)])
                    if not method_udm:
                        self.env['parameter.analytical.method.price.uom'].create(
                            {
                                'analytical_method_id': method.id,
                                'uom_id': None,
                                'parent_id': None,
                            }
                        )
                else:
                    for udm in self.parameter_uom:
                        method_udm = self.env['parameter.analytical.method.price.uom'].search(
                            [("analytical_method_id", "=", method.id), ('uom_id', '=', udm.id)])
                        if not method_udm:
                            self.env['parameter.analytical.method.price.uom'].create(
                                {
                                    'analytical_method_id': method.id,
                                    'uom_id': udm.id,
                                    'parent_id': None,
                                }
                            )
        return res

    def _get_limit_value_char(self, limits):
        limit_result_char = ""
        if limits:
            for parameter_line in limits:
                if parameter_line.type == "LIMIT" and parameter_line.state == "conform":
                    if parameter_line.operator_from not in ('', False):
                        limit_result_char = (
                            "{operator_from} {value_from: .2f}"
                        ).format(
                            operator_from=parameter_line.operator_from,
                            value_from=parameter_line.limit_value_from,
                        )
                    if parameter_line.operator_to not in ('', False):
                        limit_result_char = ("{operator_to} {value_to: .2f}").format(
                            operator_to=parameter_line.operator_to,
                            value_to=parameter_line.limit_value_to,
                        )
                if (
                    parameter_line.type == "BETWEEN"
                    and parameter_line.state == "conform"
                ):
                    limit_result_char = (
                        "Entre {value_from: .2f} y {value_to: .2f}"
                    ).format(
                        value_from=parameter_line.limit_value_from,
                        value_to=parameter_line.limit_value_to,
                    )
                if (
                    parameter_line.type == "ISPRESENT"
                    and parameter_line.state == "conform"
                ):
                    if parameter_line.is_present:
                        limit_result_char = "Present"
                    else:
                        limit_result_char = "Not Present"
                if (
                    parameter_line.type == "ISCORRECT"
                    and parameter_line.state == "conform"
                ):
                    if parameter_line.is_correct:
                        limit_result_char = "Correct"
                    else:
                        limit_result_char = "Not correct"

        return limit_result_char

    def _get_limit_value(self):
        limit_result = 0.00
        for parameter_line in self.limit_ids:
            if parameter_line.type == "LIMIT" and parameter_line.state == "conform":
                if parameter_line.limit_value_from > 0.0:
                    limit_result = parameter_line.limit_value_from
                else:
                    limit_result = parameter_line.limit_value_to
        return limit_result

    def _get_between_limit_value(self):
        between_limit_result = ""
        for parameter_line in self.limit_ids:
            if parameter_line.type == "BETWEEN" and parameter_line.state == "conform":
                between_limit_result = ("{value_from: .2f} and {value_to: .2f}").format(
                    value_from=parameter_line.limit_value_from,
                    value_to=parameter_line.limit_value_to,
                )
        return between_limit_result

    def _get_between_limit_value_char(self, limit):
        between_limit_result = ("Entre {value_from: .2f} y {value_to: .2f}").format(
                value_from=limit.limit_value_from,
                value_to=limit.limit_value_to,
            )
        return between_limit_result

    def _get_limit_comment(self, limit_ids, value=None, iscorrect_value=None, ispresent_value=None):
        comment_result = ""
        limit_result = ""
        between_result = ""
        is_present_result = ""
        is_correct_result = ""
        if value is None and iscorrect_value is None and ispresent_value is None:
            return comment_result
        if not limit_ids:
            return comment_result
        for parameter_result in limit_ids.limit_result_line_ids:
            limit_result_line = ""
            between_result_line = ""
            is_present_result_line = ""
            is_correct_result_line = ""
            if parameter_result.type == "LIMIT":
                limit_result_line = parameter_result.get_comment_when_limit(value)
                if limit_result_line != "":
                    limit_result = limit_result_line
            if parameter_result.type == "BETWEEN":
                between_result_line = parameter_result.get_comment_when_between(value)
                if between_result_line != "":
                    between_result = between_result_line
            if parameter_result.type == "ISPRESENT":
                is_present_result_line = parameter_result.get_comment_when_ispresent(
                    ispresent_value
                )
                if is_present_result_line != "":
                    is_present_result = is_present_result_line
            if parameter_result.type == "ISCORRECT":
                is_correct_result_line = parameter_result.get_comment_when_iscorrect(
                    iscorrect_value
                )
                if is_correct_result_line != "":
                    is_correct_result = is_correct_result_line
        if limit_result != "":
            comment_result = limit_result
        if between_result != "":
            comment_result = between_result
        if is_present_result != "":
            comment_result = is_present_result
        if is_correct_result != "":
            comment_result = is_correct_result
        return comment_result

    def get_anlysis_result(self, limit_ids, value=None, iscorrect_value=None, ispresent_value=None):
        result = ""
        limit_result = ""
        between_result = ""
        is_present_result = ""
        is_correct_result = ""
        eval_in_group = False
        if value is None and iscorrect_value is None and ispresent_value is None:
            return result, eval_in_group
        if not limit_ids:
            return result, eval_in_group
        for parameter_result in limit_ids.limit_result_line_ids:
            limit_result_line = ""
            between_result_line = ""
            is_present_result_line = ""
            is_correct_result_line = ""
            if parameter_result.type == "LIMIT":
                limit_result_line = parameter_result.get_result_when_limit(value)
                if limit_result_line != "":
                    limit_result = limit_result_line
            if parameter_result.type == "BETWEEN":
                between_result_line = parameter_result.get_result_when_between(value)
                # eval_in_group = True
                if between_result_line != "":
                    between_result = between_result_line
            if parameter_result.type == "ISPRESENT":
                is_present_result_line = parameter_result.get_result_when_ispresent(
                    ispresent_value
                )
                if is_present_result_line != "":
                    is_present_result = is_present_result_line
            if parameter_result.type == "ISCORRECT":
                is_correct_result_line = parameter_result.get_result_when_iscorrect(
                    iscorrect_value
                )
                if is_correct_result_line != "":
                    is_correct_result = is_correct_result_line
        if limit_result != "":
            result = limit_result
        if between_result != "":
            result = between_result
        if is_present_result != "":
            result = is_present_result
        if is_correct_result != "":
            result = is_correct_result
        if result == "conform":
            result = "pass"
        if result == "not_conform":
            result = "fail"
        return result, eval_in_group

    def _get_parameter_analysis_result(self, value=None, use_legislation=False):
        if value is None:
            return "fail"
        result = "fail"
        limit_result = ""
        between_result = ""
        is_present_result = ""
        is_correct_result = ""
        if use_legislation:
            limits = self.legislation_limit_ids
        else:
            limits = self.limit_ids
        for parameter_result in limits:
            limit_result_line = ""
            between_result_line = ""
            is_present_result_line = ""
            is_correct_result_line = ""
            if parameter_result.type == "LIMIT":
                limit_result_line = parameter_result.get_result_when_limit(value)
                if limit_result_line != "":
                    limit_result = limit_result_line
            if parameter_result.type == "BETWEEN":
                between_result_line = parameter_result.get_result_when_between(value)
                if between_result_line != "":
                    between_result = between_result_line
            if parameter_result.type == "ISPRESENT":
                is_present_result_line = parameter_result.get_result_when_ispresent(
                    value
                )
                if is_present_result_line != "":
                    is_present_result = is_present_result_line
            if parameter_result.type == "ISCORRECT":
                is_correct_result_line = parameter_result.get_result_when_iscorrect(
                    value
                )
                if is_correct_result_line != "":
                    is_correct_result = is_correct_result_line

        if limit_result != "":
            result = limit_result
        if between_result != "":
            result = between_result
        if is_present_result != "":
            result = is_present_result
        if is_correct_result != "":
            result = is_correct_result
        if result == "conform":
            result = "pass"
        if result == "not_conform":
            result = "fail"
        return result

    def _get_parameter_analysis_comment(self, value=None, use_legislation=False):
        if value is None:
            return ""
        comment_result = ""
        if use_legislation:
            limits = self.legislation_limit_ids
        else:
            limits = self.limit_ids
        for parameter_result in limits:
            limit_result_line = ""
            between_result_line = ""
            is_present_result_line = ""
            is_correct_result_line = ""
            if parameter_result.type == "LIMIT":
                limit_result_line = parameter_result.get_comment_when_limit(value)
                if limit_result_line != "":
                    comment_result = limit_result_line
            if parameter_result.type == "BETWEEN":
                between_result_line = parameter_result.get_comment_when_between(value)
                if between_result_line != "":
                    comment_result = between_result_line
            if parameter_result.type == "ISPRESENT":
                is_present_result_line = parameter_result.get_comment_when_ispresent(
                    value
                )
                if is_present_result_line != "":
                    comment_result = is_present_result_line
            if parameter_result.type == "ISCORRECT":
                is_correct_result_line = parameter_result.get_comment_when_iscorrect(
                    value
                )
                if is_correct_result_line != "":
                    comment_result = is_correct_result_line
        return comment_result

    def _get_iscorrect_default(self, limits):
        if limits:
            for parameter_line in limits:
                if parameter_line.type == "ISCORRECT" and parameter_line.state == "conform":
                    return parameter_line.is_correct
                return False
    def _get_ispresent_default(self, limits):
        if limits:
            for parameter_line in limits:
                if parameter_line.type == "ISPRESENT" and parameter_line.state == "conform":
                    return parameter_line.is_present
                return False

    @api.onchange("required_commentary")
    def _onchange_required_commentary(self):
        for limit_header in self.limit_ids:
            for limit_line in limit_header.limit_result_line_ids:
                limit_line.required_comment = self.required_commentary

    def unlink(self):
        for rec in self:
            for method in rec.analytical_method_price_ids:
                method.unlink()
            for limit in rec.limits_ids:
                for line in limit.limit_result_line_ids:
                    line.unlink()
                limit.unlink()
        return super().unlink()
