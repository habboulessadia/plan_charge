from odoo import fields, models, api


class Order(models.Model):
    _inherit = 'sale.order'

    planned_workload_id = fields.Many2one('imofer.planned.workload', string="Planned Workload")



