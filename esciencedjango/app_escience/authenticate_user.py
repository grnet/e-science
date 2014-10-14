# -*- coding: utf-8 -*-

'''
This script authenticates escience users.

@author: Ioannis Stenos, Nick Vrionis
'''

import logging
from kamaki.clients.astakos import AstakosClient
from kamaki.clients import ClientError

# Definitions of return value errors
error_authentication = -1

# Constants
AUTHENTICATED = 1
NOT_AUTHENTICATED = 0

def check_credentials(token, auth_url='https://accounts.okeanos.grnet.gr'
                      '/identity/v2.0'):
    '''Identity,Account/Astakos. Test authentication credentials'''
    logging.info( ' Test the credentials')
    try:
        auth = AstakosClient(auth_url, token)
        auth.authenticate()
        logging.info(' Authentication verified')
        return AUTHENTICATED
    except ClientError:
        logging.error('Authentication failed with url %s and token %s' % (
                      auth_url, token))
        return NOT_AUTHENTICATED
