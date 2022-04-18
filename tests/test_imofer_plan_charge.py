import time
from datetime import datetime, timedelta
from odoo.tests import common, Form
from odoo.exceptions import UserError, AccessError


class TestPlanCharge(common.TransactionCase):

    def setUp(self):
        super().setUp()

        # Relative models
        self.ResPartner = self.env['res.partner']
        self.VehicleFleet = self.env['fleet.vehicle']
        self.ProductTemplate = self.env['product.template']
        self.PlanningWorkload = self.env['imofer.planned.workload']
        self.SaleOrder = self.env['sale.order']

        #Créer 2 Véhicules ( fleet.vehicle )avec chacun
        # un conducteur et un poids respectif de 100kg et 200kg
        # Create driver
        self.driver1 = self.ResPartner.create({
            'name': "driver1",
            'email': "driver1@yourcompany.example.com",
        })
        self.driver2 = self.ResPartner.create({
            'name': "driver2",
            'email': "driver2@yourcompany.example.com",
        })
        # create vehicle

        model = self.env['fleet.vehicle.model'].create({
            'name': 'Opel Model',
            'brand_id': self.env.ref('fleet.brand_opel').id,
        })

        self.vehicle1 = self.VehicleFleet.create({
            'model_id': model.id,
            'license_plate': '1-JFC-095',
            'acquisition_date': time.strftime('%Y-01-01'),
            'co2': 88,
            'driver_id': self.driver1.id,
            'plan_to_change_car': True,
            'car_value': 38000,
            'vehicle_capacity': 100

        })
        self.vehicle2 = self.VehicleFleet.create({
            'model_id': model.id,
            'license_plate': '1-JFC-095',
            'acquisition_date': time.strftime('%Y-01-01'),
            'co2': 88,
            'driver_id': self.driver2.id,
            'plan_to_change_car': True,
            'car_value': 38000,
            'vehicle_capacity': 200

        })
        #Créer 4 articles stockable (product.template) avec des poids de 12, 5, 9,20 kg
        #Récuperer les variantes d'articles (product.product) de ces articles créés
        # avec la methode "product_variant_ids[0]"
        #create Article
        self.product1 = self.env['product.template'].create({
            'name': 'product1',
            'type': 'product',
            'weight': 12
        })
        self.product2 = self.env['product.template'].create({
            'name': 'product2',
            'type': 'product',
            'weight': 5
        })
        self.product3 = self.env['product.template'].create({
            'name': 'product3',
            'type': 'product',
            'weight': 9
        })
        self.product4 = self.env['product.template'].create({
            'name': 'product4',
            'type': 'product',
            'weight': 20
        })
        # variante article
        self.article1_variant = self.product1.product_variant_ids[0]
        self.article2_variant = self.product2.product_variant_ids[0]
        self.article3_variant = self.product3.product_variant_ids[0]
        self.article4_variant = self.product4.product_variant_ids[0]

        # Créer 4 devis ( SO1, SO2, SO3, SO4 ) ( sale.order ) avec chacune
        # minimum deux lignes de devis contenants les variantes d'articles.
        #create sale order
        self.partner1 = self.ResPartner.create({
            'name': "partner1",
            'email': "partner1@yourcompany.example.com",
        })
        self.so1 = self.env['sale.order'].create({
            'name': 'SO/01/01',
            'reference': 'so1',
            'partner_id': self.partner1.id,
            'order_line': [(0, 0, {
                'product_id': self.article1_variant.id,
                'product_uom_qty': 20,
                'price_unit': 15,
            },
            {
                'product_id': self.article2_variant.id,
                'product_uom_qty': 16,
                'price_unit': 100,
            })]
        })

        self.partner2 = self.ResPartner.create({
            'name': "partner2",
            'email': "partner2@yourcompany.example.com",
        })

        self.so2 = self.env['sale.order'].create({
            'name': 'SO/02/02',
            'reference': 'so2',
            'partner_id': self.partner2.id,
            'order_line': [(0, 0, {
                'product_id': self.article2_variant.id,
                'product_uom_qty': 10,
                'price_unit': 20,
            },
            {
                'product_id': self.article3_variant.id,
                'product_uom_qty': 34,
                'price_unit': 100,
            }
            )]
        })
        self.partner3 = self.ResPartner.create({
            'name': "partner3",
            'email': "partner3@yourcompany.example.com",
        })
        self.so3 = self.env['sale.order'].create({
            'name': 'SO/03/03',
            'reference': 'so3',
            'partner_id': self.partner3.id,
            'order_line': [(0, 0, {
                'product_id': self.article3_variant.id,
                'product_uom_qty': 30,
                'price_unit': 20,
            },
            {
                 'product_id': self.article3_variant.id,
                 'product_uom_qty': 34,
                 'price_unit': 100,
            }
            )]
        })
        self.partner4 = self.ResPartner.create({
            'name': "partner4",
            'email': "partner4@yourcompany.example.com",
        })
        self.so4 = self.env['sale.order'].create({
            'name': 'SO/04/04',
            'reference': 'so4',
            'partner_id': self.partner4.id,
            'order_line': [(0, 0, {
                'product_id': self.article4_variant.id,
                'product_uom_qty': 20,
                'price_unit': 20,
            },
            {
                'product_id': self.article3_variant.id,
                'product_uom_qty': 34,
                'price_unit': 100,
            }
            )]
        })
        #Créer 4 plan de charges PC1, PC2, PC3, PC4
        self.pc1 = self.PlanningWorkload.create({
            'vehicle_id' : self.vehicle1.id,
            'date' : time.strftime('%Y-06-06'),
            'orders_ids' : self.so1
        })
        self.sopc2 = [self.so2, self.so3]
        self.pc2 = self.PlanningWorkload.create({
            'vehicle_id': self.vehicle2.id,
            'date': time.strftime('%Y-10-11'),
            'orders_ids': [(6, 0, [s.id for s in self.sopc2])]
        })
        self.pc3 = self.PlanningWorkload.create({
            'vehicle_id': self.vehicle1.id,
            'date': time.strftime('%Y-10-11'),
        })
        self.pc4 = self.PlanningWorkload.create({
            'vehicle_id': self.vehicle2.id,
            'date': time.strftime('%Y-10-11'),
            'orders_ids': self.so4
        })

    def test_imofer_plan_charge(self):
        print('---------------------------------------------hhhh-----------------------')
        # Check vehicle
        self.assertTrue(self.vehicle1.id, 'Vehicle1 not created')
        self.assertTrue(self.vehicle2.id, 'Vehicle2 not created')
        #check driver
        self.assertTrue(self.driver1.id, 'driver1 not created')
        self.assertTrue(self.driver2.id, 'driver1 not created')
        # check sale order
        self.assertTrue(self.so1.id, 'so1 not created')
        self.assertTrue(self.so2.id, 'so2 not created')
        self.assertTrue(self.so3.id, 'so3 not created')
        self.assertTrue(self.so4.id, 'so4 not created')
        # check pc
        self.assertTrue(self.pc1.id, 'pc1 not created')
        self.assertTrue(self.pc2.id, 'pc2 not created')
        self.assertTrue(self.pc3.id, 'pc3 not created')
        self.assertTrue(self.pc4.id, 'pc4 not created')
        # Check
        self.assertEqual(self.driver1.name, 'driver1','wong name')

        ## generate pc lines
        self.pc1.action_generate_order_line()
        ## test generation
        self.assertTrue(self.pc1.planned_workload_line_ids, 'pc1 lines not generated')
        ##modify quantity
        self.pc1.planned_workload_line_ids.planned_quantity = self.pc1.planned_workload_line_ids.planned_quantity - 2
        ## confirmer plan charge
        self.pc1.confirm_pc()
        ## confirm so1
        self.so1.action_confirm()
        ## test delivery_ids
        self.assertTrue(self.pc1.picking_ids, 'delivery ids not genrated')

        #raise error pc3
        with self.assertRaises(UserError):
            self.pc3.confirm_pc()

        #generate lines and confirm pc2
            ## generate pc lines
            self.pc2.action_generate_order_line()
            ## test generation
            self.assertTrue(self.pc2.planned_workload_line_ids, 'pc2 lines not generated')
            ## confirmer plan charge
            self.pc2.confirm_pc()
            #bon de commande pc2
            self.so2.action_confirm()
            self.so2._create_invoices()
            # Check pc2 invoices and so2 invoices
            self.assertEqual(self.pc2.invoices_ids, self.so2.invoice_ids, 'wrong pc2 invoices')

        #pc4
            with self.assertRaises(UserError):
                self.pc4.confirm_pc()
            ## generate pc lines
            self.pc4.action_generate_order_line()
            ## test generation
            self.assertTrue(self.pc4.planned_workload_line_ids, 'pc4 lines not generated')
            ## confirmer plan charge
            self.pc4.confirm_pc()

        #creation manufacturing order
        self.mo = self.env['mrp.production'].create({
            'origin' : self.so4.name,
            'product_id': self.article4_variant.id,
            'product_uom_id': 18,
        })
        ## tester manufacturing_ids
        self.assertTrue(self.pc4.manufacturing_ids, 'manufacturing_ids not generated')




