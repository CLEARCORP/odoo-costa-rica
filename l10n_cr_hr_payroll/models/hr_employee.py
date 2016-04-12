# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class hr_employee(models.Model):

    _inherit = 'hr.employee'

    def _check_report_number_child(self, cr, uid, ids, context=None):
        for employee in self.browse(cr, uid, ids, context=context):
            if employee.report_number_child < 0:
                return False
        return True

    @api.onchange('marital')
    def _onchange_marital(self):
        self.report_spouse = False

    marital= fields.Selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')], String = 'Marital')
    report_spouse= fields.Boolean('Report Spouse', help="If this employee reports his spouse for rent payment")
    report_number_child= fields.Integer('Number of children to report', help="Number of children to report for rent payment")
    personal_email=fields.Char('Personal Email')

    _defaults = {
        'report_number_child': 0,
    }

    _constraints = [
        (_check_report_number_child, 'Error! The number of child to report must be greater or equal to zero.', ['report_number_child'])
    ]