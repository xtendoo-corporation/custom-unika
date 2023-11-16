# Copyright 2021 - Manuel Calero <https://xtendoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP


class ProductTemplate(models.Model):
    _inherit = "product.template"

    WARNING_MESSAGE_ANALYSIS = [
        ('no-message', 'No Message'),
        ('required_images', 'Required images'),
    ]

    WARNING_HELP_ANALYSIS = 'When selecting the "Required Images" option, the user will be notified with the message "You must add image/s".'

    analysis_warn = fields.Selection(
        WARNING_MESSAGE_ANALYSIS,
        'Analysis Warnings',
        default='no-message',
        help=WARNING_HELP_ANALYSIS)

    number_of_samples = fields.Integer(default=1, string="Número de muestras", store=True)

    @api.depends("analysis_warn")
    def _compute_analysis_warn_msg(self):
        analysis_warn_msg = False
        if self.analysis_warn == 'required_images':
            analysis_warn_msg = _("Images are required")
        self.analysis_warn_msg = analysis_warn_msg

    analysis_warn_msg = fields.Text('Message for Analysis', compute="_compute_analysis_warn_msg")

    is_product_sample = fields.Boolean(
        string="Is a product sample",
        default=False,
    )
    analysis_ids = fields.Many2many(
        "lims.analysis",
        "product_template_lims_analysis_rel",
        "product_id",
        "analysis_id",
        string="Analysis",
    )

    analysis_count = fields.Integer(
        "Number of Analysis Generated",
        compute="_compute_analysis_count",
    )

    @api.onchange("analysis_ids")
    def _onchange_analysis_ids(self):
        product_price = sum(analysis.price for analysis in self.analysis_ids if analysis.price > 0.00)
        self.list_price = product_price if product_price > 0.00 else 0.00

    @api.constrains("is_product_sample", "type")
    def _check_is_product_sample(self):
        if self.is_product_sample and self.type != "product":
            raise ValidationError(
                _("You can only create sample products if they are storable.")
            )
        self.tracking = "lot"

    def _compute_analysis_count(self):
        for order in self:
            order.analysis_count = len(self._get_analysis())

    def _get_analysis(self):
        return self.env["lims.analysis.line"].search([("product_id", "=", (self.id))])

    def action_view_analysis(self):
        self.ensure_one()
        analysis_line_ids = self._get_analysis().ids
        action = {
            "res_model": "lims.analysis.line",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
        }
        if len(analysis_line_ids) == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": analysis_line_ids[0],
                }
            )
        else:
            action.update(
                {
                    "name": _("Analysis from Product %s", self.name),
                    "domain": [("id", "in", analysis_line_ids)],
                }
            )
        return action


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_analysis(self):
        return self.env["lims.analysis.line"].search(
            [("product_id", "=", (self.product_tmpl_id.id))]
        )

    def action_view_analysis(self):
        self.ensure_one()
        analysis_line_ids = self._get_analysis().ids
        action = {
            "res_model": "lims.analysis.line",
            "type": "ir.actions.act_window",
            "view_mode": "form" if len(analysis_line_ids) == 1 else "tree,form",
        }
        if len(analysis_line_ids) != 1:
            action.update(
                {
                    "name": _("Analysis from Product %s", self.name),
                    "domain": [("id", "in", analysis_line_ids)],
                }
            )
        return action
