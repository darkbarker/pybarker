ALPHABET_BITCOIN = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
ALPHABET_RIPPLE = 'rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz'
_BASE_COUNT = 58


def base58encode(num, alphabet=ALPHABET_BITCOIN):
    """ Returns integer from a base58-encoded string """
    encoded = ''

    if (num < 0):
        raise TypeError('negative')

    while (num >= _BASE_COUNT):
        num, mod = divmod(num, _BASE_COUNT)
        encoded = alphabet[mod] + encoded

    encoded = alphabet[num] + encoded

    return encoded


def base58decode(s, alphabet=ALPHABET_BITCOIN):
    """ Decodes the base58-encoded string into an integer """
    decoded = 0
    for char in s:
        decoded = decoded * _BASE_COUNT + alphabet.index(char)
    return decoded
