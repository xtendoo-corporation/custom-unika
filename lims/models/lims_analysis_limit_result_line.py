# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class LimsAnalysisParameterLimitResultLine(models.Model):
    _name = "lims.analysis.limit.result.line"
    _description = "parameter LIMS Limit Result Line"
    _order = 'sequence'
    sequence = fields.Integer(string='Secuencia', help='Define el orden de las líneas')

    # limit_result_id = fields.Many2one('lims.analysis.limit.result', string='Limit Result', required=True, ondelete='cascade', index=True,
    #                            copy=False)
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

    #is_legislation = fields.Boolean(string="Legislación", store=True)

    @api.model
    def create(self, vals):
        if not vals.get("parent_id"):
            vals["parent_id"] = self.env.context.get("parent_id")
            if not vals.get("required_comment"):
                vals["required_comment"] = self.env.context.get("required_comment")
        return super(LimsAnalysisParameterLimitResultLine, self).create(vals)

    def _get_required_comment(self):
        if self.parameter_ids:
            self.required_comment = self.parameter_ids.required_commentary
        if self.parameter_legislation_ids:
            self.required_comment = self.parameter_legislation_ids.required_commentary

    def get_comment_when_between(self, value):
        comment = ""
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
            comment = self.message
        return comment

    def get_comment_when_limit(self, value):
        comment = ""
        if self.operator_from is not False:
            if self.operator_from == ">" and value > self.limit_value_from:
                comment = self.message
            if self.operator_from == ">=" and value >= self.limit_value_from:
                comment = self.message
            if self.operator_from == "=" and value == self.limit_value_from:
                comment = self.message
        else:
            if self.operator_to == "<" and value < self.limit_value_to:
                comment = self.message
            if self.operator_to == "<=" and value <= self.limit_value_to:
                comment = self.message
            if self.operator_to == "=" and value == self.limit_value_to:
                comment = self.message
        return comment

    def get_comment_when_ispresent(self, value):
        comment = ""
        if value == self.is_present:
            comment = self.message
        return comment

    def get_comment_when_iscorrect(self, value):
        comment = ""
        if value == self.is_correct:
            comment = self.message
        return comment

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

    def get_result_when_limit(self, value):
        result = ""
        if self.operator_from is not False:
            if self.operator_from == ">" and value > self.limit_value_from:
                result = self.state
            if self.operator_from == ">=" and value >= self.limit_value_from:
                result = self.state
            if self.operator_from == "=" and value == self.limit_value_from:
                result = self.state
        else:
            if self.operator_to == "<" and value < self.limit_value_to:
                result = self.state
            if self.operator_to == "<=" and value <= self.limit_value_to:
                result = self.state
            if self.operator_to == "=" and value == self.limit_value_to:
                result = self.state
        return result

    def get_result_when_ispresent(self, value):
        result = ""
        if value == self.is_present:
            result = self.state
        return result

    def get_result_when_iscorrect(self, value):
        result = ""
        if value == self.is_correct:
            result = self.state
        return result

    def get_comment_when_between(self, value):
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
            result = self.message
        return result

    def get_comment_when_limit(self, value):
        result = ""
        if self.operator_from is not False:
            if self.operator_from == ">" and value > self.limit_value_from:
                result = self.message
            if self.operator_from == ">=" and value >= self.limit_value_from:
                result = self.message
            if self.operator_from == "=" and value == self.limit_value_from:
                result = self.message
        else:
            if self.operator_to == "<" and value < self.limit_value_to:
                result = self.message
            if self.operator_to == "<=" and value <= self.limit_value_to:
                result = self.message
            if self.operator_to == "=" and value == self.limit_value_to:
                result = self.message
        return result

    def get_comment_when_ispresent(self, value):
        result = ""
        if value == self.is_present:
            result = self.message
        return result

    def get_comment_when_iscorrect(self, value):
        result = ""
        if value == self.is_correct:
            result = self.message
        return result

    def get_correct_limit(self):
        limit = ""
        if self.type == "ISPRESENT" and self.state == 'conform':
            if self.is_present:
                limit = "Presente"
            else:
                limit = "Not Present"
        elif self.type == "ISCORRECT" and self.state == 'conform':
            if self.is_correct:
                limit = "Correct"
            else:
                limit = "Not Correct"
        elif self.type == "LIMIT" and self.state == 'conform':
            limit = self._get_limit_value_char()
        elif self.type == "BETWEEN" and self.state == 'conform':
            limit = self._get_between_limit_value()
        return limit

    def _get_limit_value_char(self):
        limit_char = ""
        value = ""
        if self.operator_from not in ('', False):

            limit_char = (
                "{operator_from} {value_from: .2f}"
            ).format(
                operator_from=self.operator_from,
                value_from=self.limit_value_from,
            )
            value = self.limit_value_from
        if self.operator_to not in ('', False):

            limit_char = ("{operator_to} {value_to: .2f}").format(
                operator_to=self.operator_to,
                value_to=self.limit_value_to,
            )
            value = self.limit_value_to
        if self.parent_id.parameter_ids.show_potency:
            superindice_unicode = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
            value = (f"{value:.1E}")
            exponent_position = value.find("E")
            parte_entera = value[0:exponent_position]
            exponente = value[exponent_position + 1:]
            if exponente.find("+") == 0:
                exponente = exponente[1:]
                if exponente.find("0") == 0:
                    exponente = exponente[1:]
            exponente_superindice = exponente.translate(superindice_unicode)
            value = "{}x10{}".format(parte_entera, exponente_superindice)
            limit_char = ("{operator_to} {value_to:}").format(
                operator_to=self.operator_to,
                value_to=value,
            )

        return limit_char

    def _get_between_limit_value(self):
        if self.parent_id.parameter_ids.show_potency:
            superindice_unicode = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
            value_from = (f"{self.limit_value_from:.1E}")
            exponent_position = value_from.find("E")
            parte_entera_from = value_from[0:exponent_position]
            exponente_from = value_from[exponent_position+1:]
            if exponente_from.find("+") == 0:
                exponente_from = exponente_from[1:]
                if exponente_from.find("0") == 0:
                    exponente_from = exponente_from[1:]
            exponente_superindice_from = exponente_from.translate(superindice_unicode)
            value_from = "{}x10{}".format(parte_entera_from, exponente_superindice_from)
            value_to = (f"{self.limit_value_to:.1E}")
            exponent_position = value_to.find("E")
            parte_entera_to = value_to[0:exponent_position]
            exponente_to = value_to[exponent_position+1:]
            if exponente_to.find("+") == 0:
                exponente_to = exponente_to[1:]
                if exponente_to.find("0") == 0:
                    exponente_to = exponente_to[1:]
            exponente_superindice_to = exponente_to.translate(superindice_unicode)
            value_to = "{}x10{}".format(parte_entera_to, exponente_superindice_to)
            between_limit_result = ("{operator_from} {value_from} y {operator_to} {value_to}").format(
                operator_from=self.operator_from,
                value_from=value_from,
                operator_to=self.operator_to,
                value_to=value_to,
            )
        else:
            between_limit_result = ("{operator_from} {value_from: .2f} y {operator_to} {value_to: .2f}").format(
                operator_from=self.operator_from,
                value_from=self.limit_value_from,
                operator_to=self.operator_to,
                value_to=self.limit_value_to,
            )
        return between_limit_result

