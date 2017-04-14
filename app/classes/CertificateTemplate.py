# Import section
import os,ConfigParser,json

class CertificateTemplate():
    def __init__(self):
        self.extensions = {}
        self.extensions['crl'] = {}
        self.extensions['aia'] = {}		

    def __repr__(self):
    	return "<Template, name=%r, dscr=%r, extensions=%r>" % (self.name,self.dscr,json.dumps(self.extensions))

    @staticmethod
    def from_file(file):
        try:
            if os.path.exists(file) == False:
                return None

            # Initializing config
            config = ConfigParser.RawConfigParser()
            config.read(file)

            # Initializing template
            template = CertificateTemplate()
            # Getting name and description
            template.name = config.get("general","name")
            template.dscr = config.get("general","dscr")
            	        
	        # Getting extensions
            template.extensions['keylen'] = config.get("keylen","length")
            template.extensions['altname'] = config.get("general","alt")
            value = config.get("key_usages","key_usage")
            template.extensions['ku'] = ([] if value == "" else value.split(","))
            value = config.get("key_usages","ext_key_usage")
            template.extensions['sku'] = ([] if value == "" else value.split(","))
            value = config.get("policy","policies")
            template.extensions['policies'] = ([] if value == "" else value.split(","))
            template.extensions['altname'] = config.get("general","alt")
            template.extensions['crl']['inherit'] = config.get("crl","inherit")
            template.extensions['crl']['full'] = config.get("crl","full")
            template.extensions['crl']['freshest'] = config.get("crl","freshest")
            template.extensions['aia']['inherit'] = config.get("aia","inherit")
            template.extensions['aia']['ocsp'] = config.get("aia","ocsp")
            template.extensions['aia']['issuers'] = config.get("aia","issuers")
            return template
        except Exception as e:
            return None

    @staticmethod
    def from_option(option):
    	try:
            template = CertificateTemplate()
            template.name = option.name
            template.dscr = option.dscr
            template.extensions['keylen'] = option.keylen
            template.extensions['altname'] = option.altname
            template.extensions['ku'] = ([] if option.keyusage == "" else option.keyusage.split(","))
            template.extensions['sku'] = ([] if option.extkeyusage == "" else option.extkeyusage.split(","))
            template.extensions['crl']['full'] = option.fullcrl
            template.extensions['crl']['freshest'] = option.deltacrl
            if option.fullcrl != "" and option.deltacrl != "":
    		    template.extensions['crl']['inherit'] = 0
            else:
                template.extensions['crl']['inherit'] = 1
                template.extensions['aia']['ocsp'] = option.ocspurl
                template.extensions['aia']['issuers'] = option.issuersurl
                if option.ocspurl != "" and option.issuersurl != "":
                    template.extensions['aia']['inherit'] = 0
                else:
            	    template.extensions['aia']['inherit'] = 1
            	template.extensions['policies'] = ([] if option.policies == "" else option.policies.split(","))
            return template
    	except Exception as e:
    		return None

    def to_json(self):
    	return json.dumps(self.__dict__)
