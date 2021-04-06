import unittest

from pybarker.utils.base58 import base58decode, base58encode, ALPHABET_BITCOIN, ALPHABET_RIPPLE


class Test(unittest.TestCase):

    def test_base58encode(self):
        self.assertEqual(base58encode(0x666, alphabet=ALPHABET_BITCOIN), 'VF')
        self.assertEqual(base58encode(0x1234567890987654321, alphabet=ALPHABET_BITCOIN), '4i32pzW53qfDr')

        self.assertEqual(base58encode(0, alphabet=ALPHABET_BITCOIN), '1')
        self.assertEqual(base58encode(1, alphabet=ALPHABET_BITCOIN), '2')
        self.assertEqual(base58encode(57, alphabet=ALPHABET_BITCOIN), 'z')
        self.assertEqual(base58encode(58, alphabet=ALPHABET_BITCOIN), '21')
        self.assertEqual(base58encode(59, alphabet=ALPHABET_BITCOIN), '22')
        self.assertEqual(base58encode(115, alphabet=ALPHABET_BITCOIN), '2z')
        self.assertEqual(base58encode(116, alphabet=ALPHABET_BITCOIN), '31')
        self.assertEqual(base58encode(117, alphabet=ALPHABET_BITCOIN), '32')

        self.assertEqual(base58encode(25420294593250030202636073700053352635053786165627414518, alphabet=ALPHABET_BITCOIN), '6UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM')
        self.assertEqual(base58encode(0x73696d706c792061206c6f6e6720737472696e67, alphabet=ALPHABET_BITCOIN), '2cFupjhnEsSn59qHXstmK2ffpLv2')

        with self.assertRaises(TypeError):
            base58encode(-1, alphabet=ALPHABET_BITCOIN)

    def test_base58decode(self):
        self.assertEqual(base58decode('VF', alphabet=ALPHABET_BITCOIN), 0x666)
        self.assertEqual(base58decode('4i32pzW53qfDr', alphabet=ALPHABET_BITCOIN), 0x1234567890987654321)

        self.assertEqual(base58decode('1', alphabet=ALPHABET_BITCOIN), 0)
        self.assertEqual(base58decode('2', alphabet=ALPHABET_BITCOIN), 1)
        self.assertEqual(base58decode('z', alphabet=ALPHABET_BITCOIN), 57)
        self.assertEqual(base58decode('21', alphabet=ALPHABET_BITCOIN), 58)
        self.assertEqual(base58decode('22', alphabet=ALPHABET_BITCOIN), 59)
        self.assertEqual(base58decode('2z', alphabet=ALPHABET_BITCOIN), 115)
        self.assertEqual(base58decode('31', alphabet=ALPHABET_BITCOIN), 116)
        self.assertEqual(base58decode('32', alphabet=ALPHABET_BITCOIN), 117)

        self.assertEqual(base58decode('6UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM', alphabet=ALPHABET_BITCOIN), 25420294593250030202636073700053352635053786165627414518)
        self.assertEqual(base58decode('2cFupjhnEsSn59qHXstmK2ffpLv2', alphabet=ALPHABET_BITCOIN), 0x73696d706c792061206c6f6e6720737472696e67)

        self.assertEqual(base58decode('base58', alphabet=ALPHABET_BITCOIN), 0x0548FE3143)


if __name__ == '__main__':
    unittest.main()
