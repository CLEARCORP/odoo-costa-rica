# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from openerp.tools.translate import _
from openerp.osv import fields, osv


class hrRulesalary(osv.Model):

    _inherit = 'hr.salary.rule'

    _defaults = {
        'amount_python_compute': '''
# Available variables:
#----------------------
# payslip: object containing the payslips
# employee: hr.employee object
# contract: hr.contract object
# rules: object containing the rules code (previously computed)
# categories: object containing the computed salary rule categories
(sum of amount of all rules belonging to that category).
# worked_days: object containing the computed worked days.
# inputs: object containing the computed inputs.
# company: object of res_company. It is a browse record
# hr_salary_rule: object for call hr_salary_rule functions
# cr: cursor 
# uid: uid

# Note: returned value have to be set in the variable 'result'

result = contract.wage * 0.10''',
        'condition_python':
'''
# Available variables:
#----------------------
# payslip: object containing the payslips
# employee: hr.employee object
# contract: hr.contract object
# rules: object containing the rules code (previously computed)
# categories: object containing the computed salary rule categories
(sum of amount of all rules belonging to that category).
# worked_days: object containing the computed worked days
# inputs: object containing the computed inputs
# company: object of res_company. It is a browse record
# hr_salary_rule: object for call hr_salary_rule functions
# cr: cursor 
# uid: uid

# Note: returned value have to be set in the variable 'result'

result = rules.NET > categories.NET * 0.10''',
    }

    def satisfy_condition(self, cr, uid, rule_id, localdict, context=None):
        """In this method we add a new BrowsableObject from hr.config settings.
        This is for use rent configuration for each company and compute the rent 
        amount in a standard way."""
        #Get user's company and hr.config.settings associated to the company
        company_obj = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id

        #Update localdict with new variable
        localdict.update({'company':company_obj})

        hr_salary_rule_obj = self.pool.get('hr.salary.rule') #object from hr salary rule to use in python code
        localdict.update({'hr_salary_rule':hr_salary_rule_obj})

        #add cr, uid at dictionary as a variables in python code
        localdict.update({'cr':cr})
        localdict.update({'uid':uid})

        result = super(hrRulesalary, self).satisfy_condition(cr, uid, rule_id, localdict, context=context)
        return result

    def compute_rent_employee(self, company, employee, SBT):
        """This function is designed to be called from python code in the salary rule.
        It receive as parameters the variables that can be used by default in 
        python code on salary rule.

        This function compute rent for a employee"""
        subtotal = 0.0
        exceed_2 = 0.0
        exceed_1 = 0.0
        total = 0.0

        limit1 = company.first_limit #From hr.conf.settings, it's in company
        limit2 = company.second_limit

        spouse_amount = company.amount_per_spouse
        child_amount = company.amount_per_child

        children_numbers = employee.report_number_child

        #exceed second limit
        if SBT >= limit2:
            exceed_2 = SBT - limit2
            subtotal += exceed_2 * 0.15 #15% of limit2
            limit_temp = (limit2 - limit1) * 0.10 #10% of difference between limits
            subtotal += limit_temp

        #exceed first limit
        elif SBT >= limit1:
            exceed_1 = SBT - limit1
            subtotal += exceed_1 * 0.10 #10% of limit1

        if subtotal and employee.report_spouse:
            total = subtotal - spouse_amount - (child_amount * children_numbers)
        elif subtotal:
            total = subtotal - (child_amount * children_numbers)
        return total

# =============================================================================
#     This function is designed to be called from python code in the salary
# rule.
#     It receive as parameters the variables that can be used by default in
#     python code on salary rule.
#     It receive company, a parameter and it is a res.company object, but also,
#     it can be declare inside in function
# =============================================================================
    def compute_total_rent(self, cr, uid, company, inputs, employee,
                           categories, payslip):
        """
            This function computes, based on previous gross salary and future
            base salary, the rent amount for current payslip. This is a
            "dynamic" way to compute amount rent for each payslip
        """
        """Objects"""
        payslip_obj = self.pool.get('hr.payslip')
        
        """
            If the payslip is a refund, we need to use the same amount calculated above
        """
        if payslip.credit_note:
            original_name = payslip.name.replace(_('Refund: '),'')
            original_payslip_id = payslip_obj.search(cr, uid, [('name','=',original_name),('employee_id','=', employee.id), ('date_to', '=', payslip.date_to), ('date_from','=', payslip.date_from)])[0]
            original_payslip = payslip_obj.browse(cr, uid, original_payslip_id)
            for line in original_payslip.line_ids:
                if line.code == 'RENTA':
                    return line.total
            return 0.0
        
        """Principal variables"""
        SBA = 0.0 #Previous Gross Salary
        SBP = 0.0 #Currently Gross Salary
        SBF = 0.0 #Future Base Salary
        SBT = 0.0 #Gross Salary Total (this is SBA + SBP + SBF)
        
        """Other variables"""
        rent_empl_total = 0.0
        total_curr_rent = 0.0
        total_paid_rent= 0.0
        total_payments = 0

        """"Get total payments"""
        previous_payments = payslip_obj.get_qty_previous_payment(cr, uid, employee, payslip)
        future_payments = payslip_obj.qty_future_payments(cr, uid, payslip)
        actual_payment = 1
        total_payments = previous_payments + actual_payment + future_payments

        """Update payments amount"""
        SBA = payslip_obj.get_SBA(cr, uid, employee, payslip)
        SBP = categories.BRUTO
        SBF = categories.BASE * future_payments
        SBT = SBA + SBP + SBF

        """Compute rent"""
        rent_empl_total = self.compute_rent_employee(company, employee, SBT) #Rent for a complete month
        total_paid_rent = payslip_obj.get_previous_rent(cr,uid,employee,payslip) #Rent already paid
        total_curr_rent = (rent_empl_total - total_paid_rent) / (future_payments + actual_payment) 

        return total_curr_rent

    def python_expresion_rent(self, cr, uid, company, inputs, employee, categories, payslip):
        """Function that evaluated if compute rent applies to salary rule"""
        total = self.compute_total_rent(cr, uid, company, inputs, employee, categories, payslip)
        if total != 0.0:
            return True
        else:
            return False
