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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class resCompanyInherit(osv.Model):

    _inherit = 'res.company'

    _columns = {
        'first_limit': fields.float('First Limit', digits_compute=dp.get_precision('Payroll')),
        'second_limit':fields.float('Second Limit', digits_compute=dp.get_precision('Payroll')), 
        'amount_per_child': fields.float('Amount per Child', digits_compute=dp.get_precision('Payroll')),
        'amount_per_spouse': fields.float('Amount per spouse', digits_compute=dp.get_precision('Payroll')),
        
    }