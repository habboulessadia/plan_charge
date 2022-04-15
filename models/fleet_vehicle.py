from odoo import models, fields, api


class Vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    vehicle_capacity = fields.Float(string="Capacity")
