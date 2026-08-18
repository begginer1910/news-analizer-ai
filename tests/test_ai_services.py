import pytest
import httpx
import respx
import json
from app.services.ai_service import Groq_ai
from app.exceptions import AIServiceError


@pytest.mark.asyncio
async def test_summarize_via_http(respx_mock):
    respx_mock.post("https://api.groq.com/openai/v1/chat/completions").respond(
        json={
            "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content":'{"summary": "ok", "sentiment":1}'}}]
        }
    )
    ai = Groq_ai("dummy_key")
    result = await ai.summarize("test title", "test description","test content", "english")
    assert result["summary"] == "ok"


@pytest.mark.asyncio
async def test_wrong_json(respx_mock):
    respx_mock.post("https://api.groq.com/openai/v1/chat/completions").respond(
        json={"choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": "not a json"}}]}
    )
    ai = Groq_ai("dummy_key")
    with pytest.raises(AIServiceError) as excinfo:
        await ai.summarize("test title", "test description","test content", "english")
    assert isinstance(excinfo.value.__cause__, ValueError)
    assert "AI response missing required data" in str(excinfo.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("content, missing_key",[
    ('{"summary": "text"}', "sentiment"),
    ('{"sentiment": 0}', "summary"),
])
async def test_no_summary_or_sentiment(respx_mock, content, missing_key):
    respx_mock.post("https://api.groq.com/openai/v1/chat/completions").respond(
        json={"choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": content}}]}
    )
    ai = Groq_ai("dummy_key")
    with pytest.raises(AIServiceError) as excinfo:
        await ai.summarize("test title", "test description","test content","english")
    
    assert isinstance(excinfo.value.__cause__, ValueError)
    assert "AI response missing required data" in str(excinfo.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code, side_effect, expected_msg",[
    (500, None, "AI service internal error"),
    (None, httpx.TimeoutException("timeout"), "Network error:"),
])
async def test_network_error(respx_mock, status_code, side_effect, expected_msg):
    route = respx_mock.post("https://api.groq.com/openai/v1/chat/completions")
    if side_effect:
        route.mock(side_effect=side_effect)
    else:
        route.respond(status_code=status_code)
    ai = Groq_ai("dummy_key")
    with pytest.raises(AIServiceError) as excinfo:
        await ai.summarize("test title", "test description","test content", "english")
    assert expected_msg in str(excinfo.value)

    if side_effect:  
        from groq import APITimeoutError
        assert isinstance(excinfo.value.__cause__, APITimeoutError)
    else:  
        from groq import InternalServerError
        assert isinstance(excinfo.value.__cause__, InternalServerError)


@pytest.mark.asyncio
async def test_empty_input_data(respx_mock):
    respx_mock.post("https://api.groq.com/openai/v1/chat/completions").respond(
        json={
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": '{"summary": "", "sentiment":0}'}}]
        }
    )
    ai = Groq_ai("dummy_key")
    result = await ai.summarize("", "", "", "")
    assert result["summary"] == ""
    assert result["sentiment"] == 0


@pytest.mark.asyncio
async def test_check_prompt(respx_mock):
    route = respx_mock.post("https://api.groq.com/openai/v1/chat/completions").respond(
        json = {"choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": '{"summary": "hello", "sentiment":1}'}}]
                }
    )
    ai = Groq_ai("dummy_key")
    await ai.summarize("test title", "test description","test content", "english")
    request = route.calls.last.request
    body = request.content.decode()
    body_dict = json.loads(body)
    assert body_dict["model"] == "openai/gpt-oss-20b"
    assert body_dict["response_format"]["type"] == "json_object"
    assert body_dict["messages"][0]["role"] == "system"
    assert body_dict["messages"][0]["content"] == "You are a news editor"
    assert "test title" in body_dict["messages"][1]["content"]