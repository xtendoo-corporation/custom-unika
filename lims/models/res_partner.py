# Copyright 2021 - Manuel Calero <https://xtendoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_lab = fields.Boolean(
        string="Laboratory",
    )
    is_maker = fields.Boolean(
        string="Maker",
    )
    send_by_mail = fields.Boolean(
        string="Enviar por boletin correo",
        default=True,
    )
    send_confirmation_mail = fields.Boolean(
        string="Enviar email de recpción",
        default=True,
    )

    analysis_count = fields.Integer(
        "Number of Analysis Generated",
        compute="_compute_analysis_count",
    )


    def _compute_analysis_count(self):
        for partner in self:
            partner.analysis_count = len(self._get_analysis())

    def _get_analysis(self):
        return self.env["lims.analysis.line"].search(
            [("customer_id", "=", self.id)]
        )

    def action_view_analysis(self):
        self.ensure_one()
        analysis_line_ids = self._get_analysis().ids
        action = {
            "res_model": "lims.analysis.line",
            "type": "ir.actions.act_window",
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
                    "name": _("Analisis del cliente  %s", self.name),
                    "domain": [("id", "in", analysis_line_ids)],
                    "view_mode": "tree,form",
                }
            )
        return action
