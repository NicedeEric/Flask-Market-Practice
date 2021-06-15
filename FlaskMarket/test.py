from passlib.hash import sha256_crypt
passw = '123'
hash = sha256_crypt.hash(secret='123')
a = sha256_crypt.verify(passw, hash)
print(a)