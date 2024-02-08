from odoo import fields, models, api


class SaleChanges(models.TransientModel):
    _inherit = 'res.config.settings'

    merge_sale_order_lines = fields.Boolean(string='Merge Order Lines',
                                            help="If enabled, merge all sale order lines containing the same product.")

    def set_values(self):
        super(SaleChanges, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('merge_sale_order_lines', self.merge_sale_order_lines)

    def get_values(self):
        res = super(SaleChanges, self).get_values()

        merge_sale_order_lines = self.env['ir.config_parameter'].sudo().get_param('merge_sale_order_lines',
                                                                                  default=False)
        res.update(
            merge_sale_order_lines=merge_sale_order_lines
        )
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):
        merge_enabled = self.env['ir.config_parameter'].sudo().get_param('merge_sale_order_lines', default=False)

        if merge_enabled:
            existing_line = self.search(
                [('order_id', '=', vals.get('order_id')), ('product_id', '=', vals.get('product_id'))])
            if existing_line:
                existing_line.write({'product_uom_qty': existing_line.product_uom_qty + vals.get('product_uom_qty')})
                return existing_line

        return super(SaleOrderLine, self).create(vals)
