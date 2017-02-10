# Import section
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Table, Text
from database import Base
from sqlalchemy.orm import relationship
from OpenSSL import crypto, SSL
import hashlib,uuid,config,base64

# Models
class CertificateAuthority(Base):
    __tablename__ = "ca"
    id = Column(Integer,primary_key=True)
    root_ca = Column(Integer,default=0)
    name = Column(String(256),index=True)
    dscr = Column(String(256),index=True)
    subject_dn = Column(String(128),index=True)
    extensions = Column(Text,index=False)

    # Relationships
    keys = relationship('Key')
    certificates = relationship("Certificate")

    def __init__(self,name=None,subject_dn=""):
        self.name = name
        self.subject_dn = subject_dn

    def __repr__(self):
        return "<Certificate Authority: %r, Subject DN=%r" % (self.name,self.subject_dn)

    def set_root(self,ca_id):
        self.root_ca = ca_id

class Key(Base):
    __tablename__ = "ca_keys"
    # Columns
    id = Column(Integer,primary_key=True)
    ca = Column(Integer,ForeignKey('ca.id'))
    private = Column(Text)
    public = Column(Text)
    expires_in = Column(DateTime)

    # Fields
    pkey = None
    def __init__(self):
        pass
    def __repr__(self):
        return "Key, private=%r, public=%r" % (self.private,self.public)

    def generate_private_key(self,password,length):
        self.pKey = crypto.PKey()
        self.pKey.generate_key(crypto.TYPE_RSA, length)
        # Assigning private key
        self.private = crypto.dump_privatekey(crypto.FILETYPE_PEM,self.pKey,cipher="AES256",passphrase=str(password))

    def generate_public_key(self,subject,months,root_key=None,root_ca=None,extensions=[]):
        
        # Generating the serial number
        md5_hash = hashlib.md5()
        md5_hash.update(str(uuid.uuid4()))
        serial = int(md5_hash.hexdigest(), 24)        
        
        # Generating the certificate
        ca_cert = crypto.X509()
        ca_cert.get_subject().C = subject['C']
        ca_cert.get_subject().O = subject['O']
        ca_cert.get_subject().OU = subject['OU']
        ca_cert.get_subject().CN = subject['CN']
        ca_cert.set_version(2)
        ca_cert.set_serial_number(1000)
        ca_cert.gmtime_adj_notBefore(0)
        ca_cert.gmtime_adj_notAfter(months*12*24*60*60)
        ca_cert.set_pubkey(self.pKey)
        if root_ca is not None:
            ca_cert.set_issuer(root_ca.get_subject())
            ca_cert.add_extensions([crypto.X509Extension(config.extensions['bc'], True,"CA:TRUE"),\
                crypto.X509Extension(config.extensions['ku'], True,"keyCertSign, cRLSign"),crypto.X509Extension(config.extensions['ski'], False, "hash",subject=ca_cert),crypto.X509Extension(config.extensions['aki'], False,'keyid,issuer', issuer=root_ca)])
        else:
            ca_cert.set_issuer(ca_cert.get_subject())
            ca_cert.add_extensions([crypto.X509Extension(config.extensions['bc'], True,"CA:TRUE"),\
                crypto.X509Extension(config.extensions['ku'], True,"keyCertSign, cRLSign"),crypto.X509Extension(config.extensions['ski'], False, "hash",subject=ca_cert),crypto.X509Extension(config.extensions['aki'], False,'keyid,issuer', issuer=ca_cert)])
        
        # Adding additional extensions
        for extension in extensions:
            ca_cert.add_extensions([crypto.X509Extension(config.extensions[extension['name']],extension['crit'],str(extension['value']))])            
        if root_key is not None:
            ca_cert.sign(root_key, 'sha1')
        else:
            ca_cert.sign(self.pKey, 'sha1')
              

        # Setting the public key
        self.public = crypto.dump_certificate(crypto.FILETYPE_PEM,ca_cert)

class Certificate(Base):
    __tablename__ = "certificates"

    # Columns
    id = Column(Integer,primary_key=True)
    ca = Column(Integer,ForeignKey('ca.id'))                     # The certificate authority that issued this certificate
    serial = Column(String(64))                                  # Certificate serial number
    p12 = Column(Text)                                           # PFX data in Base
    status = Column(Integer,default=1)                           # Current status: 1 = Active, 2 = Revoked, 3 = Expired
    code_revoke = Column(Integer,default=-1)                     # Revocation code
    reason_revoke = Column(String(256),nullable=True,default="") # Revocation reason (if any)

    # Relationship
    authority = relationship('CertificateAuthority')

    # Initializing the certificate
    def __init__(self):
        pass

    def __repr__(self):
        return "<Certificate, serial=%r, status=%r, pfxdata=%r" % (self.serial,self.status,self.p12)

    # Generating new certificate from provided data
    @staticmethod
    def generate(ca_id,subject,months,password=None,extensions=[]):
        '''
            Function used to generate new certificate from provided data
            ca_id = Certificate Authority ID (to get the Issuer DN and private key to sign the certificate)
            dn_json = Subject DN in JSON format
            years = number of months after which the certificate will expire
            password = password used to protect PFX file. BY default, the password used to encrypt CA private key will be used
        '''
        
        # Getting the Certificate Authority
        key = Key.query.get(ca_id)
        if not key:
            return None

        # Checking password (temp)
        if password is None:
            password = "testtest"
        
        # Getting public and private key
        private_key = crypto.load_privatekey(crypto.FILETYPE_PEM,key.private,passphrase="testtest")
        public_key = crypto.load_certificate(crypto.FILETYPE_PEM,key.public)

        # Generating new Private Key for certificate
        pKey = crypto.PKey()
        pKey.generate_key(crypto.TYPE_RSA, 2048)

        # Generating the serial number
        md5_hash = hashlib.md5()
        md5_hash.update(str(uuid.uuid4()))
        serial = int(md5_hash.hexdigest()[:-16], 16)

        cert = crypto.X509()
        if "C" in subject:
            cert.get_subject().C = subject['C']
        if "OU" in subject:
            cert.get_subject().OU = subject['OU']
        if "O" in subject:
            cert.get_subject().O = subject['O']
        if "L" in subject:
            cert.get_subject().L = subject['L']
        if "ST" in subject:
            cert.get_subject().ST = subject['ST']
        if "E" in subject:
            cert.get_subject().emailAddress = subject['C']
        if "CN" in subject:
            cert.get_subject().CN = subject['CN']

        cert.set_version(2)
        cert.set_serial_number(serial)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(months*30*24*60*60)
        cert.set_issuer(public_key.get_subject())
        cert.set_pubkey(pKey)
        for extension in extensions:
            cert.add_extensions([crypto.X509Extension(config.extensions[extension['name']],extension['crit'],str(extension['value']))])
        cert.sign(private_key, 'sha256')

        # Dumping into a file
        with open("test.crt","w") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM,cert))

        # Generating PFX
        pfx = crypto.PKCS12Type()
        pfx.set_privatekey(pKey)
        pfx.set_certificate(cert)
        pfxdata = pfx.export(password)

        # Creating new Certificate object
        certificate = Certificate()
        certificate.serial = hex(serial)[2:]
        certificate.p12 = base64.b64encode(pfxdata)
        certificate.status = 1

        return certificate

class Template(Base):
    __tablename__ = "templates"

    # Columns
    id = Column(Integer,primary_key=True)
    name = Column(String(128),index=True)
    dscr = Column(String(256),index=True)
    extensions = Column(Text)

    def __init__(self,name,dscr):
        self.name = name
        self.dscr = dscr

    def __repr__(self):
        return "<Template, name=%r, dscr=%r, extensions=%r" % (self.name,self.dscr,self.extensions)