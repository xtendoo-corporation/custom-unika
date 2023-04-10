# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError

class LimsAnalysisNormative(models.Model):
    _name = "lims.analysis.normative"
    _description = "parameter LIMS normative"

    name = fields.Char(string="Name", store=True)
    parameter_ids = fields.Many2one(
        "lims.analysis.parameter",
        "Analysis lims parameter",
    )
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")
    parameter_uom = fields.Many2many(related="parameter_ids.parameter_uom")
    limit_result_line_ids = fields.One2many('lims.analysis.normative.result.line', 'parent_id', string='Limits Line')
    is_acreditation = fields.Boolean(string="Is Acreditation", store=True)

    # @api.constrains('parameter_ids', 'type', 'uom_id')
    # def _check_no_repeat(self):
    #     for record in self:
    #         ids = self.env['lims.analysis.limit'].search([('parameter_ids', '=', record.parameter_ids.id),('type', '=', record.type),('uom_id', '=', record.uom_id.id)])
    #         if ids:
    #             for id in ids:
    #                 if id.id != record.id:
    #                     uom_name = "Without UDM"
    #                     if id.uom_id:
    #                         uom_name = id.uom_id.name
    #                     raise ValidationError(
    #                     _('A combination already exists with the parameter %s, type %s y %s', id.parameter_ids.name, id.type, uom_name))
    #
    #
    # def open_limits_form(self):
    #     action = self.env["ir.actions.act_window"]._for_xml_id(
    #         "lims.open_limits_form"
    #     )
    #     action["context"] = {
    #         "parent_id": self.id,
    #         "required_comment": self.parameter_ids.required_comment,
    #     }
    #     action["domain"] = [('parent_id', '=', self.id)]
    #     if not self.uom_id.name:
    #         action["display_name"] = _("%s", self.type)
    #         return action
    #     type_text = self.type
    #     if self.type == 'technical':
    #         type_text = 'Ficha técnica'
    #     if self.type == 'legislation':
    #         type_text = 'Legislación'
    #     # if self.type == 'label':
    #     #     type_text = 'Etiquetado'
    #     action["display_name"] = _("%s -> %s", type_text, self.uom_id.name)
    #     return action






