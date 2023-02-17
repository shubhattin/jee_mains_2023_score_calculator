from fastapi import APIRouter, HTTPException, status
from .process_data.load_data import (
    load_data,
    get_metadata,
    serialize_Result_JSON,
    QUESTION_URL_PREFIX,
)
from .process_data.get_result import get_result
from kry.datt import deta_val, PROD_ENV, Base
from pydantic import BaseModel
import requests
import os

DETA_ENV = os.getenv("DETA_SPACE_APP") == "true"

router = APIRouter(prefix=("/api" if not DETA_ENV else ""))


def upadate_result_view_count():
    if PROD_ENV:
        # Tracking the number of times the result is viewed
        result_count = deta_val("result_view_count", "counts")
        result_count += 1
        Base("counts").put(result_count, "result_view_count")


class ResultRequestDate(BaseModel):
    ApplicationNumber: str
    DateOfBirth: str


@router.post("/get_result")
async def get_result_post(bdy: ResultRequestDate):
    dt = deta_val(bdy.ApplicationNumber, "info")

    if not dt:  # it means the application number is not found
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            headers={"X-error": "appl_numb_not_found"},
        )
    if dt["DOB"] != bdy.DateOfBirth:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            headers={"X-error": "dob_did_not_match"},
        )

    dt = deta_val(bdy.ApplicationNumber, "data")

    upadate_result_view_count()

    return {"result": dt["result"], "data": dt["data"]}


class SubmitRequestData(BaseModel):
    ResponsePageData: str
    AnswerKeyData: str
    DateOfBirth: str


@router.post("/submit_result_data")
async def submit_result_data(bdy: SubmitRequestData):
    try:
        URL = bdy.ResponsePageData.split("/")[0]
        if URL.startswith(QUESTION_URL_PREFIX):
            bdy.ResponsePageData = requests.get(URL).text
        data = load_data(bdy.AnswerKeyData, bdy.ResponsePageData)
        result = get_result(data)
        upadate_result_view_count()
        return_data = {"result": result.__dict__, "data": data.__dict__}
        if True:  # Caching the data
            meta = get_metadata(bdy.ResponsePageData)
            Base("info").put(
                {
                    "DOB": bdy.DateOfBirth,
                    "name": meta.Name,
                    "roll": meta.RollNumber,
                    "date": meta.TestDate,
                    "time": meta.TestTime,
                },
                meta.ApplicationNumber,
            )
            Base("data").put(
                {
                    "result": serialize_Result_JSON(result),
                    "data": data.__dict__,
                },
                meta.ApplicationNumber,
            )
        return return_data
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            headers={"X-error": "invalid_data"},
        )


@router.post("/get_sample_result")
async def get_sample_result():
    # Just for demonstration
    datt = deta_val("sample_result", "data")
    return {"data": datt["data"], "result": datt["result"]}


@router.post("/page_view_count")
def page_view_count():
    # Tracking the number of times the page is viewed
    page_view_count = deta_val("page_view_count", "counts")
    page_view_count += 1
    Base("counts").put(page_view_count, "page_view_count")
    return {
        "page_view_count": page_view_count,
        "result_view_count": deta_val("result_view_count", "counts"),
    }
