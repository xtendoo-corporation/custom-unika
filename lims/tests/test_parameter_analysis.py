# Copyright 2022 - Daniel Domínguez <https://xtendoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestParameterAnalysis(TransactionCase):
    def _create_order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )

    def _create_line(self, order, product_id):
        self.env["sale.order.line"].create(
            {
                "name": product_id.name,
                "product_id": product_id.id,
                "product_uom_qty": 1,
                "product_uom": product_id.uom_id.id,
                "price_unit": 1000.00,
                "order_id": order.id,
            }
        )

    def _create_analytical_method(self, ref, name, uncertainty, description):
        self.env["lims.analytical.method"].create(
            {
                "default_code": ref,
                "name": name,
                "uncertainty": uncertainty,
                "description": description,
            }
        )

    def _create_limit_result(
        self,
        parameter_id,
        operator_from,
        limit_value_from,
        operator_to,
        limit_value_to,
        ptype,
        state,
    ):
        self.env["lims.analysis.parameter.limit.result"].create(
            {
                "parameter_ids": parameter_id,
                "operator_from": operator_from,
                "limit_value_from": limit_value_from,
                "operator_to": operator_to,
                "limit_value_to": limit_value_to,
                "type": ptype,
                "state": state,
            }
        )

    def _create_analysis_package(self, name, description, price, parameters_ids):
        self.env["lims.analysis"].create(
            {
                "name": name,
                "description": description,
                "price": price,
                "parameter_ids": parameters_ids,
            }
        )

    def _get_purchase_order_by_origin(self, origin):
        return self.env["purchase.order"].search([("origin", "=", origin)])

    def _get_stock_picking_by_purchase(self, purchase):
        return self.env["stock.picking"].search([("origin", "=", purchase)])

    def setUp(self):
        super(TestParameterAnalysis, self).setUp()

        self.partner = self.env["res.partner"].create(
            {
                "name": "Test",
            }
        )
        self.supplier = self.env["res.partner"].create(
            {
                "name": "Supplier Test",
            }
        )

        self.analytical_method_1 = self._create_analytical_method(
            "MET1", "Sample Method 1", 0.01, "Sample Method 1"
        )
        self.analytical_method_2 = self._create_analytical_method(
            "MET2", "Sample Method 2", 0.001, "Sample Method 2"
        )

        self.parameter_1 = self.env["lims.analysis.parameter"].create(
            {
                "default_code": "PAR1",
                "name": "Sample parameter 1",
                "parameter_uom": self.env.ref("uom.product_uom_unit").id,
                "analytical_method": self.analytical_method_1,
                "price": 15.23,
            }
        )
        # self._create_parameter(1,"PAR1", "Sample parameter 1", self.env.ref("uom.product_uom_unit").id, self.analytical_method_1, 15.23)
        self._create_limit_result(
            self.parameter_1.id, ">=", 3, None, None, "LIMIT", "not_conform"
        )
        self._create_limit_result(
            self.parameter_1.id, None, None, "<", 3, "LIMIT", "conform"
        )

        self.parameter_2 = self.env["lims.analysis.parameter"].create(
            {
                "default_code": "PAR2",
                "name": "Sample parameter 2",
                "parameter_uom": self.env.ref("uom.product_uom_unit").id,
                "analytical_method": self.analytical_method_2,
                "price": 10.12,
            }
        )
        self._create_limit_result(
            self.parameter_2.id, ">", 3, None, None, "LIMIT", "conform"
        )
        self._create_limit_result(
            self.parameter_2.id, None, None, "<", 3, "LIMIT", "not_conform"
        )

        self.analysis_package_1 = self._create_analysis_package(
            "Package Test", "Package Test", 12.56, self.parameter_1
        )
        self.product_sample = self.env["product.product"].create(
            {
                "name": "Sample Product",
                "is_product_sample": True,
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
                "analysis_ids": self.analysis_package_1,
            }
        )
        self.product_sample_2 = self.env["product.product"].create(
            {
                "name": "Sample Product 2",
                "is_product_sample": True,
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
            }
        )

    ##Crear venta con muestra para crear su analisis
    def test_create_sale_sample(self):
        order = self._create_order()
        self._create_line(order, self.product_sample)
        order.action_confirm()
        purchase_order = self._get_purchase_order_by_origin(order.name)
        stock_picking = self._get_stock_picking_by_purchase(purchase_order.name)

        self.assertEqual(len(stock_picking.move_ids_without_package), 1)
        for move in stock_picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        stock_picking.button_validate()
        stock_picking.create_all_analysis()
