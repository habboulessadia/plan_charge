from odoo import fields, models


class Picking(models.Model):
    _inherit = 'stock.picking'

    planned_workload_id = fields.Many2one('imofer.planned.workload', string="Planned Workload")

