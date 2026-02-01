import random
import secrets

class Cryptography:
    
    #DHE ====================================================================================================
    # RFC 3526 Group 14 (2048-bit MODP) source: https://www.ietf.org/rfc/rfc3526.txt
    DH_PRIME = int(
    "FFFFFFFF FFFFFFFF C90FDAA2 2168C234 C4C6628B 80DC1CD1"
    "29024E08 8A67CC74 020BBEA6 3B139B22 514A0879 8E3404DD"
    "EF9519B3 CD3A431B 302B0A6D F25F1437 4FE1356D 6D51C245"
    "E485B576 625E7EC6 F44C42E9 A637ED6B 0BFF5CB6 F406B7ED"
    "EE386BFB 5A899FA5 AE9F2411 7C4B1FE6 49286651 ECE45B3D"
    "C2007CB8 A163BF05 98DA4836 1C55D39A 69163FA8 FD24CF5F"
    "83655D23 DCA3AD96 1C62F356 208552BB 9ED52907 7096966D"
    "670C354E 4ABC9804 F1746C08 CA18217C 32905E46 2E36CE3B"
    "E39E772C 180E8603 9B2783A2 EC07A28F B5C55DF0 6F4C52C9"
    "DE2BCBF6 95581718 3995497C EA956AE5 15D22618 98FA0510"
    "15728E5A 8AACAA68 FFFFFFFF FFFFFFFF".replace(" ", ""),
    16)
    DH_GENERATOR = 2

    # I had to look this up. Both miller_rabin & mod_inverse are taken from www.geeksforgeeks.org
    @staticmethod
    def miller_rabin(n, rounds=40):
        if n < 2:
            return False
        if n == 2 or n == 3:
            return True
        if n % 2 == 0:
            return False
        
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2
        
        for _ in range(rounds):
            a = secrets.randbelow(n - 3) + 2
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True

    @staticmethod
    def mod_inverse(e, phi):
        def egcd(a, b):
            if a == 0:
                return b, 0, 1
            g, x, y = egcd(b % a, a)
            return g, y - (b // a) * x, x
        
        g, x, _ = egcd(e % phi, phi)
        if g != 1:
            raise ValueError("No modular inverse")
        return x % phi
    
    @staticmethod
    def generate_prime(bits):
        while True:
            n = secrets.randbits(bits) | (1 << (bits - 1)) | 1  # MSB and LSB set
            if Cryptography.miller_rabin(n):
                return n


    @staticmethod
    def generate_DHE_key(p):
        return secrets.randbelow(((p-1) //2 ) -3 ) + 2
    
    @staticmethod
    def compute_public_key(g, a, p):
        return pow(g, a, p) # g to the power a mod p
    
    @staticmethod
    def compute_shared_secret( x, a, p):
        return pow(x, a, p)
    
    @staticmethod
    def generate_rsa_keypair(bits=1024):
        p = Cryptography.generate_prime(bits // 2)
        q = Cryptography.generate_prime(bits // 2)
        n = p * q
        phi = (p - 1) * (q - 1)
        e = 65537
        d = Cryptography.mod_inverse(e, phi)
        return (n, e), (n, d)  # public, private