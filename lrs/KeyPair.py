from Crypto.Util import number

class KeyPair:
    def __init__(self, q, g):
        self.q = q
        self.g = g
        self.private_key, self.public_key = self.generate_key_pair()

    def generate_key_pair(self):
        private_key = number.getRandomRange(1, self.q - 1)
        public_key = pow(self.g, private_key, self.q)
        return private_key, public_key
