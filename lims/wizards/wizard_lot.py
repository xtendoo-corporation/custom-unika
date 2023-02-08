from odoo import fields, models


class LotWiward(models.TransientModel):
    _name = "lims.wizard.lot"

    def _compute_number_from(self):
        return (
            self.env["ir.sequence"]
            .search([("code", "=", "stock.lot.serial")])
            .number_next_actual
        )

    number_from = fields.Integer(string="Primer Lote", default=_compute_number_from)
    quantity = fields.Integer(string="Cantidad", default="1")
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        domain=[
            ('parent_id', '=', False),
            ('is_maker', '=', False),
            ('is_lab', '=', False)
        ]
    )

    def generate_lots(self):
        lots = []
        for _ in range(self.quantity):
            partner_id = None
            if self.partner_id:
                partner_id = self.partner_id.id
            lot_create = (
                self.env["stock.production.lot"]
                .sudo()
                .create(
                    {
                        "name": self.env["ir.sequence"].next_by_code("stock.lot.serial")
                        or "/",
                        "company_id": self.env.company.id,
                        "partner_id": partner_id
                    }
                )
            )
            lots.append(lot_create.id)
        return lots

    def generate_and_print_lots(self):
        lots = self.generate_lots()
        lots_ids = self.env["stock.production.lot"].search([("id", "in", lots)])
        return self.env.ref("lims.lims_report_label_lot").report_action(lots_ids)
