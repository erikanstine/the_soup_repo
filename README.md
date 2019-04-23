# the_soup_repo

Adding these files to my personal git to be a resource for Plaiderdays slackbot authors.

There are a lot of helpful tutorials, just look for `python slackbot tutorial`.

Implementaion notes:

  -Error:
  `slackclient.server.SlackConnectionError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1056`
  
  -Solution:
    Versioning.
    
    Latest - `websocket-client==0.54.0`
    
    Works - `websocket-client==0.47.0`
