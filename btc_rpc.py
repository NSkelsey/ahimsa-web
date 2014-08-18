import sys, threading

import psutil
from bitcoinrpc.authproxy import AuthServiceProxy

def url(user, passw, port):
    '''
    Returns the properly formatted rpc url for a local connection
    '''
    url = 'http://{0}:{1}@localhost:{2}'.format(user, passw, port)
    return url


def make_proxy(url):
    '''
    Returns an instantiated rpc connection to the local bitcoin node. Raises an
    exception if the connection doesn't work.
    '''
    proxy = AuthServiceProxy(url)
    try:
        proxy.getinfo()
    except ValueError:
        print 'RPC is not working correctly, check bitcoin and url: %s' % url
        sys.exit(1)
    return proxy

def update_globals(proxy, jinja_globals):

    def query_daemons():
        btcjson = proxy.getinfo()
        peers = btcjson['connections']
        jinja_globals['bitcoind_peers'] = peers

        for proc in psutil.process_iter():
            name = proc.name()
            if name == 'ahimsad':
                jinja_globals['ahimsad_status'] = proc.status()
            if name == 'bitcoind':
                jinja_globals['bitcoind_status'] = proc.status()

    query_daemons()
    threading.Timer(60, query_daemons).start()
    

