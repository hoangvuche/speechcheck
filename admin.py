import hashlib


# This package generates activation key for users
seed = '{}{}'.format('WD-WXB1A88C1VLV', 'hoangvu.che@gmail.com')
result = hashlib.md5(seed.encode())
print(result.hexdigest().upper())
