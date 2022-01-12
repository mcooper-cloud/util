#!/usr/bin/env python3


###############################################################################
###############################################################################
##
##  the purpose of this Lambda function is to 
##  manage events from an Auth0 log stream
##
###############################################################################
###############################################################################

import json
import base64
import os
import uuid
import requests
import urllib.parse
import datetime
import argparse

###############################################################################
###############################################################################
##
## Arguments - allows user to call from command line
##
###############################################################################
###############################################################################


class Args(object):

    parser = argparse.ArgumentParser(description='Auth0 user search utility')

    parser.add_argument(
        '--query', '--q',
        dest='query', 
        nargs=1, 
        help='User search query parameters'
    )

    parser.add_argument(
        '--include-totals',
        dest='include_totals', 
        action='store_true',
        help='Include totals in output'
    )

    parser.add_argument(
        '--outfile', '--o',
        dest='outfile', 
        nargs=1, 
        help='File where user search results will be written (JSON format)'
    )

    def print_help(self):
        self.parser.print_help()
        exit(1)
        return

    def parse(self):
        args = self.parser.parse_args()
        return args


###############################################################################
###############################################################################
##
## Arguments - allows user to call from command line
##
###############################################################################
###############################################################################


class Auth0(object):

    def __init__( self, 
                  client_id=None, 
                  client_secret=None,
                  auth0_domain=None ):

        if client_id is None or client_secret is None or auth0_domain is None:
            ##
            ## get client_id, client_secret, auth0_domain from env
            ##
            self.client_id = os.environ.get('AUTH0_CLIENT_ID')
            self.client_secret = os.environ.get('AUTH0_CLIENT_SECRET')
            self.auth0_domain = os.environ.get('AUTH0_DOMAIN')

        else:

            self.client_id = client_id
            self.client_secret = client_secret
            self.auth0_domain = auth0_domain

        base_url = 'https://{}'.format(self.auth0_domain)

        self.mgmt_endpoint = '{}/api/v2'.format(base_url)
        self.token_endpoint = '{}/oauth/token'.format(base_url)
        self.get_token()


    ##########################################################################
    ##########################################################################
    ##
    ## get token
    ##
    ##########################################################################
    ##########################################################################


    def get_token(self):

        token_data = {
            'client_id' : self.client_id,
            'client_secret' : self.client_secret,
            'audience' : '{}/'.format(self.mgmt_endpoint),
            'grant_type' : 'client_credentials'
        }

        print('[+] Getting access token from : {}'.format(self.token_endpoint))

        token_response = requests.post(self.token_endpoint, json=token_data)

        self.access_token = token_response.json()['access_token']

        return self.access_token


    ##########################################################################
    ##########################################################################
    ##
    ## search user
    ##
    ##########################################################################
    ##########################################################################


    def search_user(self, query=None, include_totals=False):

        if query is not None:

            query = urllib.parse.quote_plus(query)
            header = {'Authorization' : 'Bearer {}'.format(self.access_token)}

            ##
            ## TODO: add pagination
            ##

            if include_totals is True:
                url = '{}/users?q={}&include_totals=true&search_engine=v3'.format(self.mgmt_endpoint, query)
            else:
                url = '{}/users?q={}&search_engine=v3'.format(self.mgmt_endpoint, query)


            print('[+] Searching for user record for query: {}'.format(query))
            user_response = requests.get(url, headers=header)
            user_json = user_response.json()

        else:
            return

        return user_json


###############################################################################
###############################################################################
##
## MAIN
##
###############################################################################
###############################################################################

if __name__ == '__main__':


    a = Args()
    args = a.parse()


    ##
    ## example query:
    ##
    ##      'app_metadata.primary_id:"auth0|1122334455"'
    ##

    query = args.query[0] if args.query else None
    outfile = args.outfile[0] if args.outfile else None

    include_totals = args.include_totals if args.include_totals else False

    client_id = None
    client_secret = None
    auth0_domain = None

    print('[+] Creating Auth0 management client')
    auth0_tenant = Auth0( client_id=client_id, 
                          client_secret=client_secret,
                          auth0_domain=auth0_domain )

    query = query
    user_data = auth0_tenant.search_user(query=query, include_totals=include_totals)

    print('[+] Writing user search output to {}'.format(outfile))
    with open(outfile, 'w') as f:
        f.write(json.dumps(user_data, indent=4))

    print('User: \n {}'.format(json.dumps(user_data, indent=4)))

