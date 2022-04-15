from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class plannedWorkloadLine(models.Model):
    _name = 'imofer.planned.workload.line'
    _description = 'imofer.planned.workload.line'

    product_template_id = fields.Many2one('product.template', string='Product', readonly=True)
    description = fields.Char(string="Description", readonly=True)
    planned_workload_id = fields.Many2one('imofer.planned.workload', string="Planned Workload")
    quotation_id = fields.Many2one('sale.order', string="Quotation", readonly=True)
    customer_id = fields.Many2one('res.partner', string="Customer", readonly=True)
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure", readonly=True)
    product_weight = fields.Float(string="Product weight", related="product_template_id.weight")
    quantity = fields.Float(string="Quantity", readonly=True)
    planned_quantity = fields.Float(string="Planned Quantity", readonly=False)
    total_weight = fields.Float(string="Total weight", compute='compute_total_weight', readonly=True)

    def compute_total_weight(self):
        for r in self:
            r.total_weight = 0
            if r.product_weight and r.planned_quantity:
                r.total_weight = r.product_weight * r.planned_quantity

    @api.onchange('planned_quantity')
    def _check_planned_quantity(self):
        for r in self:
            if r.planned_quantity and r.quantity and r.planned_quantity > r.quantity:
                raise ValidationError(
                      ('Planned quantities on planned workload lines should not be greater than the quantities order.'))

