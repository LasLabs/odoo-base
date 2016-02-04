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

import operator

from openerp import http
from openerp.http import request
from openerp.addons.auth_signup.controllers.main import AuthSignupHome
from openerp.addons.web.controllers.main import ensure_db, Session
from openerp.tools.translate import _


class PasswordSecuritySession(Session):

    @http.route('/web/session/change_password', type='json', auth="user")
    def change_password(self, fields):
        new_password = operator.itemgetter('new_password')(
            dict(map(operator.itemgetter('name', 'value'), fields))
        )
        user = request.env.user
        user.check_password(new_password)
        return super(PasswordSecuritySession, self).change_password(fields)


class PasswordSecurityHome(AuthSignupHome):

    def do_signup(self, qcontext):
        password = qcontext.get('password')
        user_id = request.env['res.users'].browse(request.uid)
        user_id.check_password(password)
        return super(PasswordSecurityHome, self).do_signup(qcontext)

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        response = super(PasswordSecurityHome, self).web_login(*args, **kw)
        if not request.httprequest.method == 'POST':
            return response
        uid = request.session.authenticate(
            request.session.db,
            request.params['login'],
            request.params['password']
        )
        if not uid:
            return response
        users_obj = request.env['res.users'].sudo()
        user_id = users_obj.browse(request.uid)
        if not user_id._password_has_expired():
            return response
        user_id.action_expire_password()
        redirect = user_id.partner_id.signup_url
        return http.redirect_with_hash(redirect)

    @http.route(
        '/web/reset_password',
        type='http',
        auth='public',
        website=True
    )
    def web_auth_reset_password(self, *args, **kw):
        response = super(PasswordSecurityHome, self).web_auth_reset_password(
            *args,
            **kw
        )
        qcontext = response.qcontext
        if 'error' not in qcontext and qcontext.get('token'):
            qcontext['error'] = _("Your password has expired")
            return request.render('auth_signup.reset_password', qcontext)
        return response
