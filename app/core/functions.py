# Import section
import os,ConfigParser,json


def force_bytes(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_bytes, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.
    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons.
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)
    if strings_only and is_protected_type(s):
        return s
    if isinstance(s, memoryview):
        return bytes(s)
    if not isinstance(s, str):
        try:
            return str(s).encode(encoding)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return b' '.join(force_bytes(arg, encoding, strings_only, errors)
                                 for arg in s)
            return str(s).encode(encoding, errors)
    else:
        return s.encode(encoding, errors)


# Function used to print title in the CLI mode
def print_title(title):
    print "\n=========================================================="
    print "         %s        " % title
    print "==========================================================\n"

def print_message(message,level="ERROR"):
    print "\n     [%s]: %s\n" % (level,message)

def get_key_usage(key,value_list=[]):
    for ku in value_list:
        if ku['value'] == key:
            return ku['name']
    return key

def template_from_file(file):
    
    try:
        template = {}
        template['extensions'] = {}
        template['extensions']['crl'] = {}
        template['extensions']['aia'] = {}
        # Initializing config
        config = ConfigParser.RawConfigParser()
        config.read(file)
        value = ""

        # Getting name and description
        template['name'] = config.get("general","name")
        template['dscr'] = config.get("general","dscr")
        
        # Getting extensions
        template['extensions']['altname'] = config.get("general","alt")
        value = config.get("key_usages","key_usage")
        template['extensions']['ku'] = ([] if value == "" else value.split(","))
        value = config.get("key_usages","ext_key_usage")
        template['extensions']['sku'] = ([] if value == "" else value.split(","))
        value = config.get("policy","policies")
        template['extensions']['policies'] = ([] if value == "" else value.split(","))
        template['extensions']['altname'] = config.get("general","alt")
        template['extensions']['crl']['inherit'] = config.get("crl","inherit")
        template['extensions']['crl']['full'] = config.get("crl","full")
        template['extensions']['crl']['freshest'] = config.get("crl","freshest")
        template['extensions']['aia']['inherit'] = config.get("aia","inherit")
        template['extensions']['aia']['ocsp'] = config.get("aia","ocsp")
        template['extensions']['aia']['issuers'] = config.get("aia","issuers")
        return template
        
    except Exception as e:
        print str(e)
        return None

def write_status(guid,status,path=""):

    ''' This function writes a status of the long-running operation into specified file '''
    with open(os.path.join(os.getcwd(),path) % guid,"w") as f:
        f.write(json.dumps(status))

def get_status(guid,path):
    ''' Function returns the current status of the operation '''
    status = {}
    try:
        with open(os.path.join(os.getcwd(),path) % guid,"r") as f:
            status = json.loads(f.read())
        return status
    except Exception as e:
        return {"value":-1,"status":""}

def remove_status(guid,path):
    try:
        os.remove(os.path.join(os.getcwd(),path) % guid)
    except Exception as e:
        pass