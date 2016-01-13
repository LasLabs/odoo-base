# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: James Foster <jfoster@laslabs.com>
#    Copyright: 2016 LasLabs, Inc [https://laslabs.com]
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

import re

from datetime import datetime
from openerp import api, fields, models, _
from openerp.addons.auth_signup.res_users import now
from openerp.exceptions import Warning as UserError


class ResUsers(models.Model):
    _inherit = 'res.users'
    password_write_date = fields.Date(
        'Latest password update', select=1, copy=False
    )

    @api.model
    def create(self, vals, ):
        vals['password_write_date'] = fields.Date.today()
        return super(ResUsers, self).create(vals)

    @api.one
    def write(self, vals, ):
        if vals.get('password'):
            self.check_password(vals['password'])
            vals['password_write_date'] = fields.Date.today()
        return super(ResUsers, self).write(vals)

    def password_match_message(self, ):
        company = self.company_id
        message = [
            'Password must be %d characters or more.' %
            company.password_length]
        message.append('Must contain the following:')
        if company.password_lower:
            message.append('Lowercase letter.')
        if company.password_upper:
            message.append('Uppercase letter.')
        if company.password_numeric:
            message.append('Numeric digit.')
        if company.password_special:
            message.append('Special character !@#$%^&*')
        return '\r'.join(message)

    def check_password(self, password, ):
        company = self.company_id
        if (company.password_length > len(password) or
                company.password_lower and not re.search('[a-z]', password) or
                company.password_upper and not re.search('[A-Z]', password) or
                company.password_numeric and not
                re.search('[0-9]', password) or
                company.password_special and not
                re.search('[!@#$%^&*]', password)):
            raise UserError(_(self.password_match_message()))
        return True

    def _password_has_expired(self, ):
        if self.password_write_date:
            password_write_date = datetime.strptime(
                self.password_write_date, '%Y-%m-%d')
            today = datetime.strptime(
                fields.Date.today(), '%Y-%m-%d')
            days = (today - password_write_date).days
            return (days > self.company_id.password_expiration)
        return True

    def expire_password(self, login):
        users = self.search([('login', '=', login)])
        if not users:
            users = self.search([('email', '=', login)])
        if len(users) != 1:
            raise Exception(_('Reset password: invalid username or email'))
        return users.action_expire_password()

    @api.multi
    def action_expire_password(self):
        expiration = now(days=+1)
        self.mapped('partner_id').signup_prepare(
            signup_type="reset", expiration=expiration)
