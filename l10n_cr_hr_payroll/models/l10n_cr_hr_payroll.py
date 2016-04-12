# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tools
from openerp.osv import fields, osv
from datetime import datetime, date, timedelta
from openerp.tools.translate import _


class hrContract(osv.Model):
    """Employee contract based on the visa, work permits
    allows to configure different Salary structure"""

    _inherit = 'hr.contract'
    _columns = {
        'schedule_pay': fields.selection([
            ('fortnightly', 'Fortnightly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('semi-annually', 'Semi-annually'),
            ('annually', 'Annually'),
            ('weekly', 'Weekly'),
            ('bi-weekly', 'Bi-weekly'),
            ('bi-monthly', 'Bi-monthly'),
            ], 'Scheduled Pay', select=True),
    }

    _defaults = {
        'schedule_pay': 'monthly',
    }


class hrPaysliprun(osv.Model):

    _inherit = 'hr.payslip.run'

    _columns = {
        'schedule_pay': fields.selection([
            ('fortnightly', 'Fortnightly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('semi-annually', 'Semi-annually'),
            ('annually', 'Annually'),
            ('weekly', 'Weekly'),
            ('bi-weekly', 'Bi-weekly'),
            ('bi-monthly', 'Bi-monthly'),
            ], 'Scheduled Pay', select=True, readonly=True,
               states={'draft': [('readonly', False)]}),
    }


class hrPayslipinherit(osv.Model):

    _name = 'hr.payslip'

    _inherit = ['mail.thread', 'hr.payslip']

    # Get total payment per month
    def get_qty_previous_payment(self, cr, uid, employee, actual_payslip,
                                 context=None):
        payslip_ids = []
        date_to = datetime.strptime(actual_payslip.date_to, '%Y-%m-%d')
        if date_to.month < 10:
            first = str(date_to.year) + "-" + "0"+str(date_to.month) + "-" + "01"
        else:
             first = str(date_to.year) + "-" +str(date_to.month) + "-" + "01"
        first_date = datetime.strptime(first, '%Y-%m-%d')
        payslip_ids = self.pool.get('hr.payslip').search(cr, uid, [('employee_id','=', employee.id), ('date_to', '>=', first_date), ('date_to','<', actual_payslip.date_from)], context=context)
        return len(payslip_ids)

    # Get the previous payslip for an employee. Return all payslip that are in
    # the same month than current payslip
    def get_previous_payslips(self, cr, uid, employee, actual_payslip, context=None):
        payslip_list = []
        date_to = datetime.strptime(actual_payslip.date_to, '%Y-%m-%d')
        month_date_to = date_to.month
        year_date_to = date_to.year
        payslip_ids = self.pool.get('hr.payslip').search(cr, uid, [('employee_id','=', employee.id), ('date_to','<=', actual_payslip.date_to)], context=context)
        if actual_payslip.id in payslip_ids:
            position = payslip_ids.index(actual_payslip.id) 
            del payslip_ids[position] 
        
        for empl_payslip in self.pool.get('hr.payslip').browse(cr, uid, payslip_ids, context=context):
            temp_date = datetime.strptime(empl_payslip.date_to, '%Y-%m-%d')
            if (temp_date.month == month_date_to) and (temp_date.year == year_date_to):
                payslip_list.append(empl_payslip)
        return payslip_list

    # get SBA for employee (Gross salary for an employee)
    def get_SBA(self, cr, uid, employee, actual_payslip, context=None):
        SBA = 0.0
        payslip_list = self.get_previous_payslips(cr, uid, employee, actual_payslip, context=context) #list of previous payslips
        
        for payslip in payslip_list:
            for line in payslip.line_ids:
                if line.code == 'BRUTO':
                    if payslip.credit_note:
                        SBA -= line.total
                    else:
                        SBA += line.total
        return SBA

    # get previous rent
    def get_previous_rent(self, cr, uid, employee, actual_payslip, context=None):
        rent = 0.0
        payslip_list = self.get_previous_payslips(cr, uid, employee, actual_payslip, context=context) #list of previous payslips

        for payslip in payslip_list:
            for line in payslip.line_ids:
                if line.code == 'RENTA':
                    if payslip.credit_note:
                        rent -= line.total
                    else:
                        rent += line.total
        return rent

    # Get quantity of days between two dates
    def days_between_days(self, cr, uid, date_from, date_to, context=None):
        return abs((date_to - date_from).days)

    # Get number of payments per month
    def qty_future_payments(self, cr, uid, payslip, context=None):
        payments = 0

        date_from = datetime.strptime(payslip.date_from, '%Y-%m-%d')
        date_to = datetime.strptime(payslip.date_to, '%Y-%m-%d')

        dbtw = (self.days_between_days(cr, uid, date_from, date_to, context=context)) + 1#take in account previous date for start date

        next_date = date_to + timedelta(days=dbtw)
        month_date_to = date_to.month

        if month_date_to == 2:
            next_date = next_date - timedelta(days=2)

        month_date_next = next_date.month

        while(month_date_to == month_date_next):
            next_date = next_date + timedelta(days=dbtw)
            month_date_next = next_date.month
            payments += 1
        return payments

    def action_payslip_send(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the payslip template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'l10n_cr_hr_payroll', 'email_template_payslip')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'hr.payslip',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
