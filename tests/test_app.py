import pytest
import requests


url = 'http://0.0.0.0:5000'


def test_index():
    r = requests.get(url + '/')
    assert r.status_code == 200
