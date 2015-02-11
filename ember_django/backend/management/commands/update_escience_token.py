# django-admin command to run on the backend
# Periodically checks and updates the escience token in the database
# Triggers the update_token function of the Token model

import datetime
import time
from django.core.management.base import BaseCommand, CommandError
from backend.models import Token
from django.utils import timezone

class Command(BaseCommand):
    help = 'Updates escience token periodically'

    def handle(self, *args, **options):
        # two options
        # first, without arguments
        #     it checks every hour and
        #     expires tokens that are over 1 month
        # second with two arguments
        #     the first argument defines the period for this function 
        #     to trigger the update token function in the database
        #     the second argument defines the expiration time for the escience token
        #     both arguments are expressed in seconds

        if len(args) == 0:
            while True:
                # wait for 3600 (1 hour)
                time.sleep(1);
                # for all tokens
                for token in Token.objects.all():
                    # trigger the update function
                    # set expiration timeout to 2592000 seconds (1 month)
                    token.update_token(30);
        elif len(args) == 2:
            while True:
                # wait for a period of time (first argument)
                time.sleep(int(args[0]));
                # for all tokens
                for token in Token.objects.all():
                    # trigger the update function
                    # set expiration timeout as the second argument defines
                    token.update_token(int(args[1]));
        else:
            self.stdout.write('Invalid number of arguments.')
