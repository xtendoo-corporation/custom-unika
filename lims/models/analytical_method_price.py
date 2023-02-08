# Copyright 2020 Xtendoo - Manuel Calero
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _


class ParameterAnalyticalMethodRel(models.Model):
    _name = "analytical.method.price"
    _description = "Analytical Method Price"

    analytical_method_id = fields.Many2one(
        "lims.analytical.method", string="Method", ondelete="cascade", required=True
    )
    parameter_id = fields.Many2one(
        comodel_name="lims.analysis.parameter",
        string="Parameter",
    )
    name = fields.Char(string="Name", store=True)
    price = fields.Float("Price", store=True)
    cost = fields.Float("Cost", store=True)
    external_lab = fields.Many2one(
        comodel_name="res.partner",
        string="External Lab",
    )

    def _get_company_id(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=_get_company_id
    )

    @api.onchange('analytical_method_id')
    def _compute_name(self):
        if not self.analytical_method_id.name:
            self.name = _("%s", self.parameter_id.name)
            return
        self.name = _("%s - %s", self.parameter_id.name, self.analytical_method_id.name)




