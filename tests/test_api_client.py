from __future__ import absolute_import

import os
import pokitdok
from unittest import TestCase
import vcr


# Fake client id/secret for local testing
CLIENT_ID = 'oB7rLIqHmdoAXHRAmWtM'
CLIENT_SECRET = 'ZE8xqtUY5kYqmHIhd8lzdjqD1CPa8sRBPvmF9UuG'
BASE_URL = 'http://localhost:5002'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

pd_vcr = vcr.VCR(
    cassette_library_dir='tests/fixtures/vcr_cassettes',
    record_mode='once',
    filter_headers=['authorization']
)


class TestAPIClient(TestCase):
    def setUp(self):
        with pd_vcr.use_cassette('access_token.yml'):
            self.pd = pokitdok.api.connect(CLIENT_ID, CLIENT_SECRET, base=BASE_URL)
            assert isinstance(self.pd, pokitdok.api.PokitDokClient)

    def test_activities(self):
        with pd_vcr.use_cassette('activities.yml'):
            activities_response = self.pd.activities()
            assert "meta" in activities_response
            assert "data" in activities_response

    def test_eligibility(self):
        with pd_vcr.use_cassette('eligibility.yml'):
            eligibility_response = self.pd.eligibility({
                "member": {
                    "birth_date": "1970-01-01",
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "id": "W000000000"
                },
                "provider": {
                    "first_name": "JEROME",
                    "last_name": "AYA-AY",
                    "npi": "1467560003"
                },
                "service_types": ["health_benefit_plan_coverage"],
                "trading_partner_id": "MOCKPAYER"
            })
            assert "meta" in eligibility_response
            assert "data" in eligibility_response
            assert len(eligibility_response['data']['coverage']['deductibles']) == 8

    def test_payers(self):
        with pd_vcr.use_cassette('payers.yml'):
            payers_response = self.pd.payers()
            assert "meta" in payers_response
            assert "data" in payers_response
            for payer in payers_response['data']:
                assert 'trading_partner_id' in payer

    def test_plans(self):
        with pd_vcr.use_cassette('plans.yml'):
            plans_response = self.pd.plans(state='TX', plan_type='EPO')
            assert "meta" in plans_response
            assert "data" in plans_response
            for plan in plans_response['data']:
                assert plan['state'] == 'TX'
                assert plan['plan_type'] == 'EPO'
                assert 'trading_partner_id' in plan

    def test_providers_with_id(self):
        with pd_vcr.use_cassette('providers_id.yml'):
            providers_response = self.pd.providers(npi='1467560003')
            assert "meta" in providers_response
            assert "data" in providers_response
            assert providers_response['data']['provider']['last_name'] == 'AYAAY'

    def test_cash_prices_zip_and_cpt(self):
        with pd_vcr.use_cassette('cash_prices_zip_cpt.yml'):
            prices_response = self.pd.cash_prices(zip_code='94101', cpt_code='95017')
            assert "meta" in prices_response
            assert "data" in prices_response
            assert prices_response['data'] == [
                {
                    'average_price': 299.11868972705673,
                    'cpt_code': '95017',
                    'geo_zip_area': '941',
                    'high_price': 424.72616491010086,
                    'low_price': 60.04033765355346,
                    'median_price': 290.34018519305926,
                    'standard_deviation': 85.05257902012636
                }
            ]

    def test_insurance_prices_zip_and_cpt(self):
        with pd_vcr.use_cassette('insurance_prices_zip_cpt.yml'):
            prices_response = self.pd.insurance_prices(zip_code='32218', cpt_code='87799')
            assert "meta" in prices_response
            assert "data" in prices_response
            assert prices_response['data'] == {
                'amounts': [
                    {
                        'average_price': 54.5895,
                        'high_price': 159.75,
                        'low_price': 19.98,
                        'median_price': 56.25,
                        'payer_type': 'insurance',
                        'payment_type': 'allowed',
                        'standard_deviation': 36.41382675904168
                    },
                    {
                        'average_price': 104.77350000000001,
                        'high_price': 188.91,
                        'low_price': 88.02,
                        'median_price': 97.02,
                        'payer_type': 'insurance',
                        'payment_type': 'submitted',
                        'standard_deviation': 26.57623445180863
                    },
                    {
                        'average_price': 82.336343612,
                        'payer_type': 'medicare',
                        'payment_type': 'allowed'
                    },
                    {
                        'average_price': 100.28768722,
                        'payer_type': 'medicare',
                        'payment_type': 'submitted'
                    },
                    {
                        'average_price': 57.623480175999994,
                        'payer_type': 'medicare',
                        'payment_type': 'paid'
                    }
                ],
                'cpt_code': '87799',
                'geo_zip_area': '322'
            }

    def test_claim_status(self):
        with pd_vcr.use_cassette('claim_status.yml'):
            claim_status_response = self.pd.claims_status({
                "patient": {
                    "birth_date": "1970-01-01",
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "id": "W000000000"
                },
                "provider": {
                    "first_name": "JEROME",
                    "last_name": "AYA-AY",
                    "npi": "1467560003"
                },
                "service_date": "2014-01-01",
                "trading_partner_id": "MOCKPAYER"
            })
            assert "meta" in claim_status_response
            assert "data" in claim_status_response
            assert claim_status_response['data']['patient'] == {
                'claims': [
                    {
                        'applied_to_deductible': False,
                        'total_claim_amount': {'currency': 'USD', 'amount': '150'},
                        'service_end_date': '2014-01-01',
                        'claim_control_number': 'E1TWCYYMF00',
                        'check_number': '08608-035632423',
                        'claim_payment_amount': {'currency': 'USD', 'amount': '125'},
                        'adjudication_finalized_date': '2014-03-21',
                        'tracking_id': 'E1TWCYYMF',
                        'services': [
                            {
                                'cpt_code': '99214',
                                'service_end_date': '2014-03-05',
                                'payment_amount': {'currency': 'USD', 'amount': '125'},
                                'charge_amount': {'currency': 'USD', 'amount': '150'},
                                'service_date': '2014-03-05',
                                'statuses': [
                                    {
                                        'status_code': 'Processed according to contract provisions (Contract refers to provisions that exist between the Health Plan and a Provider of Health Care Services)',
                                        'status_effective_date': '2014-04-24',
                                        'status_category': 'Finalized/Payment-The claim/line has been paid.'
                                    }
                                ]
                            }
                        ],
                        'remittance_date': '2014-04-09',
                        'service_date': '2014-01-01',
                        'statuses': [
                            {
                                'total_claim_amount': {'currency': 'USD', 'amount': '150'},
                                'status_category': 'Finalized/Payment-The claim/line has been paid.',
                                'status_code': 'Processed according to contract provisions (Contract refers to provisions that exist between the Health Plan and a Provider of Health Care Services)',
                                'claim_payment_amount': {'currency': 'USD', 'amount': '125'},
                                'adjudication_finalized_date': '2014-03-21',
                                'remittance_date': '2014-04-09',
                                'check_number': '08608-035632423',
                                'status_effective_date': '2014-04-24'
                            }
                        ]
                    }
                ]
            }

    def test_trading_partners(self):
        with pd_vcr.use_cassette('trading_partners.yml'):
            trading_partner_response = self.pd.trading_partners("MOCKPAYER")
            assert "meta" in trading_partner_response
            assert "data" in trading_partner_response
            assert trading_partner_response['data'].get('id') == "MOCKPAYER"
            assert trading_partner_response['data'].get('name') == "Mock Payer for Testing"

    def test_referrals(self):
        with pd_vcr.use_cassette('referrals.yml'):
            response = self.pd.referrals({
                "event": {
                    "category": "specialty_care_review",
                    "certification_type": "initial",
                    "delivery": {
                        "quantity": 1,
                        "quantity_qualifier": "visits"
                    },
                    "diagnoses": [
                        {
                            "code": "384.20",
                            "date": "2014-09-30"
                        }
                    ],
                    "place_of_service": "office",
                    "provider": {
                        "first_name": "JOHN",
                        "npi": "1154387751",
                        "last_name": "FOSTER",
                        "phone": "8645822900"
                    },
                    "type": "consultation"
                },
                "patient": {
                    "birth_date": "1970-01-01",
                    "first_name": "JANE",
                    "last_name": "DOE",
                    "id": "1234567890"
                },
                "provider": {
                    "first_name": "CHRISTINA",
                    "last_name": "BERTOLAMI",
                    "npi": "1619131232"
                },
                "trading_partner_id": "MOCKPAYER"
            })
            assert "meta" in response
            assert "data" in response
            assert response['data']['event']['review']['certification_number'] == 'AUTH0001'
            assert response['data']['event']['review']['certification_action'] == 'certified_in_total'

    def test_authorizations(self):
        with pd_vcr.use_cassette('authorizations.yml'):
            response = self.pd.authorizations({
                "event": {
                    "category": "health_services_review",
                    "certification_type": "initial",
                    "delivery": {
                        "quantity": 1,
                        "quantity_qualifier": "visits"
                    },
                    "diagnoses": [
                        {
                            "code": "789.00",
                            "date": "2014-10-01"
                        }
                    ],
                    "place_of_service": "office",
                    "provider": {
                        "organization_name": "KELLY ULTRASOUND CENTER, LLC",
                        "npi": "1760779011",
                        "phone": "8642341234"
                    },
                    "services": [
                        {
                            "cpt_code": "76700",
                            "measurement": "unit",
                            "quantity": 1
                        }
                    ],
                    "type": "diagnostic_imaging"
                },
                "patient": {
                    "birth_date": "1970-01-01",
                    "first_name": "JANE",
                    "last_name": "DOE",
                    "id": "1234567890"
                },
                "provider": {
                    "first_name": "JEROME",
                    "npi": "1467560003",
                    "last_name": "AYA-AY"
                },
                "trading_partner_id": "MOCKPAYER"
            })
            assert "meta" in response
            assert "data" in response
            assert response['data']['event']['review']['certification_number'] == 'AUTH0001'
            assert response['data']['event']['review']['certification_action'] == 'certified_in_total'

