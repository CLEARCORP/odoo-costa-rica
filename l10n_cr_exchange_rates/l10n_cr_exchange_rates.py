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

from osv import osv, fields
from tools.translate import _

class AccountAccount(osv.osv):
    _name = "account.account"
    _inherit = "account.account"
    
    _columns = {
        'exchange_rate_adjustment': fields.boolean('Exchange rate adjustment', help="Choose if the account needed an adjusted exchange rate"),
    }
    
class AccountMoveLine(osv.osv):
    _name = "account.move.line"
    _inherit = "account.move.line"
    
    def _amount_exchange_rate(self, cr, uid, ids, field_names, args, context=None):
        """
           This function returns an amount of exchange rate base in the debit/credit and amount_currency,
           and returns an amount of exchange rate of the day.
        """
        res = {}
        if context is None:
            context = {}
        res_currency_obj = self.pool.get('res.currency')
        res_currency_rate_obj = self.pool.get('res.currency.rate')
        res_users_obj = self.pool.get('res.users')
        
        res_user = res_users_obj.browse(cr, uid, uid, context=context)
        company_currency = res_user.company_id.currency_id
        
        lines = self.browse(cr, uid, ids, context=context)
        for move_line in lines:
            res[move_line.id] = {
                'amount_exchange_rate': 0.0,
                'amount_base_import_exchange_rate': 0.0,
            }

            if not move_line.currency_id or move_line.amount_currency == 0:
                continue
            if move_line.debit and move_line.debit > 0.00:
                sign = move_line.amount_currency < 0 and -1 or 1
                result = sign * move_line.debit / move_line.amount_currency
                res[move_line.id]['amount_exchange_rate'] = res_currency_obj.round(cr, uid, move_line.currency_id, result) or result
            elif move_line.credit and move_line.credit > 0.00:
                sign = move_line.amount_currency < 0 and -1 or 1
                result = sign * move_line.credit / move_line.amount_currency
                res[move_line.id]['amount_exchange_rate'] = res_currency_obj.round(cr, uid, move_line.currency_id, result) or result
            res[move_line.id]['amount_base_import_exchange_rate'] = res_currency_obj.get_exchange_rate(cr, uid, move_line.currency_id, company_currency, move_line.date, context)
        return res
    
    _columns = {
        'amount_exchange_rate': fields.function(_amount_exchange_rate, string='Amount of exchange rate', multi="residual", help="The amount of exchange rate."),
        'amount_base_import_exchange_rate': fields.function(_amount_exchange_rate, string='Base amount exchange rate', multi="residual", help="Exchange rate in the system."),
        'adjustment': fields.many2one('account.move.line', 'Adjustment'),
    }
    
    def copy(self, cr, uid, id, default={}, context=None):
        default.update({
            'adjustment':False,
        })

class AccountMove(osv.osv):
    _name = "account.move"
    _inherit = "account.move"
    
    def get_balance_amount(self, cr, uid, id, context):
        cr.execute( 'SELECT SUM(debit-credit) '\
                    'FROM account_move_line '\
                    'WHERE move_id = %s ', (id,))
        result = cr.fetchall()
        return result[0][0] or 0.00
    
    def generate_adjustment_move(self, cr, uid, reference, journal, period, context=None):
        move_line_obj = self.pool.get('account.move.line')
        res_currency_obj = self.pool.get('res.currency')
        res_currency_rate_obj = self.pool.get('res.currency.rate')
            
        res_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_currency = res_user.company_id.currency_id
        name = reference + " " + period.name
        
        move_created = {
                    'ref': name,
                    'journal_id': journal.id,
                    'period_id': period.id,
                    'to_check': False,
                    'company_id': res_user.company_id.id,
                    }
        move_created_id = self.create(cr, uid, move_created)
        
        total_credit = 0.00
        total_debit = 0.00
        exchange_rate_end_period = res_currency_obj._current_rate(cr, uid, [company_currency.id], period.date_stop, arg=None, context=context)[company_currency.id]
        
        account_ids = self.pool.get('account.account').search(cr, uid, [('exchange_rate_adjustment', '=', True)], context=context)
        line_ids = move_line_obj.search(cr, uid, [('currency_id','!=',None), ('period_id','=',period.id), ('amount_currency','!=',0), ('account_id','in',account_ids), ('adjustment','=',None)], context=context)
        lines = move_line_obj.browse(cr, uid, line_ids, context=context)
        
    
        for line in lines:
            if line.move_id.state == 'draft' or not line.amount_currency:
                continue
            
            sign_amount_currency = line.amount_currency < 0 and -1 or 1
            line_difference = 0
            if line.credit != 0:
                line_difference = sign_amount_currency * line.amount_currency * exchange_rate_end_period - line.credit
            elif line.debit != 0:
                line_difference = sign_amount_currency * line.amount_currency * exchange_rate_end_period - line.debit
            
            sign = line_difference < 0 and -1 or 1
            if line_difference == 0:
                continue
            elif line.credit == 0 and exchange_rate_end_period > line.amount_exchange_rate or line.debit == 0 and exchange_rate_end_period < line.amount_exchange_rate:
                credit = 0.00
                debit = sign * line_difference
            else:
                credit = sign * line_difference
                debit = 0.00
            
            move_line = {
                         'name': line.name or '',
                         'ref': line.ref or '',
                         'debit': debit,
                         'credit': credit,
                         'account_id':line.account_id.id,
                         'move_id': move_created_id,
                         'period_id': line.period_id.id,
                         'journal_id': line.journal_id.id,
                         'partner_id': line.partner_id.id,
                         'currency_id': line.account_id.currency_id.id,
                         'amount_currency': 0.00,
                         'state': 'valid',
                         'company_id': line.company_id.id,
                         }
            line_created_id = move_line_obj.create(cr, uid, move_line)
            move_line_obj.write(cr, uid, [line.id], {'adjustment' : line_created_id})
    
        amount = self.get_balance_amount(cr, uid, move_created_id, context=context)
        if amount > 0:
            account_id = res_user.company_id.expense_currency_exchange_account_id.id
            credit = amount
            debit = 0.00
        else:
            account_id = res_user.company_id.income_currency_exchange_account_id.id
            credit = 0.00
            debit = amount * -1
        move_line = {
                             'name': name,
                             'ref': name,
                             'debit': debit,
                             'credit': credit,
                             'account_id': account_id,
                             'move_id': move_created_id,
                             'period_id': period.id,
                             'journal_id': journal.id,
                             'currency_id': False,
                             'amount_currency': 0.00,
                             'state': 'valid',
                             'company_id': res_user.company_id.id,
                             }
        line_created_id = move_line_obj.create(cr, uid, move_line)
        return move_created_id
    
