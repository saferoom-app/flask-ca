# Import section
from core.cliparser import init_parser
import requests,json,os,ConfigParser,datetime
from core.functions import print_message,get_key_usage,template_from_file
from core.texttable import Texttable
from classes.CertificateTemplate import CertificateTemplate
import config.caconfig as config

# Initializing the parser
new_parser = init_parser()
option = new_parser.parse_args()

def send_request(method,url,params=[],headers=[]):
    try:
        
    	# Sending request
        if method == "GET":
    	    r = requests.get("%s/%s" % (config.server_url,url))
        elif method == "POST":
    	    r = requests.post("%s/%s" % (config.server_url,url),data=params,headers=headers)
        elif method == "DELETE":
    	    r = requests.delete("%s/%s" % (config.server_url,url),json=params,headers=headers)
        
        # Processing response
        data = json.loads(r.text)
    	if not data:
    		print_message("Error processing the JSON response from server: %s" % r.text)
    		exit()
    	
    	if r.status_code != config.http_ok and r.status_code != config.http_created:
    		print_message(data['message'])
    		exit()

    	return data

    except requests.exceptions.ConnectionError as e:
    	print_message(str(e))

def send_file_request(method,url,params=[],headers=[]):
    try:
        # Sending request
        if method == "GET":
            r = requests.get("%s/%s" % (config.server_url,url))
        elif method == "POST":
            r = requests.post("%s/%s" % (config.server_url,url),data=params,headers=headers)
        return r.text
    except requests.exceptions.ConnectionError as e:
        print_message(str(e))

def send_json_request(method,url,params=[]):
    headers = {'Content-Type': 'application/json'}
    data = send_request(method,url,params=params,headers=headers)
    print_message(data['message'],level="INFO")
    exit()

def print_table(items):   


    table = Texttable()
    table.set_cols_align(["c"]*len(items[0].keys()))
    table.set_cols_align(["m"]*len(items[0].keys()))
    table.add_row([key.upper() for key in items[0].keys()])    
    for item in items:
        row = []
        for key in item.keys():
            row.append(item[key])
        table.add_row(row)
    print table.draw()


#########################################################
#	              Template operations                   #
#########################################################

if option.which == "template":

    # Listing the template
    if option.operation == "list":
        data = send_request("GET","tpls/list")
        # Preparing the table
        table = Texttable()
        table.set_cols_align(["c", "c","c"])
        table.set_cols_valign(["m", "m","m"])
        table.add_row(["Id", "Name","Description"])
        for tpl in data['templates']:
            table.add_row([tpl['id'], tpl['name'],tpl['dscr']])
        print table.draw()

    # Displaying the specific template
    elif option.operation == "show":
    	if not option.id:
    		print_error(config.error_template_id)        
        data = send_request("GET","tpls/get/%s" % option.id)
        table = Texttable()
        table.set_cols_align(["c", "c"])
        table.set_cols_valign(["m", "m"])
        table.add_row(["Field", "Value"])
        table.add_row(["Name", data['template']['name']])
        table.add_row(["Description", data['template']['dscr']])
        table.add_row(["Key Usage", ", ".join([get_key_usage(key,config.key_usages) for key in data['template']['extensions']['ku']])])
        table.add_row(["Extended Key Usage", ", ".join([get_key_usage(key,config.ext_key_usages) for key in data['template']['extensions']['sku']])])
        table.add_row(["CRL Distribution Point",data['template']['extensions']['crl']['full']])
        table.add_row(["Freshest CRL (Delta) Distribution Point",data['template']['extensions']['crl']['freshest']])
        table.add_row(["Certificate policies",", ".join(data['template']['extensions']['policies'])])
        table.add_row(["OCSP URL",data['template']['extensions']['aia']['ocsp']])
        table.add_row(["CA Issuers URL",data['template']['extensions']['aia']['issuers']])
        table.add_row(["Subject Alternative name",data['template']['extensions']['altname']])
        table.add_row(["Key Length",data['template']['keylen']])
        print table.draw()

    # Deleting templates
    elif option.operation == "delete":
    	if not option.id:
    		print_error(config.error_template_id)
        proceed = raw_input("Do you really want to delete specified template(s)? [y/n]: ")
    	if proceed.lower() == "y":
            # Sending request to create template
            send_json_request("DELETE","tpls/delete",params=json.dumps(([] if option.id == "" else option.id.split(","))))            

    # Creating templates
    elif option.operation == "create":

        # Checking if name is specified
        template = {}

        # Checking if file is specified
        if option.file:
            if os.path.exists(option.file) == False:
                print_message(config.error_file_notfound % option.file)
                exit()

            template = CertificateTemplate.from_file(option.file)
            if not template:
                exit()
        else:
            if not option.name:
                print_message(config.error_name_mandatory)
                exit()

            # Getting the template data from CLI params
            template = CertificateTemplate.from_option(option)
            if not template:
                exit()

        # Sending request to create template
        send_json_request("POST","tpls/create",params=template.to_json())        

                     
#########################################################
#	              User operations                       #
#########################################################	

elif option.which == "user":

    # Listing users
    if option.operation == "list":
        data = send_request("POST","users/list")
        table = Texttable()
        table.set_cols_align(["c", "c","c","c"])
        table.set_cols_valign(["m", "m","m","m"])
        table.add_row(["Id", "Name","Email","Subject"])
        for user in data['users']:
            table.add_row([user['id'], user['name'],user['email'],user['subject']])
        print table.draw()

    # Creating
    elif option.operation == "create":
        
        # Checking input data
        if not option.name:
            print_message(config.error_name_mandatory)
            exit()

        # Generating Subject DN
        subject = []
        if option.name:
            subject.append("CN=%s" % option.name)
        if option.email:
            subject.append("E=%s" % option.email)
        if option.country:
            subject.append("C=%s" % option.country)
        if option.org:
            subject.append("O=%s" % option.org)
        if option.dep:
            subject.append("OU=%s" % option.dep)
        if option.state:
            subject.append("ST=%s" % option.state)
        if option.city:
            subject.append("L=%s" % option.city)

        # Preparing data for the JSON request
        user = {"name":option.name,"email":option.email,"subject":",".join(subject)}
        
        # Sending request to user
        send_json_request("POST","users/create",params=json.dumps(user))
        

    # Deleting users
    elif option.operation == "delete":
        if not option.user_id:
            print_error(config.error_template_id)
            exit()
        proceed = raw_input("Do you really want to delete specified user(s)? [y/n]: ")
        if proceed.lower() == "y":
            
            # Sending request to create template
            send_json_request("DELETE","users/delete",params=json.dumps(([] if option.user_id == "" else option.user_id.split(","))))
            

#########################################################
#                 CA operations                         #
#########################################################   

elif option.which == "ca":

    # Listing CAs
    if option.operation == "list":
        headers = {'Content-Type': 'application/json'}
        data = send_request("POST","ca/list",params=json.dumps({"search":""}),headers=headers)
        table = Texttable()
        table.set_cols_align(["c", "c","c","c"])
        table.set_cols_valign(["m", "m","m","m"])
        table.add_row(["Id", "Name","Description","Root CA"])
        for ca in data['cas']:
            table.add_row([ca['id'], ca['name'],ca['dscr'],ca['root_ca']])
        print table.draw()

    # Creating CA
    elif option.operation == "create":
        
        # Checking the mandatory fields
        if not option.name:
            print_message(config.error_field_mandatory % "name")
            exit()
        if not option.password:
            print_message(config.error_field_mandatory % "password")
            exit()

        # Initializing the request object
        ca = {}
        ca['name'] = option.name
        ca['dscr'] = option.description
        ca['pass'] = option.password
        ca['keylen'] = option.keylen
        ca['hash'] = option.hashalg
        ca['subjectDN'] = {}
        ca['extensions'] = {}
        ca['extensions']['crl'] = ""
        ca['extensions']['ocsp'] = ""
        ca['extensions']['issuers'] = ""
        
        # Setting the Subject DN
        ca['subjectDN']['CN'] = option.name
        if option.email:
            ca['subjectDN']['E'] = option.email
        if option.country:
            ca['subjectDN']['C'] = option.country
        if option.org:
            ca['subjectDN']['O'] = option.org
        if option.dep:
            ca['subjectDN']['OU'] = option.dep
        if option.state:
            ca['subjectDN']['ST'] = option.state
        if option.city:
            ca['subjectDN']['L'] = option.city

        # Setting validity
        ca['valid'] = option.valid

        # Setting the Root CA
        ca['root_ca'] = {}
        ca['root_ca']['ca_id'] = option.root_ca
        ca['root_ca']['pass'] = option.root_password
        if option.root_ca > 0 and option.root_password == "":
            print_message(config.error_field_mandatory % "root_ca and root_password")
            exit()

        # Setting extensions
        if option.include_crl == True:
            ca['extensions']['crl'] = config.crl_url
        if option.include_ocsp == True:
            ca['extensions']['ocsp'] = config.ocsp_url
        if option.include_issuers == True:
            ca['extensions']['issuers'] = config.issuers_url

        # Sending request to create Certificate Authority
        send_json_request("POST","ca/create",params=json.dumps(ca))
        
    # Displaying information about CA
    elif option.operation == "show":
        
        # Checking if ID is specified
        if not option.id:
            print_message(config.error_field_mandatory % "id")

        # Getting CA information
        data = send_request("GET","ca/get/%s" % option.id)
        
        # Displaying the CA information
        table = Texttable()
        table.set_cols_align(["c", "c"])
        table.set_cols_valign(["m", "m"])
        table.add_row(["Field", "Value"])
        table.add_row(["ID", data['id']])
        table.add_row(["Name", data['name']])
        table.add_row(["Subject DN",data['subject_dn'] ])
        table.add_row(["Description", data['dscr']])
        table.add_row(["Expires", datetime.datetime.fromtimestamp(data['expires']).strftime('%Y-%m-%d %H:%M:%S')])
        table.add_row(["CRL Distribution Point", data['extensions']['crl'].replace("<ca_id>",str(data['id']))])
        table.add_row(["OCSP URL", data['extensions']['ocsp'].replace("<ca_id>",str(data['id']))])
        table.add_row(["Issuers URL", data['extensions']['issuers'].replace("<ca_id>",str(data['id']))])
        print table.draw()
    
    # Deleting CA
    elif option.operation == "delete":
        pass

    # Getting CRT certificate
    elif option.operation == "get-cert":
        if not option.id:
            print_message(config.error_field_mandatory % "id")
            exit()

        print send_file_request("GET","ca/%s/crt" % option.id)
        exit()

    # Getting Private key
    elif option.operation == "get-private":
        if not option.id:
            print_message(config.error_field_mandatory % "id")
            exit()

        print send_file_request("GET","ca/%s/pkey" % option.id)
        exit()

    # Generating new CRL
    elif option.operation == "generate-crl":
        # Checking if ID is specified
        if not option.id:
            print_message(config.error_field_mandatory % "id")
            exit()

        # Checking if ID is specified
        if not option.password:
            print_message(config.error_field_mandatory % "password")
            exit()

        # Sending request to generate CRL
        send_json_request("POST","ca/%s/crl/generate" % option.caid,params=json.dumps({"pass":option.password}))        

    # Listing the CRLs for specific CA
    elif option.operation == "list-crl":
        # Checking if ID is specified
        if not option.id:
            print_message(config.error_field_mandatory % "id")
            exit()

        # Sending request
        data = send_request("GET","ca/%s/crl/list" % option.id)
        table = Texttable()
        table.set_cols_align(["c", "c"])
        table.set_cols_valign(["m", "m"])
        table.add_row(["Id", "Created"])
        for crl in data['crls']:
            table.add_row([crl['id'], crl['created']])
        print table.draw()
        exit()

    # Downloading CRL
    elif option.operation == "get-crl":
        # Checking if ID is specified
        if not option.id:
            print_message(config.error_field_mandatory % "id")
            exit()

        # Getting the CRL
        print send_file_request("GET","ca/crl/get/%s" % option.id)

#########################################################
#                 Certificate operations                #
######################################################### 

elif option.which == "certificate":
    
    # Listing the certificates
    if option.operation == "list":
        
        # Getting certificates
        data = {"search":option.name,"status":option.status,"ca":option.caid,"page":option.page}
        headers = {'Content-Type': 'application/json'}
        response = send_request("POST","certificates/list",\
            params=json.dumps(data),\
            headers=headers)

        # Displaying certificates
        status = ""
        table = Texttable()
        table.set_cols_align(["c", "c","c","c","c"])
        table.set_cols_valign(["m", "m","m","m","m"])
        table.add_row(["Id", "Name","Serial","Status","Comment"])
        for cert in response['certificates']:
            if cert['status'] == config.STATUS_REVOKED:
                status = "Revoked"
            elif cert['status'] == config.STATUS_PAUSED:
                status = "Paused"
            elif cert['status'] == config.STATUS_EXPIRED:
                status = "Expired"
            else:
                status = "Active"
            table.add_row([cert['id'], cert['name'],cert['serial'],status,(cert['reason'] if cert['reason'] != "" else "n/a" )])
        print table.draw()        

    # Showing the certficate
    elif option.operation == "show":
        pass

    # Revoking the certificate
    elif option.operation == "revoke":
        
        # Certificate ID is mandatory
        if not option.certificate_id:
            print_message(config.error_field_mandatory % "certificate_id")
            exit()

        # Sending revocation request
        rev_request = {"certs":[option.certificate_id],"reason":option.reason_revoke,"comment":option.comment}
        send_json_request("POST","certificates/revoke",params=json.dumps(rev_request))
        

    # Restoring the certificate
    elif option.operation == "restore":
        
        # Certificate ID is mandatory
        if not option.certificate_id:
            print_message(config.error_field_mandatory % "certificate_id")
            exit()

        # Sending Restore request
        send_json_request("POST","certificates/restore",params=json.dumps({"id":option.certificate_id}))

    # Generating certificate
    elif option.operation == "generate":

        import uuid
        
        # Template ID is mandatory
        if not option.template_id:
            print_message(config.error_field_mandatory % "template_id")
            exit()

        # CA ID is mandatory
        if not option.caid:
            print_message(config.error_field_mandatory % "caid")
            exit()

        # User field is mandatory
        if not option.user_id:
            print_message(config.error_field_mandatory % "user_id")
            exit()

        # Creating the request object to send
        cert_request = {"sid":"","certificates":[]}
        cert_request['sid'] = str(uuid.uuid4())
        cert_request['pass'] = option.password
        cert_request['certificates'].append({"uid":option.user_id,"valid":option.valid,"tpl":option.template_id,"ca":option.caid,"pass":option.pfxpassword})        

        # Sending request to create Certificate Authority
        headers = {'Content-Type': 'application/json'}
        data = send_request("POST","certificates/generate",params=json.dumps(cert_request),headers=headers)
        print_message(data['message'],level="INFO")

    # Getting public key
    elif option.operation == "get-public":
        # Certificate ID is mandatory
        if not option.certificate_id:
            print_message(config.error_field_mandatory % "certificate_id")
            exit()

        # Sending file request
        print send_file_request("GET","certificates/download/public/%s" % option.certificate_id)

    # Getting public key
    elif option.operation == "get-pfx":
        # Certificate ID is mandatory
        if not option.certificate_id:
            print_message(config.error_field_mandatory % "certificate_id")
            exit()

        # Sending file request
        print send_file_request("GET","certificates/download/%s" % option.certificate_id)  

#########################################################
#                 Helper operations                     #
######################################################### 

elif option.which == "helper":

    # Getting a list of countries
    if option.operation == "list-countries":
        headers = {'Content-Type': 'application/json'}
        data = send_request("GET","static/countries.json",params=[],headers=headers)
        if option.name:
            countries = [{"code":country['code'],"name":country['name']} for country in data if option.name in country['name']]
        else:
            countries = data


        print_table(countries)

    # Listing the revocation reasons
    elif option.operation == "list-reasons":    
        

    # Listing the Key Usage values
    elif option.operation == "list-ku":
        table = Texttable()
        table.set_cols_align(["c", "c","c"])
        table.set_cols_valign(["m", "m","m"])
        table.add_row(["Value", "Name","Description"])
        for ku in config.key_usages:
            table.add_row([ku['value'],ku['name'],ku['dscr']])
        print table.draw()
        exit()

    # Listing the Extended Key Usage values
    elif option.operation == "list-sku":
        table = Texttable()
        table.set_cols_align(["c", "c"])
        table.set_cols_valign(["m", "m"])
        table.add_row(["Value", "Name"])
        for ku in config.ext_key_usages:
            table.add_row([ku['value'],ku['name']])
        print table.draw()
        exit()       