# Import section
from OpenSSL import crypto, SSL
import hashlib,uuid,base64,json,ConfigParser,datetime
from flask_sqlalchemy import SQLAlchemy
from webapp.config import caconfig as config
db = SQLAlchemy()

# Define a base model for other database tables to inherit
class CertificateAuthority(db.Model):
    __tablename__ = "ca"
    id = db.Column(db.Integer,primary_key=True)
    root_ca = db.Column(db.Integer,default=0)
    name = db.Column(db.String(256),index=True)
    dscr = db.Column(db.String(256),index=True)
    subject_dn = db.Column(db.String(128),index=True)
    extensions = db.Column(db.Text,index=False)

    # Relationships
    keys = db.relationship('Key',cascade="all,delete")
    certificates = db.relationship("Certificate",cascade="all,delete")
    crls = db.relationship("CRL",cascade="all,delete")

    def __init__(self,name=None,subject_dn=""):
        self.name = name
        self.subject_dn = subject_dn

    def __repr__(self):
        return "<Certificate Authority: %r, Subject DN=%r" % (self.name,self.subject_dn)

    def set_root(self,ca_id):
        self.root_ca = ca_id

    def list_dict(self):
       ca =  {c.name: getattr(self, c.name) for c in self.__table__.columns}
       ca['extensions'] = json.loads(ca['extensions'])
       return ca

class Key(db.Model):
    __tablename__ = "ca_keys"
    # Columns
    id = db.Column(db.Integer,primary_key=True)
    ca = db.Column(db.Integer,db.ForeignKey('ca.id'))
    private = db.Column(db.Text)
    public = db.Column(db.Text)
    expires_in = db.Column(db.DateTime)

    # Fields
    pkey = None
    def __init__(self):
        pass
    def __repr__(self):
        return "Key, private=%r, public=%r" % (self.private,self.public)

    def generate_private_key(self,password,length):
        self.pKey = crypto.PKey()
        self.pKey.generate_key(crypto.TYPE_RSA, int(length))
        # Assigning private key
        self.private = crypto.dump_privatekey(crypto.FILETYPE_PEM,self.pKey,cipher="AES256",passphrase=str(password))

    def generate_public_key(self,json,root_key=None,root_ca=None,ca_id=None):

        # Generating the serial number
        md5_hash = hashlib.md5()
        md5_hash.update(str(uuid.uuid4()))
        serial = int(md5_hash.hexdigest(), 24)
        
              
        # Generating the certificate
        ca_cert = crypto.X509()
        if "C" in json['subjectDN']:
            ca_cert.get_subject().C = json['subjectDN']['C']
        if "O" in json['subjectDN']:
            ca_cert.get_subject().O = json['subjectDN']['O']
        if "OU" in json['subjectDN']:
            ca_cert.get_subject().OU = json['subjectDN']['OU']
        if "CN" in json['subjectDN']:
            ca_cert.get_subject().CN = json['subjectDN']['CN']
        ca_cert.set_version(2)
        ca_cert.set_serial_number(serial)
        ca_cert.gmtime_adj_notBefore(0)
        ca_cert.gmtime_adj_notAfter(int((self.expires_in - datetime.datetime.now()).total_seconds()))
        ca_cert.set_pubkey(self.pKey)
        if root_ca is not None:
            ca_cert.set_issuer(root_ca.get_subject())
            ca_cert.add_extensions([crypto.X509Extension(config.extensions['bc'], True,"CA:TRUE"),\
                crypto.X509Extension(config.extensions['ku'], True,"digitalSignature,keyCertSign, cRLSign"),crypto.X509Extension(config.extensions['ski'], False, "hash",subject=ca_cert),crypto.X509Extension(config.extensions['aki'], False,'keyid,issuer', issuer=root_ca)])
        else:
            ca_cert.set_issuer(ca_cert.get_subject())
            ca_cert.add_extensions([crypto.X509Extension(config.extensions['bc'], True,"CA:TRUE"),\
                crypto.X509Extension(config.extensions['ku'], True,"keyCertSign, cRLSign"),crypto.X509Extension(config.extensions['ski'], False, "hash",subject=ca_cert),crypto.X509Extension(config.extensions['aki'], False,'keyid,issuer', issuer=ca_cert)])
        
        # Adding additional extensions
        url = ""
        if json['extensions']['crl'] != "":
            url = "URI:%s" % (json['extensions']['crl'].replace("<ca_id>",str(ca_id)))
            ca_cert.add_extensions([crypto.X509Extension(config.extensions['crl'],True,str(url))])

        if json['extensions']['ocsp'] != "":
            url = "OCSP;URI:%s" % (json['extensions']['ocsp'].replace("<ca_id>",str(ca_id)))
            ca_cert.add_extensions([crypto.X509Extension(config.extensions['aia'],True,str(url))])

        if json['extensions']['issuers'] != "":
            url = "caIssuers;URI:%s" % (json['extensions']['issuers'].replace("<ca_id>",str(ca_id)))
            ca_cert.add_extensions([crypto.X509Extension(config.extensions['aia'],True,str(url))])
        
        if root_key is not None:
            ca_cert.sign(root_key, str(json['hash']))
        else:
            ca_cert.sign(self.pKey, str(json['hash']))
              

        # Setting the public key
        self.public = crypto.dump_certificate(crypto.FILETYPE_PEM,ca_cert)

    def dump(self,path):
        with open(path % self.id+".private.key","wb") as f:
            f.write(self.private)
        with open(path % self.id+".public.key","wb") as f:
            f.write(self.public)
        return path % self.id+".private.key",path % self.id+".public.key" 

class Certificate(db.Model):
    __tablename__ = "certificates"

    # Columns
    id = db.Column(db.Integer,primary_key=True)
    ca = db.Column(db.Integer,db.ForeignKey('ca.id'))                     # The certificate authority that issued this certificate
    name = db.Column(db.String(128),index=True,nullable=False)
    serial = db.Column(db.String(64))                                  # Certificate serial number
    public = db.Column(db.Text)                                        # Public key
    p12 = db.Column(db.Text)                                           # PFX data in Base
    status = db.Column(db.Integer,default=1)                           # Current status: 1 = Active, 2 = Revoked, 3 = Expired
    created = db.Column(db.DateTime,default=datetime.datetime.now())
    code_revoke = db.Column(db.Integer,default=-1)                     # Revocation code
    reason_revoke = db.Column(db.String(256),nullable=True,default="") # Revocation reason (if any)
    date_revoke = db.Column(db.DateTime,nullable=True,default=None)

    # Relationship
    authority = db.relationship('CertificateAuthority')

    # Initializing the certificate
    def __init__(self):
        pass

    def __repr__(self):
        return "<Certificate, serial=%r, status=%r, pfxdata=%r" % (self.serial,self.status,self.p12)

    def dump(self,path):
        with open(path % self.id+".cert.pem","wb") as f:
            f.write(self.public)
        return path % self.id+".cert.pem"

class Template(db.Model):
    __tablename__ = "templates"

    # Columns
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(128),index=True)
    dscr = db.Column(db.String(256),index=True)
    extensions = db.Column(db.Text)

    def __init__(self,name,dscr):
        self.name = name
        self.dscr = dscr

    def set_extensions(self,extensions=[]):
        self.extensions = json.dumps(extensions)

    def __repr__(self):
        return "<Template, name=%r, dscr=%r, extensions=%r" % (self.name,self.dscr,self.extensions)

    def as_dict(self):
       return {
            "name":self.name,\
            "dscr":self.dscr,\
            "extensions":json.loads(self.extensions)
       }

    def list_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @staticmethod
    def from_file(path):
        pass

class User(db.Model):
    __tablename__ = "users"

    # Columns
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(128),index=True)
    email = db.Column(db.String(256),index=True)
    subject = db.Column(db.String(256),nullable=True,index=True)

    def __init__(self,name):
        self.name = name
    
    def __repr__(self):
        return "<User, name=%r, email=%r,subject=%r>" % (self.name,self.email,self.subject)

    def set_email(self,email):
        self.email = email

    def set_dn(self,dn):
        self.subject = dn

    def as_dict(self):

        user = {}
        user['id'] = self.id
        user['name'] = self.name
        user['email'] = self.email
        user['subject'] = {}

        # Splitting the Subject DN
        array = self.subject.split(",")
        temp_array = []
        for item in array:
            temp_array = item.split("=")
            user['subject'][temp_array[0].strip()] = temp_array[1].strip()     
        return user

class CRL(db.Model):
    __tablename__ = "crls"

    # Columns
    id = db.Column(db.Integer,primary_key=True)
    ca = db.Column(db.Integer,db.ForeignKey('ca.id'))
    created = db.Column(db.DateTime,nullable=True,default=datetime.datetime.utcnow)
    crl = db.Column(db.LargeBinary,nullable=False)   

    # Methods
    def __init__(self):
        pass