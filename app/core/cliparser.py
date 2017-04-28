# Import section
import argparse
import config.caconfig as config

# Function used to init the parser
def init_parser():
    new_parser = argparse.ArgumentParser(description="CLI Utility used to work with Flask Certificate Authority",formatter_class=argparse.RawTextHelpFormatter)
    subparsers = new_parser.add_subparsers(help='sub-command help')

	# Templates parser
    parser_tpls = subparsers.add_parser('template', help='Commands used to manage the Certificate templates',formatter_class=argparse.RawTextHelpFormatter)
    parser_tpls.add_argument("operation",nargs='?',help="The operation to perform on templates\nSupported operations are: list, create, delete, show\n\n > list = list all the templates\n Example: python cli.py template list\n\n > create = create a new Certificate template\n Example: python cli.py template create --name \"Client Authentication\" --keyusage digitalSignature,nonRepudiation --extkeyusage serverAuth\n\n > delete = delete specified template(s)\n Example: python cli.py template delete --id 5,6\n\n > show = display information about specific template\n Example: python cli.py template show --id 1", choices=["list","create","delete","show"])
    parser_tpls.add_argument("--id","--i",required=False,help="Template's ID. While deleting templates you can specify multiple IDs, separated by commas\n")
    parser_tpls.add_argument("--name","-n",required=False,help="Specify the template's name")
    parser_tpls.add_argument("--dscr","-d",required=False,help="Specify the template's description",default="")
    parser_tpls.add_argument("--file","-f",required=False,help="Template configuration file to use\nInstead of specifying all template's data manually, you can create the configuration template and use it as a reference\n\n")
    parser_tpls.add_argument("--keyusage","-ku",required=False,help="List of comma-separated Key Usage values to be included in the template. \n\nExample:\ncrlSign, digitalSignature\n\nSupported values are:\n%s" % (" \n".join([" > " + key['value'] for key in config.key_usages]))+"\n\n",default=[])

    parser_tpls.add_argument("--extkeyusage","-eku",required=False,help="List of comma-separated Extended Key Usage values to be included in the template. \n\nExample:\n crlSign, digitalSignature\n\nSupported values are: \n%s " % ("\n".join([" > " + key['value'] for key in config.ext_key_usages]))+"\n\n",default="")
    parser_tpls.add_argument("--fullcrl","-full",required=False,help="Specify the Distribution Point for Full CRL\nIf not specified, the CRL Distribution Point will be taken from issuing CA configuration\n\n",default="")
    parser_tpls.add_argument("--deltacrl","-delta",required=False,help="Specify the Distribution Point for Delta CRL (FreshestCRL)\nIf not specified, the Freshest CRL Distribution Point will be taken from issuing CA configuration\n\n",default="")
    parser_tpls.add_argument("--ocspurl","-ocsp",required=False,help="Specify the OCSP URL (AIA Extension)\nIf not specified, the AIA OCSP URL will be taken from issuing CA configuration\n\n",default="")
    parser_tpls.add_argument("--issuersurl","-issuers",required=False,help="Specify the Issuer URL (AIA Extension)\nIf not specified, the AIA Issuers URL will be taken from issuing CA configuration\n\n",default="")
    parser_tpls.add_argument("--altname","-alt",required=False,help="Specify the Subject Alternative name\n\n",default="")
    parser_tpls.add_argument("--policies","-pid",required=False,help="Comma-separated list of Certificate Policies that will be included in the certificate\nIf not specified, the list of Certificate Policies will be taken from issuing CA configuration\n\n",default="")
    parser_tpls.add_argument("--keylen","-k",required=False,help="Specify the key length",default=2048,type=int,choices=[512,1024,2048,4096,8192])
    parser_tpls.set_defaults(which='template')

    # Users parser
    parser_users = subparsers.add_parser('user', help='Commands used to manage the users',formatter_class=argparse.RawTextHelpFormatter)
    parser_users.add_argument("operation",nargs='?',help="The operation to perform on users. Supported operations are: list, create and delete\n\n > list = display a list of created users\n Example: python cli.py user list\n\n > create = create user\n Example: python cli.py create --name 'John Smith' --email 'john.smith@example.com' --country US --organization 'Sunshine Inc.'\n\n > delete = delete specified user(s)\nExample: python cli.py user delete --user_id 5",choices=["list","create","delete"])
    parser_users.add_argument("--name","-n",required=False,help="Specify the user's name\n\n")
    parser_users.add_argument("--email","-e",required=False,help="Specify the user's email\n\n")
    parser_users.add_argument("--country","-c",required=False,help="Specify the user's country (2-letter index)\nUse 'helper country-list' command to find the index\n\n")
    parser_users.add_argument("--org","-o",required=False,help="Specify the user's organization\n\n")
    parser_users.add_argument("--dep","-ou",required=False,help="Specify the user's department\n\n")
    parser_users.add_argument("--state","-st",required=False,help="Specify the user's state\n\n")
    parser_users.add_argument("--city","-l",required=False,help="Specify the user's city\n\n")
    parser_users.add_argument("--user_id","-uid",required=False,help="Specify the user's ID\n\n")
    parser_users.set_defaults(which='user')

    # CA parser
    parser_cas = subparsers.add_parser('ca', help='Commands used to manage Certificate Authorities',formatter_class=argparse.RawTextHelpFormatter)
    parser_cas.add_argument("operation",nargs='?',help="The operation to perform on Certificate Authority\nSupported operations are: list, create and delete, show, generate-crl, get-cert, list-crl, get-crl, get-private\n\n > list = display the list of created Certificate Authorities\n Example: python cli.py ca list\n\n > create = create new Certificate Authority\n Example: python cli.py ca create --name 'Root CA' --password testtest --hashalg sha1 --keylen 4096 --include-crl True\n\n > delete = delete specified Certificate Authority\n Example: python cli.py ca delete --id 1\n\n > show = display information about specific CA\n Example: python cli.py ca show --id 1\n\n > generate-crl = generate Full CRL for specific CA\n Example: python cli.py ca generate-crl --id 1\n\n > get-cert = display the CA certificate (public key)\n Example: python cli.py ca get-cert --id 1\n\n > get-crl = display specified CRL\n Example: python cli.py ca get-crl --id 1\n\n > get-private = display the CA private key\n Example: python cli.py ca get-private --id 1\n\n > list-crl = display the list of CRLs generated for specific CA\n Example: python cli.py ca list-crl --id 1",choices=["list","create","show","delete","generate-crl","get-cert","list-crl","get-crl","get-private"])
    parser_cas.add_argument("--id","-id",required=False,help="Certificate Authority or CRL ID\n\n")
    parser_cas.add_argument("--name","-n",required=False,help="Certificate Authority name\n\n")
    parser_cas.add_argument("--description","-dscr",required=False,help="Certificate Authority description\n\n",default="")
    parser_cas.add_argument("--password","-p",required=False,help="Password to encrypt/decrypt CA' private key\n\n")
    parser_cas.add_argument("--email","-e",required=False,help="Specify email for the Certificate Authority\n\n")
    parser_cas.add_argument("--country","-c",required=False,help="Specify the CA country (2-letter index)\nUse the command 'helper country-list' to find country index\n\n")
    parser_cas.add_argument("--org","-o",required=False,help="Specify CA's organization\n\n",default="")
    parser_cas.add_argument("--dep","-ou",required=False,help="Specify CA's department\n\n",default="")
    parser_cas.add_argument("--state","-st",required=False,help="Specify CA's state\n\n",default="")
    parser_cas.add_argument("--city","-l",required=False,help="Specify CA's city\n\n",default="")
    parser_cas.add_argument("--root_ca","-r",required=False,help="Root CA ID (if you're creating Intermediate CA)\n\n",type=int,default=-1)
    parser_cas.add_argument("--root_password","--rp",required=False,help="Root CA private key password (if you're creating Intermediate CA)\n\n",default="")
    parser_cas.add_argument("--valid","-v",required=False,help="Specify the number of months the CA will be valid. Default: 12 months (1 year)\n\n",default=12,type=int)
    parser_cas.add_argument("--keylen","-k",required=False,help="Specify the Key Length. Default: 2048 bits\n\n",default=2048,type=int,choices=[512,1024,2048,4096,8192])
    parser_cas.add_argument("--hashalg","-ha",required=False,help="Specify the Hash algorithm. Default: sha256\n\n",default="sha256",choices=["sha1","sha2","sha256"])
    parser_cas.add_argument("--include-crl","-crl",required=False,help="Specify whether to include the CDP and Freshest CRL information in CA certificate\n\n",type=bool,default=False,choices=[False,True])
    parser_cas.add_argument("--include-ocsp","-ocsp",required=False,help="Specify whether to include the OCSP AIA extension in CA certificate\n\n",type=bool,default=False, choices=[False,True])
    parser_cas.add_argument("--include-issuers","-issuers",required=False,help="Specify whether to include the OCSP Issuers extension in CA certificate\n\n",type=bool,default=False,choices=[False,True])
    parser_cas.set_defaults(which='ca')

    # Certificate parser
    parser_certs = subparsers.add_parser('certificate', help='Commands used to manage certificates',formatter_class=argparse.RawTextHelpFormatter)
    parser_certs.add_argument("operation",nargs='?',help="The operation to perform on certificates.\nSupported operations are: \n\n > list = Listing the generated certificates\n Example: python cli.py certificate list --name Authentication --status 1\n\n > generate = generate the certificates for specific user with the specified template\n Example: python cli.py certificate generate --template_id 1 --caid 1 --user_id 2 --password testtest\n\n > delete = delete specified certificates\n Example: python cli.py certificate delete -id 1\n\n > show = Display certificate information\n Example: python cli.py certificate show -id 1\n\n > revoke = revoke specified certificate with specific reason\n Example: python cli.py certificate revoke -id 1 --reason_revoke 1 --comment 'Test Reason'\n\n > restore = restore the certificate that was revoked with 'Certificate Hold' reason\n Example: python cli.py certificate restore -id 1\n\n > get-public = get certificate in Base64 (public key)\n Example: python cli.py certificate get-public -id 1\n\n > get-pfx = getting the PFX (PKCS#12) data (public key + private key, protected by password)\n Example: python cli.py certificate get-pfx -id 1",choices=["list","generate","show","delete","revoke","restore","get-public","get-pfx"])
    parser_certs.add_argument("--certificate_id","-id",required=False,help="Certificate's ID\n ",default="")
    parser_certs.add_argument("--name","-n",required=False,help="Specify the name of the certificate to be searched for.\nYou can specify the part of its name. For example 'John D'\n ",default="")
    parser_certs.add_argument("--status","-s",required=False,help="Specify the certificate statuses to filter the results. \nYou can specify several values separated by comma. You can use the following statuses: \nActive = 1\nRevoked = 2\nPaused = 3\nExpired = 4\n ",default=[])
    parser_certs.add_argument("--caid","-c",required=False,help="Specify the Certificate Authority ID to filter the list of certificates. \nYOu can specify several values separated by comma\n ",default=[])
    parser_certs.add_argument("--page","-pg",required=False,help="Specify the page to display the results. \nIf the total number of found certificates is above [ITEMS_PER_PAGE] value, then list is splitted into pages. \nITEMS_PER_PAGE is specified in the app configuration file: /config/caconfig.py\n ",default=1)
    parser_certs.add_argument("--template_id","-tplid",required=False,help="Specify the template ID to generate certificates\n ",default="")
    parser_certs.add_argument("--password","-p",required=False,help="Specify the password to decrypt issuing CA's private key\n ",default="")
    parser_certs.add_argument("--user_id","-uid",required=False,help="User's ID\n ",default="")
    parser_certs.add_argument("--pfxpassword","-pf",required=False,help="Password to protect PFX\n ",default="")
    parser_certs.add_argument("--valid","-v",required=False,help="Certificate validity in months. Default: 12 months\nIf this value is greater than issuing CA expiration date, then app will use the CA expiration date\n ",default=12)
    parser_certs.add_argument("--reason_revoke","-rr",required=False,help="Certificate's revocation reason. The following values are supported: \n0 = Unspecified\n1 = Key compromise\n2 = CA Compromise\n3 = Affiliation changed\n4 = Superseeded\n5 = Cessation of Operation\n6 = Certificate Hold\n\nDefault value: 0(Unspecified)\n ",default=0,choices=[0,1,2,3,4,5,6],type=int)
    parser_certs.add_argument("--comment","-cm",required=False,help="Comment to revoked certificate.\nHere you can specify some additional information about certificate revocation\n ",default="")
    parser_certs.set_defaults(which='certificate')

    # Helper parser
    parser_helper = subparsers.add_parser('helper', help='Helper commands used to get additional information, like Country Indexes, Revocation reasons and etc',formatter_class=argparse.RawTextHelpFormatter)
    parser_helper.add_argument("operation",nargs='?',help='Supported operations are the following:\n\n > list-countries = list all countries and their 2-letter indexes\n\n > list-reasons = list all revocation reasons with corresponding codes\n\n > list-ku = list all Key Usage extension values with explanation\n\n > list-sku = list all Extended Key Usage extensions values with explanation',choices=["list-countries","list-reasons","list-ku", "list-sku"])
    parser_helper.add_argument("--name","-n",required=False,help="Name or part of country's name to filter the list",default="")
    parser_helper.set_defaults(which='helper')

    return new_parser