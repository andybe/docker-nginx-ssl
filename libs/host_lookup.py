#!/usr/bin/python3
import socket
from urllib.request import urlopen
import re
from dns import resolver



# simple
# this works with single IP
def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = None
    finally:
        s.close()
    return IP

# only works for ipv4
def get_public_ip():
    data = str(urlopen('http://checkip.dyndns.com/').read())
    # data = '<html><head><title>Current IP Check</title></head><body>Current IP Address: 65.96.168.198</body></html>\r\n'
    return re.compile(r'(?:(?!\n)\s)(((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\s*$)').search(data).group(1)


def find_host_a_record(hostname,host_ip, quiet=False):
  res = resolver.query(hostname,'A')
  for o in res:
    if str(o) == host_ip:
        return True
  return False