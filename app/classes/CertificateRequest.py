# Import section
from app.core.models import Certificate
import time,datetime,hashlib,uuid,json,base64
from OpenSSL import crypto, SSL



class CertificateRequest():

    def __init__(self):
        self.name = ""
        self.template = None
        self.subject = {}
        self.valid = 0
        self.password = "" 
        self.extensions = []
        self.keylen = 0    

    def __repr__(self):
        return "Certificate Request, name=%r, subject=%r,valid=%r" % (self.name,self.subject,self.valid)

    def set_subject(self,subject_dn):
        ''' Function generates the dictionary from SubjectDN String '''
        array = subject_dn.split(",")
        for item in array:
            self.subject[item.split("=")[0].strip()] = item.split("=")[1]

    def set_valid(self,valid,expires_in):
        seconds = time.mktime(expires_in.timetuple())-time.mktime(datetime.datetime.now().timetuple())
        max_months = round(seconds/(60*60*24*30))
        if valid > max_months:
            self.valid = max_months
       	else:
       	    self.valid = valid
        
    def set_extensions(self,ca,template,extensions):

    	result = json.loads(template.extensions)
    	ca_extensions = json.loads(ca.extensions)
    	
    	# Key Usage extensions
    	if result['ku']:
    		self.extensions.append({"name":extensions['ku'],"crit":True,"value":str(",".join(result['ku']))})
        
        # Extended Key Usage extensions
    	if result['sku']:
    		self.extensions.append({"name":extensions['eku'],"crit":True,"value":str(",".join(result['sku']))})

    	# Policies
    	#if "policies" in result:
    	#	self.extensions.append({"name":config.extensions['cp'],"crit":False,"value":"Policy:%s" % str(",".join(result['policies']))})

    	# CRL Distribution Points
    	if result['crl']['inherit'] == 1:
            if ca_extensions['crl']:
                self.extensions.append({"name":extensions['crl'],"crit":True,"value":"URI:%s" % str(ca_extensions['crl'].replace("<ca_id>",str(ca.id)))})
    	else:
            if result['crl']['full']:
                self.extensions.append({"name":extensions['crl'],"crit":True,"value":"URI:%s" % str(result['crl']['full'])})

    	# CRL Distribution Points
    	if result['aia']['inherit'] == 1:
            if ca_extensions['ocsp']:
                self.extensions.append({"name":extensions['aia'],"crit":True,"value":"OCSP;URI:%s" % str(ca_extensions['ocsp'].replace("<ca_id>",str(ca.id)))})
            if ca_extensions['issuers']:
                self.extensions.append({"name":extensions['aia'],"crit":True,"value":"caIssuers;URI:%s" % str(ca_extensions['issuers'].replace("<ca_id>",str(ca.id)))})
    	else:
            if result['aia']['ocsp']:
                self.extensions.append({"name":extensions['aia'],"crit":False,"value":"OCSP;URI:%s" % str(result['aia']['ocsp'])})
            if result['aia']['issuers']:
                self.extensions.append({"name":extensions['aia'],"crit":False,"value":str("caIssuers;URI:%s" % result['aia']['issuers'])})

    	# Alternative name
    	if result['altname'] != "":
    		self.extensions.append({"name":extensions['salt'],"crit":False,"value":result['altname']})

        # Setting keylen
        self.keylen = int(result['keylen'])
    	
    def generate(self,root_private,root_public,password):
        ''' 
        	Function generates certificate from specified template 

        		> root_private = Issuing CA private Key
        		> root_public  = Issuing CA public key
        		> password: Password to protect PFX
        		> template: Certificate template
        '''

        # Generating new Private Key for certificate
        pKey = crypto.PKey()
        pKey.generate_key(crypto.TYPE_RSA, self.keylen)

	    # Generating the serial number
        md5_hash = hashlib.md5()
        md5_hash.update(str(uuid.uuid4()))
        serial = int(md5_hash.hexdigest()[:-16], 16)        

        cert = crypto.X509()
        if "C" in self.subject:
            cert.get_subject().C = self.subject['C']
        if "OU" in self.subject:
            cert.get_subject().OU = self.subject['OU']
        if "O" in self.subject:
            cert.get_subject().O = self.subject['O']
        if "L" in self.subject:
            cert.get_subject().L = self.subject['L']
        if "ST" in self.subject:
            cert.get_subject().ST = self.subject['ST']
        if "E" in self.subject:
            cert.get_subject().emailAddress = self.subject['E']
        if "CN" in self.subject:
            cert.get_subject().CN = self.subject['CN']
        
        # Setting certificate parameters
        cert.set_version(2)
        cert.set_serial_number(serial)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(int(self.valid)*30*24*60*60)
        cert.set_issuer(root_public.get_subject())
        cert.set_pubkey(pKey)

        # Adding extensions
        print self.extensions
        for extension in self.extensions:
            if extension['value']:
                cert.add_extensions([crypto.X509Extension(extension['name'],extension['crit'],extension['value'])])
        
        # Signing certificate
        cert.sign(root_private, 'sha256')

        # Generating PFX
        pfx = crypto.PKCS12Type()
        pfx.set_privatekey(pKey)
        pfx.set_certificate(cert)
        pfxdata = pfx.export(password)

        # Creating new Certificate object
        certificate = Certificate()
        certificate.serial = hex(serial)[2:]
        certificate.public = crypto.dump_certificate(crypto.FILETYPE_PEM,cert)
        certificate.p12 = base64.b64encode(pfxdata)
        certificate.status = 1

        return certificate      