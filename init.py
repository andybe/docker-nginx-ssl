#!/usr/bin/python3
import sys
from os import path, mkdir, system
import shutil
import random
from OpenSSL import crypto, SSL


# this mirror the default structur form a normal nginx installation
# /etc/nginx/nginx.conf
# /etc/nginx/nginx.d
# /etc/nginx/ssl
# /var/www/ -> main docker-compose.yml
# /var/www/example.domain/ (docker-compose.yml)
# /var/www/example.domain/html
# /var/www/example.domain/ssl (private certifications)

directories = { 
    'nginx' : '/etc/nginx',
    'nginx.conf.d' : '/etc/nginx/conf.d',
    'nginx.ssl' : '/etc/nginx/ssl',
    'www' : '/var/www',
    'nginx.log' : '/var/log/nginx',
    'docker-composer' : '/var/www',
}

configs = {
    '/etc/nginx/nginx.conf': 'tmpl/nginx.conf.tmpl',
    '/var/www/docker-compose.yml':'tmpl/docker-compose-master.yml',
}

DH_PARAM = '/etc/nginx/ssl/dhparam.pem'
DH_SIZE = 2048

templates = {
    'default' : 'tmpl/default.conf.tmpl', # website configuration
    'ssl' : 'tmpl/ssl.conf.tmpl', # website configuration
    'index.html' : 'tmpl/index.html.tmpl' # standard web page
}

def check_directories():

    changes = 0
    
    for d in directories:
        directory = directories[d]
        if not path.isdir(directory):
              mkdir(directory)
              print("created: " + directory)
              changes += 1
    if not changes:
        print("Directories exist.")

    return changes

def check_default_configurations():

    changes = 0

    for c in configs:
        try:
            f = open(str(c))
            f.close()
        except FileNotFoundError:
            shutil.copy2(str(configs[c]),str(c))
            print("Copy " + str(configs[c]) + " - >" + str(c))
            changes += 1
    if not changes:
        print("Default configuratins are exist.")
    
    try:
        f = open(DH_PARAM)
        f.close
    except Exception:
        print("Openssl write: " + DH_PARAM)
        #keep it simple
        system("sh -c 'openssl dhparam -out " + DH_PARAM + " " + str(DH_SIZE) + "'")
        changes += 1

    return changes


def do_check():
    check_directories()
    check_default_configurations()
    pass

def help():
    do_check()
    pass

def init():
    check_directories()
    check_default_configurations()
    pass

#this is only a dummy operation
def create_ssl_cert(ssl_dir:str = '', domain:str ='', dummy: bool = True):

    print("create ssl key for >" + domain + "< in '" + ssl_dir + "'.")
    
    if dummy:
        emailAddress="webmaster@" + domain
        commonName="Big Apple"
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

def create_domain(domains = []):
    domain = domains[0]
    conf_dir = directories['nginx.conf.d'] 
    composer_dir = directories['docker-composer'] +  "/" + domain
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
    #create default http
#    f = open(templates['default'],"r")
#    data = f.read()
#    f.close
#    data = data.replace('__DOMAINS__', ' '.join(domains))
#    data =data.replace('__DOMAIN__', domain)
#    f = open(default_config,'w')
#    f.write(data)
#    f.close

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
        f = open(templates['ssl'],"r")
        data = f.read()
        f.close
        data = data.replace('__DOMAINS__', ' '.join(domains))
        data =data.replace('__DOMAIN__', domain)
        config.write(data)
        config.close

    create_ssl_cert(ssl_dir, domain)


if __name__ == "__main__":

    if len(sys.argv)<2:
        help()
        quit()
    
    do_check()
    l = sys.argv
    del l[0]
    create_domain(l)