import pytest
import requests

url = 'http://0.0.0.0:5000'

def test_api_ocr_page():
    r = requests.get(url + '/api/ocr')
    assert r.status_code == 200
