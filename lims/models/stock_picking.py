# Copyright 2021 - Manuel Calero <https://xtendoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models, api
import datetime as dt
from jinja2 import Template
from odoo.exceptions import UserError, AccessError


class StockPicking(models.Model):
    _inherit = "stock.picking"
    analysis_count = fields.Integer(
        "Number of Analysis Generated",
        compute="_compute_analysis_count",
    )

    email_to_send = fields.Char()
    def _compute_lot_name(self):
        for order in self:
            order.lot_name = order.move_line_ids_without_package[0].lot_name
    lot_name = fields.Char(
        string="Lote",
        compute="_compute_lot_name",
    )
    def button_validate(self):
        # date_validate = dt.datetime.now()
        # format = "%Y-%m-%d %H:%M:%S"
        # date_validate.strftime(format)
        partner_id = self.partner_id.id
        for line in self.move_line_ids_without_package:
            self.env["stock.production.lot"].search(
                [("id", "=", line.lot_id.id)]
            ).write(
                {
                    "recepcion_date": self.scheduled_date,
                    "partner_id": partner_id,
                }
            )
        res = super(StockPicking, self).button_validate()
        if self.partner_id.send_confirmation_mail:
            self.send_recepcion_email()
        return res

    def _compute_analysis_count(self):
        for order in self:
            order.analysis_count = len(self._get_analysis())

    def _get_analysis(self):
        return self.env["lims.analysis.line"].search(
            [("stock_move_line_id", "in", (self.move_line_nosuggest_ids.ids))]
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
                    "name": _("Analysis from %s", self.name),
                    "domain": [("id", "in", analysis_line_ids)],
                    "view_mode": "tree,form",
                }
            )
        return action

    def create_all_analysis(self):
        for line in self.move_line_ids_without_package:

            if line.product_id.number_of_samples:
                if not self.env["lims.analysis.line"].search(
                        [
                            ("stock_move_line_id", "=", line.id),
                            ("lot_id", "=", line.lot_id.id),
                        ]
                ):
                    self.env["lims.analysis.line"].create(
                        {
                            "product_id": line.product_id.product_tmpl_id.id,
                            "stock_move_line_id": line.id,
                            "customer_id": self.partner_id.id,
                            "customer_contact_id": self.partner_id.id,
                            "lot_id": line.lot_id.id,
                            "pricelist_id": self.get_pricelist_id(line),
                            "lot_name": line.lot_name,
                            "take_for": line.lot_id.take_for,
                            "date_sample_collection": line.lot_id.collection_date,
                        }
                    )
                    return
            if (
                line.product_id.is_product_sample
                and line.move_id.purchase_line_id.sale_line_id.parameter_ids
            ):
                for (
                    analytical_method
                ) in line.move_id.purchase_line_id.sale_line_id.parameter_ids:
                    if not self.env["lims.analysis.line"].search(
                        [
                            ("stock_move_line_id", "=", line.id),
                            ("lot_id", "=", line.lot_id.id),
                        ]
                    ):
                        self.env["lims.analysis.line"].create(
                            {
                                "product_id": line.product_id.product_tmpl_id.id,
                                "stock_move_line_id": line.id,
                                "customer_id": self.partner_id.id,
                                "customer_contact_id": self.partner_id.id,
                                "lot_id": line.lot_id.id,
                                "pricelist_id": self.get_pricelist_id(line),
                            }
                        )

    def get_pricelist_id(self, line):
        if line.move_id.purchase_line_id.sale_order_id.pricelist_id:
            return line.move_id.purchase_line_id.sale_order_id.pricelist_id.id
        elif self.partner_id.parent_id and self.partner_id.parent_id.pricelist_id:
            return self.partner_id.parent_id.pricelist_id.id
        elif self.partner_id.pricelist_id:
            return self.partner_id.pricelist_id.id
        else:
            return 1  # Buscar tarifa publica para evitar usar el id


    #Envio automatico de email.
    # @api.onchange('stage_id')

    def set_email_to_send(self):
        email = self.partner_id.email
        if self.partner_id.child_ids:
            for child in self.partner_id.child_ids:
                if child.type == 'other':
                    email = child.email
                    break
        self.email_to_send = email
    def send_recepcion_email(self):
        self.set_email_to_send()
        self.ensure_one()
        template = self.env.ref('lims.email_template_reception')
        email_message = template.with_context(mail_notify_force_send=True).send_mail(self.id)
        return email_message

    def _get_correct_value(self, parameter, uom):
        value = ""
        if parameter:
            limits = self.env["lims.analysis.limit"].search(
                [
                    ("parameter_ids", "=", parameter.id),
                    ("uom_id", "=", uom.id),
                ]
            )

            if limits:
                limit_result = limits.limit_result_line_ids.filtered(
                    lambda r: r.state == "conform"
                )
                if limit_result:
                    if limit_result[0].type == 'LIMIT':
                        value = parameter._get_limit_value_char(limit_result)
                    if limit_result[0].type == 'BETWEEN':
                        value = parameter._get_between_limit_value_char(limit_result)
                    if limit_result[0].type == 'ISPRESENT':
                        if limit_result[0].is_present:
                            value = "Presencia"
                        else:
                            value = "Ausencia"

            return value


