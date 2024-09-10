# Copyright 2024 Xtendoo.es - Daniel Domínguez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields

class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_report_base_filename(self):
        self.ensure_one()
        # Reemplaza los caracteres no válidos y personaliza el nombre del archivo
        customer_name = (self.partner_id.name or 'Customer').replace('/', '_')
        invoice_name = (self.name or 'INV').replace('/', '_')
        return f'{invoice_name}-{customer_name}'

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_sample_number_id(self, record):
        if record.move_id.invoice_origin:
            lista = [elemento.strip() for elemento in record.move_id.invoice_origin.split(',')]
            sales = self.env['sale.order'].search([('name', 'in', lista)])
            if sales:
                for sale in sales:
                    for line in sale.order_line:
                        if line._get_invoice_lines().id == record.id:
                            purchase_line = self.env['purchase.order.line'].search([('sale_line_id', '=', line.id)])
                            if purchase_line:
                                pickings = purchase_line.order_id.picking_ids
                                if pickings:
                                    for picking in pickings:
                                        if picking.move_ids_without_package:
                                            for move in picking.move_ids_without_package:
                                                if move.product_id == record.product_id:
                                                    move_lines = self.env['stock.move.line'].search(
                                                        [('move_id', '=', move.id)])
                                                    if move_lines:
                                                        for move_line in move_lines:
                                                            if move_line.lot_id:
                                                                return move_line.lot_id

        return
    def _get_sample_description(self):
        for record in self:
            sample_number_id = self._get_sample_number_id(record)
            if sample_number_id:
                record.description_in_lot = sample_number_id.description
            else:
                record.description_in_lot = ""

    description_in_lot = fields.Char(string="Description", compute='_get_sample_description')



    def _get_sample_number(self):
        for record in self:
            sample_number_id = self._get_sample_number_id(record)
            if sample_number_id:
                record.sample_number = sample_number_id.name
            else:
                record.sample_number = ""

    sample_number=fields.Char(string="Sample Number", compute='_get_sample_number')

    def _get_analysis_name(self):
        for record in self:
            analysis_name = ""
            if record.move_id.invoice_origin:
                lista = [elemento.strip() for elemento in record.move_id.invoice_origin.split(',')]
                sales = self.env['sale.order'].search([('name', 'in', lista)])
                if sales:
                    for sale in sales:
                        for line in sale.order_line:
                            if line._get_invoice_lines().id == record.id:
                                purchase_line = self.env['purchase.order.line'].search([('sale_line_id', '=', line.id)])
                                if purchase_line:
                                    pickings = purchase_line.order_id.picking_ids
                                    if pickings:
                                        for picking in pickings:
                                            analysis = picking._get_analysis()
                                            if analysis:
                                                analysis_name= analysis.name

            record.analysis_name = analysis_name

    analysis_name=fields.Char(string="Analysis Name", compute='_get_analysis_name')