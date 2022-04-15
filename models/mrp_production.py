from odoo import fields, models


class Manufacturing(models.Model):
    _inherit = 'mrp.production'

    planned_workload_id = fields.Many2one('imofer.planned.workload', string="Planned Workload")

