# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class LimsAnalysis(models.Model):
    _name = "lims.analysis"
    _description = "Analysis LIMS"
    name = fields.Char(string="Name", store=True)

    def _is_name_in_use(self, name):
        package = self.env['lims.analysis'].search(
            [
                ("name", "=", name),
            ], )
        if package:
            return True
        return False

    description = fields.Char(string="Description", store=True)

    product_ids = fields.Many2many(
        "product.template",
        "product_template_lims_analysis_group_rel",
        "analysis_group_id",
        "product_id",
        "Products",
    )
    sale_line_ids = fields.Many2many(
        "sale.order.line",
        "line_analysis_group_rel",
        "analysis_group_id",
        "sale_line_id",
        "Lines",
    )

    @api.depends('parameter_method_ids')
    def _get_parameter_domain(self):
        parameters_ids = []
        for method in self.parameter_method_ids:
            parameters_ids.append(method.parameter_id.id)
        parameter_used = self.env['analytical.method.price'].search([('parameter_id', 'in', parameters_ids)])
        self.parameter_used_ids = parameter_used

    parameter_method_ids = fields.One2many(
        "parameter.analytical.method.price.uom",
        "parent_id",
    )
    parameter_used_ids = fields.Many2many(
        "analytical.method.price",
        store=False,
        compute=_get_parameter_domain

    )
    price = fields.Float("Price", store=True)
    def _get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=_get_company_id,
    )
    active = fields.Boolean(default=True, string="Active")

    @api.model
    def create(self, vals):
        if vals['name'] and vals['name'] != '':
            is_in_use = self._is_name_in_use(vals['name'])
            if is_in_use:
                if not self.name:
                    raise UserError(_("El nombre debe ser único para cada paquete analítico"))
                else:
                    vals['name'] = vals['name'] + '(Copia)'
        res = super(LimsAnalysis, self).create(vals)
        for parameter_method in self.parameter_method_ids:
            self.env['parameter.analytical.method.price.uom'].create({
                'parent_id': res.id,
                'analytical_method_id': parameter_method.analytical_method_id.id,
                'uom_id': parameter_method.uom_id.id,
                'use_acreditation': parameter_method.use_acreditation,
                'used_acreditation': parameter_method.used_acreditation,
                'use_normative': parameter_method.use_normative,
                'used_normative': parameter_method.used_normative,
            })
        return res


    def write(self, vals):
        if vals.get('name'):
            if vals['name']:
                package = self.env['lims.analysis'].search(
                    [
                        ("name", "=", vals['name']),
                        ("id", "!=", self.id),
                    ], )
                if package:
                    raise UserError(_("El nombre debe ser único para cada paquete analítico"))
        res = super(LimsAnalysis, self).write(vals)
        return res

        if self.parameter_method_ids and res:
            parameter_values = [{
                'parent_id': res.id,
                'analytical_method_id': parameter.analytical_method_id.id,
                'uom_id': parameter.uom_id.id,
                'use_acreditation': parameter.use_acreditation,
                'used_acreditation': parameter.used_acreditation,
                'use_normative': parameter.use_normative,
                'used_normative': parameter.used_normative,
            } for parameter in self.parameter_method_ids]

            self.env['parameter.analytical.method.price.uom'].create(parameter_values)

        return res