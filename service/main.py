"""This file contains the fastapi app and all functions for this small microservice."""
import os

import fastapi
import requests
from pydantic import BaseModel

API_KEY: str = os.getenv("API_KEY")  # type: ignore
TAG_LOOKUP_BASE_URL = (
    "https://api.worldoftanks.eu/wot/clans/info/?application_id={api_key}&fields=tag&clan_id={clan_id}"
)
ID_LOOKUP_BASE_URL = (
    "https://api.worldoftanks.eu/wot/clans/list/?application_id={api_key}&search={clan_tag}&fields=clan_id%2C+tag"
)
TIMEOUT = 5

app = fastapi.FastAPI()


class ClanModel(BaseModel):
    """Base Pydantic Model to represent the most import data for a single clan."""
    clan_id: int
    clan_tag: str


def api_get_clan_by_id(clan_id: int, api_key: str) -> tuple[ClanModel, None] | tuple[None, str]:
    """
    Look up the clan tag for a given clan id in the wargaming clan api.
    :param clan_id: clan id to lookup clan tag for
    :param api_key: valid api key for WG-api
    :return: ClanModel and None if the clan could be identified by the clan id else None and an error message
    """
    request_url = TAG_LOOKUP_BASE_URL.format(clan_id=clan_id, api_key=api_key)
    try:
        response = requests.get(request_url, timeout=TIMEOUT)
        response.raise_for_status()
        response_json = response.json()
        if response_json["status"] != "ok":
            return None, f"API Request responded with an error: {response_json['error']['message']}"
        tag = response_json["data"][str(clan_id)]["tag"]
        if not tag:
            return None, f"No clan was found for this id: {clan_id}"
        return ClanModel(clan_id=clan_id, clan_tag=tag), None
    # TODO specific error handling
    except Exception as error:  # pylint: disable=broad-except
        return None, f"An Exception was raised during the api request. {error.__class__.__name__}: {error.args[0]}."


def api_get_clan_by_tag(clan_tag: str, api_key: str) -> tuple[ClanModel, None] | tuple[None, str]:
    """
    Look up the clan tag for a given clan tag in the wargaming clan api.
    :param clan_tag: clan tag to lookup clan id for
    :param api_key: valid api key for WG-api
    :return: ClanModel and None if the clan could be identified by the clan tag else None and an error message
    """
    request_url = ID_LOOKUP_BASE_URL.format(clan_tag=clan_tag, api_key=api_key)
    try:
        response = requests.get(request_url, timeout=TIMEOUT)
        response.raise_for_status()
        response_json = response.json()
        if response_json["status"] != "ok":
            return None, f"API Request responded with an error: {response_json['error']['message']}"
        valid_responses = [result for result in response_json["data"] if result["tag"] == clan_tag]
        if len(valid_responses) == 0:
            return None, f"No clan was found for this id: {clan_tag}"
        return ClanModel(clan_id=valid_responses[0]["clan_id"], clan_tag=clan_tag), None
    # TODO specific error handling
    except Exception as error:  # pylint: disable=broad-except
        return None, f"An Exception was raised during the api request. {error.__class__.__name__}: {error.args[0]}."


@app.get(
    "/clan/tag/{clan_tag}",
    response_model=ClanModel,
    responses={
        400: {"description": "Error in Request: Request could not be answered successful."},
        404: {"description": "Missing ressource: No clan was found for the requested tag."},
    },
    description="Returns clan id and clan tag for the requested clan.",
)
def get_clan_id(clan_tag: str) -> ClanModel:
    """
    api endpoint to look up the clan id.
    :param clan_tag: clan tag to search for
    :return: ClanModel on success else error code + message
    """
    result, err = api_get_clan_by_tag(clan_tag=clan_tag.upper(), api_key=API_KEY)
    if err and "No clan was found" in err:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail=err)
    if err or result is None:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail=err)
    return result


@app.get(
    "/clan/id/{clan_id}",
    response_model=ClanModel,
    responses={
        400: {"description": "Error in Request: Request could not be answered successful."},
        404: {"description": "Missing ressource: No clan was found for the requested id."},
    },
    description="Returns clan id and clan tag for the requested clan.",
)
def get_clan_tag(clan_id: int) -> ClanModel:
    """
    api endpoint to look up the clan tag.
    :param clan_id: clan id to search for
    :return: ClanModel on success else error code + message
    """
    result, err = api_get_clan_by_id(clan_id=clan_id, api_key=API_KEY)
    if err and "No clan was found" in err:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail=err)
    if err or result is None:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail=err)
    return result
