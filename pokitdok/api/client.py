# -*- coding: utf-8 -*-
#
# Copyright (C) 2014, All Rights Reserved, PokitDok, Inc.
# https://www.pokitdok.com
#
# Please see the License.txt file for more information.
# All other rights reserved.
#

from __future__ import absolute_import
import json
import os
import platform
import pokitdok
from requests_oauthlib import OAuth2Session, TokenUpdated
from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError
from warnings import warn


class PokitDokClient(object):
    """
        PokitDok Platform API Client
        This class provides a wrapper around requests and requests-oauth
        to handle common API operations
    """
    def __init__(self, client_id, client_secret, base="https://platform.pokitdok.com", version="v4",
                 redirect_uri=None, scope=None, auto_refresh=False, token_refresh_callback=None, code=None,
                 token=None):
        """
            Initialize a new PokitDok API Client

            :param client_id: The client id for your PokitDok Platform Application
            :param client_secret: The client secret for your PokitDok Platform Application
            :param base: The base URL to use for API requests.  Defaults to https://platform.pokitdok.com
            :param version: The API version that should be used for requests.  Defaults to the latest version.
            :param redirect_uri: The Redirect URI set for the PokitDok Platform Application.
                                 This value is managed at https://platform.pokitdok.com in the App Settings
            :param scope: a list of scope names that should be used when requesting authorization
            :param auto_refresh: Boolean to indicate whether or not access tokens should be automatically
                                 refreshed when they expire.
            :param token_refresh_callback: a function that should be called when token information is refreshed.
            :param code: code value received from an authorization code grant
            :param token: The current API access token for your PokitDok Platform Application. If not provided a new
                token is generated. Defaults to None.
             API clients to reuse an access token across requests. Defaults to None.
        """
        self.base_headers = {
            'User-Agent': 'pokitdok-python#{0}#{1}#{2}#{3}'.format(pokitdok.__version__,
                                                                   platform.python_version(),
                                                                   platform.system(),
                                                                   platform.release())
        }
        self.json_headers = {
            'Content-type': 'application/json',
        }
        self.json_headers.update(self.base_headers)
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.code = code
        self.auto_refresh = auto_refresh
        self.token_refresh_callback = token_refresh_callback
        self.token = token
        self.url_base = "{0}/api/{1}".format(base, version)
        self.token_url = "{0}/oauth2/token".format(base)
        self.authorize_url = "{0}/oauth2/authorize".format(base)
        self.api_client = None
        self.status_code = 0

        self.activities_url = "/activities/{0}"
        self.authorizations_url = "/authorizations/"
        self.ccd_url = "/ccd/"
        self.claims_url = "/claims/"
        self.claims_convert_url = "/claims/convert"
        self.claims_status_url = "/claims/status"
        self.eligibility_url = "/eligibility/"
        self.enrollment_url = "/enrollment/"
        self.enrollment_snapshot_url = "/enrollment/snapshot"
        self.enrollment_snapshot_data_url = "/enrollment/snapshot/{0}/data"
        self.icd_url = "/icd/convert/{0}"
        self.identity_post_url = "/identity/"
        self.identity_put_url = "/identity/{0}"
        self.identity_get_url = "/identity"
        self.identity_match_url = "/identity/match"
        self.identity_history_url = "{0}/identity/{1}/history"
        self.identity_proof_generate_url = "/identity/proof/questions/generate/"
        self.identity_proof_score_url = "/identity/proof/questions/score/"
        self.identity_proof_valid_url = "/identity/proof/valid/"
        self.mpc_url = "/mpc/{0}"
        self.oop_insurance_estimate_url = "/oop/insurance-estimate"
        self.oop_insurance_price_url = "/oop/insurance-load-price"
        self.pharmacy_formulary_url = "/pharmacy/formulary"
        self.pharmacy_network_url = "/pharmacy/network"
        self.pharmacy_plans_url = "/pharmacy/plans"
        self.plans_url = "/plans/"
        self.prices_cash_url = "/prices/cash"
        self.prices_insurance_url = "/prices/insurance"
        self.providers_url = "/providers/{0}"
        self.referrals_url = "/referrals/"
        self.appointments_url = "/schedule/appointments/{0}"
        self.appointment_types_url = "/schedule/appointmenttypes/{0}"
        self.schedulers_url = "/schedule/schedulers/{0}"
        self.schedule_slots_url = "/schedule/slots/"
        self.trading_partners_url = "/tradingpartners/{0}"

        self.initialize_api_client()
        if self.token is None:
            self.fetch_access_token(code=self.code)

    def initialize_api_client(self):
        """
            Initialize OAuth2Session client depending on client credentials flow or authorization grant flow
        """
        if self.code is None:
            # client credentials flow
            self.api_client = OAuth2Session(self.client_id, client=BackendApplicationClient(self.client_id),
                                            token=self.token)
        else:
            # authorization grant flow
            refresh_url = self.token_url if self.auto_refresh else None
            self.api_client = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri, scope=self.scope,
                                            auto_refresh_url=refresh_url, token_updater=self.token_refresh_callback,
                                            auto_refresh_kwargs={
                                                'client_id': self.client_id,
                                                'client_secret': self.client_secret})

    def authorization_url(self):
        """
            Construct OAuth2 Authorization Grant URL
            :return: (authorization url, state value) tuple
        """
        self.initialize_api_client()
        return self.api_client.authorization_url(self.authorize_url)

    def fetch_access_token(self, code=None):
        """
            Retrieves an OAuth2 access token.
            :param code: optional code value obtained via an authorization grant
            :return: the client application's token information as a dictionary
        """
        self.api_client.token = None
        self.token = self.api_client.fetch_token(token_url=self.token_url, code=code, client_id=self.client_id,
                                                 client_secret=self.client_secret, scope=self.scope)
        return self.token

    def request(self, path, method='get', data=None, files=None, **kwargs):
        """
        General method for submitting an API request

        :param path: the API request path
        :param method: the http request method that should be used
        :param data: dictionary of request data that should be used for post/put requests
        :param files: dictionary of file information when the API accepts file uploads as input
        :param kwargs: optional keyword arguments to be relayed along as request parameters
        :return:
        """
        if data and not files:
            headers = self.json_headers
            request_data = json.dumps(data)
        else:
            headers = self.base_headers
            request_data = data

        request_url = "{0}{1}".format(self.url_base, path)
        request_method = getattr(self.api_client, method)
        try:
            response = request_method(request_url, data=request_data, files=files, params=kwargs, headers=headers)
            self.status_code = response.status_code
            if self.status_code == 401:
                # if TokenExpiredError is not raised but it should have been, we'll raise it explicitly here
                # https://github.com/oauthlib/oauthlib/pull/506 could cause this code path to be followed.
                # this special handling can likely be removed once https://github.com/oauthlib/oauthlib/pull/506
                # rolls into a new oauthlib release
                raise TokenExpiredError('Access Token has expired. Please, re-authenticate. '
                                        'Use auto_refresh=True to have your client auto refresh')
            return response.json()
        except (TokenUpdated, TokenExpiredError):
            if self.auto_refresh:
                # Re-fetch token and try request again
                self.fetch_access_token(self.code)
                return request_method(request_url, data=request_data, files=files, params=kwargs, headers=headers).json()
            else:
                self.status_code = 401  # UNAUTHORIZED
                raise TokenExpiredError('Access Token has expired. Please, re-authenticate. '
                                        'Use auto_refresh=True to have your client auto refresh')

    def get(self, path, **kwargs):
        """
            Convenience method for submitting a GET API request via the `request` method
        """
        return self.request(path, method='get', **kwargs)

    def put(self, path, **kwargs):
        """
            Convenience method for submitting a PUT API request via the `request` method
        """
        return self.request(path, method='put', **kwargs)

    def post(self, path, **kwargs):
        """
            Convenience method for submitting a POST API request via the `request` method
        """
        return self.request(path, method='post', **kwargs)

    def delete(self, path, **kwargs):
        """
            Convenience method for submitting a DELETE API request via the `request` method
        """
        return self.request(path, method='delete', **kwargs)

    def activities(self, activity_id=None, **kwargs):
        """
            Fetch platform activity information

            :param activity_id: the id of a specific platform activity that should be retrieved.
                                If omitted, an index listing of activities is returned.  If included
                                other keyword arguments are ignored.

            Keyword arguments that may be used to refine an activity search:

            :param parent_id: The parent activity id of the activities.  This is used to track
                              child activities that are the result of a batch operation.

        """
        path = self.activities_url.format(activity_id if activity_id else '')
        return self.get(path, **kwargs)

    def cash_prices(self, **kwargs):
        """
            Fetch cash price information
        """
        return self.get(self.prices_cash_url, **kwargs)

    def ccd(self, ccd_request):
        """
            Submit a continuity of care document (CCD) request

            :param ccd_request: dictionary representing a CCD request
        """
        return self.post(self.ccd_url, data=ccd_request)

    def claims(self, claims_request):
        """
            Submit a claims request

            :param claims_request: dictionary representing a claims request
        """
        return self.post(self.claims_url, data=claims_request)

    def claims_convert(self, x12_claims_file):
        """
            Submit a raw X12 837 file to convert to a claims API request and map any ICD-9 codes to ICD-10

            :param x12_claims_file: the path to a X12 claims file to be submitted to the platform for processing
        """
        return self.post(self.claims_convert_url, files={
            'file': (os.path.split(x12_claims_file)[-1], open(x12_claims_file, 'rb'), 'application/EDI-X12')
        })

    def claims_status(self, claims_status_request):
        """
            Submit a claims status request

            :param claims_status_request: dictionary representing a claims status request
        """
        return self.post(self.claims_status_url, data=claims_status_request)

    def mpc(self, code=None, **kwargs):
        """
            Access clinical and consumer friendly information related to medical procedures

            :param code: A specific procedure code that should be used to retrieve information

            Keyword arguments that may be used to refine a medical procedure search:

            :param name: Search medical procedure information by consumer friendly name
            :param description: A partial or full description to be used to locate medical procedure information
        """
        path = self.mpc_url.format(code if code else '')
        return self.get(path, **kwargs)

    def icd_convert(self, code):
        """
            Locate the appropriate diagnosis mapping for the specified ICD-9 code

            :param code: A diagnosis code that should be used to retrieve information
        """
        return self.get(self.icd_url.format(code))

    def eligibility(self, eligibility_request):
        """
            Submit an eligibility request

            :param eligibility_request: dictionary representing an eligibility request
        """
        return self.post(self.eligibility_url, data=eligibility_request)

    def enrollment(self, enrollment_request):
        """
            Submit a benefits enrollment/maintenance request

            :param enrollment_request: dictionary representing an enrollment request
        """
        return self.post(self.enrollment_url, data=enrollment_request)

    def enrollment_snapshot(self, trading_partner_id, x12_file):
        """
            Submit a X12 834 file to the platform to establish the enrollment information within it
            as the current membership enrollment snapshot for a trading partner

            :param trading_partner_id: the trading partner associated with the enrollment snapshot
            :param x12_file: the path to a X12 834 file that contains the current membership enrollment information
        """
        return self.post(self.enrollment_snapshot_url, data={'trading_partner_id': trading_partner_id},
                         files={
                             'file': (os.path.split(x12_file)[-1], open(x12_file, 'rb'), 'application/EDI-X12')
                         })

    def enrollment_snapshots(self, snapshot_id=None, **kwargs):
        """
            List enrollment snapshots that are stored for the client application
        """
        path = self.enrollment_snapshot_url
        if snapshot_id:
            path += "/{0}".format(snapshot_id)
        return self.get(path, **kwargs)

    def enrollment_snapshot_data(self, snapshot_id, **kwargs):
        """
            List enrollment request objects that make up the specified enrollment snapshot

            :param snapshot_id: the enrollment snapshot id for the enrollment data
        """
        path = self.enrollment_snapshot_data_url.format(snapshot_id)
        return self.get(path, **kwargs)

    def insurance_prices(self, **kwargs):
        """
            Fetch insurance price information
        """
        return self.get(self.prices_insurance_url, **kwargs)

    def oop_insurance_prices(self, request_data):
        """
        Loads procedure prices for a specific trading partner
        """
        return self.post(self.oop_insurance_price_url, data=request_data)

    def oop_insurance_delete_price(self, load_price_uuid, request_data=None):
        """
        Delete a procedure price for a specific trading partner
        """
        path = "{0}/{1}".format(self.oop_insurance_price_url, str(load_price_uuid))
        return self.delete(path, data=request_data)

    def oop_insurance_estimate(self, request_data):
        """
        Returns estimated out of pocket cost and eligibility information for a given procedure
        """
        return self.post(self.oop_insurance_estimate_url, data=request_data)

    # BACKWARDS COMPATIBILITY AND FEATURE DEPRECATION NOTICE:
    def payers(self, **kwargs):
        """
            Fetch payer information for supported trading partners

        """
        warn(DeprecationWarning('This convenience function will be deprecated '
                                'in an upcoming release. Use trading_partners instead.'), stacklevel=2)
        return self.get('/payers/',  **kwargs)

    def plans(self, **kwargs):
        """
            Fetch insurance plans information
        """
        return self.get(self.plans_url, **kwargs)

    def providers(self, npi=None, **kwargs):
        """
            Search health care providers in the PokitDok directory

            :param npi: The National Provider Identifier for an Individual Provider or Organization
                        When a NPI value is specified, no other parameters will be considered.

            Keyword arguments that may be used to refine a providers search:

            :param address_lines: Any or all of number, street name, apartment, suite number 
            :param zipcode: Zip code to search in
            :param city: City to search in
            :param state: State to search in
            :param radius: A value representing the search distance from a geographic center point
                           May be expressed in miles like: 10mi.  zipcode or city and state must
                           be provided to enable distance sorting with specified radius
            :param first_name: The first name of a provider to include in the search criteria
            :param last_name: The last name of a provider to include in the search criteria
            :param organization_name: The organization_name of a provider.  Do not pass first_name 
                                      or last_name with this argument
            :param limit: The number of provider results that should be included in search results
            :param sort: Accepted values include 'distance' (default) or 'rank'.  'distance' sort 
                         requires city & state or zipcode parameters otherwise sort will be 'rank'.

        """
        path = self.providers_url.format(npi if npi else '')
        return self.get(path, **kwargs)

    def trading_partners(self, trading_partner_id=None):
        """
            Search trading partners in the PokitDok Platform

            :param trading_partner_id: the ID used by PokitDok to uniquely identify a trading partner

            :returns a dictionary containing the specified trading partner or, if called with no arguments, a list of
                     available trading partners
        """
        path = self.trading_partners_url.format(trading_partner_id if trading_partner_id else '')
        return self.get(path)

    def referrals(self, referral_request):
        """
            Submit a referral request
            :param referral_request: dictionary representing a referral request
        """
        return self.post(self.referrals_url, data=referral_request)

    def authorizations(self, authorizations_request):
        """
            Submit an authorization request
            :param authorizations_request: dictionary representing an authorization request
        """
        return self.post(self.authorizations_url, data=authorizations_request)

    def schedulers(self, scheduler_uuid=None):
        """
            Get information about supported scheduling systems or fetch data about a specific scheduling system
            :param scheduler_uuid: The uuid of a specific scheduling system.
        """
        path = self.schedulers_url.format(scheduler_uuid if scheduler_uuid else '')
        return self.get(path)

    def appointment_types(self, appointment_type_uuid=None):
        """
            Get information about appointment types or fetch data about a specific appointment type
            :param appointment_type_uuid: The uuid of a specific appointment type.
        """
        path = self.appointment_types_url.format(appointment_type_uuid if appointment_type_uuid else '')
        return self.get(path)

    def schedule_slots(self, slots_request):
        """
            Submit an open slot for a provider's schedule
            :param slots_request: dictionary representing a slots request
        """
        return self.post(self.schedule_slots_url, data=slots_request)

    def get_appointments(self, appointment_uuid=None, **kwargs):
        """
            Query for open appointment slots or retrieve information for a specific appointment
            :param appointment_uuid: The uuid of a specific appointment.
        """
        path = self.appointments_url.format(appointment_uuid if appointment_uuid else '')
        return self.get(path, **kwargs)

    # BACKWARDS COMPATIBILITY AND FEATURE DEPRECATION NOTICE:
    def appointments(self, appointment_uuid=None, **kwargs):
        warn(DeprecationWarning('This convenience function will be deprecated '
                                'in an upcoming release. Use get_appointments instead.'), stacklevel=2)

        return self.get_appointments(appointment_uuid, **kwargs)

    def book_appointment(self, appointment_uuid, appointment_request):
        """
            Book an appointment
            :param appointment_uuid: The uuid of a specific appointment to be booked.
            :param appointment_request: the appointment request data
        """
        path = self.appointments_url.format(appointment_uuid)
        return self.put(path, data=appointment_request)

    update_appointment = book_appointment

    def cancel_appointment(self, appointment_uuid):
        """
            Cancel an appointment
            :param appointment_uuid: The uuid of a specific appointment.
        """
        path = self.appointments_url.format(appointment_uuid)
        return self.delete(path)

    def create_identity(self, identity_request):
        """
            Creates an identity resource.
            :param identity_request: The dictionary containing the identity request data.
            :returns: The new identity resource.
        """
        return self.post(self.identity_post_url, data=identity_request)

    def update_identity(self, identity_uuid, identity_request):
        """
           Updates an existing identity resource.
           :param identity_uuid: The identity resource's uuid.
           :param identity_request: The updated identity resource.
           :returns: The updated identity resource.
        """
        path = self.identity_put_url.format(identity_uuid)
        return self.put(path, data=identity_request)

    def get_identity(self, identity_uuid=None, **kwargs):
        """
            Queries for an existing identity resource by uuid or for multiple resources using parameters.
            :uuid: The identity resource uuid. Used to execute an exact match query by uuid.
            :kwargs: Additional query parameters using resource fields such as first_name, last_name, email, etc.
            :returns: list containing the search results. A search by uuid returns an empty list or a list containing
            a single identity record.
        """
        path = self.identity_get_url
        if identity_uuid:
            path += '/{0}'.format(identity_uuid)
        return self.get(path, **kwargs)

    # BACKWARDS COMPATIBILITY AND FEATURE DEPRECATION NOTICE:
    def identity(self, identity_uuid=None, **kwargs):
        warn(DeprecationWarning('This convenience function will be deprecated '
                                'in an upcoming release. Use get_identity instead.'), stacklevel=2)

        return self.get_identity(identity_uuid, **kwargs)

    def validate_identity(self, identity_payload):
        """
        Tests the validity of an identity through the Identity Proof api (our knowledge based authentication solution)
        :param identity_payload:
        :return: validation_response
        """
        return self.post(self.identity_proof_valid_url, data=identity_payload)

    def create_proof_questionnaire(self, identity_payload):
        """
        Validates an identity proof request and generates a Knowledge Based Authentication questionnaire if possible
        :return: questionnaire_response
        """
        return self.post(self.identity_proof_generate_url, data=identity_payload)

    def answer_proof_question(self, answer_request):
        """
        Submit a user’s response to a knowledge based authentication question
        :return: the answer response
        """
        return self.post(self.identity_proof_score_url, data=answer_request)

    def identity_history(self, identity_uuid, historical_version=None):
        """
            Queries for an identity record's history.
            Returns a history summary including the insert date and version number or a specific record version, if
            the historical_version argument is provided.
            :param identity_uuid: The identity resource's uuid.
            :param historical_version: The historical version id. Used to return a historical identity record
            :return: history result (list)
        """
        path = self.identity_history_url.format(self.url_base, str(identity_uuid))

        if historical_version is not None:
            path = "{0}/{1}".format(path, historical_version)

        return self.api_client.get(path, headers=self.base_headers).json()

    def identity_match(self, identity_match_data):
        """
            Creates an identity match job.
            :param identity_match_data: The dictionary containing the identity match data.
            :returns: An activity id of the identity match job
        """
        return self.post(self.identity_match_url, data=identity_match_data)

    def pharmacy_plans(self, **kwargs):
        """
            Search drug plan information by trading partner and various plan identifiers

            :param kwargs: pharmacy plans API request parameters
            :return: drug plan information if a match is found
        """
        return self.get(self.pharmacy_plans_url, **kwargs)

    def pharmacy_formulary(self, **kwargs):
        """
            Search drug plan formulary information to determine if a drug is covered by the specified
            drug plan.

            :param kwargs: pharmacy formulary API request parameters
            :return: formulary information if a match is found
        """
        return self.get(self.pharmacy_formulary_url, **kwargs)

    def pharmacy_network(self, npi=None, **kwargs):
        """
            Search for in-network pharmacies

            :param npi: The National Provider Identifier for a pharmacy
            :param kwargs: pharmacy network API request parameters
            :return: If an NPI is included in the request, details about the pharmacy are returned.
            Otherwise, a list of in-network pharmacies is returned.
        """
        path = self.pharmacy_network_url
        if npi:
            path += '/{0}'.format(npi)
        return self.get(path, **kwargs)
