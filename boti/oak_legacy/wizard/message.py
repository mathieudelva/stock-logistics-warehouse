from odoo import fields, models


# info message box
class MessageBox(models.TransientModel):
    _name = "message.box"
    _description = "Message box for warnings, success, ..."

    def get_default(self):
        if self.env.context.get("message", False):
            return self.env.context.get("message")
        return False

    name = fields.Text(string="message", readonly=True, default=get_default)
