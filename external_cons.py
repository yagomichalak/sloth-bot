# import.standard
import os
from typing import Any

# import.thirdparty
import praw
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

async def the_reddit() -> Any:
    """ Gets the Reddit connection. """

    reddit = praw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'),  # client id
                        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),  # my client secret
                        user_agent=os.getenv('USER_AGENT'),  # my user agent. It can be anything
                        username='',  # Not needed
                        password='')  # Not needed

    return reddit

async def the_drive() -> Any:
    """ Gets the GoogleDrive connection. """

    gauth = GoogleAuth()
    # gauth.LocalWebserverAuth()
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # This is what solved the issues:
        gauth.GetFlow()
        gauth.flow.params.update({'access_type': 'offline'})
        gauth.flow.params.update({'approval_prompt': 'force'})

        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:

        # Refresh them if expired
        gauth.Refresh()
    else:

        # Initialize the saved creds
        gauth.Authorize()

    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")

    drive = GoogleDrive(gauth)
    return drive