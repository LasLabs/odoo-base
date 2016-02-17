# -*- coding: utf-8 -*-
# © 2015-TODAY LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields
from openerp.tests.common import TransactionCase


class TestModel(models.Model):
    _name = 'test.model'
    enc_test = fields.EncryptedText()


class TestEncryptedText(TransactionCase):

    ORIG = 'TEST'

    def setUp(self):
        super(TestEncryptedText, self).setUp()
        self.fixture = {
            'enc_test': self.ORIG,
        }
        self.mdl = self.env['test.model']

    # def test_database_create_encrypt(self, ):
    #     """
    #     Verifies encryption method called on create
    #     """
    #     rec = self.mdl.create(self.fixture)
    #     actual = rec.enc_test

    def test_no_error_on_update_or_create(self, ):
        rec = self.mdl.create(self.fixture)
        rec.update({
            'enc_test': 'Derp'
        })

    def test_read_equals_orig(self, ):
        rec = self.mdl.create(self.fixture)
        self.assertEqual(self.ORIG, rec.enc_text)
