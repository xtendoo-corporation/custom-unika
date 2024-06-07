# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo import _, api, fields, models
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    analysis_count = fields.Integer(
        "Number of Analysis Generated",
        compute="_compute_analysis_count",
    )
    date_validity = fields.Datetime(
        store=True,
        index=True,
    )
    normative_used = fields.Text(
        string="Normativa aplicable",
        store=True,
        tracking=True,
    )
    observations = fields.Text(
        string="Comentarios",
        store=True,
        tracking=True,
    )

    def _get_price_in_pricelist_item(
        self, pricelist_item, pricelist_type, product=None
    ):
        price = 0.00
        if pricelist_type == "4_analysis_group":
            product = pricelist_item.analysis_group_ids
        elif pricelist_type == "5_analytical_method":
            product = pricelist_item.analitycal_method_ids
        if pricelist_item.compute_price == "fixed":
            price = pricelist_item.fixed_price
        if pricelist_item.compute_price == "percentage":
            price = product.price - product.price * (pricelist_item.percent_price / 100)
        if pricelist_item.compute_price == "formula":
            if pricelist_item.base == "pricelist":
                if pricelist_item.base_pricelist_id:
                    parent_pricelist_item = self.env["product.pricelist.item"].search(
                        [
                            ("analysis_group_ids", "=", product.id),
                            ("pricelist_id", "=", pricelist_item.base_pricelist_id.id),
                        ],
                        limit=1,
                    )
                    if parent_pricelist_item:
                        price = self._get_price_in_pricelist_item(
                            parent_pricelist_item, parent_pricelist_item.applied_on
                        )
                    else:
                        parent_pricelist_item = self.env[
                            "product.pricelist.item"
                        ].search(
                            [
                                ("analitycal_method_ids", "=", product.id),
                                (
                                    "pricelist_id",
                                    "=",
                                    pricelist_item.base_pricelist_id.id,
                                ),
                            ],
                            limit=1,
                        )
                        if parent_pricelist_item:
                            price = self._get_price_in_pricelist_item(
                                parent_pricelist_item, parent_pricelist_item.applied_on
                            )
                        else:
                            parent_pricelist_item = self.env[
                                "product.pricelist.item"
                            ].search(
                                [
                                    ("applied_on", "=", "3_global"),
                                    (
                                        "pricelist_id",
                                        "=",
                                        pricelist_item.base_pricelist_id.id,
                                    ),
                                ],
                                limit=1,
                            )
                            price = self._get_price_in_pricelist_item(
                                parent_pricelist_item,
                                parent_pricelist_item.applied_on,
                                product,
                            )
                else:
                    price = product.price
            else:
                price = product.price
            price = (
                price
                - price * (pricelist_item.price_discount / 100)
                + pricelist_item.price_surcharge
            )
        return price

    def _get_parameter_individual_price(self, parameter):
        print(parameter.analytical_method_id)
        pricelist_item = self.env["product.pricelist.item"].search(
            [
                ("analitycal_method_ids", "=", parameter.analytical_method_id.id),
                ("pricelist_id", "=", self.pricelist_id.id),
            ],
            limit=1,
        )
        if pricelist_item:
            price = self._get_price_in_pricelist_item(
                pricelist_item, pricelist_item.applied_on
            )
        else:
            pricelist_item_all = self.env["product.pricelist.item"].search(
                [
                    ("applied_on", "=", "3_global"),
                    ("pricelist_id", "=", self.pricelist_id.id),
                ],
                limit=1,
            )
            if pricelist_item_all:
                price = self._get_price_in_pricelist_item(
                    pricelist_item_all,
                    pricelist_item.applied_on,
                    parameter.analytical_method_id,
                )
            else:
                price = parameter.price
        return price

    def _get_group_price(self, analysis_id):

        pricelist_item = self.env["product.pricelist.item"].search(
            [
                ("analysis_group_ids", "=", analysis_id.id),
                ("pricelist_id", "=", self.pricelist_id.id),
            ],
            limit=1,
        )
        if pricelist_item:
            price = self._get_price_in_pricelist_item(
                pricelist_item, pricelist_item.applied_on
            )
        else:
            pricelist_item_all = self.env["product.pricelist.item"].search(
                [
                    ("applied_on", "=", "3_global"),
                    ("pricelist_id", "=", self.pricelist_id.id),
                ],
                limit=1,
            )
            if pricelist_item_all:
                price = self._get_price_in_pricelist_item(
                    pricelist_item_all, pricelist_item.applied_on, analysis_id
                )
            else:
                price = analysis_id.price
        return price

    def _get_parameter_in_group(self):
        groups = {}
        line = self.order_line[0]
        parameters_data = {}
        if not line.analysis_group_ids:
            for parameter in line.parameter_ids:
                parameter_price = parameter.price
                if self.pricelist_id:
                    parameter_price = self._get_parameter_individual_price(parameter)
                parameters_data[parameter.id] = {
                    'name': parameter.parameter_id.name,
                    'group_price': 'None',
                    'parameter_price': parameter_price,
                    'parameter_code': parameter.parameter_id.default_code,
                    'parameter_units': line.product_uom_qty,
                }
            groups['None'] = parameters_data
            return groups
        else:
            for group in line.analysis_group_ids:
                group_price = group.price
                if self.pricelist_id:
                    group_price = self._get_group_price(group)

                if group.parameter_method_ids:
                    for parameter in group.parameter_method_ids:
                        parameter_price = parameter.price
                        if self.pricelist_id:
                            parameter_price = self._get_parameter_individual_price(parameter)

                        parameters_data[parameter.id] = {
                            'name': parameter.parameter_id.name,
                            'group_price': group_price,
                            'parameter_price': parameter_price,
                            'parameter_code': parameter.parameter_id.default_code,
                            'parameter_units': line.product_uom_qty,
                        }
                if parameters_data:
                    groups[group.name] = parameters_data
                    parameters_data = {}
            for parameter in line.parameter_ids:
                if parameter not in line.analysis_group_ids.parameter_method_ids:
                    parameter_price = parameter.price
                    if self.pricelist_id:
                        parameter_price = self._get_parameter_individual_price(parameter)
                    parameters_data[parameter.id] = {
                        'name': parameter.parameter_id.name,
                        'group_price': 'None',
                        'parameter_price': parameter_price,
                        'parameter_code': parameter.parameter_id.default_code,
                        'parameter_units': line.product_uom_qty,
                    }
            if parameters_data:
                groups['None'] = parameters_data
        return groups


        # return groups

    def _compute_analysis_count(self):
        for order in self:
            order.analysis_count = len(self._get_analysis())

    def _get_analysis(self):
        purchase_order = self.env["purchase.order"].search(
            [("origin", "=", (self.name))]
        )
        stock_picking = self.env["stock.picking"].search(
            [("purchase_id", "=", (purchase_order.id))]
        )

        return stock_picking._get_analysis()

    sale_warn_msg = fields.Text(compute="_compute_sale_warn_msg")

    @api.depends(
        "state", "partner_id.sale_warn", "partner_id.commercial_partner_id.sale_warn"
    )
    def _compute_sale_warn_msg(self):

        for sale in self:
            if sale.state not in ["draft", "sent"]:
                sale.sale_warn_msg = False
                return
            line_nums = len(sale.order_line)
            line_act = 0
            sale_warn_msg = ""
            for line in sale.order_line:
                line_act = line_act + 1

                if line.product_id.sale_line_warn == "warning":
                    if line_act != line_nums:
                        line_break = "\n"
                    else:
                        line_break = ""
                    sale_line_msg = _("%s - %s", line.product_id.name, line.product_id.sale_line_warn_msg)
                    sale_warn_msg += sale_line_msg + line_break
            sale.sale_warn_msg = sale_warn_msg

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

    def _action_confirm(self):
        result = super(SaleOrder, self)._action_confirm()
        for order in self:
            order.order_line.sudo()._purchase_sample_generation()
        return result


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    analysis_group_ids = fields.Many2many(
        "lims.analysis",
        "line_analysis_group_rel",
        "sale_line_id",
        "analysis_group_id",
        string="Analysis",
    )

    parameter_ids = fields.Many2many(
        "parameter.analytical.method.price.uom",
        "line_parameter_method_rel",
        "sale_line_id",
        "parameter_id",
        string="Parameters",
    )

    price_type = fields.Selection(
        [
            ("parameter", "Por parámetros"),
            ("package", "Por paquete"),
        ],
        default='package',

    )

    @api.depends('parameter_ids')
    def _get_parameter_domain(self):
        parameters_ids = []
        if not self.parameter_ids:
            self.parameter_used_ids = None
            return
        for parameter in self.parameter_ids:
            parameters_ids.append(parameter._origin.parameter_id.id)
            parameter_used = self.env['parameter.analytical.method.price.uom'].search([('parameter_id', 'in', parameters_ids)])
        if parameter_used:
            self.parameter_used_ids = parameter_used
        else:
            self.parameter_used_ids = None

    parameter_used_ids = fields.Many2many(
        "parameter.analytical.method.price.uom",
        store=False,
        compute=_get_parameter_domain

    )

    @api.onchange("product_id")
    def _charge_analysis(self):
        if self.product_id:
            if self.product_id.analysis_ids:
                if self.analysis_group_ids != self.product_id.analysis_ids:
                    self.analysis_group_ids = None
                self.analysis_group_ids = self.product_id.analysis_ids
                self._charge_parameters()
                self._get_price_unit_sample

    @api.onchange("analysis_group_ids")
    def _charge_parameters(self):
        self.parameter_ids = None
        if self.analysis_group_ids:
            for analysis in self.analysis_group_ids:
                if analysis.parameter_method_ids:
                    self.parameter_ids += analysis.parameter_method_ids
    def button_edit_parameters(self):
        self.ensure_one()
        view = self.env.ref("lims.anaytical_method_price_tree_update_in_sale")
        return {
            "name": _("Parameters"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": self._name,
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": self.id,
            "context": self.env.context,
        }

    def write(self, values):
        increased_lines = None
        decreased_lines = None
        increased_values = {}
        decreased_values = {}
        if "product_uom_qty" in values:
            precision = self.env["decimal.precision"].precision_get(
                "Product Unit of Measure"
            )
            increased_lines = self.sudo().filtered(
                lambda r: r.product_id.is_product_sample
                and r.purchase_line_count
                and float_compare(
                    r.product_uom_qty,
                    values["product_uom_qty"],
                    precision_digits=precision,
                )
                == -1
            )
            decreased_lines = self.sudo().filtered(
                lambda r: r.product_id.is_product_sample
                and r.purchase_line_count
                and float_compare(
                    r.product_uom_qty,
                    values["product_uom_qty"],
                    precision_digits=precision,
                )
                == 1
            )
            increased_values = {
                line.id: line.product_uom_qty for line in increased_lines
            }
            decreased_values = {
                line.id: line.product_uom_qty for line in decreased_lines
            }

        result = super(SaleOrderLine, self).write(values)

        if increased_lines:
            increased_lines._purchase_increase_ordered_qty(
                values["product_uom_qty"], increased_values
            )
        if decreased_lines:
            decreased_lines._purchase_decrease_ordered_qty(
                values["product_uom_qty"], decreased_values
            )
        return result

    def _purchase_sample_create(self, line):
        supplier_po_map = {}
        line = line.with_company(line.company_id)
        # determine vendor of the order (take the first matching company and product)
        purchase_order = self._get_purchase_order(line)
        # add a PO line to the PO
        values = line._purchase_sample_prepare_line_values(purchase_order)
        line.env["purchase.order.line"].create(values)
        origins = []
        if purchase_order.origin:
            origins = purchase_order.origin.split(", ") + origins
        if line.order_id.name not in origins:
            origins += [line.order_id.name]
            purchase_order.write({"origin": ", ".join(origins)})
        supplier_po_map[line.order_id.partner_id.id] = purchase_order
        return purchase_order

    def _get_purchase_order(self, line):
        PurchaseOrder = self.env["purchase.order"]
        purchase_order = PurchaseOrder.search(
            [
                ("partner_id", "=", line.order_id.partner_id.id),
                ("state", "=", "draft"),
                ("company_id", "=", line.company_id.id),
            ],
            limit=1,
        )
        if purchase_order:
            return purchase_order
        return self._create_purchase_order(line)

    def _create_supplier_line(self, line):
        self.ensure_one()
        vals = [
            ("name", "=", line.order_id.partner_id.id),
            ("product_tmpl_id", "=", line.product_id.product_tmpl_id.id),
        ]
        have_supplier = self.env["product.supplierinfo"].search(vals)
        if len(have_supplier) < 1:
            self.env["product.supplierinfo"].sudo().create(
                {
                    "name": line.order_id.partner_id.id,
                    "product_tmpl_id": line.product_id.product_tmpl_id.id,
                }
            )

    def _create_purchase_order(self, line):
        self._create_supplier_line(line)
        PurchaseOrder = self.env["purchase.order"]
        values = line._purchase_sample_prepare_order_values(line.order_id.partner_id)
        purchase_order = PurchaseOrder.create(values)
        # purchase_order.button_confirm()
        return purchase_order

    def _purchase_sample_generation(self):
        """Create a Purchase for the first time
        from the sale line.
         If the SO line already created a PO, it
        will not create a second one.
        """
        sale_line_purchase_map = ""
        for line in self:
            # Do not regenerate PO line if the SO line has already
            # created one in the past (SO cancel/reconfirmation case)
            if line.product_id.is_product_sample:
                if not line.purchase_line_count:
                    result = line._purchase_sample_create(line)
                    sale_line_purchase_map = result
        for purchase in sale_line_purchase_map:
            purchase.button_confirm()
        return sale_line_purchase_map

    def _purchase_sample_prepare_order_values(self, supplierinfo):
        self.ensure_one()
        date_order = datetime.datetime.now()
        return {
            "partner_id": supplierinfo.id,
            "partner_ref": supplierinfo.ref,
            "company_id": self.company_id.id,
            "currency_id": supplierinfo.property_purchase_currency_id.id
            or self.env.company.currency_id.id,
            "dest_address_id": False,  # False since only supported in stock
            "origin": self.order_id.name,
            "payment_term_id": supplierinfo.property_supplier_payment_term_id.id,
            "date_order": date_order,
        }

    def _purchase_sample_prepare_line_values(self, purchase_order, quantity=False):
        self.ensure_one()
        # compute quantity from SO line UoM
        product_quantity = self.product_uom_qty
        purchase_qty_uom = self.product_uom._compute_quantity(
            product_quantity, self.product_id.uom_po_id
        )
        price_unit = 0.0
        date_planned = datetime.datetime.now()
        if self.product_id.number_of_samples != purchase_qty_uom:
            purchase_qty_uom = self.product_id.number_of_samples
        return {
            "name": "[%s] %s" % (self.product_id.default_code, self.name)
            if self.product_id.default_code
            else self.name,
            "product_qty": purchase_qty_uom,
            "product_id": self.product_id.id,
            "product_uom": self.product_id.uom_po_id.id,
            "price_unit": price_unit,
            "date_planned": date_planned,
            "taxes_id": None,
            "order_id": purchase_order.id,
            "sale_line_id": self.id,
        }

    def _purchase_decrease_ordered_qty(self, new_qty, origin_values):
        """Decrease the quantity from SO line will add a next
        acitivities on the related purchase order
        :param new_qty: new quantity (lower than the current
        one on SO line), expressed
            in UoM of SO line.
        :param origin_values: map from sale line id to old
        value for the ordered quantity (dict)
        """
        purchase_to_notify_map = {}  # map PO -> set(SOL)
        last_purchase_lines = self.env["purchase.order.line"].search(
            [("sale_line_id", "in", self.ids)]
        )
        for purchase_line in last_purchase_lines:
            purchase_to_notify_map.setdefault(
                purchase_line.order_id, self.env["sale.order.line"]
            )
            purchase_to_notify_map[purchase_line.order_id] |= purchase_line.sale_line_id

        # create next activity
        for purchase_order, sale_lines in purchase_to_notify_map.items():
            render_context = {
                "sale_lines": sale_lines,
                "sale_orders": sale_lines.mapped("order_id"),
                "origin_values": origin_values,
            }
            purchase_order._activity_schedule_with_view(
                "mail.mail_activity_data_warning",
                user_id=purchase_order.user_id.id or self.env.uid,
                views_or_xmlid="sale_purchase.exception_purchase_on_sale_quantity_decreased",
                render_context=render_context,
            )

    def _purchase_increase_ordered_qty(self, new_qty, origin_values):
        """Increase the quantity on the related purchase lines
        :param new_qty: new quantity (higher than the current one on SO line), expressed
            in UoM of SO line.
        :param origin_values: map from sale line id to old value for the ordered quantity (dict)
        """
        for line in self:
            last_purchase_line = self.env["purchase.order.line"].search(
                [("sale_line_id", "=", line.id)], order="create_date DESC", limit=1
            )
            if last_purchase_line.state in [
                "draft",
                "sent",
                "to approve",
            ]:  # update qty for draft PO lines
                quantity = line.product_uom._compute_quantity(
                    new_qty, last_purchase_line.product_uom
                )
                last_purchase_line.write({"product_qty": quantity})
            elif last_purchase_line.state in [
                "purchase",
                "done",
                "cancel",
            ]:  # create new PO, by forcing the quantity as the difference from SO line
                quantity = line.product_uom._compute_quantity(
                    new_qty - origin_values.get(line.id, 0.0),
                    last_purchase_line.product_uom,
                )
                line._purchase_service_create(quantity=quantity)

    def _get_display_price(self, product):
        res = super(SaleOrderLine, self)._get_display_price(product)
        price = 0.00
        if product.is_product_sample:
            price = self._get_price_unit_sample()
        if price != 0.00:
            return price
        return res
    @api.onchange("price_type")
    def _onchange_price_type(self):
        if not self.price_type:
            self.price_type = "package"
        self._get_price_unit_sample()

    def _get_price_unit_sample(self):
        price_unit = 0.00
        if self.price_type == "package":
            if self.order_id.pricelist_id:
                for analysis in self.analysis_group_ids:
                    analysis_id = self.env["lims.analysis"].search(
                        [("name", "=", analysis.name)], limit=1
                    )
                    pricelist_item = self.env["product.pricelist.item"].search(
                        [
                            ("analysis_group_ids", "=", analysis_id.id),
                            ("pricelist_id", "=", self.order_id.pricelist_id.id),
                        ],
                        limit=1,
                    )
                    if pricelist_item:
                        price_unit += self._get_price_in_pricelist_item(
                            pricelist_item, pricelist_item.applied_on
                        )
                    else:
                        pricelist_item_all = self.env["product.pricelist.item"].search(
                            [
                                ("applied_on", "=", "3_global"),
                                ("pricelist_id", "=", self.order_id.pricelist_id.id),
                            ],
                            limit=1,
                        )
                        if pricelist_item_all:
                            price_unit += self._get_price_in_pricelist_item(
                                pricelist_item_all, pricelist_item.applied_on, analysis_id
                            )
                        else:
                            price_unit += analysis_id.price

                for parameter in self.parameter_ids:
                    if parameter not in self.analysis_group_ids.parameter_method_ids:
                        parameter_id = self.env["analytical.method.price"].search(
                            [("name", "=", parameter.name)], limit=1
                        )
                        pricelist_item = self.env["product.pricelist.item"].search(
                            [
                                ("analitycal_method_ids", "=", parameter_id.id),
                                ("pricelist_id", "=", self.order_id.pricelist_id.id),
                            ],
                            limit=1,
                        )
                        if pricelist_item:
                            price_unit += self._get_price_in_pricelist_item(
                                pricelist_item, pricelist_item.applied_on
                            )
                        else:
                            pricelist_item_all = self.env["product.pricelist.item"].search(
                                [
                                    ("applied_on", "=", "3_global"),
                                    ("pricelist_id", "=", self.order_id.pricelist_id.id),
                                ],
                                limit=1,
                            )
                            if pricelist_item_all:
                                price_unit += self._get_price_in_pricelist_item(
                                    pricelist_item_all,
                                    pricelist_item.applied_on,
                                    parameter_id,
                                )
                            else:
                                price_unit += parameter_id.price
        if self.price_type == "parameter":
            for parameter in self.parameter_ids:
                if parameter in self.parameter_ids:
                    parameter_id = self.env["analytical.method.price"].search(
                        [("name", "=", parameter.name)], limit=1
                    )
                    pricelist_item = self.env["product.pricelist.item"].search(
                        [
                            ("analitycal_method_ids", "=", parameter_id.id),
                            ("pricelist_id", "=", self.order_id.pricelist_id.id),
                        ],
                        limit=1,
                    )
                    if pricelist_item:
                        price_unit += self._get_price_in_pricelist_item(
                            pricelist_item, pricelist_item.applied_on
                        )
                    else:
                        pricelist_item_all = self.env["product.pricelist.item"].search(
                            [
                                ("applied_on", "=", "3_global"),
                                ("pricelist_id", "=", self.order_id.pricelist_id.id),
                            ],
                            limit=1,
                        )
                        if pricelist_item_all:
                            price_unit += self._get_price_in_pricelist_item(
                                pricelist_item_all,
                                pricelist_item.applied_on,
                                parameter_id,
                            )
                        else:
                            price_unit += parameter_id.price
        self.price_unit = price_unit

    @api.onchange("parameter_ids", "analysis_group_ids")
    def _onchange_analysis_ids(self):
        self._get_price_unit_sample()

    def _get_price_in_pricelist_item(
        self, pricelist_item, pricelist_type, product=None
    ):
        price = 0.00
        if pricelist_type == "4_analysis_group":
            product = pricelist_item.analysis_group_ids
        elif pricelist_type == "5_analytical_method":
            product = pricelist_item.analitycal_method_ids
        if pricelist_item.compute_price == "fixed":
            price = pricelist_item.fixed_price
        if pricelist_item.compute_price == "percentage":
            price = product.price - product.price * (pricelist_item.percent_price / 100)
        if pricelist_item.compute_price == "formula":
            if pricelist_item.base == "pricelist":
                if pricelist_item.base_pricelist_id:
                    parent_pricelist_item = self.env["product.pricelist.item"].search(
                        [
                            ("analysis_group_ids", "=", product.id),
                            ("pricelist_id", "=", pricelist_item.base_pricelist_id.id),
                        ],
                        limit=1,
                    )
                    if parent_pricelist_item:
                        price = self._get_price_in_pricelist_item(
                            parent_pricelist_item, parent_pricelist_item.applied_on
                        )
                    else:
                        parent_pricelist_item = self.env[
                            "product.pricelist.item"
                        ].search(
                            [
                                ("analitycal_method_ids", "=", product.id),
                                (
                                    "pricelist_id",
                                    "=",
                                    pricelist_item.base_pricelist_id.id,
                                ),
                            ],
                            limit=1,
                        )
                        if parent_pricelist_item:
                            price = self._get_price_in_pricelist_item(
                                parent_pricelist_item, parent_pricelist_item.applied_on
                            )
                        else:
                            parent_pricelist_item = self.env[
                                "product.pricelist.item"
                            ].search(
                                [
                                    ("applied_on", "=", "3_global"),
                                    (
                                        "pricelist_id",
                                        "=",
                                        pricelist_item.base_pricelist_id.id,
                                    ),
                                ],
                                limit=1,
                            )
                            price = self._get_price_in_pricelist_item(
                                parent_pricelist_item,
                                parent_pricelist_item.applied_on,
                                product,
                            )
                else:
                    price = product.price
            else:
                price = product.price
            price = (
                price
                - price * (pricelist_item.price_discount / 100)
                + pricelist_item.price_surcharge
            )
        return price
