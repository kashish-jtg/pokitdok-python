|version|

PokitDok Platform API Client for Python
=======================================

Installation
------------

Install from PyPI_ using pip_

.. code-block:: bash

    $ pip install pokitdok


Resources
---------

Please see the documentation_ for detailed information on all of the PokitDok Platform APIs.
The documentation includes Python client examples for each API.

Report API client issues_ on GitHub


Handling your client_id and client_secret keys
-----------

We recommend using environment variables to store your `client_id` and `client_secret` keys. This can be done via a config module or using system variables.
The following steps create system variables for your PokitDok keys.

To create system variables from a Linux terminal, first open your `.bashrc` file in your text editor of choice.

.. code-block:: bash

    vi $HOME/.bashrc

Next, add the two lines below to update your `.bashrc` to export `POKITDOK_*` environment variables. You will need to use your client_id and client_secret for your PokitDok application. These variables store the client credentials for your PokitDok App (you should never check your client_id and secret into publicly available code)

.. code-block:: bash

    export POKITDOK_CLIENT_ID=<client id>
    export POKITDOK_CLIENT_SECRET=<client secret>

Lastly, open a terminal and source your `.bashrc` to make the variables accessible in your localhost:

.. code-block:: bash

    source $HOME/.bashrc

Then, to access your variables within a Python script:

.. code-block:: python
    
    import os
    import pokitdok

    client_id = os.environ['POKITDOK_CLIENT_ID']
    client_secret = os.environ['POKITDOK_CLIENT_SECRET']
    client_settings = {
        'client_id': client_id,
        'client_secret': client_secret,
    }
    pd = pokitdok.api.connect(**client_settings)


Quick start
---------------

The client offers a few options for making API requests. High level convenience functions are available for each of the APIs for convenience. The example below demonstrates how to connect and use the `eligibility` convenience function to submit an eligibility request:

.. code-block:: python

    import pokitdok
    import os
    pd = pokitdok.api.connect(os.environ['POKITDOK_CLIENT_ID'], os.environ['POKITDOK_CLIENT_SECRET'])

    #submit an eligibility request
    pd.eligibility({
        "member": {
            "birth_date": "1970-01-01",
            "first_name": "Jane",
            "last_name": "Doe",
            "id": "W000000000"
        },
        "trading_partner_id": "MOCKPAYER"
    })

If your application would prefer to interact with the APIs at a lower level,
you may elect to use the general purpose request method or one of the http method aliases built around it.

.. code-block:: python

    # a low level "request" method is available that allows you to have more control over the construction of the API request

    import pokitdok
    import os
    pd = pokitdok.api.connect(os.environ['POKITDOK_CLIENT_ID'], os.environ['POKITDOK_CLIENT_SECRET'])

    pd.request('/activities', method='get')

    pd.request('/eligibility/', method='post', data={
        "member": {
            "birth_date": "1970-01-01",
            "first_name": "Jane",
            "last_name": "Doe",
            "id": "W000000000"
        },
        "trading_partner_id": "MOCKPAYER"
    })

    # Convenience methods are available for the commonly used http methods built around the request method
    pd.get('/activities')

    pd.post('/eligibility/', data={
        "member": {
            "birth_date": "1970-01-01",
            "first_name": "Jane",
            "last_name": "Doe",
            "id": "W000000000"
        },
        "trading_partner_id": "MOCKPAYER"
    })

    # higher level functions are also available to access the APIs
    pd.activities()

    pd.eligibility({
        "member": {
            "birth_date": "1970-01-01",
            "first_name": "Jane",
            "last_name": "Doe",
            "id": "W000000000"
        },
        "trading_partner_id": "MOCKPAYER"
    })


Authentication and Authorization
--------------------------------

Access to PokitDok APIs is controlled via OAuth2.  Most APIs are accessible with an
access token acquired via a client credentials grant type since scope and account context
are not required for their use.

If you'd like your access token to automatically refresh when using the authorization flow, you can connect like this:

.. code-block:: python

    import pokitdok
    import os
    pd = pokitdok.api.connect(os.environ['POKITDOK_CLIENT_ID'],
                              os.environ['POKITDOK_CLIENT_SECRET'],
                              auto_refresh=True)


That instructs the Python client to use your refresh token to request a new access token
when the access token expires after 1 hour.

For APIs that require a specific scope/account context in order to execute,  you'll need to request
authorization from a user prior to requesting an access token.

.. code-block:: python

    import pokitdok
    import os

    def new_token_handler(token):
        print('new token received: {0}'.format(token))
        # persist token information for later use

    pd = pokitdok.api.connect(**client_settings,
                              redirect_uri='https://yourapplication.com/redirect_uri',
                              scope=['user_schedule'],
                              auto_refresh=True,
                              token_refresh_callback=new_token_handler)

    authorization_url, state = pd.authorization_url()
    #redirect the user to authorization_url


You may set your application's redirect uri value via the PokitDok Platform Dashboard (https://platform.pokitdok.com)
The redirect uri specified for authorization must match your registered redirect uri exactly.

After a user has authorized the requested scope, the PokitDok Platform will redirect back to your application's
Redirect URI along with a code and the state value that was included in the authorization url.
If the state matches the original value, you may use the code to fetch an access token:

.. code-block:: python

    import pokitdok
    import os

    pd = pokitdok.api.connect(os.environ['POKITDOK_CLIENT_ID'], os.environ['POKITDOK_CLIENT_SECRET'])
    pd.fetch_access_token(code='<code value received via redirect>')


Your application may now access scope protected APIs on behalf of the user that authorized the request.
Be sure to retain the token information to ensure you can easily request an access token when you need it
without going back through the authorization code grant redirect flow.   If you don't retain the token
information or the user revokes your authorization, you'll need to go back through the authorization process
to get a new access token for scope protected APIs.

Check SSL protocol and cipher
-----------------------------

.. code-block:: python

    import pokitdok
    import os

    pd = pokitdok.api.connect(os.environ['POKITDOK_CLIENT_ID'], os.environ['POKITDOK_CLIENT_SECRET'])
    pd.request('/ssl/', method='get')


Jupyter Notebooks
-------
We have a notebook available for you to use that demos how to use our APIs. To use that notebook, you will need to execute these commands from a terminal to then have access to the `PlatformQuickStartDemo.ipynb` notebook within a browser window.

.. code-block:: bash

    $ pip install jupyter
    $ cd notebooks/
    $ jupyter notebook



Supported Python Versions
-------------------------

This library is tested within the [official Docker images](https://hub.docker.com/_/python/) for the following Python versions:

* 2.7
* 3.2
* 3.3
* 3.4
* 3.5
* pypy:2-5.6.0

If you already have docker, you can run the tests yourself via docker by running the testing script included in this repository:

.. code-block:: bash

    $ sh run_tests_in_docker.sh

To use the testing process, you will need to drop your `client_id` and `client_secret` in a file called `env.list` with the structure:

.. code-block:: bash

    POKITDOK_CLIENT_ID=<your_id>
    POKITDOK_CLIENT_SECRET=<your_secret>

You may have luck with other interpreters - let us know how it goes.


License
-------

Copyright (c) 2018 PokitDok, Inc.  See LICENSE_ for details.

.. _documentation: https://platform.pokitdok.com/documentation/v4/?python#
.. _issues: https://github.com/pokitdok/pokitdok-python/issues
.. _PyPI: https://pypi.python.org/pypi
.. _pip: https://pypi.python.org/pypi/pip
.. _LICENSE: LICENSE.txt
.. _Jupyter: http://jupyter.org/
.. _notebook: notebooks/PlatformQuickStartDemo.ipynb

.. |version| image:: https://badge.fury.io/py/pokitdok.svg
    :target: https://pypi.python.org/pypi/pokitdok/
