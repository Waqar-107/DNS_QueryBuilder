#from dust i have come, dust i will be

from DNS_QueryBuilder import *

q = dns_query("8.8.8.8", 53)
ip = q.getIP("codeforces.com", True)

print(ip)