# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from report import report_sxw
from tools.translate import _
import pooler
from osv import fields,osv

from openerp.addons.account_financial_report_webkit.report.trial_balance import TrialBalanceWebkit
from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser

def sign(number):
    return cmp(number, 0)

class ProfitStatementReport(TrialBalanceWebkit):
    def __init__(self, cr, uid, name, context):
        super(ProfitStatementReport, self).__init__(cr, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr
        #This line is to delete, the header of trial balance
        self.localcontext['additional_args'][4] = ('--header-left', '')
        self.localcontext.update({
            'cr': self.cr,
            'uid': self.uid,
            'get_fiscalyear': self.get_fiscalyear,
            'get_last_period': self.get_last_period,
            'get_data': self.get_data,
        })
        
    def set_context(self, objects, data, ids, report_type=None):
        start_period = self._get_form_param('period_from', data)
        
        self.localcontext.update({
            'start_period': start_period,
            })
        return super(ProfitStatementReport, self).set_context(objects, data, ids, report_type=report_type)
    
    def get_last_period_fiscalyear(self, cr, uid, fiscalyear):
        account_period_obj = self.pool.get('account.period')
        period_ids = account_period_obj.search(cr, uid, [('fiscalyear_id', '=', fiscalyear.id), ('special', '=', False)])
        periods = account_period_obj.browse(cr, uid, period_ids)
        period_select = periods[0]
        for current_period in periods:
            if current_period.date_start > period_select.date_start:
                period_select = current_period
        return period_select
    
    def get_last_period(self, cr, uid, start_period):
        account_period_obj = self.pool.get('account.period')
        period_ids = account_period_obj.search(cr, uid, [('fiscalyear_id', '=', start_period.fiscalyear_id.id), ('special', '=', False)])
        periods = account_period_obj.browse(cr, uid, period_ids)
        period_select = start_period
        for period in periods:
            if (period.date_start < start_period.date_start and period.date_start > period_select.date_start) or (period.date_start < start_period.date_start and start_period == period_select):
                period_select = period
        if period_select == start_period:
            fiscalyear = self.get_fiscalyear(cr, uid, start_period)
            fiscalyear_select = fiscalyear
            account_fiscalyear_obj = self.pool.get('account.fiscalyear')
            all_fiscalyears_ids = account_fiscalyear_obj.search(cr, uid, [])
            all_fiscalyears = account_fiscalyear_obj.browse(cr, uid, all_fiscalyears_ids)
            for current_fiscalyear in all_fiscalyears:
                if (current_fiscalyear.date_start < fiscalyear.date_start and current_fiscalyear.date_start > fiscalyear_select.date_start) or (current_fiscalyear.date_start < fiscalyear.date_start and fiscalyear == fiscalyear_select):
                    fiscalyear_select = current_fiscalyear
            if fiscalyear_select == fiscalyear:
                raise osv.except_osv(_('Error fiscal year'),_('There is no previous period to compare'))
            period_select = self.get_last_period_fiscalyear(cr, uid, fiscalyear_select)
        return period_select
        
    def get_fiscalyear(self, cr, uid, start_period):
        fiscalyear = start_period.fiscalyear_id
        return fiscalyear
     
    def get_data(self, cr, uid, data, context={}):
        account_account_obj = self.pool.get('account.account')
        account_period_obj = self.pool.get('account.period')
        library_obj = self.pool.get('account.webkit.report.library')
        
        #TODO: remove dependency of c2c
        account_chart_id = self._get_form_param('chart_account_id', data)
        
        account_chart = account_account_obj.browse(cr, uid, account_chart_id)
        company_id = account_chart['company_id'].id
        category_account_ids = library_obj.get_category_accounts(cr, uid, company_id)
        period = account_period_obj.browse(cr, uid, self._get_form_param('period_from', data))
        last_period = self.get_last_period(cr, uid, period)
        fiscal_year = self.get_fiscalyear(cr, uid, period)
        filter_type = self._get_filter(data)
        
        #build account_ids list
        income_account_ids = library_obj.get_account_child_ids(cr, uid, category_account_ids['income'])
        expense_account_ids = library_obj.get_account_child_ids(cr, uid, category_account_ids['expense'])
        
        #build accounts list
        income_accounts = account_account_obj.browse(cr, uid, income_account_ids)
        expense_accounts = account_account_obj.browse(cr, uid, expense_account_ids)
        
        #build balances
        income_period_balances =        library_obj.get_account_balance(cr, uid, income_account_ids,  ['balance'], start_period_id=period.id, end_period_id=period.id,filter_type=filter_type)
        expense_period_balances =       library_obj.get_account_balance(cr, uid, expense_account_ids, ['balance'], start_period_id=period.id, end_period_id=period.id,filter_type=filter_type)
        income_last_period_balances =   library_obj.get_account_balance(cr, uid, income_account_ids,  ['balance'], start_period_id=last_period.id, end_period_id=last_period.id,filter_type=filter_type)
        expense_last_period_balances =  library_obj.get_account_balance(cr, uid, expense_account_ids, ['balance'], start_period_id=last_period.id, end_period_id=last_period.id,filter_type=filter_type)
        income_fiscal_year_balances =   library_obj.get_account_balance(cr, uid, income_account_ids,  ['balance'], end_period_id=period.id, fiscal_year_id=fiscal_year.id,filter_type=filter_type)
        expense_fiscal_year_balances =  library_obj.get_account_balance(cr, uid, expense_account_ids, ['balance'], end_period_id=period.id, fiscal_year_id=fiscal_year.id, filter_type=filter_type)
        
        #build total balances
        total_income_balances = {
            'period':       income_period_balances[category_account_ids['income'].id]['balance'],
            'last_period':  income_last_period_balances[category_account_ids['income'].id]['balance'],
            'fiscal_year':  income_fiscal_year_balances[category_account_ids['income'].id]['balance'],
        }
        total_expense_balances = {
            'period':       expense_period_balances[category_account_ids['expense'].id]['balance'],
            'last_period':  expense_last_period_balances[category_account_ids['expense'].id]['balance'],
            'fiscal_year':  expense_fiscal_year_balances[category_account_ids['expense'].id]['balance'],
        }
            
        return {
            'income_accounts':              income_accounts,
            'expense_accounts':             expense_accounts,
            'income_account_ids':           income_account_ids,
            'expense_account_ids':          expense_account_ids,
            'total_income_balances':        total_income_balances,
            'total_expense_balances':       total_expense_balances,
            'income_period_balances':       income_period_balances,
            'expense_period_balances':      expense_period_balances,
            'income_last_period_balances':  income_last_period_balances,
            'expense_last_period_balances': expense_last_period_balances,
            'income_fiscal_year_balances':  income_fiscal_year_balances,
            'expense_fiscal_year_balances': expense_fiscal_year_balances,
        }
        

HeaderFooterTextWebKitParser(
    'report.l10n_cr_account_financial_statements.account.profit_statement_report',
    'account.account',
    'addons/l10n_cr_account_financial_statements/report/profit_statement_report.mako',
    parser=ProfitStatementReport)
