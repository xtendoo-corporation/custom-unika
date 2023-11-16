# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class LimsAnalysis(models.Model):
    _name = "lims.analysis"
    _description = "Analysis LIMS"
    name = fields.Char(string="Name", store=True)
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
        tracking=True,
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

    @api.model
    def create(self, vals):
        res = super(LimsAnalysis, self).create(vals)

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

