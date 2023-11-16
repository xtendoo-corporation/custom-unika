# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError

class LimsAnalysisLimit(models.Model):
    _name = "lims.analysis.limit"
    _description = "parameter LIMS Limit"
    parameter_ids = fields.Many2one(
        "lims.analysis.parameter",
        "Analysis lims parameter",
    )
    type = fields.Selection(
        [
            ("technical", "Data sheet"),
            ("legislation", "Legislation"),
        ])
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")
    legislation_name = fields.Char(
        string="Nombre Legislación",
    )
    parameter_uom = fields.Many2many(related="parameter_ids.parameter_uom")
    limit_result_line_ids = fields.One2many('lims.analysis.limit.result.line', 'parent_id', string='Limits Line')

    @api.constrains('parameter_ids', 'type', 'uom_id')
    def _check_no_repeat(self):
        for record in self:
            domain = [
                ('parameter_ids', '=', record.parameter_ids.id),
                ('type', '=', record.type),
                ('uom_id', '=', record.uom_id.id),
            ]

            existing_records = self.env['lims.analysis.limit'].search(domain)

            for existing_record in existing_records.filtered(lambda r: r.id != record.id):
                uom_name = existing_record.uom_id.name if existing_record.uom_id else "Without UDM"
                raise ValidationError(
                    _('A combination already exists with the parameter %s, type %s and %s',
                      existing_record.parameter_ids.name, existing_record.type, uom_name)
                )

    def open_limits_form(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("lims.open_limits_form")
        action_context = {
            "parent_id": self.id,
            "required_comment": self.parameter_ids.required_comment,
        }
        action_domain = [('parent_id', '=', self.id)]
        if not self.uom_id.name:
            action["display_name"] = _(f"{self.type}")
        else:
            type_text = {
                'technical': 'Ficha técnica',
                'legislation': 'Legislación',
                # Agrega más mapeos según sea necesario
            }.get(self.type, self.type)
            display_name = f"{type_text} -> {self.uom_id.name}"
            action["display_name"] = _(display_name)
        action.update({
            "context": action_context,
            "domain": action_domain,
        })
        return action






