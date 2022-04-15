from odoo import fields, models


class Order(models.Model):
    _inherit = 'account.move'

    planned_workload_id = fields.Many2one('imofer.planned.workload', string="Planned Workload")

