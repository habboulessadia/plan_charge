from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class plannedWorkload(models.Model):
    _name = 'imofer.planned.workload'

    name = fields.Char(readonly=True, index=True, string="Panned workload name")
    responsible_id = fields.Many2one('res.users', string="Responsible", default=lambda self: self.env.user,
                                     required=True, tracking=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    driver_id = fields.Many2one(string="Driver", related='vehicle_id.driver_id', readonly=False)
    vehicle_capacity = fields.Float(string="Vehicle capacity", related='vehicle_id.vehicle_capacity')
    date = fields.Date(string="Date", default=fields.Date.today)
    weight_progress = fields.Float('Vehicle Weight progress', compute='compute_weight_progress')

    planned_workload_line_ids = fields.One2many('imofer.planned.workload.line', 'planned_workload_id',
                                                string="Planned workload lines",
                                                states={'cancel': [('readonly', True)], 'done': [('readonly', True)]},
                                                track_visibility='onchange')

    customer_id = fields.Many2one(string="Customer", related='planned_workload_line_ids.customer_id')
    state = fields.Selection([('draft', "Draft"), ('confirm', "Confirmed"), ('canceled', "Canceled")], string="State",
                             default='draft')
    note = fields.Text(string='Note')
    orders_ids = fields.One2many('sale.order', 'planned_workload_id', string="Orders")
    picking_ids = fields.One2many('stock.picking','planned_workload_id', string="Picking")
    manufacturing_ids = fields.One2many('mrp.production','planned_workload_id', string="Manufacturing")
    blance_reliquat_ids = fields.One2many('sale.order','planned_workload_id', string="Reliquat")
    invoices_ids = fields.One2many('account.move','planned_workload_id', string="invoices")
    # smart buttons
    orders_count = fields.Integer('Orders count', compute='compute_orders_count')
    invoice_count = fields.Integer('Invoice count', compute='compute_invoice_count')
    delivery_count = fields.Integer('Delivery count', compute='compute_delivery_count')
    manufacturing_order_count = fields.Integer('Manufacturing order count', compute='compute_manufacturing_order_count')
    reliquat_order_count = fields.Integer('Reliquat count', compute='compute_reliquat_order')


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env.ref("imofer_plan_charge.imofer_planned_load_sequence", raise_if_not_found=False) \
                .next_by_id()
        return super().create(vals_list)

    @api.depends("orders_ids")
    def compute_planned_workload_line_ids(self):
        for r in self:
            r.planned_workload_line_ids = False
            if len(r.orders_ids) > 0:
                for order in r.orders_ids:
                    for line in order.order_line:
                        pc_line_id = self.env['imofer.planned.workload.line'].sudo().create({
                            'product_template_id': line.product_template_id.id,
                            'description': line.name,
                            'quotation_id': line.order_id.id,
                            'customer_id': line.order_id.partner_id.id,
                            'uom_id': line.product_uom.id,
                            'quantity': line.product_uom_qty,
                            'planned_quantity': line.product_uom_qty,
                        }).id
                        r.planned_workload_line_ids = [(4, pc_line_id)]

    @api.depends('vehicle_id', 'planned_workload_line_ids')
    def compute_weight_progress(self):
        for r in self:
            total_weight = 0
            r.weight_progress = 0
            if len(r.planned_workload_line_ids) > 0:
                for pwl in r.planned_workload_line_ids:
                    if pwl.total_weight:
                        total_weight += pwl.total_weight
            if r.vehicle_capacity:
                r.weight_progress = (total_weight / r.vehicle_capacity) * 100

    def compute_orders_count(self):
        for order in self:
            order.orders_count = len(order.orders_ids)

    def compute_invoice_count(self):
        for r in self:
            r.invoice_count = len(r.invoices_ids)

    def compute_delivery_count(self):
        for r in self:
            r.delivery_count = len(r.picking_ids)

    def compute_manufacturing_order_count(self):
        for r in self:
            r.manufacturing_order_count = len(r.manufacturing_ids)

    def compute_reliquat_order(self):
        for r in self:
            r.reliquat_order_count = len(r.blance_reliquat_ids)

    def confirm_planning_workload(self):
        for r in self:
            r.state = 'confirm'

    def cancel_planning_workload(self):
        for r in self:
            r.state = 'canceled'

    def balance_quotation_view(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        orders = self.mapped('blance_reliquat_ids')
        if len(orders) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = orders.id
        else:
            action['domain'] = [('id', 'in', self.mapped('blance_reliquat_ids.id'))]
            action['context'] = dict(self._context, create=False)
        return action

    def orders_view(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        orders = self.mapped('orders_ids')
        if len(orders) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = orders.id
        else:
            action['domain'] = [('id', 'in', self.mapped('orders_ids.id'))]
            action['context'] = dict(self._context, create=False)
        return action

    def action_get_stock_picking(self):
        action = self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_all')
        action['domain'] = [('id', '=', self.picking_ids.id)]
        return action

    def action_view_picking(self):
        return self._get_action_view_picking(self.picking_ids)

    def _get_action_view_picking(self, pickings):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")

        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
            picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
            if picking_id:
              picking_id = picking_id[0]
            else:
              picking_id = pickings[0]
            action['context'] = dict(self._context, default_picking_type_id=picking_id.picking_type_id.id, default_origin=self.name)
        return action

    def manufacturing_order_view(self):
        pass

    def confirm_pc(self):
        for r in self.planned_workload_line_ids:
            if r.quantity > r.planned_quantity:
                sale_order = self.env['sale.order'].create({
                    'partner_id': self.customer_id.id,
                    'date_order': fields.Datetime.now(),
                    'order_line': [(0, 0, {
                        'product_id': r.product_template_id.id,
                        'product_uom_qty': r.quantity - r.planned_quantity,
                    })]
                })
                self.blance_reliquat_ids = sale_order
        for r in self:
            r.state = 'confirm'

    def cancel_pc(self):
        pass

    def action_generate_order_line(self):
        if self.orders_ids:
            for r in self:
                r.planned_workload_line_ids = False
                if len(r.orders_ids) > 0:
                    for order in r.orders_ids:
                        for line in order.order_line:
                            pc_line_id = self.env['imofer.planned.workload.line'].sudo().create({
                                'product_template_id': line.product_template_id.id,
                                'description': line.name,
                                'quotation_id': line.order_id.id,
                                'customer_id': line.order_id.partner_id.id,
                                'uom_id': line.product_uom.id,
                                'quantity': line.product_uom_qty,
                                'planned_quantity': line.product_uom_qty,
                            }).id
                            r.planned_workload_line_ids = [(4, pc_line_id)]
        else:
            raise ValidationError(
                ('Sale order required'))

