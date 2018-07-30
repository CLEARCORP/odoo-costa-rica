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
    'name': 'Promerica Bank Statement Importer',
    'version' : '1.0',
    'author' : 'CLEARCORP S.A.',
    'complexity': 'normal',
    'description': '''
Promerica Bank Statement Importer
=================================
Parser for Promerica's Bank Statements for the use with account_banking_ccorp module. 

Main Features
-------------
* Parse xlsx format bank statements.
* Serve bank statements to account_banking_ccorp module.
''',
    'category': 'Accounting & Finance',
    'sequence': 3,
    'website' : 'http://clearcorp.co.cr',
    'images' : [],
    'depends' : [
                 'account_banking_ccorp',
                ],
    'data' : [],
    'init_xml' : [],
    'demo_xml' : [],
    'update_xml' : [],
    'test' : [],
    'external_dependencies': {
        'python': ['openpyxl'],
    },
    'auto_install': False,
    'application': False,
    'installable': False,
    'license': 'AGPL-3',
}
