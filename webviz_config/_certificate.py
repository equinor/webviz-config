import os
import re
import sys
import socket
import datetime
import getpass
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa


NAME = x509.Name([
          x509.NameAttribute(NameOID.COUNTRY_NAME, 'NO'),
          x509.NameAttribute(NameOID.LOCALITY_NAME, 'Trondheim'),
          x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Webviz'),
          x509.NameAttribute(NameOID.COMMON_NAME, f'{getpass.getuser()}'),
          x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, 'Webviz'),
       ])

CA_KEY_FILENAME = 'ca.key'
CA_CRT_FILENAME = 'ca.crt'

SERVER_KEY_FILENAME = 'server.key'
SERVER_CRT_FILENAME = 'server.crt'

DNS_NAME = re.sub('[0-9]+', '*', socket.getfqdn())


def user_data_dir():
    '''Returns platform specific path to store user application data
    '''

    if sys.platform == "win32":
        return os.path.normpath(os.path.expanduser('~/Application Data/'
                                                   'webviz_cert'))
    elif sys.platform == 'darwin':
        return os.path.expanduser('~/Library/Application Support/webviz')
    else:
        return os.path.expanduser("~/.local/share/webviz")


def create_key(key_path):

    key = rsa.generate_private_key(public_exponent=65537,
                                   key_size=2048,
                                   backend=default_backend())

    with open(key_path, "wb") as fh:
        fh.write(key.private_bytes(
               encoding=serialization.Encoding.PEM,
               format=serialization.PrivateFormat.TraditionalOpenSSL,
               encryption_algorithm=serialization.NoEncryption()
              ))

    return key


def certificate_template(subject, issuer, public_key, ca=False):

    if ca:
        not_valid_after = datetime.datetime.utcnow() + \
                          datetime.timedelta(days=365)

    else:  # shorter valid length for on-the-fly certificates
        not_valid_after = datetime.datetime.utcnow() + \
                          datetime.timedelta(days=7)

    return x509.CertificateBuilder()\
               .subject_name(subject)\
               .issuer_name(issuer)\
               .public_key(public_key)\
               .serial_number(x509.random_serial_number())\
               .not_valid_before(datetime.datetime.utcnow())\
               .not_valid_after(not_valid_after)\
               .add_extension(x509.SubjectAlternativeName(
                                      [
                                       x509.DNSName('localhost'),
                                       x509.DNSName(DNS_NAME)
                                      ]),
                              critical=True)\
               .add_extension(x509.BasicConstraints(ca=ca, path_length=None),
                              critical=True)


def create_ca(args):

    directory = user_data_dir()

    os.makedirs(directory, exist_ok=True)

    ca_key_path = os.path.join(directory, CA_KEY_FILENAME)
    ca_crt_path = os.path.join(directory, CA_CRT_FILENAME)

    if not args.force and os.path.isfile(ca_crt_path):
        raise OSError(f'The file {ca_crt_path} already exists. Add the '
                      'command line flag --force if you want to overwrite')

    key = create_key(ca_key_path)

    subject = issuer = NAME

    cert = certificate_template(subject, issuer, key.public_key(), ca=True)\
        .sign(key, hashes.SHA256(), default_backend())

    with open(ca_crt_path, "wb") as fh:
        fh.write(cert.public_bytes(serialization.Encoding.PEM))

    sha1 = "-".join(re.findall('.{8,8}',
                               cert.fingerprint(hashes.SHA1()).hex())).upper()

    print(f'''\n\033[1m\033[94m
 Created CA key and certificate files (both saved in {directory}).
 Keep the key file ({CA_KEY_FILENAME}) private. The certificate file
 ({CA_CRT_FILENAME}) is not sensitive, and you can import it in
 your browser(s).

 To install it in Chrome:

    - Open Chrome and go to chrome://settings/privacy
    - Select "Manage certificates"
    - Under the tab "Trusted Root Certificatation Authorities", click "Import"
    - Go to {directory} and select the created certificate ({CA_CRT_FILENAME}).
    - Click "Next" and select "Place all certificates in the following store"
    - Click "Next" and then "Finished"
    - If a dialog box appears, you can verify that the displayed thumbprint is
      the same as this one:
       {sha1}
    - Restart Chrome

 When done, you do not have to rerun "webviz certificate" or do this procedure
 before the certificate expiry date has passed. The certificate is only valid
 for localhost and {DNS_NAME}.''')


def create_certificate(directory):

    ca_directory = user_data_dir()
    ca_key_path = os.path.join(ca_directory, CA_KEY_FILENAME)
    ca_crt_path = os.path.join(ca_directory, CA_CRT_FILENAME)

    server_key_path = os.path.join(directory, SERVER_KEY_FILENAME)
    server_crt_path = os.path.join(directory, SERVER_CRT_FILENAME)

    if not os.path.isfile(ca_key_path) or not os.path.isfile(ca_crt_path):
        raise RuntimeError('Could not find CA key and certificate. Please '
                           'run the command "webviz certificate" and '
                           'try again')

    with open(ca_key_path, 'rb') as fh:
        ca_key = serialization.load_pem_private_key(
            data=fh.read(),
            password=None,
            backend=default_backend()
        )

    with open(ca_crt_path, 'rb') as f:
        ca_crt = x509.load_pem_x509_certificate(data=f.read(),
                                                backend=default_backend())

    server_key = create_key(server_key_path)

    crt = certificate_template(NAME, ca_crt.subject, server_key.public_key())\
        .add_extension(critical=True,
                       extension=x509.KeyUsage(
                                           digital_signature=True,
                                           key_encipherment=True,
                                           content_commitment=True,
                                           data_encipherment=False,
                                           key_agreement=False,
                                           encipher_only=False,
                                           decipher_only=False,
                                           key_cert_sign=False,
                                           crl_sign=False))\
        .add_extension(critical=False,
                       extension=x509.AuthorityKeyIdentifier
                       .from_issuer_public_key(ca_key.public_key()))\
        .sign(private_key=ca_key,
              algorithm=hashes.SHA256(),
              backend=default_backend())

    with open(server_crt_path, 'wb') as f:
        f.write(crt.public_bytes(encoding=serialization.Encoding.PEM))
