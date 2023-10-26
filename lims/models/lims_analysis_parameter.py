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
    parameter_uom = fields.Many2many("uom.uom", string="Unit of Measure")
    required_comment = fields.Boolean(string="Required Commentary", store=True)
    show_potency = fields.Boolean(string="Mostrar en potencia", store=True)
    change_value_for_comment = fields.Boolean(string="Cambiar valor por comentario", store=True)


    def _is_code_in_use(self, code):
        parameter = self.env['lims.analysis.parameter'].search(
            [
                ("default_code", "=", code),
            ], )
        if parameter:
            return True
        return False

    def write(self, vals):
        if vals.get('default_code'):
            if vals['default_code']:
                parameter = self.env['lims.analysis.parameter'].search(
                    [
                        ("default_code", "=", vals['default_code']),
                        ("id", "!=", self.id),
                    ], )
                if parameter:
                    raise UserError(_("La referencia debe ser única por parámetro"))
        if vals.get('name'):
            for method in self.analytical_method_price_ids:
                method.write(
                    {
                        'name': vals['name'] + " - " + method.analytical_method_id.name,
                        'display_name': vals['name'] + " - " + method.analytical_method_id.name,
                    }
                )
        return super(LimsAnalysisParameter, self).write(vals)

    @api.model
    def create(self, vals):
        if vals['default_code'] and vals['default_code'] != '':
            is_in_use = self._is_code_in_use(vals['default_code'])
            if is_in_use:
                if not self.default_code:
                    raise UserError(_("La referencia debe ser única por parámetro"))
                else:
                    vals['default_code'] = ''
        res = super(LimsAnalysisParameter, self).create(vals)
        if self.limits_ids and res:
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
        if self.analytical_method_price_ids and res:
            methods = res['analytical_method_price_ids']
            res['analytical_method_price_ids'] = [(5, 0, 0)]
            method_ids = ()
            for method in methods:
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
                method_udm = self.env['parameter.analytical.method.price.uom'].search(
                    [("analytical_method_id", "=", new_method.id), ('parent_id', '=', False)])
                if not method_udm:
                    self.env['parameter.analytical.method.price.uom'].create(
                        {
                            'analytical_method_id': new_method.id,
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
                method_udm = self.env['parameter.analytical.method.price.uom'].search([("analytical_method_id", "=", method.id),('parent_id', '=', False)])
                if not method_udm:
                    self.env['parameter.analytical.method.price.uom'].create(
                        {
                            'analytical_method_id': method.id,
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
        if value is None and iscorrect_value is None and ispresent_value is None:
            return
        if not limit_ids:
            return
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
        return result

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
