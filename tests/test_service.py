import responses

from fastapi.testclient import TestClient

import service.main
from service.main import app, ID_LOOKUP_BASE_URL, TAG_LOOKUP_BASE_URL


client = TestClient(app)
service.main.API_KEY = "dummy"


@responses.activate
def test_get_clan_tag_endpoint_success():
    responses.add(
        responses.GET,
        ID_LOOKUP_BASE_URL.format(api_key="dummy", clan_tag="EXAMPLE"),
        json={"status": "ok", "meta": {"count": 1, "total": 1}, "data": [{"clan_id": 5000000, "tag": "EXAMPLE"}]},
        status=200,
    )

    response = client.get("/clan/tag/EXAMPLE")
    assert response.status_code == 200
    assert response.json() == {"clan_tag": "EXAMPLE", "clan_id": 5000000}


@responses.activate
def test_get_clan_tag_endpoint_api_error():
    responses.add(
        responses.GET,
        ID_LOOKUP_BASE_URL.format(api_key="dummy", clan_tag="EXAMPLE"),
        json={"status": "error", "error": {"message": "TEST_API_ERROR"}},
        status=200,
    )

    response = client.get("/clan/tag/EXAMPLE")
    assert response.status_code == 400
    assert response.json() == {"detail": "API Request responded with an error: TEST_API_ERROR"}


@responses.activate
def test_get_clan_tag_endpoint_api_not_found():
    responses.add(
        responses.GET,
        ID_LOOKUP_BASE_URL.format(api_key="dummy", clan_tag="EXAMPLE"),
        json={"status": "ok", "data": []},
        status=200,
    )

    response = client.get("/clan/tag/EXAMPLE")
    assert response.status_code == 404
    assert response.json() == {"detail": "No clan was found for this id: EXAMPLE"}


@responses.activate
def test_get_clan_tag_endpoint_unexpected_error():
    responses.add(
        responses.GET, ID_LOOKUP_BASE_URL.format(api_key="dummy", clan_tag="EXAMPLE"), json={"status": "ok"}, status=200
    )

    response = client.get("/clan/tag/EXAMPLE")
    assert response.status_code == 400
    assert response.json() == {"detail": "An Exception was raised during the api request. KeyError: data."}


@responses.activate
def test_get_clan_id_endpoint_success():
    responses.add(
        responses.GET,
        TAG_LOOKUP_BASE_URL.format(api_key="dummy", clan_id=5000000),
        json={"status": "ok", "meta": {"count": 1}, "data": {"5000000": {"tag": "EXAMPLE"}}},
        status=200,
    )

    response = client.get("/clan/id/5000000")
    assert response.status_code == 200
    assert response.json() == {"clan_tag": "EXAMPLE", "clan_id": 5000000}


@responses.activate
def test_get_clan_id_endpoint_api_error():
    responses.add(
        responses.GET,
        TAG_LOOKUP_BASE_URL.format(api_key="dummy", clan_id=5000000),
        json={"status": "error", "error": {"message": "TEST_API_ERROR"}},
        status=200,
    )

    response = client.get("/clan/id/5000000")
    assert response.status_code == 400
    assert response.json() == {"detail": "API Request responded with an error: TEST_API_ERROR"}


@responses.activate
def test_get_clan_id_endpoint_api_not_found():
    responses.add(
        responses.GET,
        TAG_LOOKUP_BASE_URL.format(api_key="dummy", clan_id=5000000),
        json={"status": "ok", "data": {"5000000": {"tag": None}}},
        status=200,
    )

    response = client.get("/clan/id/5000000")
    assert response.status_code == 404
    assert response.json() == {"detail": "No clan was found for this id: 5000000"}


@responses.activate
def test_get_clan_id_endpoint_unexpected_error():
    responses.add(
        responses.GET, TAG_LOOKUP_BASE_URL.format(api_key="dummy", clan_id=5000000), json={"status": "ok"}, status=200
    )

    response = client.get("/clan/id/5000000")
    assert response.status_code == 400
    assert response.json() == {"detail": "An Exception was raised during the api request. KeyError: data."}
