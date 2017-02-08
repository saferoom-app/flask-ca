# Key usages
key_usage = {"digsign":"digitalSignature","nonrep":"nonRepudiation","keysign":"keyCertSign",\
"crlsign":"cRLSign","keyenc":"keyEncipherment","keyag":"keyAgreement","enconly":"encipherOnly","deconly":"decipherOnly"}

# Extended Key Usages
ext_key_usage = {"sa":"serverAuth","ca":"clientAuth","code":"codeSigning","email":"emailProtection","time":"timeStamping"}

# HTTP codes
http_created = 201
http_ok = 200
http_forbidden = 403
http_badrequest = 400
http_notfound = 404
http_notauthorized = 401
http_internal_error = 500