import sys
import re
from os import path, mkdir, system
import shutil
import random
from OpenSSL import crypto, SSL

from libs.host_structur import directories,templates
from libs.host_lookup import get_host_ip

single_forward_http_https = \
    'server {\n' \
    '    listen 80;\n' \
    '    listen [::]:80;\n' \
    '\n' \
    '    server_name __DOMAINS__;\n' \
    '\n' \
    '    location / { \n'\
    '      return 301 https://__DOMAIN__$request_uri;\n' \
    '    }\n' \
    '\n' \
    '    location ^~/.well-known/acme-challenge/ { \n'\
    '      allow all;\n'\
    '      root /var/www/letsencrypt;\n'\
    '      default_type "text/plain";\n' \
    '    }\n' \
    '}\n' \
    '\n'

single_forward_https = \
    'server {\n' \
    '    listen 443 ssl;\n' \
    '    listen [::]:443 ssl;\n' \
    '\n' \
    '    server_name __DOMAINS__;\n' \
    '\n' \
    '    ssl_certificate     /var/www/__DOMAIN__/ssl/__SSL_DOMAIN__.crt;\n' \
    '    ssl_certificate_key /var/www/__DOMAIN__/ssl/__SSL_DOMAIN__.key;\n' \
    '\n' \
    '    return 301 https://__DOMAIN__$request_uri;\n' \
    '}\n'

single_https = \
    'server {\n' \
    '    listen 443 ssl;\n' \
    '    listen [::]:443 ssl;\n' \
    '\n' \
    '    server_name __DOMAIN__;\n' \
    '\n' \
    '    ssl_certificate     /var/www/__DOMAIN__/ssl/__SSL_DOMAIN__.crt;\n' \
    '    ssl_certificate_key /var/www/__DOMAIN__/ssl/__SSL_DOMAIN__.key;\n' \
    '\n' \
    '    location / { \n'\
    '      root /var/www/__DOMAIN__/html;\n' \
    '      index index.html;\n' \
    '    }\n' \
    '}\n'

def https_config(xs):
    if isinstance(xs, list) and len(xs) == 1:
        xs = xs[0]

    if isinstance(xs, str):
        stream = single_forward_http_https.replace('__DOMAINS__', xs)
        stream += single_https
        return stream.replace('__DOMAIN__', xs)

    stream = single_forward_http_https.replace('__DOMAINS__',' '.join(xs))
    domain = xs[-1]
    xs = xs[:-1]
    stream += single_forward_https
    stream += single_https
    stream = stream.replace('__DOMAINS__', ' '.join(xs))
    stream = stream.replace('__SSL_DOMAIN__', xs[0])
    return stream.replace('__DOMAIN__', domain)

#this is only a dummy operation
def create_ssl_cert(ssl_dir:str = '', domain:str ='', dummy: bool = True):

    print("create ssl key for >" + domain + "< in '" + ssl_dir + "'.")
    
    if dummy:
        emailAddress="webmaster@" + domain
        commonName= domain
        countryName="US"
        localityName="New York"
        stateOrProvinceName="New York"
        organizationName="Hight IT"
        organizationUnitName="Central Computing"
        serialNumber=0
        validityStartInSeconds=0
    else:
         raise Exception("only dummy works for now")

    validityEndInSeconds=10*365*24*60*60
    KEY_FILE = ssl_dir + "/" + domain + ".key"
    CERT_FILE= ssl_dir + "/" +domain + ".crt"
    #can look at generated file using openssl:
    #openssl x509 -inform pem -in selfsigned.crt -noout -text
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)
    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = countryName
    cert.get_subject().ST = stateOrProvinceName
    cert.get_subject().L = localityName
    cert.get_subject().O = organizationName
    cert.get_subject().OU = organizationUnitName
    cert.get_subject().CN = commonName
    cert.get_subject().emailAddress = emailAddress
    cert.set_serial_number(serialNumber)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(validityEndInSeconds)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha512')
    with open(CERT_FILE, "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    with open(KEY_FILE, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))


def in_one_domain(xs: [] = ''):
    if isinstance(xs, str):
        return True
    return True if ' '.join(xs).count(xs[0]) == len(xs) else False


def all_fqn(xs=''):
    if isinstance(xs, str):
        if is_fqdn(xs):
            return True
        else:
            print("This is not fqn: " + str)
        return False
    for s in xs:
        if not is_fqdn(s):
            print("This is not a fqn:" + s)
            return False
    return True


def is_fqdn(hostname: str):
    return True if re.match('(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63}$)', hostname,
                            re.IGNORECASE) else False


def create_https_domain(domains = []):
    if not in_one_domain(domains):
        print("A website can only be in one domain:")
        print(str(domains) + "! Exit.")
        return

    if not all_fqn(domains):
       return

    domain = domains[0]
    conf_dir = directories['nginx.conf.d'] 
    composer_dir = directories['docker-composer'] +  "/" + domains[-1]
    log_dir= directories["nginx.log"] + "/" + domain
    ssl_dir = composer_dir + "/ssl"

    default_config = conf_dir + "/" + domain + ".conf"
    try:
        f = open(default_config)
        f.close()
        print("Default configuration exist:" +default_config)
        return
    except FileNotFoundError as e:
        pass

    if not path.isdir(composer_dir):
        mkdir(composer_dir)
        #create a default html directory
        mkdir(composer_dir + "/html")
        shutil.copy2(templates['index.html'], composer_dir + "/html/index.html")

    if not path.isdir(log_dir):
        mkdir(log_dir)

    if not path.isdir(ssl_dir):
        mkdir(ssl_dir)

    # append ssl / for now we over write
    with open(default_config,'w') as config:
        data = https_config(domains)
        config.write(data)
        config.close

    create_ssl_cert(ssl_dir, domain)
