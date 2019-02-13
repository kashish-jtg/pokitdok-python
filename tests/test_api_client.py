from __future__ import absolute_import

import pokitdok
import copy
from tests import client_settings


class TestAPIClient(object):
    """
    Validates that PokitDok API client requests are well formed.
    Httmock (https://pypi.python.org/pypi/httmock/) is used to provide mock HTTP responses.
    """
    ASSERTION_EQ_MSG = 'Expected {} != Actual {}'
    def __init__(self):
        """
            Defines instance attributes used in test cases
            - pd_client = PokitDok API client instance
            - current_request = The requests request object for the current test case request
        """
        self.pd_client = pokitdok.api.connect(**client_settings)

    #
    # ******************************
    # client set up tests
    # ******************************
    #
    def assert_helper(self, response, status_code):
        """
        helper function for assert statement pattern
        :param response_payload: the payload to test
        :param status_code: the expected status code
        """
        assert response["meta"] is not None, "The meta section is unexpectedly empty. Full reponse: {}" .format(str(response))
        assert response["data"] is not None, "The data section is unexpectedly empty. Full reponse: {}" .format(str(response))
        assert self.pd_client.status_code == status_code, str(response)

    def test_connect(self):
        """
        tests the basic init of the client
        :return:
        """
        assert self.pd_client.api_client is not None, "The api client was not initialized."
        assert self.pd_client.api_client.token is not None, "The api client was not initialized."
        assert "pokitdok-python" in self.pd_client.base_headers["User-Agent"],\
            self.ASSERTION_EQ_MSG.format("pokitdok-python", self.pd_client.base_headers)

    def test_connect_existing_token(self):
        """
            Tests pokitdok.api.connect (PokitDok.__init__()) with an existing token
            Validates that the API client instantiation supports an existing token
        """
        self.pd_client = pokitdok.api.connect(**client_settings)
        first_token = copy.deepcopy(self.pd_client.token)

        self.pd_client = pokitdok.api.connect(token=first_token, **client_settings)
        second_token = copy.deepcopy(self.pd_client.token)
        # first token should be equal to the second
        assert first_token == second_token, "The tokens do not match"

        # validate unique tokens for new client instances
        self.pd_client = pokitdok.api.connect(**client_settings)
        third_token = copy.deepcopy(self.pd_client.token)
        assert third_token not in [first_token, second_token], "The tokens are not unique"

    #
    # ******************************
    # error tests
    # ******************************
    #

    def test_http_error_400(self):
        """
        Error Test: test for an expected 400 response via a missing trading_partner id
        """
        self.pd_client = pokitdok.api.connect(**client_settings)
        request = {
            "member": {
                "birth_date": "1970-01-25",
                "first_name": "Jane",
                "last_name": "Doe",
                "id": "W000000000"
            },
            "provider": {
                "first_name": "JEROME",
                "last_name": "AYA-AY",
                "npi": "1467560003"
            },
        }
        response = self.pd_client.eligibility(request)
        self.assert_helper(response, 400)

    def test_http_error_422(self):
        """
        Error Test: test for an expected 422 response via different types of bad requests
        """
        self.pd_client = pokitdok.api.connect(**client_settings)
        request = "bad request"
        response = self.pd_client.eligibility(request)
        self.assert_helper(response, 422)

        request = {
            "member": {
                "birth_date": "1970-01-25",
                "first_name": "Jane",
                "last_name": "Doe",
                "id": "1"
            },
            "trading_partner_id": 'MOCKPAYER'
        }
        response = self.pd_client.eligibility(request)
        self.assert_helper(response, 422)

        request = {
            "member": {
                "birth_date": "1970-01-25",
                "first_name": "Jane",
                "last_name": "Doe",
                "id": "W000000000"
            },
            "provider": {
                "first_name": "JEROME",
                "last_name": "AYA-AY",
                "npi": "3"
            },
            "trading_partner_id": 'MOCKPAYER'
        }
        response = self.pd_client.eligibility(request)
        self.assert_helper(response, 422)

    #
    # ******************************
    # get/post/put tests
    # ******************************
    #
    #
    def test_post(self):
        """
        POST Test
        """
        self.pd_client = pokitdok.api.connect(**client_settings)
        request = {
            "member": {
                "birth_date": "1970-01-25",
                "first_name": "Jane",
                "last_name": "Doe",
                "id": "W000000000"
            },
            "provider": {
                "first_name": "JEROME",
                "last_name": "AYA-AY",
                "npi": "1467560003"
            },
            "trading_partner_id": "MOCKPAYER"
        }
        response = self.pd_client.request(self.pd_client.eligibility_url, method='post', data=request)
        self.assert_helper(response, 200)

    def test_put_delete_claims_activities(self):
        """
            Exercise the workflow of submitting a and deleting a claim'
        """
        test_claim = {
            "transaction_code": "chargeable",
            "trading_partner_id": "MOCKPAYER",
            "billing_provider": {
                "taxonomy_code": "207Q00000X",
                "first_name": "Jerome",
                "last_name": "Aya-Ay",
                "npi": "1467560003",
                "address": {
                    "address_lines": [
                        "8311 WARREN H ABERNATHY HWY"
                    ],
                    "city": "SPARTANBURG",
                    "state": "SC",
                    "zipcode": "29301"
                },
                "tax_id": "123456789"
            },
            "subscriber": {
                "first_name": "Jane",
                "last_name": "Doe",
                "member_id": "W000000000",
                "address": {
                    "address_lines": ["123 N MAIN ST"],
                    "city": "SPARTANBURG",
                    "state": "SC",
                    "zipcode": "29301"
                },
                "birth_date": "1970-01-25",
                "gender": "female"
            },
            "claim": {
                "total_charge_amount": 60.0,
                "service_lines": [
                    {
                        "procedure_code": "99213",
                        "charge_amount": 60.0,
                        "unit_count": 1.0,
                        "diagnosis_codes": [
                            "J10.1"
                        ],
                        "service_date": "2016-01-25"
                    }
                ]
            }
        }
        # assert success of the claim post
        response = self.pd_client.claims(test_claim)
        self.assert_helper(response, 200)

        # use the activities endpoint via a GET to analyze the current status of this claim
        activity_id = response["meta"]["activity_id"]
        activity_url = "/activities/" + activity_id
        get_response = self.pd_client.request(activity_url, method='get', data={})
        self.assert_helper(response, 200)

        # look in the history to see if it has transitioned from state "init" to "canceled"
        history = get_response["data"]["history"]
        if len(history) != 1:
            # this means that the claim is been picked up and is processing within the internal pokitdok system
            # we aim to test out the put functionality by deleting the claim,
            # so we need to resubmit a claim to get one that is going to stay in the INIT stage
            response = self.pd_client.claims(test_claim)
            self.assert_helper(response, 200)
            activity_id = response["meta"]["activity_id"]
            activity_url = "/activities/" + activity_id

        # exercise the PUT functionality to delete the claim from its INIT status
        put_response = self.pd_client.request(activity_url, method='put', data={"transition": "cancel"})
        self.assert_helper(response, 200)

        # look in the history to see if it has transitioned from state "init" to "canceled"
        history = put_response["data"]["history"]
        assert len(history) > 2, "Tested for cancelled claim, but recived the following claim history: {}".format(str(history))

        # exercise the PUT functionality to delete an already deleted claim
        put_response = self.pd_client.request(activity_url, method='put', data={"transition": "cancel"})
        assert put_response["data"]["errors"] is not None, "Expected an errors section and it is missing. Full response: {}".format(str(response))
        assert self.pd_client.status_code == 422, self.ASSERTION_EQ_MSG.format("422", self.pd_client.status_code)

        # exercise the activities endpoint to get the status of this claims transaction
        assert activity_id in activity_url, 'Expected {} to be within {}'.format(activity_id, activity_url)
        activities_response = self.pd_client.activities(activity_id)
        self.assert_helper(response, 200)
    #
    # ******************************
    # X12 API tests
    # ******************************
    #

    def test_claims_status(self):
        """
        X12 API Convenience function test: claims_status
        make a call to the live endpoint for: claims_status
        """
        request = {
            "patient": {
                "birth_date": "1970-01-25",
                "first_name": "JANE",
                "last_name": "DOE",
                "id": "1234567890"
            },
            "provider": {
                "first_name": "Jerome",
                "last_name": "Aya-Ay",
                "npi": "1467560003"
            },
            "service_date": "2014-01-25",
            "trading_partner_id": "MOCKPAYER"
        }
        response = self.pd_client.claims_status(request)
        self.assert_helper(response, 200)

    def test_claims_convert(self):
        """
        X12 API Convenience function test: claims_convert
        make a call to the live endpoint for: claims_convert
        """
        request = "tests/chiropractic_example.837"
        response = self.pd_client.claims_convert(request)
        self.assert_helper(response, 200)

    def test_eligibility(self):
        """
        X12 API Convenience function test: eligibility
        make a call to the live endpoint for: eligibility
        """
        request = {
            "member": {
                "birth_date": "1970-01-25",
                "first_name": "Jane",
                "last_name": "Doe",
                "id": "W000000000"
            },
            "provider": {
                "first_name": "JEROME",
                "last_name": "AYA-AY",
                "npi": "1467560003"
            },
            "trading_partner_id": "MOCKPAYER"
        }
        response = self.pd_client.eligibility(request)
        self.assert_helper(response, 200)

    #
    # ******************************
    # Data API tests
    # ******************************
    #

    def test_cash_prices(self):
        """
        Data API Convenience function test: cash_prices
        make a call to the live endpoint for: cash_prices
        """
        response = self.pd_client.cash_prices(zip_code='29412', cpt_code='99385')
        self.assert_helper(response, 200)
        assert type(response["data"]) is list, self.ASSERTION_EQ_MSG.format("list", type(response["data"]))
        assert type(response["meta"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["meta"]))

    def test_icd_convert(self):
        """
        Data API Convenience function test: icd_convert
        make a call to the live endpoint for: icd_convert
        """
        response = self.pd_client.icd_convert('250.12')
        self.assert_helper(response, 200)
        assert type(response["data"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["data"]))
        assert type(response["meta"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["meta"]))

    def test_mpc(self):
        """
        Data API Convenience function test: mpc
        make a call to the live endpoint for: mpc
        """
        response = self.pd_client.mpc(code='99213')
        self.assert_helper(response, 200)
        assert type(response["data"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["data"]))
        assert type(response["meta"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["meta"]))

    def test_insurance_prices(self):
        """
        Data API Convenience function test: insurance_prices
        make a call to the live endpoint for: insurance_prices
        """
        response = self.pd_client.insurance_prices(zip_code='94401', cpt_code='90658')
        self.assert_helper(response, 200)
        assert type(response["data"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["data"]))
        assert type(response["meta"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["meta"]))

    def test_oop_insurance_prices(self):
        """
        Data API Convenience function test: oop_insurance_prices
        make a call to the live endpoint for: oop_insurance_prices
        """
        request = {
            "trading_partner_id": "MOCKPAYER",
            "cpt_bundle": ["81291", "99999"],
            "price": {
                "amount": "1300",
                "currency": "USD"
            }
        }
        response = self.pd_client.oop_insurance_prices(request_data=request)
        self.assert_helper(response, 200)
        assert type(response["data"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["data"]))
        assert type(response["meta"]) is dict, self.ASSERTION_EQ_MSG.format("dict", str(response))
        load_uuid = response['data']['uuid']

        # test oop insurance estimate from loaded data
        request = {
            "trading_partner_id":"MOCKPAYER",
            "cpt_bundle": ["99999", "81291"],
            "service_type_codes": ["30"],
            "eligibility": {
                "provider": {
                    "npi": "1912301953",
                    "organization_name": "PokitDok, Inc"
                },
                "member": {
                    "birth_date": "1975-04-26",
                    "first_name": "Joe",
                    "last_name": "Immortan",
                    "id": "999999999"
                }
            }
        }
        response = self.pd_client.oop_insurance_estimate(request)
        self.assert_helper(response, 200)
        assert type(response["data"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["data"]))
        assert type(response["meta"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["meta"]))

        # test the deletion of the loaded data
        response = self.pd_client.oop_insurance_delete_price(load_price_uuid=load_uuid)
        self.assert_helper(response, 200)
        assert type(response["data"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["data"]))
        assert type(response["meta"]) is dict, self.ASSERTION_EQ_MSG.format("dict", str(response))

    def test_plans(self):
        """
        Data API Convenience function test: plans
        make a call to the live endpoint for: plans
        """
        response = self.pd_client.plans(state='SC', plan_type='PPO')
        self.assert_helper(response, 200)
        assert type(response["data"]) is list, self.ASSERTION_EQ_MSG.format("list", type(response["data"]))
        assert type(response["meta"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["meta"]))

    def test_providers(self):
        """
        Data API Convenience function test: providers
        make a call to the live endpoint for: providers
        """
        response = self.pd_client.providers(npi='1467560003')
        self.assert_helper(response, 200)
        assert type(response["data"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["data"]))
        assert type(response["meta"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["meta"]))

    def test_trading_partners(self):
        """
        Data API Convenience function test: trading_partners
        make a call to the live endpoint for: trading_partners
        """
        response = self.pd_client.trading_partners('aetna')
        self.assert_helper(response, 200)
        assert type(response["data"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["data"]))
        assert type(response["meta"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["meta"]))

    #
    # ******************************
    # Pharmacy API Convenience Functions
    # ******************************
    #

    def test_pharmacy_plans(self):
        """
        Pharmacy API Convenience function test: pharmacy_plans
        make a call to the live endpoint for: pharmacy_plans
        """
        response = self.pd_client.pharmacy_plans(trading_partner_id='medicare_national', plan_number='S5820003')
        self.assert_helper(response, 200)
        assert type(response["data"]) is list, self.ASSERTION_EQ_MSG.format("list", type(response["data"]))
        assert type(response["meta"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["meta"]))

    def test_pharmacy_formulary(self):
        """
        Pharmacy API Convenience function test: pharmacy_formulary
        make a call to the live endpoint for: pharmacy_formulary
        """
        response = self.pd_client.pharmacy_formulary(trading_partner_id='medicare_national', plan_number='S5820003', drug='simvastatin')
        self.assert_helper(response, 200)
        assert type(response["data"]) is list, self.ASSERTION_EQ_MSG.format("list", type(response["data"]))
        assert type(response["meta"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["meta"]))

    def test_pharmacy_network(self):
        """
        Pharmacy API Convenience function test: pharmacy_network
        make a call to the live endpoint for: pharmacy_network
        """
        response = self.pd_client.pharmacy_network(npi='1427382266', trading_partner_id='medicare_national', plan_number='S5820003')
        self.assert_helper(response, 200)
        assert type(response["data"]) is list, self.ASSERTION_EQ_MSG.format("list", type(response["data"]))
        assert type(response["meta"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["meta"]))

    #
    # ******************************
    # identity tests
    # ******************************
    #

    def test_validate_identity(self):
        """
        Pharmacy API Convenience function test: validate_identity
        make a call to the live endpoint for: validate_identity
        """
        request = {
            "first_name": 'Duard',
            "last_name": 'Osinski',
            "birth_date": {
                "day": 12,
                "month": 3,
                "year": 1952
            },
            "ssn": '491450000',
            "address": {
                "city": 'North Perley',
                "country_code": 'US',
                "postal_code": '24330',
                "state_or_province": 'GA',
                "street1": '41072 Douglas Terrace ',
                "street2": 'Apt. 992'
            }
        }
        response = self.pd_client.validate_identity(request)
        self.assert_helper(response, 200)
        assert type(response["data"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["data"]))
        assert type(response["meta"]) is dict, self.ASSERTION_EQ_MSG.format("dict", type(response["meta"]))

