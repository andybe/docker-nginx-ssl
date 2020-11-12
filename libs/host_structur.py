import sys
from os import path, mkdir, system
import shutil

# this mirror the default structur form a normal nginx installation
# /etc/nginx/nginx.conf
# /etc/nginx/nginx.d
# /etc/nginx/ssl
# /var/www/ -> main docker-compose.yml
# /var/www/example.domain/ (docker-compose.yml)
# /var/www/example.domain/html
# /var/www/example.domain/ssl (private certifications)
# /etc/letsencrypt 
# /var/logs/letsencrypt

directories = {
    'nginx' : '/etc/nginx',
    'nginx.conf.d' : '/etc/nginx/conf.d',
    'nginx.ssl' : '/etc/nginx/ssl',
    'www' : '/var/www',
    'nginx.log' : '/var/log/nginx',
    'docker-composer' : '/var/www',
    'letsencrypt' : '/etc/letsencrypt',
    'letsencrypt.log' : '/var/log/letsencrypt/',
    'letsencrypt.acme' : '/var/www/letsencrypt/',
    'nginx' : '/etc/nginx'
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

##########################################
# Host structur                          #
##########################################

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


def do_host_check():
    check_directories()
    check_default_configurations()
    pass
