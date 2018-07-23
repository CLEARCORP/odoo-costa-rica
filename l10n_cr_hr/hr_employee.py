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

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from openerp.tools.translate import _

class HREmployee(models.Model):
    _inherit = 'hr.employee'
    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        if default.get('identification_id'):
            default['identification_id'] = False
        return super(HREmployee, self).copy(default)

    _sql_constraints = [
        ('identification_unique',
        'UNIQUE(identification_id)',
        'The Nº Identification already exist for other employee')
                        ]

