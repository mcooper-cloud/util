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

    parser = argparse.ArgumentParser(description='Auth0 field name replacement for user app_metadata')

    parser.add_argument(
        '--find', '--f',
        dest='find_value', 
        nargs=1, 
        help='Value to be replaced with replace_value'
    )

    parser.add_argument(
        '--replace', '--r',
        dest='replace_value', 
        nargs=1, 
        help='Value to replace find_value'
    )

    parser.add_argument(
        '--infile', '--i',
        dest='infile', 
        nargs=1, 
        help='File where user will be read in (JSON format)'
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
    ## update user
    ##
    ##########################################################################
    ##########################################################################


    def update_user(self, user_id=None, user_metadata=None, app_metadata=None, kwargs=None):


        header = {'Authorization' : 'Bearer {}'.format(self.access_token)}

        if user_id is not None:
 
            user_id = user_id
            user_data = {}

            if kwargs is not None:
                user_data = kwargs

            if user_metadata is not None:
                user_data['user_metadata'] = user_metadata

            if app_metadata is not None:
                user_data['app_metadata'] = app_metadata


            url = '{}/users/{}'.format(self.mgmt_endpoint, user_id)

            print('[+] Updating user record for user: {}'.format(user_id))
            user_response = requests.patch(url, json=user_data, headers=header)

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


    find_value = args.find_value[0] if args.find_value else None
    replace_value = args.replace_value[0] if args.replace_value else None
    infile = args.infile[0] if args.infile else None

    client_id = None
    client_secret = None
    auth0_domain = None

    print('[+] Creating Auth0 management client')
    auth0_tenant = Auth0( client_id=client_id, 
                          client_secret=client_secret,
                          auth0_domain=auth0_domain )


    if infile is not None:
        with open(infile, 'rb') as f:
            data = json.load(f)

            if 'users' in data:
                data = data['users']

            for d in data:

                if 'app_metadata' in d:

                    if find_value in d['app_metadata']:

                        user_id = d['user_id']

                        print('Old app_metadata: {}'.format(d['app_metadata']))

                        d['app_metadata'][find_value] = None
                        d['app_metadata'][replace_value] = d['app_metadata'][find_value]
                        d['app_metadata'].pop(find_value)

                        print('NEW app_metadata: {}'.format(d['app_metadata']))

                        auth0_tenant.update_user(user_id=user_id, app_metadata=d['app_metadata'])



