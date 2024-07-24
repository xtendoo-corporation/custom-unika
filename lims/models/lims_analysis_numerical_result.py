# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class LimsAnalysisNumericalResult(models.Model):
    _name = "lims.analysis.numerical.result"
    _description = "LIMS Analysis Numerical Result"

    analysis_ids = fields.Many2one(
        "lims.analysis.line",
        "Analysis lims Line",
    )
    parameter_ids = fields.Many2one(
        "lims.analysis.parameter",
        "Analysis lims parameter line",
    )
    parameter_extra_comment = fields.Many2one(
        "parameter.extra.comment",
        "Comentario Extra",
    )

    def get_name_with_index(self, indexed_comments):
        self.ensure_one()
        if self.parameter_extra_comment:
            for key, value in indexed_comments.items():
                print("value:", value)
                if self.parameter_extra_comment.name == value:
                    return f"{self.parameter_ids.name}{key}"
        return self.parameter_ids.name

    lot_id = fields.Many2one(related="analysis_ids.lot_id", string="Sample num.")
    def _compute_parameter_nethod(self):
        for line in self:
            method = ""
            purchase = self.env['purchase.order'].search([('name', '=', line.analysis_ids.stock_move_line_id.move_id.picking_id.origin)])
            if purchase:
                sale = self.env['sale.order'].search([('name', '=', purchase.origin)])
                if sale:
                    for sale_line in sale.order_line:
                        for parametro in sale_line.parameter_ids:
                            if parametro.analytical_method_id.parameter_id.name == line.parameter_ids.name:
                                method = parametro.analytical_method_id.analytical_method_id.name
            line.method = method



    method = fields.Char(string="Método", compute="_compute_parameter_nethod")

    type_tags = fields.Many2one(related="parameter_ids.type_tags", string="Type tags")

    value = fields.Float(string="Value", store=True, default="", digits=(5, 8))

    parameter_uom = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
    )
    parameter_uom_all = fields.Many2many(
        related="parameter_ids.parameter_uom", string="parameter_uom"
    )

    limit_value_char = fields.Char(string="Valor limite texto", store=True)
    limit_value = fields.Float(string="Limit Value", store=True)
    legislation_limit_value = fields.Char(string="Between Limit Value", store=True)
    is_present = fields.Boolean(string="Is Present", store=True)
    is_correct = fields.Boolean(string="Is Correct", store=True)
    legislation_value = fields.Char(string="Corrected Value", store=True)
    data_sheet = fields.Char(string="Data sheet", store=True)
    reason = fields.Char(string="Reason", store=True)
    comment = fields.Char(string="Comment", store=True)
    valor_informe = fields.Char(string="Valor informe", store=True)
    print_valor_informe = fields.Boolean(string="Imprimir valor informe", store=True)
    lot_name = fields.Char(
        string="Lote",
        copy=False,
    )
    sample_sub_number = fields.Integer(string="SubNúmero de muestra", store=True)
    @api.depends("value", "show_potency")
    def _compute_valor_potencia(self):
        for line in self:
            valor_potencia = ""
            valor_exponente = ""
            if line.show_potency and line.value != 0.0:
                valor_potencia = f"{line.value:.1E}"
                valor_potencia = str(valor_potencia)
                if "E" in valor_potencia:
                    valor_exponente = valor_potencia.split("E")[1]
            line.valor_potencia = valor_potencia
            line.valor_exponente = valor_exponente

    valor_potencia = fields.Char(string="Valor Potencia", compute="_compute_valor_potencia")
    valor_exponente = fields.Char(string="Valor Exponente", compute="_compute_valor_potencia")
    required_comment = fields.Boolean(related="parameter_ids.required_comment", store=True)
    show_potency = fields.Boolean(related="parameter_ids.show_potency", store=True)
    show_description = fields.Boolean(related="parameter_ids.show_description", store=True)
    change_value_for_comment = fields.Boolean(related="parameter_ids.change_value_for_comment", store=True)
    analytical_method_id = fields.Many2one(
        "lims.analytical.method", string="Método analítico", ondelete="cascade", required=True
    )
    result_legislation = fields.Selection(
        [
            ("none", "Unrealized"),
            ("pass", "Approved"),
            ("fail", "Failed"),
            ("warning", "Warning"),
        ],
        string="Result Legislation",
        default="none",
        store=True,
    )
    result_datasheet = fields.Selection(
        [
            ("none", "Unrealized"),
            ("pass", "Approved"),
            ("fail", "Failed"),
            ("warning", "Warning"),
        ],
        string="Result dataSheet",
        default="none",
        store=True,
    )
    global_result = fields.Selection(
        [
            ("none", "Unrealized"),
            ("pass", "Approved"),
            ("fail", "Failed"),
            ("warning", "Warning"),
        ],
        string="Global Result",
        default="none",
        store=True,
    )
    legislation_used_name = fields.Char(
        string="Legislación",
    )
    to_invoice = fields.Boolean(string="billable", store=True, default=True)
    show_in_report = fields.Boolean(string="Show in Report", store=True, default=True)
    price = fields.Float("Price", store=True)
    use_acreditation = fields.Boolean(string="Use acreditation", store=True)
    use_normative = fields.Boolean(string="Use normative", store=True)
    eval_in_group = fields.Boolean(string="Eval in group", store=True)

    def _get_parameter_values(self, vals):
        parameter = self.env["lims.analysis.parameter"].browse(vals.get("parameter_ids"))
        result_value = parameter._get_parameter_analysis_result(vals.get("value"))
        if result_value in ["warning", "not_conform", "conform"]:
            result_value = {"warning": "warning", "not_conform": "fail", "conform": "pass"}.get(result_value, "")
        return result_value

    def _get_value_result(self, value, use_legislation):
        for parameter in self.parameter_ids:
            return parameter._get_parameter_analysis_result(value, use_legislation)

    def _get_comment_result(self, value, use_legislation):
        for parameter in self.parameter_ids:
            return parameter._get_parameter_analysis_comment(value, use_legislation)

    @api.onchange("value")
    def _onchange_value(self):
        self._compute_valor_potencia()
        for line in self:
            if self.is_correct:
                if self.data_sheet:
                    line.result_datasheet = "pass"
                if self.legislation_value:
                    line.result_legislation = "pass"
            else:
                limit_ids_filter = line.parameter_ids.limits_ids.filtered(lambda r: r.uom_id == line.parameter_uom)
                #technical
                #Elección de si esta usa acreditación o no
                if line.use_acreditation:
                    limit_ids_technical = self.env["lims.analysis.normative"].search(
                        [
                            ("parameter_ids", "=", line.parameter_ids.id),
                            ("is_acreditation", "=", True),
                            ("uom_id", "=", line.parameter_uom.id)
                        ]
                    )
                elif line.use_normative:
                    limit_ids_technical = self.env["lims.analysis.normative"].search(
                        [
                            ("parameter_ids", "=", line.parameter_ids.id),
                            ("is_acreditation", "=", False),
                            ("uom_id", "=", line.parameter_uom.id)
                        ]
                    )
                else:
                    limit_ids_technical = limit_ids_filter.filtered(lambda r: r.type == 'technical')
                technical_result, eval_in_group = (line.parameter_ids.get_anlysis_result(limit_ids_technical, value=line.value))
                technical_comment = line.parameter_ids._get_limit_comment(limit_ids_technical, value=line.value)
                if technical_result != "":
                    line.result_datasheet = technical_result

                #legislation
                limit_ids_legislation = limit_ids_filter.filtered(lambda r: r.type == 'legislation')
                legislation_result, eval_in_group = (line.parameter_ids.get_anlysis_result(limit_ids_legislation, value=line.value))
                legislation_comment = line.parameter_ids._get_limit_comment(limit_ids_legislation, value=line.value)
                if legislation_result != "":
                    line.result_legislation = legislation_result
                    line.comment = legislation_comment
                    line.eval_in_group = eval_in_group

    def _update_global_result(self, result):
        analysis_id = str(self.analysis_ids.id)
        partes = analysis_id.split("_")
        analysis_id = partes[-1]
        analysis_id = int(analysis_id)
        line_id = str(self.id)
        partes_line = line_id.split("_")
        line_id = partes_line[-1]
        line_id = int(line_id)
        related_lines = self.env['lims.analysis.numerical.result'].search([
            ('parameter_ids', '=', self.parameter_ids.id),
            ('analysis_ids', '=', analysis_id),
            ('id', '!=', line_id)
        ])
        for line in related_lines:
            if line.global_result != result:
                line.global_result = result

    def get_fail_sample_num(self):
        analysis_id = str(self.analysis_ids.id)
        partes = analysis_id.split("_")
        analysis_id = partes[-1]
        analysis_id = int(analysis_id)
        line_id = str(self.id)
        partes_line = line_id.split("_")
        line_id = partes_line[-1]
        line_id = int(line_id)
        related_lines = self.env['lims.analysis.numerical.result'].search([
            ('parameter_ids', '=', self.parameter_ids.id),
            ('analysis_ids', '=', analysis_id),
            ('id', '!=', line_id)
        ])
        fail_num = sum(1 for line in related_lines if line.eval_in_group == True)
        return fail_num

    def _set_global_result(self, max_samples, max_samples_act):
        analysis_id = str(self.analysis_ids.id)
        partes = analysis_id.split("_")
        analysis_id = partes[-1]
        analysis_id = int(analysis_id)
        line_id = str(self.id)
        partes_line = line_id.split("_")
        line_id = partes_line[-1]
        line_id = int(line_id)
        related_lines = self.env['lims.analysis.numerical.result'].search([
            ('parameter_ids', '=', self.parameter_ids.id),
            ('analysis_ids', '=', analysis_id),
            ('id', '!=', line_id)
        ])
        for line in related_lines:
            if max_samples_act > max_samples:
                line.global_result = 'fail'
            else:
                line.global_result = 'pass'

    @api.onchange("is_present")
    def _onchange_is_present(self):
        technical_comment = ""
        for line in self:
            if self.is_correct:
                if self.data_sheet:
                    line.result_datasheet = "pass"
                if self.legislation_value:
                    line.result_legislation = "pass"
            else:
                if line.value == 0.0:
                    limit_ids_filter = line.parameter_ids.limits_ids.filtered(lambda r: r.uom_id == line.parameter_uom)
                    for limit in limit_ids_filter:
                        #technical
                        limit_ids_technical = limit_ids_filter.filtered(lambda r: r.type == 'technical')
                        if limit_ids_technical:
                            limits_technical = self.env['lims.analysis.limit.result.line'].search(
                                [
                                    ('parent_id', '=', limit_ids_technical[0].id),
                                ]
                            )

                            if limits_technical and limits_technical[0].type == 'ISPRESENT':
                                technical_result, eval_in_group = line.parameter_ids.get_anlysis_result(limit_ids_technical,
                                                                                         ispresent_value=line.is_present)
                                technical_comment = line.parameter_ids._get_limit_comment(limit_ids_technical,
                                                                                          ispresent_value=line.is_present)
                                comment = technical_comment
                                if technical_result != "":
                                    line.result_datasheet = technical_result
                        #Legislation
                        limit_ids_legislation = limit_ids_filter.filtered(lambda r: r.type == 'legislation')
                        comment = ""
                        if limit_ids_legislation:
                            limits_legislation = self.env['lims.analysis.limit.result.line'].search(
                                [
                                    ('parent_id', '=', limit_ids_legislation[0].id),
                                ]
                            )
                            if limits_legislation and limits_legislation[0].type == 'ISPRESENT':
                                legislation_result, eval_in_group = line.parameter_ids.get_anlysis_result(limit_ids_legislation,
                                                                           ispresent_value=line.is_present)
                                legislation_comment = line.parameter_ids._get_limit_comment(limit_ids_legislation,
                                                                                            ispresent_value=line.is_present)
                                if legislation_result != "":
                                    line.result_legislation = legislation_result
                                    if legislation_result in ('fail', 'warning', None, 'pass'):
                                        comment = legislation_comment
                            if line.parameter_ids.required_comment:
                                line.comment = comment

    @api.onchange("is_correct")
    def _onchange_is_correct(self):
        print("*"*50)
        print("onchange")

        for line in self:
            if self.parameter_uom:
                limit = self.parameter_ids.limits_ids.filtered(lambda r: r.uom_id == self.parameter_uom)
            else:
                limit = self.parameter_ids.limits_ids
                print("limit", limit)
            for limit_line in limit.limit_result_line_ids:
                print("limit_line", limit_line)
                if limit_line.is_correct == self.is_correct:
                    line.comment = limit_line.message
                    line.valor_informe = limit_line.message
            if self.is_correct:
                if self.legislation_value:
                    line.result_legislation = "pass"
            else:
                if self.legislation_value:
                    line.result_legislation = "fail"
        print("*" * 50)
    @api.model
    def create(self, vals):
        result = super(LimsAnalysisNumericalResult, self).create(vals)
        return result
    def get_result_when_limit(self, parameter_result, value):
        result = ""
        if parameter_result.operator_from is not False:
            if (
                parameter_result.operator_from == ">"
                and value > parameter_result.limit_value_from
            ):
                result = parameter_result.state
            if (
                parameter_result.operator_from == ">="
                and value >= parameter_result.limit_value_from
            ):
                result = parameter_result.state
            if (
                parameter_result.operator_from == "="
                and value == parameter_result.limit_value_from
            ):
                result = parameter_result.state
        else:
            if (
                parameter_result.operator_to == "<"
                and value < parameter_result.limit_value_to
            ):
                result = parameter_result.state
            if (
                parameter_result.operator_to == "<="
                and value <= parameter_result.limit_value_to
            ):
                result = parameter_result.state
            if (
                parameter_result.operator_to == "="
                and value == parameter_result.limit_value_to
            ):
                result = parameter_result.state
        return result

    def get_result_when_between(self, value):
        result = ""
        result_from = False
        result_to = False
        if self.operator_from is not False:
            if self.operator_from == ">" and value > self.limit_value_from:
                result_from = True
            if self.operator_from == ">=" and value >= self.limit_value_from:
                result_from = True
            if self.operator_from == "=" and value == self.limit_value_from:
                result_from = True
        if self.operator_to is not False:
            if self.operator_to == "<" and value < self.limit_value_to:
                result_to = True
            if self.operator_to == "<=" and value <= self.limit_value_to:
                result_to = True
            if self.operator_to == "=" and value == self.limit_value_to:
                result_to = True
        if result_from is True and result_to is True:
            result = self.state
        return result
