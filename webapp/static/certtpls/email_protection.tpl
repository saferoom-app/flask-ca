[general]
name = Email Protection
dscr = This is template used to generate Email Protection certificates
alt = 

[key_usages]
; List of comma-separated Key Usage and Extended Key Usage values. All values can be checked in "config.py" file
key_usage = digitalSignature,nonRepudiation,keyEncipherment,keyAgreement
ext_key_usage = emailProtection

[crl]
; inherit = 1: CRL parameters will be taken from issuing CA
; inherit = 0: CRL parameters will be taken from template
; <caid>: ID of issuing Certificate Authority
inherit = 0
full = http://127.0.0.1:5000/<caid>/crl/full
freshest = http://127.0.0.1:5000/<caid>/crl/delta

[aia]
; inherit = 1: AIA parameters will be taken from issuing CA
; inherit = 0: AIA parameters will be taken from template
; <caid>: ID of issuing Certificate Authority
inherit = 0
issuers = http://127.0.0.1:5000/<caid>/aia/issuers
ocsp = http://127.0.0.1:5000/<caid>/aia/ocsp

[policy]
; List of comma-separated Certificate policies
policies = 

[keylen]
length = 2048

