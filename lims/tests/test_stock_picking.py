# Copyright 2022 - Daniel Domínguez <https://xtendoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
class TestSalePurchase(TransactionCase):

    def test_correctly_computes_analysis_count(self):
        # Arrange
        order = self.env['stock.picking'].create({})
        order.move_line_nosuggest_ids = [(0, 0, {'id': 1}), (0, 0, {'id': 2})]
        order.move_line_nosuggest_ids[0].lot_id = self.env['stock.production.lot'].create({'id': 1})
        order.move_line_nosuggest_ids[1].lot_id = self.env['stock.production.lot'].create({'id': 2})

        # Act
        order._compute_analysis_count()

        # Assert
        assert order.analysis_count == 2

    def test_returns_correct_analysis_count_for_orders_with_analysis(self):
        # Arrange
        order = self.env['stock.picking'].create({})
        order.move_line_nosuggest_ids = [(0, 0, {'id': 1}), (0, 0, {'id': 2})]
        order.move_line_nosuggest_ids[0].lot_id = self.env['stock.production.lot'].create({'id': 1})
        order.move_line_nosuggest_ids[1].lot_id = self.env['stock.production.lot'].create({'id': 2})
        self.env['lims.analysis.line'].create({'stock_move_line_id': 1})
        self.env['lims.analysis.line'].create({'stock_move_line_id': 2})

        # Act
        order._compute_analysis_count()

        # Assert
        assert order.analysis_count == 2

    def test_returns_zero_for_orders_with_no_analysis(self):
        # Arrange
        order = self.env['stock.picking'].create({})

        # Act
        order._compute_analysis_count()

        # Assert
        assert order.analysis_count == 0

    def test_handles_orders_with_no_move_lines(self):
        # Arrange
        order = self.env['stock.picking'].create({})

        # Act
        order._compute_analysis_count()

        # Assert
        assert order.analysis_count == 0

    def test_handles_orders_with_move_lines_without_suggested_products(self):
        # Arrange
        order = self.env['stock.picking'].create({})
        order.move_line_nosuggest_ids = [(0, 0, {'id': 1}), (0, 0, {'id': 2})]

        # Act
        order._compute_analysis_count()

        # Assert
        assert order.analysis_count == 0

    def test_handles_orders_with_move_lines_with_non_sample_suggested_products(self):
        # Arrange
        order = self.env['stock.picking'].create({})
        order.move_line_nosuggest_ids = [(0, 0, {'id': 1}), (0, 0, {'id': 2})]
        order.move_line_nosuggest_ids[0].product_id.is_product_sample = False
        order.move_line_nosuggest_ids[1].product_id.is_product_sample = False

        # Act
        order._compute_analysis_count()

        # Assert
        assert order.analysis_count == 0