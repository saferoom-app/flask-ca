# Extensions
extensions = {"bc": "basicConstraints",\
              "ku":"keyUsage",\
              "eku":"extendedKeyUsage",\
              "ski":"subjectKeyIdentifier",\
              "aki":"authorityKeyIdentifier",\
              "salt":"subjectAltName",\
              "ialt":"issuserAltName",\
              "aia":"authorityInfoAccess",\
              "crl":"crlDistributionPoints",\
              "cp":"certificatePolicies",\
              "pc":"policyConstraints"}

# Key usages
key_usages = [{"name":"Digital Signature","key":"digsign","value":"digitalSignature","dscr":"Use when the public key is used with a digital signature mechanism to support security services other than non-repudiation, certificate signing, or CRL signing. A digital signature is often used for entity authentication and data origin authentication with integrity"},\
              {"name":"Non-Repudiation","key":"nonrep","value":"nonRepudiation","dscr":"Use when the public key is used to verify digital signatures used to provide a non-repudiation service. Non-repudiation protects against the signing entity falsely denying some action (excluding certificate or CRL signing)"},\
              {"name":"Certificate signing","key":"keysign","value":"keyCertSign","dscr":"Use when the subject public key is used to verify a signature on certificates. This extension can be used only in CA certificates"},\
              {"name":"CRL Signing","key":"crlsign","value":"cRLSign","dscr":"Use when the subject public key is to verify a signature on revocation information, such as a CRL"},\
              {"name":"Key Encipherment","key":"keyenc","value":"keyEncipherment","dscr":"Use when a certificate will be used with a protocol that encrypts keys. An example is S/MIME enveloping, where a fast (symmetric) key is encrypted with the public key from the certificate. SSL protocol also performs key encipherment"},\
              {"name":"Key Agreement","key":"keyag","value":"keyAgreement","dscr":"Use when the sender and receiver of the public key need to derive the key without using encryption. This key can then can be used to encrypt messages between the sender and receiver. Key agreement is typically used with Diffie-Hellman ciphers"},\
              {"name":"Encipher Only","key":"enconly","value":"encipherOnly","dscr":"Use only when key agreement is also enabled. This enables the public key to be used only for enciphering data while performing key agreement"},\
              {"name":"Decipher only","key":"deconly","value":"decipherOnly","dscr":"Use only when key agreement is also enabled. This enables the public key to be used only for deciphering data while performing key agreement"},\
              {"name":"Data encipherment","key":"dataEnc","value":"dataEncipherment","dscr":"Use when the public key is used for encrypting user data, other than cryptographic keys"}]

# Extended Key Usages
ext_key_usages = [{"name":"Server Authentication","key":"sa","value":"serverAuth","dscr":""},\
              {"name":"Client Authentication","key":"ca","value":"clientAuth","dscr":""},\
              {"name":"Code Signing","key":"code","value":"codeSigning","dscr":""},\
              {"name":"Email Protection","key":"email","value":"emailProtection","dscr":""},\
              {"name":"Timestamping","key":"time","value":"timeStamping","dscr":""}]

# Certificate statuses
STATUS_ACTIVE = 1
STATUS_REVOKED = 2
STATUS_PAUSED = 3
STATUS_EXPIRED = 4

statuses = [{"name":"Active","value":STATUS_ACTIVE},{"name":"Revoked","value":STATUS_REVOKED},
           {"name":"Paused","value":STATUS_PAUSED},{"name":"Expired","value":STATUS_EXPIRED}]

# Revocation reasons
reasons = {"-1":"","0":"Unspecified","1":"Key Compromise","2":"CA Compromise","3":"Affiliation Changed","4":"Superseeded","5":"Cessation of Operation","6":"Certificate Hold"}
 
# HTTP codes
http_created = 201
http_ok = 200
http_forbidden = 403
http_badrequest = 400
http_notfound = 404
http_notauthorized = 401
http_internal_error = 500
http_notimplemented = 501

# Server error messages
error_bad_request = "Bad request: Error while processing JSON data within request"
error_template_id = "Specify the template's ID"
error_template_notfound = "Specified template not found"
error_name_mandatory = "Name is mandatory"
error_field_mandatory = "Field is mandatory: [ %s ]"
error_file_notfound = "File [%s] not found"
error_pass_incorrect = "Error decrypting Root CA private key: password incorrect"
error_ca_notfound = "Specified Certificate Authority not found"
error_pkey_notfound = "Private key not found"
error_pkey_password = "Incorrect Private key password"
error_template_notfound = "Certificate template not found"
error_user_notfound = "User not found"
error_user_id = "Specify user's ID"
error_multiple_requests = "Multiple sub-requests not supported"
error_cert_notfound = "Certificate not found"
error_cert_status = "Certificate is not in [Paused] status"
error_nocerts_revoked = "There are not revoked certificates for this CA. CRL won't be generated"
error_rootca_notfound = "Root CA [ID=%s] not found"
error_crl_notfound = "CRL not found"
error_db_init = "Error while initializing the database: %s. Click on button below to continue"


# Server info messages
msg_tpl_created = "Template has been successfully created"
msg_tpls_deleted = "Selected templates have been successfully deleted"
msg_tpl_updated = "Template has been successfully updated"
msg_ca_created = "Certificate Authority has been successfully created"
msg_ca_deleted = "Certificate Authority has been successfully deleted"
msg_certificates_generated = "Certificates have been successfully generated"
msg_certs_revoked = "Certificates have been successfully revoked"
msg_cert_restored = "Certificate has been successfully restored"
msg_user_created = "User has been successfully created"
msg_user_updated = "User has been successfully updated"
msg_users_deleted = "Selected users have been successfully deleted"
msg_crl_generated = "CRL has been successfully generated"
msg_crl_deleted = "CRL has been successfully deleted"
msg_db_init = "Database has been successfully initialized. Click on button below to continue"


# Status messages
status_generate_cert = "Generating certificate for %s"

# URLs
server_url = "http://www.saferoomapp.com:5000"
crl_url = server_url + "/ca/<ca_id>/crl/full"
ocsp_url = server_url + "/ca/<ca_id>/ocsp"
issuers_url = server_url + "/ca/<ca_id>/aia"

# Paths
path_status = "app/static/tmp/%s.status"
path_keys = "app/static/tmp/%s"

# CRL global configuration
CRL_VALID_DAYS = 365 # 1 year

# System configuration
ITEMS_PER_PAGE = 30 # Items per page to be displayed

# MIME types
MIME_PEM = "application/x-pem-file"
MIME_PFX = "application/x-pkcs12"
MIME_CRL = "application/pkix-crl"
MIME_CACERT = "application/x-x509-ca-cert"

# Transfer Encoding types
ENCODING_CHUNKED = "chunked"