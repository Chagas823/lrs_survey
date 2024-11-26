from Crypto.Hash import SHA256, MD5
from Crypto.Util import number
from .Signature import Signature
from .KeyPair import KeyPair
import time

class CryptographicSystem:
    def __init__(self, q, g):
        self.q = q
        self.g = g

    def hash_to_int(self, hash_obj):
        return int.from_bytes(hash_obj.digest(), byteorder='big') % self.q

    def calculate_h(self, L):
        hash_obj = SHA256.new()
        for key in L:
            hash_obj.update(number.long_to_bytes(key))
        return self.hash_to_int(hash_obj)

    def calculate_y0(self, h, private_key):
        return pow(h, private_key, self.q)

    def generate_signature(self, public_keys, message, private_key):
      
        r =  number.getRandomRange(1, self.q - 1)
        pi = 0
        h = self.calculate_h(public_keys)
        y0 = self.calculate_y0(h, private_key)
        s_values = [number.getRandomRange(1, self.q - 1) for _ in public_keys]
        c_values = [0] * len(public_keys)

        c_pi = self.calculate_c_pi(public_keys, y0, message, s_values, c_values, r)
        s_pi = (r - c_pi * private_key) % self.q
        s_values[pi] = s_pi
        c_values[pi] = c_pi

        return Signature(y0, s_values, c_values), r

    def calculate_c_pi(self, L, y0, message, s_values, c_values, r):
        hash_obj = MD5.new()
        hash_L = MD5.new()
        for pub_key in L:
            hash_L.update(number.long_to_bytes(pub_key))
        hash_obj.update(hash_L.digest())
        hash_obj.update(number.long_to_bytes(y0))
        hash_obj.update(message.encode('utf-8'))

        for i, (s, c) in enumerate(zip(s_values, c_values)):
            if i == 0:
                z_i = pow(self.g, r, self.q)
                z_i_prime = pow(self.calculate_h(L), r, self.q)
            else:
                z_i = (pow(self.g, s, self.q) * pow(L[i], c, self.q)) % self.q
                z_i_prime = (pow(self.g, s, self.q) * pow(y0, c, self.q)) % self.q
            hash_obj.update(number.long_to_bytes(z_i))
            hash_obj.update(number.long_to_bytes(z_i_prime))

        H = self.hash_to_int(hash_obj)
        c_sum = sum(c_values) % self.q
        c_pi = (H - c_sum) % self.q
        return c_pi

    def verify_signature(self, public_keys, message, signature, r):
        h = self.calculate_h(public_keys)
        y0 = signature.y0
        s_values = signature.s_values
        c_values = signature.c_values

        hash_obj = MD5.new()
        hash_L = MD5.new()
        for pub_key in public_keys:
            hash_L.update(number.long_to_bytes(pub_key))
        hash_obj.update(hash_L.digest())
        hash_obj.update(number.long_to_bytes(y0))
        hash_obj.update(message.encode('utf-8'))

        for i, (s, c) in enumerate(zip(s_values, c_values)):
            if i == 0:
                z_i = pow(self.g, r, self.q)
                z_i_prime = pow(h, r, self.q)
            else:
                z_i = (pow(self.g, s, self.q) * pow(public_keys[i], c, self.q)) % self.q
                z_i_prime = (pow(self.g, s, self.q) * pow(y0, c, self.q)) % self.q
            hash_obj.update(number.long_to_bytes(z_i))
            hash_obj.update(number.long_to_bytes(z_i_prime))

        H = self.hash_to_int(hash_obj)
        c_sum = sum(c_values) % self.q
        return c_sum == H

    def link(self, sig1, sig2):
        return sig1.y0 == sig2.y0
    

if __name__ == "__main__":
    q = 17125458317614137930196041979257577826408832324037508573393292981642667139747621778802438775238728592968344613589379932348475613503476932163166973813218698343816463289144185362912602522540494983090531497232965829536524507269848825658311420299335922295709743267508322525966773950394919257576842038771632742044142471053509850123605883815857162666917775193496157372656195558305727009891276006514000409365877218171388319923896309377791762590614311849642961380224851940460421710449368927252974870395873936387909672274883295377481008150475878590270591798350563488168080923804611822387520198054002990623911454389104774092183
    g = 8041367327046189302693984665026706374844608289874374425728797669509435881459140662650215832833471328470334064628508692231999401840332046192569287351991689963279656892562484773278584208040987631569628520464069532361274047374444344996651832979378318849943741662110395995778429270819222431610927356005913836932462099770076239554042855287138026806960470277326229482818003962004453764400995790974042663675692120758726145869061236443893509136147942414445551848162391468541444355707785697825741856849161233887307017428371823608125699892904960841221593344499088996021883972185241854777608212592397013510086894908468466292313

    
    crypto_sys = CryptographicSystem(q, g)

    inicio = time.time()
    key1 = KeyPair(q, g)
    key2 = KeyPair(q, g)
    fim = time.time()
    tempo_total = (fim - inicio) * 1000
    print(f"Tempo para gera o par de chaves: {tempo_total} ms")
    


    public_keys = [
        key1.public_key,
        key2.public_key
    ]
    for i in range(1, 5):
        key = KeyPair(q, g)
        public_keys.append(key.public_key)

    print("numero de chaves = ", len(public_keys))


    

    
    message1 = "mensagem teste"
    message2 = "mensagem teste 2"

    
    inicio = time.time()
    signature1 = crypto_sys.generate_signature(public_keys, message1, key1.private_key)
    fim = time.time()
    tempo_total = (fim - inicio) * 1000
    print(f"Tempo de execução assinatura: {tempo_total} ms")
    signature2 = crypto_sys.generate_signature(public_keys, message2, key2.private_key)

    

    # Exibir resultados
    #print(f"h: {crypto_sys.calculate_h(public_keys)}")
    #print(f"y0 1: {crypto_sys.calculate_y0(crypto_sys.calculate_h(public_keys), key1.private_key)}")
    #print(f"Signature 1: {signature1[0].get()}")
    inicio = time.time()
    print("Link entre signature1 e signature2:", crypto_sys.link(signature1[0], signature2[0]))
    fim = time.time()
    tempo_total = (fim - inicio) * 1000
    print(f"Tempo para verificar duas mensagens emitidas pelo mesmo autor: {tempo_total} ms")

    inicio = time.time()
    crypto_sys.verify_signature(public_keys, message1, signature1[0], signature1[1])
    fim = time.time()
    tempo_total = (fim - inicio) * 1000
    print(f"Tempo de execução verificação de assinatura: {tempo_total} ms")