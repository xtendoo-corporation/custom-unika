# Copyright 2020 Xtendoo - Manuel Calero
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ParameterAnalyticalMethodUomRel(models.Model):
    _name = "parameter.analytical.method.price.uom"
    _description = "Analytical Method Price UOM"

    parent_id = fields.Many2one(
        "lims.analysis",
        "Analysis lims",
    )

    analytical_method_id = fields.Many2one(
        "analytical.method.price", string="Method", ondelete="cascade", required=True
    )
    # analysis_id = fields.Many2one(
    #     comodel_name="lims.analysis",
    #     string="Analysis_id",
    # )
    name = fields.Char(related="analytical_method_id.name")
    parameter_id = fields.Many2one(
        related="analytical_method_id.parameter_id"
    )
    price = fields.Float(related="analytical_method_id.price")
    cost = fields.Float(related="analytical_method_id.cost")
    external_lab = fields.Many2one(
        related="analytical_method_id.external_lab"
    )
    company_id = fields.Many2one(
        related="analytical_method_id.company_id"
    )
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")
    parameter_uom = fields.Many2many(related="analytical_method_id.parameter_id.parameter_uom")
    parameter_used_ids = fields.Many2many(
        related="parent_id.parameter_used_ids"

    )

    analytical_method_id = fields.Many2one(
        "analytical.method.price", string="Method", ondelete="cascade", required=True
    )
    use_acreditation = fields.Boolean(string="Use acreditation", store=True)
    used_acreditation = fields.Many2one(
        "lims.analysis.normative",
        "Acreditation",
    )

    use_normative = fields.Boolean(string="Use normative", store=True)

    used_normative = fields.Many2one(
        "lims.analysis.normative",
        "Normative",
    )

    @api.onchange('use_acreditation')
    def set_use_acreditation(self):
        if self.use_acreditation and self.use_normative:
            raise UserError(_("A parameter can only be accredited or a regulation can be applied"))
        if not self.use_acreditation:
            self.used_acreditation = False

    @api.onchange('use_normative')
    def set_use_normative(self):
        if self.use_acreditation and self.use_normative:
            raise UserError(_("A parameter can only be accredited or a regulation can be applied"))
        if not self.use_normative:
            self.used_normative = False






