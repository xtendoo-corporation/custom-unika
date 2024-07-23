# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class LimsAnalysisParameterLimitResultLine(models.Model):
    _name = "lims.analysis.limit.result.line"
    _description = "parameter LIMS Limit Result Line"
    _order = 'sequence'
    sequence = fields.Integer(string='Secuencia', help='Define el orden de las líneas')


    parent_id = fields.Many2one(
        "lims.analysis.limit",
        "Analysis lims parameter",
    )
    operator_from = fields.Selection(
        [
            (">", "Mayor que"),
            (">=", "Mayor o igual que"),
            ("=", "Igual que"),
        ],
        "Operator From",
    )
    limit_value_from = fields.Float(string="Limit Value From", store=True)
    operator_to = fields.Selection(
        [
            ("<", "Menor que"),
            ("<=", "Menor o igual que"),
            ("=", "Igual que"),
        ],
        "Operator to",
    )
    parameter_ids = fields.Many2one(
        "lims.analysis.parameter",
        "Analysis lims parameter",
    )
    parameter_legislation_ids = fields.Many2one(
        "lims.analysis.parameter",
        "Analysis lims parameter",
    )
    limit_value_to = fields.Float(string="Limit Value to", store=True)
    is_correct = fields.Boolean(string="Is Correct", store=True)
    is_present = fields.Boolean(string="Is Present", store=True)
    required_comment = fields.Boolean(related='parent_id.parameter_ids.required_comment', store=True)
    type = fields.Selection(
        [("LIMIT", "Límite"), ("BETWEEN", "Entre"), ("ISPRESENT", "Está presente"), ("ISCORRECT", "Es correcto")],
        "Type",
        store=True,
    )
    state = fields.Selection(
        [
            ("conform", "Conform"),
            ("warning", "Warning"),
            ("not_conform", "Not Conform"),
        ],
        "State",
    )
    message = fields.Char(string="Message", store=True)


    @api.model
    def create(self, vals):
        parent_id = vals.get("parent_id") or self.env.context.get("parent_id")
        required_comment = vals.get("required_comment") or self.env.context.get("required_comment")
        vals.update({
            "parent_id": parent_id,
            "required_comment": required_comment,
        })
        return super(LimsAnalysisParameterLimitResultLine, self).create(vals)

    def _get_required_comment(self):
        if self.parameter_ids:
            self.required_comment = self.parameter_ids.required_commentary
        if self.parameter_legislation_ids:
            self.required_comment = self.parameter_legislation_ids.required_commentary

    def get_comment_when_between(self, value):
        comment = ""
        result_from = (
                (self.operator_from == ">" and value > self.limit_value_from) or
                (self.operator_from == ">=" and value >= self.limit_value_from) or
                (self.operator_from == "=" and value == self.limit_value_from)
        )
        result_to = (
                (self.operator_to == "<" and value < self.limit_value_to) or
                (self.operator_to == "<=" and value <= self.limit_value_to) or
                (self.operator_to == "=" and value == self.limit_value_to)
        )
        if result_from and result_to:
            comment = self.message
        return comment

    def get_comment_when_limit(self, value):
        comment = ""
        if self.operator_from is not False:
            if (
                    (self.operator_from == ">" and value > self.limit_value_from) or
                    (self.operator_from == ">=" and value >= self.limit_value_from) or
                    (self.operator_from == "=" and value == self.limit_value_from)
            ):
                comment = self.message
        else:
            if (
                    (self.operator_to == "<" and value < self.limit_value_to) or
                    (self.operator_to == "<=" and value <= self.limit_value_to) or
                    (self.operator_to == "=" and value == self.limit_value_to)
            ):
                comment = self.message
        return comment

    def get_comment_when_ispresent(self, value):
        return self.message if value == self.is_present else ""
    def get_comment_when_is_correct(self, value):
        return self.message if value == self.is_correct else ""

    def get_result_when_between(self, value):
        result_from = (
                (self.operator_from == ">" and value > self.limit_value_from) or
                (self.operator_from == ">=" and value >= self.limit_value_from) or
                (self.operator_from == "=" and value == self.limit_value_from)
        )
        result_to = (
                (self.operator_to == "<" and value < self.limit_value_to) or
                (self.operator_to == "<=" and value <= self.limit_value_to) or
                (self.operator_to == "=" and value == self.limit_value_to)
        )

        result = self.state if result_from and result_to else ""
        return result

    def get_result_when_limit(self, value):
        result = ""
        if self.operator_from is not False:
            if (
                    (self.operator_from == ">" and value > self.limit_value_from) or
                    (self.operator_from == ">=" and value >= self.limit_value_from) or
                    (self.operator_from == "=" and value == self.limit_value_from)
            ):
                result = self.state
        else:
            if (
                    (self.operator_to == "<" and value < self.limit_value_to) or
                    (self.operator_to == "<=" and value <= self.limit_value_to) or
                    (self.operator_to == "=" and value == self.limit_value_to)
            ):
                result = self.state
        return result

    def get_result_when_ispresent(self, value):
        return self.state if value == self.is_present else ""

    def get_result_when_iscorrect(self, value):
        return self.state if value == self.is_correct else ""

    def get_comment_when_between(self, value):
        result_from = (
                (self.operator_from == ">" and value > self.limit_value_from) or
                (self.operator_from == ">=" and value >= self.limit_value_from) or
                (self.operator_from == "=" and value == self.limit_value_from)
        )
        result_to = (
                (self.operator_to == "<" and value < self.limit_value_to) or
                (self.operator_to == "<=" and value <= self.limit_value_to) or
                (self.operator_to == "=" and value == self.limit_value_to)
        )
        return self.message if result_from and result_to else ""

    def get_comment_when_limit(self, value):
        if self.operator_from is not False:
            if (
                    (self.operator_from == ">" and value > self.limit_value_from) or
                    (self.operator_from == ">=" and value >= self.limit_value_from) or
                    (self.operator_from == "=" and value == self.limit_value_from)
            ):
                return self.message
        else:
            if (
                    (self.operator_to == "<" and value < self.limit_value_to) or
                    (self.operator_to == "<=" and value <= self.limit_value_to) or
                    (self.operator_to == "=" and value == self.limit_value_to)
            ):
                return self.message

        return ""

    def get_comment_when_ispresent(self, value):
        return self.message if value == self.is_present else ""

    def get_comment_when_iscorrect(self, value):
        return self.message if value == self.is_correct else ""

    def get_correct_limit(self):
        limit = ""
        if self.state == 'conform':
            if self.type == "ISPRESENT":
                limit = "Presencia" if self.is_present else "Ausencia"
            elif self.type == "ISCORRECT":
                limit = self.parent_id.parameter_ids.limit_value_char if self.parent_id.parameter_ids.limit_value_char else ""
            elif self.type == "LIMIT":
                limit = self._get_limit_value_char()
            elif self.type == "BETWEEN":
                limit = self._get_between_limit_value()
        return limit

    def _get_limit_value_char(self):
        limit_char = ""
        value = ""
        if self.operator_from not in ('', False):
            limit_char = "{operator_from} {value_from:.2f}".format(
                operator_from=self.operator_from,
                value_from=self.limit_value_from,
            )
            value = self.limit_value_from
        if self.operator_to not in ('', False):
            limit_char = "{operator_to} {value_to:.2f}".format(
                operator_to=self.operator_to,
                value_to=self.limit_value_to,
            )
            value = self.limit_value_to
        if self.parent_id.parameter_ids.show_potency:
            superindice_unicode = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
            value = "{:.1E}".format(value)
            exponent_position = value.find("E")
            parte_entera = value[0:exponent_position]
            exponente = value[exponent_position + 1:]
            exponente_superindice = exponente.translate(superindice_unicode)
            value = "{}x10{}".format(parte_entera, exponente_superindice)
            limit_char = "{operator_to} {value_to}".format(
                operator_to=self.operator_to,
                value_to=value,
            )
        return limit_char

    def _get_between_limit_value(self):
        superindice_unicode = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
        if self.parent_id.parameter_ids.show_potency:
            value_from = "{:.1E}".format(self.limit_value_from)
            exponent_position = value_from.find("E")
            parte_entera_from = value_from[0:exponent_position]
            exponente_from = value_from[exponent_position + 1:]
            if exponente_from.find("+") == 0:
                exponente_from = exponente_from[1:]
                if exponente_from.find("0") == 0:
                    exponente_from = exponente_from[1:]
            exponente_superindice_from = exponente_from.translate(superindice_unicode)
            value_from = "{}x10{}".format(parte_entera_from, exponente_superindice_from)

            value_to = "{:.1E}".format(self.limit_value_to)
            exponent_position = value_to.find("E")
            parte_entera_to = value_to[0:exponent_position]
            exponente_to = value_to[exponent_position + 1:]
            if exponente_to.find("+") == 0:
                exponente_to = exponente_to[1:]
                if exponente_to.find("0") == 0:
                    exponente_to = exponente_to[1:]
            exponente_superindice_to = exponente_to.translate(superindice_unicode)
            value_to = "{}x10{}".format(parte_entera_to, exponente_superindice_to)
            between_limit_result = "{operator_from} {value_from} y {operator_to} {value_to}".format(
                operator_from=self.operator_from,
                value_from=value_from,
                operator_to=self.operator_to,
                value_to=value_to,
            )
        else:
            between_limit_result = "{operator_from} {value_from:.2f} y {operator_to} {value_to:.2f}".format(
                operator_from=self.operator_from,
                value_from=self.limit_value_from,
                operator_to=self.operator_to,
                value_to=self.limit_value_to,
            )
        return between_limit_result

