import respx
import pytest
from api_client import NewsApiClient


async def simulate_api_response(respx_mock, status_code, response_data):
    respx.get("https://newsapi.org/v2/top-headlines").respond(
        json=response_data, status_code=status_code
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("status, data, expected_len",[
    (200 , {"articles": [{"title": "X"}]}, 1,),
    (200, {"articles": []}, 0, ),
    (200, {}, 0,),
    (200, {"articles": None}, 0,),
    (429, {"error": "rare limit"}, 0,),
    (500, {}, 0,),
    (403, {}, 0,),
])


async def test_api(respx_mock, status, data, expected_len):
    await simulate_api_response(respx_mock, status, data)
    client = NewsApiClient()
    result = await client.get_news("general", "en", "us")
    assert len(result) == expected_len


@pytest.mark.asyncio
async def test_correct_params(respx_mock):
    route = respx_mock.get("https://newsapi.org/v2/top-headlines").respond(json={"articles": []})
    client = NewsApiClient()
    await client.get_news("business", "en", "us")
    request = route.calls.last.request
    assert request.url.params["category"] == "business"
    assert request.url.params["language"] == "en"
    assert request.url.params["country"] == "us"
    assert request.url.params["pageSize"] == "5"
    assert request.url.params["apiKey"] is not None