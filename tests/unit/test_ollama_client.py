"""
OllamaClient 单元测试
"""
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.core.ollama_client import OllamaClient


@pytest.fixture
def client():
    return OllamaClient()


class MockResponse:
    """模拟 aiohttp 响应"""
    def __init__(self, data):
        self._data = data

    async def json(self):
        return self._data

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class MockGetResponse:
    """模拟 aiohttp GET 响应"""
    def __init__(self, status=200):
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class MockSession:
    """模拟 aiohttp session"""
    def __init__(self, post_data=None, get_status=200, raise_error=False):
        self._post_data = post_data
        self._get_status = get_status
        self._raise_error = raise_error
        self.closed = False

    def post(self, url, **kwargs):
        if self._raise_error:
            raise Exception("Connection refused")
        return MockResponse(self._post_data)

    def get(self, url, **kwargs):
        if self._raise_error:
            raise Exception("Connection refused")
        return MockGetResponse(self._get_status)

    async def close(self):
        self.closed = True


class TestOllamaClientGenerateJson:
    """generate_json 方法测试"""

    @pytest.mark.asyncio
    async def test_valid_json_response(self, client):
        """测试 Ollama 返回有效 JSON"""
        response_data = {"response": '{"title": "test", "tags": ["a"]}'}
        client._session = MockSession(post_data=response_data)

        result = await client.generate_json("test prompt")
        assert result == {"title": "test", "tags": ["a"]}

    @pytest.mark.asyncio
    async def test_json_with_extra_text(self, client):
        """测试 Ollama 返回 JSON 带额外文本"""
        response_data = {"response": 'Here is the result: {"title": "test"} end'}
        client._session = MockSession(post_data=response_data)

        result = await client.generate_json("test prompt")
        assert result == {"title": "test"}

    @pytest.mark.asyncio
    async def test_invalid_json_returns_none(self, client):
        """测试 Ollama 返回无效 JSON"""
        response_data = {"response": "not json at all"}
        client._session = MockSession(post_data=response_data)

        result = await client.generate_json("test prompt")
        assert result is None

    @pytest.mark.asyncio
    async def test_empty_response(self, client):
        """测试 Ollama 返回空响应"""
        response_data = {"response": ""}
        client._session = MockSession(post_data=response_data)

        result = await client.generate_json("test prompt")
        assert result is None


class TestOllamaClientGenerate:
    """generate 方法测试"""

    @pytest.mark.asyncio
    async def test_returns_raw_text(self, client):
        """测试返回原始文本"""
        response_data = {"response": "Hello World"}
        client._session = MockSession(post_data=response_data)

        result = await client.generate("test prompt")
        assert result == "Hello World"


class TestOllamaClientIsAvailable:
    """is_available 方法测试"""

    @pytest.mark.asyncio
    async def test_available(self, client):
        """测试 Ollama 可用"""
        client._session = MockSession(get_status=200)

        result = await client.is_available()
        assert result is True

    @pytest.mark.asyncio
    async def test_unavailable(self, client):
        """测试 Ollama 不可用"""
        client._session = MockSession(raise_error=True)

        result = await client.is_available()
        assert result is False


class TestOllamaClientClose:
    """close 方法测试"""

    @pytest.mark.asyncio
    async def test_close_session(self, client):
        """测试关闭 session"""
        mock_session = MockSession()
        client._session = mock_session

        await client.close()
        assert mock_session.closed is True
        assert client._session is None

    @pytest.mark.asyncio
    async def test_close_no_session(self, client):
        """测试没有 session 时关闭"""
        client._session = None
        await client.close()  # Should not raise
