# Copyright 2021 - Manuel Calero <https://xtendoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    analysis_ids = fields.One2many(
        "lims.analysis.line",
        "stock_move_line_id",
        invisible=True,
    )
    is_product_sample = fields.Boolean(
        "Is Product Sample",
        related="product_id.is_product_sample",
        store=True,
        readonly="1",
    )
    lot_id = fields.Many2one(
        "stock.production.lot",
        "Sample number",
        check_company=True,
    )

    def create_new_analysis(self):
        if self.picking_id.state != "done":
            raise ValidationError(_("You must first validate the picking"))
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "lims.analysis_new_action"
        )
        action["context"] = {
            "stock_move_line_id": self.id,
            "lot_id": self.lot_id.id,
            "customer_id": self.picking_id.partner_id.id,
            "product_id": self.product_id.product_tmpl_id.id,
        }
        return action

    @api.constrains("lot_id", "product_id")
    def _check_lot_product(self):
        return

    def write(self, vals):
        res = super(StockMoveLine, self).write(vals)
        for line in self:
            lot_id = self.env["stock.production.lot"].search(
                [("id", "=", line.lot_id.id)]
            )
            lot_id.write(
                {
                    "product_id": line.product_id.id,
                }
            )
        return res

    @api.onchange("lot_id")
    def onchange_lot_id(self):
        print("*" * 120)
        print("Entra en domain")
        print("*" * 120)
        domain = {}
        for record in self:
            # lot_id_can_use = self.env['stock.production.lot'].search([
            #     ('product_id', '=', False),
            #     ('company_id', '=', record.company_id.id),
            #
            # ])
            partner_id = record.move_id.picking_id.partner_id
            if record.move_id.picking_id.partner_id.parent_id:
                partner_id = record.move_id.picking_id.partner_id.parent_id
            print("partner_id ", partner_id)
            lot_id_can_use = self.env['stock.production.lot'].search([
                ('product_id', '=', False),
                ('company_id', '=', record.company_id.id),
                ('partner_id', 'in', [partner_id.id, False])

            ], order="partner_id ASC, id DESC")
            print("lots", lot_id_can_use)
            domain['lot_id'] = [('id', 'in', lot_id_can_use.ids)]
        return {"domain": domain}
