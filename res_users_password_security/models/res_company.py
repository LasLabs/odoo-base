# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: James Foster <jfoster@laslabs.com>
#    Copyright: 2016-TODAY LasLabs, Inc [https://laslabs.com]
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

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    password_expiration = fields.Integer(
        'Days', default=60, help='How many days until passwords expire'
    )
    password_length = fields.Integer(
        'Characters', default=12, help='Minimum number of characters'
    )
    password_lower = fields.Boolean(
        'Lowercase', default=True, help='Require lowercase letters'
    )
    password_upper = fields.Boolean(
        'Uppercase', default=True, help='Require uppercase letters'
    )
    password_numeric = fields.Boolean(
        'Numeric', default=True, help='Require numeric digits'
    )
    password_special = fields.Boolean(
        'Special', default=True, help='Require special characters'
    )
