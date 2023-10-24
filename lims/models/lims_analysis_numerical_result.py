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
        "Analysis lims parameter",
    )

    lot_id = fields.Many2one(related="analysis_ids.lot_id", string="Sample num.")

    type_tags = fields.Many2one(related="parameter_ids.type_tags", string="Type tags")

    value = fields.Float(string="Value", store=True, default="", digits=(5, 8))

    parameter_uom = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
    )
    parameter_uom_all = fields.Many2many(
        related="parameter_ids.parameter_uom", string="parameter_uom"
    )

    limit_value_char = fields.Char(string="Limit Value", store=True)
    limit_value = fields.Float(string="Limit Value", store=True)
    legislation_limit_value = fields.Char(string="Between Limit Value", store=True)
    is_present = fields.Boolean(string="Is Present", store=True)
    is_correct = fields.Boolean(string="Is Correct", store=True)
    legislation_value = fields.Char(string="Corrected Value", store=True)
    data_sheet = fields.Char(string="Data sheet", store=True)
    # labeled = fields.Char(string="Labeled", store=True)
    # loq = fields.Float(string="LOQ", store=True)
    # corrected_loq = fields.Float(string="Corrected LOQ", store=True)
    # dil_fact = fields.Float(string="Dil. Fact.", store=True)
    reason = fields.Char(string="Reason", store=True)
    comment = fields.Char(string="Comment", store=True)
    required_comment = fields.Boolean(related="parameter_ids.required_comment", store=True)
    show_potency = fields.Boolean(related="parameter_ids.show_potency", store=True)
    change_value_for_comment = fields.Boolean(related="parameter_ids.change_value_for_comment", store=True)
    analytical_method_id = fields.Many2one(
        "lims.analytical.method", string="Método", ondelete="cascade", required=True
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
    # result_label = fields.Selection(
    #     [
    #         ("none", "Unrealized"),
    #         ("pass", "Approved"),
    #         ("fail", "Failed"),
    #         ("warning", "Warning"),
    #     ],
    #     string="Result label",
    #     default="none",
    #     store=True,
    # )
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
    to_invoice = fields.Boolean(string="billable", store=True, default=True)
    show_in_report = fields.Boolean(string="Show in Report", store=True, default=True)
    price = fields.Float("Price", store=True)
    use_acreditation = fields.Boolean(string="Use acreditation", store=True)
    use_normative = fields.Boolean(string="Use normative", store=True)

    def _get_parameter_values(self, vals):
        result_value = ""
        parameter = self.env["lims.analysis.parameter"].search(
            [("id", "=", vals.get("parameter_ids"))]
        )
        result_value = parameter._get_parameter_analysis_result(vals.get("value"))
        if result_value == "warning":
            result_value = "warning"
        if result_value == "not_conform":
            result_value = "fail"
        if result_value == "conform":
            result_value = "pass"
        return result_value

    def _get_value_result(self, value, use_legislation):
        for parameter in self.parameter_ids:
            return parameter._get_parameter_analysis_result(value, use_legislation)

    def _get_comment_result(self, value, use_legislation):
        for parameter in self.parameter_ids:
            return parameter._get_parameter_analysis_comment(value, use_legislation)

    @api.onchange("value")
    def _onchange_value(self):
        for line in self:
            if self.is_correct:
                print("*" * 50)
                print("hay correct")
                print("*" * 50)
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
                technical_result = line.parameter_ids.get_anlysis_result(limit_ids_technical, value=line.value)
                technical_comment = line.parameter_ids._get_limit_comment(limit_ids_technical, value=line.value)
                if technical_result != "":
                    line.result_datasheet = technical_result
                #legislation
                limit_ids_legislation = limit_ids_filter.filtered(lambda r: r.type == 'legislation')
                legislation_result = line.parameter_ids.get_anlysis_result(limit_ids_legislation, value=line.value)
                legislation_comment = line.parameter_ids._get_limit_comment(limit_ids_legislation, value=line.value)
                if legislation_result != "":
                    line.result_legislation = legislation_result
                # #Label
                # limit_ids_label = limit_ids_filter.filtered(lambda r: r.type == 'label')
                # label_result = line.parameter_ids.get_anlysis_result(limit_ids_label, value=line.value)
                # label_comment = line.parameter_ids._get_limit_comment(limit_ids_label, value=line.value)
                # if label_result != "":
                #     line.result_label = label_result
                # comment = technical_comment
                # if legislation_result in ('fail', 'warning', None):
                #     comment = legislation_comment
                # elif label_result in ('fail', 'warning', None):
                #     comment = label_comment
                # if line.parameter_ids.required_comment:
                #     line.comment = comment

    @api.onchange("is_present")
    def _onchange_is_present(self):
        technical_comment = ""
        for line in self:
            if self.is_correct:
                print("*" * 50)
                print("hay correct")
                print("*" * 50)
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
                                technical_result = line.parameter_ids.get_anlysis_result(limit_ids_technical,
                                                                                         ispresent_value=line.is_present)
                                technical_comment = line.parameter_ids._get_limit_comment(limit_ids_technical,
                                                                                          ispresent_value=line.is_present)
                                comment = technical_comment
                                if technical_result != "":
                                    line.result_datasheet = technical_result
                        #Legislation
                        limit_ids_legislation = limit_ids_filter.filtered(lambda r: r.type == 'legislation')
                        if limit_ids_legislation:
                            limits_legislation = self.env['lims.analysis.limit.result.line'].search(
                                [
                                    ('parent_id', '=', limit_ids_legislation[0].id),
                                ]
                            )
                            if limits_legislation and limits_legislation[0].type == 'ISPRESENT':
                                legislation_result = line.parameter_ids.get_anlysis_result(limit_ids_legislation,
                                                                           ispresent_value=line.is_present)
                                legislation_comment = line.parameter_ids._get_limit_comment(limit_ids_legislation,
                                                                                            ispresent_value=line.is_present)
                                if legislation_result != "":
                                    line.result_legislation = legislation_result
                                    if legislation_result in ('fail', 'warning', None):
                                        comment = legislation_comment
                            if line.parameter_ids.required_comment:
                                line.comment = comment

    @api.onchange("is_correct")
    def _onchange_is_correct(self):

        for line in self:
            if self.is_correct:
                print("*" * 50)
                print("hay correct")
                print("*" * 50)
                if self.data_sheet:
                    line.result_datasheet = "pass"
                if self.legislation_value:
                    line.result_legislation = "pass"
            else:
                self._onchange_is_present()
                self._onchange_value()

    @api.model
    def create(self, vals):
        parameter = self.env["lims.analysis.parameter"].search(
            [("id", "=", vals.get("parameter_ids"))]
        )
        # if not vals["result"]:
        #     vals["result"] = self._get_parameter_values(vals)
        # if not vals["limit_value_char"]:
        #     vals["limit_value_char"] = parameter._get_limit_value_char()
        # if not vals["legislation_limit_value"]:
        #     vals["legislation_limit_value"] = parameter._get_between_limit_value()
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
