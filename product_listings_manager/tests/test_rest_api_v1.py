import pytest

from mock import patch

from product_listings_manager.app import app

# Flask < 1.0 does not have get_json.
from flask import Response
import json
if not hasattr(Response, 'get_json'):
    def get_json(self, force=False, silent=False, cache=True):
        """ Minimal implementation we can use this in the tests. """
        return json.loads(self.data)
    Response.get_json = get_json


@pytest.yield_fixture
def client():
    client = app.test_client()
    yield client


class TestAbout(object):
    def test_get_version(self, client):
        from product_listings_manager import __version__
        r = client.get('/api/v1.0/about')
        assert r.status_code == 200
        assert r.get_json() == {'version': __version__}


class TestProductInfo(object):
    product_label = 'RHEL-6-Server-EXTRAS-6'
    product_info_data = ['6.9', ['EXTRAS-6']]

    @patch('product_listings_manager.products.getProductInfo', return_value=product_info_data)
    def test_get_product_info(self, mock_get_product_info, client):
        path = '/api/v1.0/product-info/{0}'.format(self.product_label)
        r = client.get(path)
        assert r.status_code == 200
        assert r.get_json() == mock_get_product_info.return_value


class TestProductListings(object):
    product_label = 'RHEL-6-Server-EXTRAS-6'
    nvr = 'dumb-init-1.2.0-1.20170802gitd283f8a.el6'
    product_listings_data = {
        'EXTRAS-6': {
            nvr: {
                'src': ['x86_64'], 'x86_64': ['x86_64']
            }
        }
    }

    @patch('product_listings_manager.products.getProductListings', return_value=product_listings_data)
    def test_get_product_listings(self, mock_get_product_listings, client):
        path = '/api/v1.0/product-listings/{0}/{1}'.format(self.product_label, self.nvr)
        r = client.get(path)
        assert r.status_code == 200
        assert r.get_json() == mock_get_product_listings.return_value
