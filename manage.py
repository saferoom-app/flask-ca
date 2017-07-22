# Import section
import os
from flask_script import Manager, Server
from webapp import app
from flask_migrate import Migrate,MigrateCommand
from webapp.models import db,CertificateAuthority,Key,Certificate,Template,User,CRL

# Initializing the manager
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command("server", Server(host="0.0.0.0"))
manager.add_command('db', MigrateCommand)


@manager.shell
def make_shell_context():
    return dict(app=app,db=db,CertificateAuthority=CertificateAuthority,Key=Key,Certificate=Certificate,Template=Template,User=User,CRL=CRL)

if __name__ == "__main__":
	manager.run()