# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class LimsAnalysisParameterNormativeResultLine(models.Model):
    _name = "lims.analysis.normative.result.line"
    _description = "parameter LIMS normative Result Line"
    _order = 'sequence'

    sequence = fields.Integer(string='Secuencia', help='Define el orden de las líneas')

    parent_id = fields.Many2one(
        "lims.analysis.normative",
        "Analysis lims parameter parent",
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
        "Analysis lims parameter legislation",
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
        if not vals.get("parent_id"):
            vals.setdefault("parent_id", self.env.context.get("parent_id"))
            vals.setdefault("required_comment", self.env.context.get("required_comment"))

        return super(LimsAnalysisParameterNormativeResultLine, self).create(vals)
    def _get_required_comment(self):
        if self.parameter_ids:
            self.required_comment = self.parameter_ids.required_commentary
        if self.parameter_legislation_ids:
            self.required_comment = self.parameter_legislation_ids.required_commentary

    def get_comment_when_between(self, value):
        comment = ""
        if (
                self.operator_from and
                (self.operator_from == ">" and value > self.limit_value_from or
                 self.operator_from == ">=" and value >= self.limit_value_from or
                 self.operator_from == "=" and value == self.limit_value_from)
        ):
            result_from = True
        else:
            result_from = False
        if (
                self.operator_to and
                (self.operator_to == "<" and value < self.limit_value_to or
                 self.operator_to == "<=" and value <= self.limit_value_to or
                 self.operator_to == "=" and value == self.limit_value_to)
        ):
            result_to = True
        else:
            result_to = False
        if result_from and result_to:
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
        comment = self.message if value == self.is_present else ""
        return comment

    def get_comment_when_iscorrect(self, value):
        comment = self.message if value == self.is_correct else ""
        return comment

    def get_result_when_between(self, value):
        result_from = (
                self.operator_from and
                (
                        (self.operator_from == ">" and value > self.limit_value_from) or
                        (self.operator_from == ">=" and value >= self.limit_value_from) or
                        (self.operator_from == "=" and value == self.limit_value_from)
                )
        )
        result_to = (
                self.operator_to and
                (
                        (self.operator_to == "<" and value < self.limit_value_to) or
                        (self.operator_to == "<=" and value <= self.limit_value_to) or
                        (self.operator_to == "=" and value == self.limit_value_to)
                )
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
        result = self.state if value == self.is_present else ""
        return result

    def get_result_when_iscorrect(self, value):
        result = self.state if value == self.is_correct else ""
        return result

    def get_comment_when_between(self, value):
        result_from = (
                self.operator_from and
                (
                        (self.operator_from == ">" and value > self.limit_value_from) or
                        (self.operator_from == ">=" and value >= self.limit_value_from) or
                        (self.operator_from == "=" and value == self.limit_value_from)
                )
        )
        result_to = (
                self.operator_to and
                (
                        (self.operator_to == "<" and value < self.limit_value_to) or
                        (self.operator_to == "<=" and value <= self.limit_value_to) or
                        (self.operator_to == "=" and value == self.limit_value_to)
                )
        )
        result = self.message if result_from and result_to else ""
        return result

    def get_comment_when_limit(self, value):
        result = ""
        if (
                self.operator_from is not False and
                (
                        (self.operator_from == ">" and value > self.limit_value_from) or
                        (self.operator_from == ">=" and value >= self.limit_value_from) or
                        (self.operator_from == "=" and value == self.limit_value_from)
                )
        ):
            result = self.message
        elif (
                self.operator_to is not False and
                (
                        (self.operator_to == "<" and value < self.limit_value_to) or
                        (self.operator_to == "<=" and value <= self.limit_value_to) or
                        (self.operator_to == "=" and value == self.limit_value_to)
                )
        ):
            result = self.message
        return result

    def get_comment_when_ispresent(self, value):
        result = self.message if value == self.is_present else ""
        return result

    def get_comment_when_iscorrect(self, value):
        result = self.message if value == self.is_correct else ""
        return result

    def get_correct_limit(self):
        if self.state != 'conform':
            return ""
        if self.type == "ISPRESENT":
            return "Presente" if self.is_present else "No Presente"
        elif self.type == "ISCORRECT":
            return "Correcto" if self.is_correct else "No Correcto"
        elif self.type == "LIMIT":
            return self._get_limit_value_char()
        elif self.type == "BETWEEN":
            return self._get_between_limit_value()
        else:
            return ""

    def _get_limit_value_char(self):
        limit_char = ""
        if self.limit_value_from > 0.0:
            limit_char += "{operator_from} {value_from:.2f}".format(
                operator_from=self.operator_from, value_from=self.limit_value_from
            )
        if self.limit_value_to > 0.0:
            limit_char += " {operator_to} {value_to:.2f}".format(
                operator_to=self.operator_to, value_to=self.limit_value_to
            )
        return limit_char.strip()
    def _get_between_limit_value(self):
        between_limit_result = (
            "{operator_from} {value_from: .2f} y {operator_to} {value_to: .2f}"
        ).format(
            operator_from=self.operator_from,
            value_from=self.limit_value_from,
            operator_to=self.operator_to,
            value_to=self.limit_value_to,
        )
        return between_limit_result

