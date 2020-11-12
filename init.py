#!/usr/bin/python3
import sys
from os import path, mkdir, system
import shutil
import random
from OpenSSL import crypto, SSL

from libs.host_structur import do_host_check,directories,templates
from libs.generate_ssl_configs import create_https_domain

def help():
    print('You need help?')
    init()
    pass

def init():
    do_host_check()
    pass


if __name__ == "__main__":

    if len(sys.argv)<2:
        help()
        quit()

    do_host_check()
    domains = sys.argv
    del domains[0]
    create_https_domain(domains)

    from libs.host_lookup import find_host_a_record,get_host_ip

    for d in domains:
        print(find_host_a_record(d,get_host_ip()))

