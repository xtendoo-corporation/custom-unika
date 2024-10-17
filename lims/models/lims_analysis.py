# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from collections import Counter


class LimsAnalysis(models.Model):
    _name = "lims.analysis"
    _description = "Analysis LIMS"
    name = fields.Char(string="Name", store=True)

    def _is_name_in_use(self, name):
        package = self.env['lims.analysis'].search(
            [
                ("name", "=", name),
            ], )
        if package:
            return True
        return False

    description = fields.Char(string="Description", store=True)

    product_ids = fields.Many2many(
        "product.template",
        "product_template_lims_analysis_group_rel",
        "analysis_group_id",
        "product_id",
        "Products",
    )
    sale_line_ids = fields.Many2many(
        "sale.order.line",
        "line_analysis_group_rel",
        "analysis_group_id",
        "sale_line_id",
        "Lines",
    )

    @api.depends('parameter_method_ids_new')
    def _get_parameter_domain(self):
        print("*"*50)
        print("En el compute")
        parameters_ids = []
        parameter_used = False
        parameter_repeat = False

        for method in self.parameter_method_ids_new:
            parameters_ids.append(method.parameter_id.id)
            print("En el compute", method.id)
            parameter_used = self.env['parameter.analytical.method.price.uom'].search([('parameter_id', 'in', parameters_ids)])
            print("En el compute", parameter_used)
        if parameter_used:
            self.parameter_used_ids = parameter_used
        else:
            self.parameter_used_ids = False
        print("*"*50)

    parameter_method_ids = fields.One2many(
        "parameter.analytical.method.price.uom",
        "parent_id",
    )
    parameter_method_ids_new = fields.Many2many(
        'parameter.analytical.method.price.uom',  # El modelo relacionado
        'parameter_method_analysis',  # Nombre de la tabla intermedia
        'parameter_method_id_new',  # Campo que apunta al modelo 'Course'
        'parent_id_new',  # Campo que apunta al modelo 'Student'
        string='Métodos'
    )
    parameter_used_ids = fields.Many2many(
        "parameter.analytical.method.price.uom",
        store=False,
        compute=_get_parameter_domain

    )
    price = fields.Float("Price", store=True)
    def _get_company_id(self):
        return self.env.user.company_id
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=_get_company_id,
    )
    active = fields.Boolean(default=True, string="Active")

    @api.model
    def create(self, vals):
        if vals['name'] and vals['name'] != '':
            is_in_use = self._is_name_in_use(vals['name'])
            if is_in_use:
                if not self.name:
                    raise UserError(_("El nombre debe ser único para cada paquete analítico"))
                else:
                    vals['name'] = vals['name'] + '(Copia)'
        res = super(LimsAnalysis, self).create(vals)
        for parameter_method in self.parameter_method_ids:
            self.env['parameter.analytical.method.price.uom'].create({
                'parent_id': res.id,
                'analytical_method_id': parameter_method.analytical_method_id.id,
                'uom_id': parameter_method.uom_id.id,
                'use_acreditation': parameter_method.use_acreditation,
                'used_acreditation': parameter_method.used_acreditation,
                'use_normative': parameter_method.use_normative,
                'used_normative': parameter_method.used_normative,
            })
        return res


    def write(self, vals):
        print("*"*50)
        print("En EL write", vals)

        parameter_repeat = False
        if vals.get('name'):
            if vals['name']:
                package = self.env['lims.analysis'].search(
                    [
                        ("name", "=", vals['name']),
                        ("id", "!=", self.id),
                    ], )
                if package:
                    raise UserError(_("El nombre debe ser único para cada paquete analítico"))
        res = super(LimsAnalysis, self).write(vals)
        # if vals.get('parameter_method_ids_new'):
        #     print("parameters", vals['parameter_method_ids_new'])
        #     print("*" * 50)
        return res

    @api.constrains('parameter_method_ids_new')
    def _check_unique_parameter_id(self):
        for record in self:
            parameter_used = []
            parameter_ids = record.parameter_method_ids_new.mapped('parameter_id')
            for parameter in record.parameter_method_ids_new:
                parameter_used.append(parameter.parameter_id.id)
            for parameter_id in parameter_ids:
                if parameter_used.count(parameter_id.id) > 1:
                    raise ValidationError(_("Parámetro %s duplicado.") % parameter_id.name)
                # parameter_id_to_check = parameter.parameter_id
                #
                # # Contar cuántas veces se repite el ID específico
                # repeticiones = len([param_id for param_id in parameter_ids if param_id == parameter_id_to_check])
                #
                # # Mostrar el resultado
                # print(f"El ID {parameter_id_to_check} se repite {repeticiones} veces.")
                # # if parameter.parameter_id in parameter_ids:
                # #     raise ValidationError(_("Parámetro %s duplicado.") % parameter.parameter_id.name)

        # if self.parameter_method_ids and res:
        #     parameter_values = [{
        #         'parent_id': res.id,
        #         'analytical_method_id': parameter.analytical_method_id.id,
        #         'uom_id': parameter.uom_id.id,
        #         'use_acreditation': parameter.use_acreditation,
        #         'used_acreditation': parameter.used_acreditation,
        #         'use_normative': parameter.use_normative,
        #         'used_normative': parameter.used_normative,
        #     } for parameter in self.parameter_method_ids]
        #
        #     self.env['parameter.analytical.method.price.uom'].create(parameter_values)
        #
        # return res
