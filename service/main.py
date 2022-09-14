import os

import fastapi
import requests
from pydantic import BaseModel

API_KEY = os.getenv("API_KEY")

app = fastapi.FastAPI()


class ClanModel(BaseModel):
    clan_id: int
    clan_tag: str


def api_get_clan_by_id(clan_id: int, api_key: str) -> tuple[ClanModel | None, str | None]:
    request_url = f"https://api.worldoftanks.eu/wot/clans/info/?application_id={api_key}&fields=tag&clan_id={clan_id}"
    try:
        response = requests.get(request_url)
        response.raise_for_status()
        response_json = response.json()
        if response_json["status"] != "ok":
            return None, f"API Request responded with an error: {response_json['error']['message']}"
        tag = response_json["data"][str(clan_id)]["tag"]
        if not tag:
            return None, f"No clan was found for this id: {clan_id}"
        return ClanModel(clan_id=clan_id, clan_tag=tag), None
    except Exception as e:  # TODO specific error handling
        return None, f"An Exception was raised during the api request. {e.__class__}: {e.args}."


def api_get_clan_by_tag(clan_tag: str, api_key: str) -> tuple[ClanModel | None, str | None]:
    request_url = \
        f"https://api.worldoftanks.eu/wot/clans/list/?application_id={api_key}&search={clan_tag}&fields=clan_id%2C+tag"
    try:
        response = requests.get(request_url)
        response.raise_for_status()
        response_json = response.json()
        if response_json["status"] != "ok":
            return None, f"API Request responded with an error: {response_json['error']['message']}"
        valid_responses = [result for result in response_json["data"] if result["tag"] == clan_tag]
        if len(valid_responses) == 0:
            return None, f"No clan was found for this id: {clan_tag}"
        return ClanModel(clan_id=valid_responses[0]["clan_id"], clan_tag=clan_tag), None
    except Exception as e:  # TODO specific error handling
        return None, f"An Exception was raised during the api request. {e.__class__}: {e.args}."


@app.get("/tag/{clan_tag}", response_model=ClanModel,
         responses={
             400: {"description": "Error in Request: Request could not be answered successful."},
             404: {"description": "Missing ressource: No clan was found for the requested tag."},
         }, description="Returns clan id and clan tag for the requested clan.")
def get_clan_id(clan_tag: str) -> ClanModel:
    result, err = api_get_clan_by_tag(clan_tag=clan_tag.upper(), api_key=API_KEY)
    if err and "No clan was found" in err:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail=err)
    if err:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail=err)
    return result


@app.get("/id/{clan_id}", response_model=ClanModel,
         responses={
             400: {"description": "Error in Request: Request could not be answered successful."},
             404: {"description": "Missing ressource: No clan was found for the requested id."}
         }, description="Returns clan id and clan tag for the requested clan.")
def get_clan_tag(clan_id: int) -> ClanModel:
    result, err = api_get_clan_by_id(clan_id=clan_id, api_key=API_KEY)
    if err and "No clan was found" in err:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail=err)
    if err:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail=err)
    return result
