import sys, threading

import psutil

def update_globals(jinja_globals):
    '''
    Every set unit of time query the system to check the status of bitcoind
    and ahimsad. This will alert the user to any potential problems caused by
    a lack of either of the two services.
    '''

    def query_daemons():
        found_ahimd, found_btcd = False, False
        for proc in psutil.process_iter():
            name = proc.name()
            if name == 'ahimsad':
                found_ahimd = True
                jinja_globals['ahimsad_status'] = proc.status()
            if name == 'bitcoind':
                found_btcd = True
                jinja_globals['bitcoind_status'] = proc.status()
        if not found_ahimd:
            jinja_globals['ahimsad_status'] = 'Dead'
        if not found_btcd:
            jinja_globals['bitcoind_status'] = 'Dead'


    query_daemons()
    threading.Timer(60, query_daemons).start()
    

