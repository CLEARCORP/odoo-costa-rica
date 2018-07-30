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
{
    'name': 'Conciliation Bank Report',
    'version': '1.0',
    'author': 'CLEARCORP S.A.',
    'category': 'Finance',
    'description': """
Install the Conciliation Bank Report.
========================================
Configuration:
-----------------
        1. Configure type account that it will appear in wizard. This configuration is in Accounting -> Account -> Account Types and check
        "Include in conciliation bank report" option.
        
        2. With previous configuration, accounts that will appears in wizard to generate report will be parents of account that match with type selected in 
        previous configuration.
        
        3. With this configuration, Conciliation Bank Report has configuration for accounts that it will be necessary, that is reconciled and transit account.
    """,
    'website': "http://clearcorp.co.cr",
    'depends': ['account_report_lib',],
    'data': [
                   'security/ir.model.access.csv',
                   'wizard/l10n_cr_account_conciliation_bank_report_wizard.xml',
                   'report/report.xml',                                     
                   'l10n_cr_account_conciliation_bank_report.xml',
                   'report_menus.xml',
                   ],                
    'installable': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
