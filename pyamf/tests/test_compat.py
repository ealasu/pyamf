# -*- encoding: utf-8 -*-
#
# Copyright (c) 2007 The PyAMF Project. All rights reserved.
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
Flex/Flash compatibility tests.

@author: U{Nick Joyce<mailto:nick@boxdesign.co.uk>}

@since: 0.1.0
"""

import unittest

import pyamf
from pyamf import compat, util, amf3

class DataOutputTestCase(unittest.TestCase):
    def setUp(self):
        self.stream = util.BufferedByteStream()
        self.encoder = amf3.Encoder(self.stream)

    def test_create(self):
        x = compat.DataOutput(self.encoder)

        self.assertEquals(x.encoder, self.encoder)
        self.assertEquals(x.stream, self.stream)
        self.assertEquals(x.stream, self.encoder.stream)

    def test_boolean_true(self):
        self.encoder.writeBoolean(True)

        val = self.stream.getvalue()
        self.stream.truncate()

        self.assertEquals(self.stream.getvalue(), '')

        x = compat.DataOutput(self.encoder)
        x.writeBoolean(True)

        self.assertEquals(self.stream.getvalue(), val)

    def test_boolean_false(self):
        self.encoder.writeBoolean(False)

        val = self.stream.getvalue()
        self.stream.truncate()

        self.assertEquals(self.stream.getvalue(), '')

        x = compat.DataOutput(self.encoder)
        x.writeBoolean(False)

        self.assertEquals(self.stream.getvalue(), val)

    def test_byte(self):
        x = compat.DataOutput(self.encoder)

        for y in xrange(10):
            x.writeByte(y)

        self.assertEquals(self.stream.getvalue(),
            '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09')

    def test_double(self):
        x = compat.DataOutput(self.encoder)

        x.writeDouble(0.0)
        self.assertEquals(self.stream.getvalue(), '\x00' * 8)
        self.stream.truncate()

        x.writeDouble(1234.5678)
        self.assertEquals(self.stream.getvalue(), '@\x93JEm\\\xfa\xad')

    def test_float(self):
        x = compat.DataOutput(self.encoder)

        x.writeFloat(0.0)
        self.assertEquals(self.stream.getvalue(), '\x00' * 4)
        self.stream.truncate()

        x.writeFloat(1234.5678)
        self.assertEquals(self.stream.getvalue(), 'D\x9aR+')

    def test_int(self):
        x = compat.DataOutput(self.encoder)

        x.writeInt(0)
        self.assertEquals(self.stream.getvalue(), '\x00\x00\x00\x00')
        self.stream.truncate()

        x.writeInt(-12345)
        self.assertEquals(self.stream.getvalue(), '\xff\xff\xcf\xc7')
        self.stream.truncate()

        x.writeInt(98)
        self.assertEquals(self.stream.getvalue(), '\x00\x00\x00b')

    def test_multi_byte(self):
        # TODO nick: test multiple charsets
        x = compat.DataOutput(self.encoder)

        x.writeMultiByte('this is a test', 'utf-8')
        self.assertEquals(self.stream.getvalue(), u'this is a test')
        self.stream.truncate()

        x.writeMultiByte(u'ἔδωσαν', 'utf-8')
        self.assertEquals(self.stream.getvalue(), '\xe1\xbc\x94\xce\xb4\xcf'
            '\x89\xcf\x83\xce\xb1\xce\xbd')

    def test_object(self):
        x = compat.DataOutput(self.encoder)
        obj = {'foo': 'bar'}

        x.writeObject(obj)
        self.assertEquals(self.stream.getvalue(),
            '\t\x01\x07foo\x06\x07bar\x01')
        self.stream.truncate()

        # check references
        x.writeObject(obj)
        self.assertEquals(self.stream.getvalue(), '\t\x00')
        self.stream.truncate()

        # check force no references, should include class def ref and refs to
        # string
        x.writeObject(obj, False)
        self.assertEquals(self.stream.getvalue(), '\t\x01\x00\x06\x02\x01')

    def test_short(self):
        x = compat.DataOutput(self.encoder)

        x.writeShort(55)
        self.assertEquals(self.stream.getvalue(), '\x007')
        self.stream.truncate()

        x.writeShort(-55)
        self.assertEquals(self.stream.getvalue(), '\xff\xc9')

    def test_uint(self):
        x = compat.DataOutput(self.encoder)

        x.writeUnsignedInt(55)
        self.assertEquals(self.stream.getvalue(), '\x00\x00\x007')
        self.stream.truncate()

        self.assertRaises(ValueError, x.writeUnsignedInt, -55)

    def test_utf(self):
        x = compat.DataOutput(self.encoder)

        x.writeUTF(u'ἔδωσαν')

        self.assertEquals(self.stream.getvalue(), '\x00\r\xe1\xbc\x94\xce\xb4'
            '\xcf\x89\xcf\x83\xce\xb1\xce\xbd')

    def test_utf_bytes(self):
        x = compat.DataOutput(self.encoder)

        x.writeUTFBytes(u'ἔδωσαν')

        self.assertEquals(self.stream.getvalue(),
            '\xe1\xbc\x94\xce\xb4\xcf\x89\xcf\x83\xce\xb1\xce\xbd')


def suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(DataOutputTestCase))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')