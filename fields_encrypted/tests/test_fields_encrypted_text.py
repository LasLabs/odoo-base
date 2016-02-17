# -*- coding: utf-8 -*-
# © 2015-TODAY LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.addons.fields_encrypted import fields
import unittest
import mock


MODULE = 'openerp.addons.fields_encrypted.fields.EncryptedText'


class TestEncryptedText(unittest.TestCase):

    def setUp(self):
        super(TestEncryptedText, self).setUp()
        self.text_enc = 'BEmyFU369FL9raBaNFLZMk3aqxBObwLMHiiPnb5LyiQ='
        self.text = 'Text'

    def _new_field(self, ):
        return fields.EncryptedText()

    def test_decrypt(self, ):
        res = self._new_field()._decrypt(self.text_enc)
        self.assertEqual(
            self.text, res,
        )

    def test_encrypt(self, ):
        ''' Relies on decrypt, but still possible for only this fail '''
        res = self._new_field()._encrypt(self.text)
        # @TODO: Figure out how to better test this
        res = self._new_field()._decrypt(res)
        self.assertEqual(
            self.text, res
        )

    def test_convert_to_cache_calls_encrypt(self, ):
        with mock.patch('%s._encrypt' % MODULE) as mk:
            self._new_field().convert_to_cache(
                self.text, mock.MagicMock(),
            )
            mk.assert_called_once_with(
                self.text,
            )

    def test_convert_to_read_calls_decrypt(self, ):
        with mock.patch('%s._decrypt' % MODULE) as mk:
            self._new_field().convert_to_read(
                self.text, mock.MagicMock(),
            )
            mk.assert_called_once_with(
                self.text,
            )

    def test_convert_to_write_returns_value(self, ):
        res = self._new_field().convert_to_write(
            self.text, mock.MagicMock(),
        )
        self.assertEqual(
            self.text, res,
        )

    def test_convert_to_onchange_calls_decrypt(self, ):
        with mock.patch('%s._decrypt' % MODULE) as mk:
            self._new_field().convert_to_onchange(
                self.text,
            )
            mk.assert_called_once_with(
                self.text,
            )

    def test_convert_to_export_calls_decrypt(self, ):
        with mock.patch('%s._decrypt' % MODULE) as mk:
            env_mk = mock.MagicMock()
            env_mk.context.get.return_value = False
            self._new_field().convert_to_export(
                self.text, env_mk,
            )
            mk.assert_called_once_with(
                self.text,
            )

    def test_convert_to_export_raw_data(self, ):
        with mock.patch('%s._decrypt' % MODULE) as mk:
            env_mk = mock.MagicMock()
            env_mk.context.get.return_value = True
            res = self._new_field().convert_to_export(
                self.text, env_mk,
            )
            mk.assert_not_called()
            self.assertEqual(
                self.text, res,
            )
