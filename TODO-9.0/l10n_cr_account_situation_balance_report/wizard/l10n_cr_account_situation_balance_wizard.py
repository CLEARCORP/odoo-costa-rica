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

from openerp.osv import fields, osv

class situationBalancereportWizard(osv.osv_memory):
    
    _inherit = "account.report.wiz"
    _name = "situation.balance.report.wiz"
    _description = "Situation Balance Report Wizard"

    _columns = {
        'account_base_report':fields.many2one('account.financial.report', string="Account Base Report",domain=[('parent_id','=', False), ('account_type.code','=','SITBAL')]),
        'out_format': fields.selection([('pdf','PDF')], 'Print Format'),
    }

    _defaults = {
            'filter': 'filter_period',
            'out_format': 'pdf',
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        mimetype = self.pool.get('report.mimetypes')
        report_obj = self.pool.get('ir.actions.report.xml')
        report_name = 'l10n_cr_account_situation_balance_report.report_situation_balance'
        
        context = context or {}
        
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': data,
            'context':context
        }


situationBalancereportWizard()
