import pytest
import httpx
import respx
import json
from ai_service import Groq_ai


@pytest.mark.asyncio
async def test_summarize_via_http(respx_mock):
    respx_mock.post("https://api.groq.com/openai/v1/chat/completions").respond(
        json={
            "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content":'{"summary": "ok", "sentiment":1}'}}]
        }
    )
    ai = Groq_ai()
    result = await ai.summarize("test title", "test description", "english")
    assert result["summary"] == "ok"


@pytest.mark.asyncio
async def test_wrong_json(respx_mock):
    respx_mock.post("https://api.groq.com/openai/v1/chat/completions").respond(
        text = "not a json"
    )
    ai = Groq_ai()
    result = await ai.summarize("test title", "test description", "english")
    assert result == {"summary": "", "sentiment": 0}


@pytest.mark.asyncio
@pytest.mark.parametrize("content, missing_key",[
    ('{"summary": "text"}', "sentiment" ),
    ('{"sentiment": 0}', "summary" ),
])
async def test_no_summary_or_sentiment(respx_mock, content, missing_key):
    respx_mock.post("https://api.groq.com/openai/v1/chat/completions").respond(
        json={"choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": content}}]}
    )
    ai = Groq_ai()
    result = await ai.summarize("test title", "test description", "english")
    assert result == {"summary": "", "sentiment": 0}



@pytest.mark.asyncio
@pytest.mark.parametrize("status_code, side_effect",[
    (500, None),
    (None, httpx.TimeoutException("timeout")),
])
async def test_network_error(respx_mock, status_code, side_effect):
    route = respx_mock.post("https://api.groq.com/openai/v1/chat/completions")
    if side_effect:
        route.mock(side_effect=side_effect)
    else:
        route.respond(status_code=status_code)
    ai = Groq_ai()
    result = await ai.summarize("test title", "test description", "english")
    assert result == {"summary": "", "sentiment": 0}


@pytest.mark.asyncio
async def test_empty_input_data(respx_mock):
    respx_mock.post("https://api.groq.com/openai/v1/chat/completions").respond(
        json={
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": '{"summary": "", "sentiment":0}'}}]
        }
    )
    ai = Groq_ai()
    result = await ai.summarize("", "", "")
    assert result == {"summary": "", "sentiment": 0}


@pytest.mark.asyncio
async def test_check_prompt(respx_mock):
    route = respx_mock.post("https://api.groq.com/openai/v1/chat/completions").respond(
        json = {"choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": '{"summary": "hello", "sentiment":1}'}}]
                }
    )
    ai = Groq_ai()
    await ai.summarize("test title", "test description", "english")
    request = route.calls.last.request
    body = request.content.decode()
    body_dict = json.loads(body)
    assert body_dict["model"] == "llama-3.1-8b-instant"
    assert body_dict["response_format"]["type"] == "json_object"
    assert body_dict["messages"][0]["role"] == "system"
    assert body_dict["messages"][0]["content"] == "You are a news editor"
    assert "test title" in body_dict["messages"][1]["content"]
