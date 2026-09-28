import datetime
from unittest import mock

import grpc
import pytest
import pytest_asyncio

from xai_sdk import AsyncClient
from xai_sdk.aio import batch as aio_batch
from xai_sdk.batch import BatchUnsupportedModelError
from xai_sdk.chat import Response, user
from xai_sdk.proto import batch_pb2, chat_pb2

from .. import server


@pytest.fixture(scope="session")
def test_server_port():
    with server.run_test_server() as port:
        yield port


@pytest_asyncio.fixture(scope="session")
async def client(test_server_port: int):
    yield AsyncClient(api_key=server.API_KEY, api_host=f"localhost:{test_server_port}")


@pytest.mark.asyncio
async def test_create_batch(client: AsyncClient):
    """Test creating a new batch."""
    batch = await client.batch.create("test_batch")

    assert batch.name == "test_batch"
    assert batch.batch_id != ""
    assert batch.state.num_requests == 0
    assert batch.state.num_pending == 0
    assert batch.state.num_success == 0
    assert batch.state.num_error == 0
    assert batch.state.num_cancelled == 0
    assert batch.create_time.seconds > 0
    assert batch.expire_time.seconds > batch.create_time.seconds

    retrieved_batch = await client.batch.get(batch.batch_id)

    assert retrieved_batch.batch_id == batch.batch_id
    assert retrieved_batch.name == batch.name
    assert retrieved_batch.state.num_requests == batch.state.num_requests
    assert retrieved_batch.state.num_pending == batch.state.num_pending
    assert retrieved_batch.state.num_success == batch.state.num_success
    assert retrieved_batch.state.num_error == batch.state.num_error
    assert retrieved_batch.state.num_cancelled == batch.state.num_cancelled
    assert retrieved_batch.create_time.seconds == batch.create_time.seconds
    assert retrieved_batch.expire_time.seconds == batch.expire_time.seconds
    assert retrieved_batch.create_api_key_id == batch.create_api_key_id
    assert retrieved_batch.cancel_time.seconds == batch.cancel_time.seconds
    assert retrieved_batch.cancel_by_xai_message == batch.cancel_by_xai_message


@pytest.mark.asyncio
async def test_add_batch_requests_with_chat_objects(client: AsyncClient):
    """Test adding requests to a batch using chat objects."""
    batch = await client.batch.create("test_batch")

    batch_requests = []
    for i, message in enumerate(["Hello", "How are you?", "Goodbye"]):
        chat = client.chat.create(model="grok-3", max_tokens=100, batch_request_id=f"req_{i}")
        chat.append(user(message))
        batch_requests.append(chat)

    await client.batch.add(batch.batch_id, batch_requests)

    retrieved_batch = await client.batch.get(batch.batch_id)
    assert retrieved_batch.state.num_requests == 3
    assert retrieved_batch.state.num_pending == 3
    assert retrieved_batch.state.num_success == 0

    batch_metadata = await client.batch.list_batch_requests(batch.batch_id)
    assert len(batch_metadata.batch_request_metadata) == 3
    for metadata in batch_metadata.batch_request_metadata:
        assert metadata.state == batch_pb2.BatchRequestMetadata.State.STATE_PENDING
        assert metadata.model == "grok-3"
        assert metadata.batch_request_id.startswith("req_")


@pytest.mark.asyncio
async def test_add_batch_requests_with_proto_objects(client: AsyncClient):
    """Test adding requests to a batch using proto objects."""
    batch = await client.batch.create("test_batch")

    requests = []
    for i in range(2):
        request = batch_pb2.BatchRequest(
            batch_request_id=f"proto_req_{i}",
            completion_request=chat_pb2.GetCompletionsRequest(
                model="grok-3-latest",
                messages=[
                    chat_pb2.Message(
                        role=chat_pb2.MessageRole.ROLE_USER, content=[chat_pb2.Content(text=f"Test message {i}")]
                    )
                ],
                max_tokens=100,
                n=1,
            ),
        )
        requests.append(request)

    await client.batch.add(batch.batch_id, requests)

    retrieved_batch = await client.batch.get(batch.batch_id)
    assert retrieved_batch.state.num_requests == 2
    assert retrieved_batch.state.num_pending == 2

    batch_metadata = await client.batch.list_batch_requests(batch.batch_id)
    assert len(batch_metadata.batch_request_metadata) == 2
    for metadata in batch_metadata.batch_request_metadata:
        assert metadata.state == batch_pb2.BatchRequestMetadata.State.STATE_PENDING
        assert metadata.model == "grok-3-latest"
        assert metadata.batch_request_id.startswith("proto_req_")


@pytest.mark.asyncio
async def test_get_batch(client: AsyncClient):
    """Test getting batch details."""
    created_batch = await client.batch.create("test_batch")

    retrieved_batch = await client.batch.get(created_batch.batch_id)

    assert retrieved_batch.batch_id == created_batch.batch_id
    assert retrieved_batch.name == created_batch.name
    assert retrieved_batch.state.num_requests == created_batch.state.num_requests


@pytest.mark.asyncio
async def test_list_batch_request_metadata(client: AsyncClient):
    """Test listing batch request metadata."""
    batch = await client.batch.create("test_batch")

    chats = []
    for i in range(2):
        chat = client.chat.create(model="grok-3-latest", batch_request_id=f"req_{i}")
        chat.append(user(f"Message {i}"))
        chats.append(chat)

    await client.batch.add(batch.batch_id, chats)

    batch_metadata = await client.batch.list_batch_requests(batch.batch_id)

    assert len(batch_metadata.batch_request_metadata) == 2

    for metadata in batch_metadata.batch_request_metadata:
        assert metadata.state == batch_pb2.BatchRequestMetadata.State.STATE_PENDING
        assert metadata.endpoint == "endpoint"
        assert metadata.model == "grok-3-latest"


@pytest.mark.asyncio
async def test_list_batch_results(client: AsyncClient):
    """Test that listing batch results processes pending requests."""
    batch = await client.batch.create("test_batch")

    batch_requests = []
    for i in range(2):
        chat = client.chat.create(model="grok-3-latest", batch_request_id=f"req_{i}")
        chat.append(user(f"Message {i}"))
        batch_requests.append(chat)

    await client.batch.add(batch.batch_id, batch_requests)

    batch_results = await client.batch.list_batch_results(batch.batch_id)

    assert len(batch_results.results) == 2
    assert batch_results.pagination_token is None or batch_results.pagination_token == ""

    for result in batch_results.results:
        assert result.is_success
        assert not result.has_error
        response = result.response
        assert isinstance(response, Response)
        assert result.batch_request_id.startswith("req_")
        assert response.content is not None
        assert "test-content" in response.content
        assert response.system_fingerprint == "dummy-fingerprint"
        assert response.usage.prompt_tokens == 10
        assert response.usage.completion_tokens == 5
        assert response.usage.total_tokens == 15

    retrieved_batch = await client.batch.get(batch.batch_id)
    assert retrieved_batch.state.num_requests == 2
    assert retrieved_batch.state.num_pending == 0
    assert retrieved_batch.state.num_success == 2

    batch_metadata = await client.batch.list_batch_requests(batch.batch_id)
    for metadata in batch_metadata.batch_request_metadata:
        assert metadata.state == batch_pb2.BatchRequestMetadata.State.STATE_SUCCEEDED


@pytest.mark.asyncio
async def test_cancel_batch(client: AsyncClient):
    """Test cancelling a batch marks pending requests as cancelled."""
    batch = await client.batch.create("test_batch")

    batch_requests = []
    for i in range(2):
        chat = client.chat.create(model="grok-3-latest", batch_request_id=f"req_{i}")
        chat.append(user(f"Message {i}"))
        batch_requests.append(chat)

    await client.batch.add(batch.batch_id, batch_requests)

    cancelled_batch = await client.batch.cancel(batch.batch_id)

    assert cancelled_batch.cancel_time.seconds > 0

    assert cancelled_batch.state.num_requests == 2
    assert cancelled_batch.state.num_pending == 0
    assert cancelled_batch.state.num_cancelled == 2

    batch_metadata = await client.batch.list_batch_requests(batch.batch_id)
    for metadata in batch_metadata.batch_request_metadata:
        assert metadata.state == batch_pb2.BatchRequestMetadata.State.STATE_CANCELLED


@pytest.mark.asyncio
async def test_add_multiple_request_batches(client: AsyncClient):
    """Test adding multiple batches of requests to the same batch."""
    batch = await client.batch.create("test_batch")

    batch_requests_one = []
    for i in range(2):
        chat = client.chat.create(model="grok-3-latest", batch_request_id=f"batch1_req_{i}")
        chat.append(user(f"First batch message {i}"))
        batch_requests_one.append(chat)

    await client.batch.add(batch.batch_id, batch_requests_one)

    batch_requests_two = []
    for i in range(3):
        chat = client.chat.create(model="grok-3-latest", batch_request_id=f"batch2_req_{i}")
        chat.append(user(f"Second batch message {i}"))
        batch_requests_two.append(chat)

    await client.batch.add(batch.batch_id, batch_requests_two)

    retrieved_batch = await client.batch.get(batch.batch_id)
    assert retrieved_batch.state.num_requests == 5
    assert retrieved_batch.state.num_pending == 5

    batch_metadata = await client.batch.list_batch_requests(batch.batch_id)
    assert len(batch_metadata.batch_request_metadata) == 5

    batch_results = await client.batch.list_batch_results(batch.batch_id)
    assert len(batch_results.results) == 5

    retrieved_batch = await client.batch.get(batch.batch_id)
    assert retrieved_batch.state.num_requests == 5
    assert retrieved_batch.state.num_pending == 0
    assert retrieved_batch.state.num_success == 5


@pytest.mark.asyncio
async def test_list_batches(client: AsyncClient):
    """Test listing all batches."""
    batch1 = await client.batch.create("batch_1")
    batch2 = await client.batch.create("batch_2")

    # List batches
    list_response = await client.batch.list()

    # Should contain our batches (and possibly others from other tests)
    batch_ids = [b.batch_id for b in list_response.batches]
    assert batch1.batch_id in batch_ids
    assert batch2.batch_id in batch_ids

    # Check that our batches have the right names
    for batch in list_response.batches:
        if batch.batch_id == batch1.batch_id:
            assert batch.name == "batch_1"
        elif batch.batch_id == batch2.batch_id:
            assert batch.name == "batch_2"


@pytest.mark.asyncio
async def test_list_batch_results_pagination(client: AsyncClient):
    """Test pagination in list_batch_results."""
    batch = await client.batch.create("test_batch")

    batch_requests = []
    for i in range(5):
        chat = client.chat.create(model="grok-3-latest", batch_request_id=f"req_{i}")
        chat.append(user(f"Message {i}"))
        batch_requests.append(chat)

    await client.batch.add(batch.batch_id, batch_requests)

    page1 = await client.batch.list_batch_results(batch.batch_id, limit=2)
    assert len(page1.results) == 2
    assert page1.pagination_token is not None

    page2 = await client.batch.list_batch_results(batch.batch_id, limit=2, pagination_token=page1.pagination_token)
    assert len(page2.results) == 2
    assert page2.pagination_token is not None

    page3 = await client.batch.list_batch_results(batch.batch_id, limit=2, pagination_token=page2.pagination_token)
    assert len(page3.results) == 1
    assert page3.pagination_token is None  # No more pages


@pytest.mark.asyncio
async def test_get_nonexistent_batch(client: AsyncClient):
    """Test getting a non-existent batch raises an error."""
    with pytest.raises(grpc.RpcError) as e:
        await client.batch.get("nonexistent_batch_id")

    assert e.value.code() == grpc.StatusCode.NOT_FOUND  # type: ignore
    assert e.value.details() == "Cannot find batch with ID nonexistent_batch_id"  # type: ignore


@pytest.mark.asyncio
async def test_add_to_nonexistent_batch(client: AsyncClient):
    """Test adding to a non-existent batch raises an error."""
    chat = client.chat.create(model="grok-3-latest")
    chat.append(user("test"))

    with pytest.raises(grpc.RpcError) as e:
        await client.batch.add("nonexistent_batch_id", [chat])

    assert e.value.code() == grpc.StatusCode.NOT_FOUND  # type: ignore
    assert e.value.details() == "Cannot find batch with ID nonexistent_batch_id"  # type: ignore


@pytest.mark.asyncio
async def test_add_unsupported_batch_model(client: AsyncClient):
    """Unsupported batch models raise BatchUnsupportedModelError with guidance."""
    batch = await client.batch.create("unsupported_model_batch")
    chat = client.chat.create(model="grok-4.5", batch_request_id="bad_model")
    chat.append(user("Say OK"))

    with pytest.raises(BatchUnsupportedModelError) as exc_info:
        await client.batch.add(batch.batch_id, [chat])

    err = exc_info.value
    assert err.model == "grok-4.5"
    assert "not supported for batch processing" in err.details
    assert "grok-4.20" in str(err)
    assert "grok-4.3" in str(err)


@pytest.mark.asyncio
async def test_wait_returns_when_batch_already_complete(client: AsyncClient):
    """wait() returns immediately when there are no pending requests."""
    batch = await client.batch.create("empty_wait_batch")
    finished = await client.batch.wait(
        batch.batch_id,
        timeout=datetime.timedelta(seconds=5),
        interval=datetime.timedelta(milliseconds=10),
    )
    assert finished.batch_id == batch.batch_id
    assert finished.state.num_pending == 0


@pytest.mark.asyncio
async def test_wait_completes_after_cancel(client: AsyncClient):
    """wait() finishes once cancel clears pending requests."""
    batch = await client.batch.create("cancel_wait_batch")
    chat = client.chat.create(model="grok-3", batch_request_id="req_0")
    chat.append(user("hello"))
    await client.batch.add(batch.batch_id, [chat])
    await client.batch.cancel(batch.batch_id)

    finished = await client.batch.wait(
        batch.batch_id,
        timeout=datetime.timedelta(seconds=5),
        interval=datetime.timedelta(milliseconds=10),
    )
    assert finished.state.num_pending == 0
    assert finished.state.num_cancelled == 1


@pytest.mark.asyncio
async def test_wait_polls_until_complete_with_mocked_stub():
    """Unit test: async wait polls GetBatch until num_pending reaches zero."""
    pending = batch_pb2.Batch(
        batch_id="batch_wait",
        state=batch_pb2.BatchState(num_requests=1, num_pending=1),
    )
    done = batch_pb2.Batch(
        batch_id="batch_wait",
        state=batch_pb2.BatchState(num_requests=1, num_pending=0, num_success=1),
    )

    async def get_side_effect(_request):
        return get_side_effect.responses.pop(0)

    get_side_effect.responses = [pending, done]

    stub = mock.MagicMock()
    stub.GetBatch = mock.AsyncMock(side_effect=get_side_effect)
    client = aio_batch.Client.__new__(aio_batch.Client)
    client._stub = stub

    with mock.patch("xai_sdk.aio.batch.asyncio.sleep", new_callable=mock.AsyncMock) as sleep_mock:
        result = await client.wait(
            "batch_wait",
            timeout=datetime.timedelta(seconds=5),
            interval=datetime.timedelta(milliseconds=1),
        )

    assert result.state.num_pending == 0
    assert result.state.num_success == 1
    assert stub.GetBatch.await_count == 2
    sleep_mock.assert_awaited()


@pytest.mark.asyncio
async def test_wait_timeout_with_mocked_stub():
    """Unit test: async wait raises TimeoutError when the batch never completes."""
    pending = batch_pb2.Batch(
        batch_id="batch_timeout",
        state=batch_pb2.BatchState(num_requests=1, num_pending=1),
    )

    async def get_pending(_request):
        return pending

    stub = mock.MagicMock()
    stub.GetBatch = mock.AsyncMock(side_effect=get_pending)
    client = aio_batch.Client.__new__(aio_batch.Client)
    client._stub = stub

    with mock.patch("xai_sdk.aio.batch.asyncio.sleep", new_callable=mock.AsyncMock):
        with pytest.raises(TimeoutError, match="waiting for batch batch_timeout to complete"):
            await client.wait(
                "batch_timeout",
                timeout=datetime.timedelta(milliseconds=5),
                interval=datetime.timedelta(milliseconds=1),
            )


@pytest.mark.asyncio
async def test_add_unsupported_model_with_mocked_stub():
    """Unit test: async add() wraps stub INVALID_ARGUMENT into BatchUnsupportedModelError."""

    class FakeRpcError(grpc.RpcError):
        def code(self):
            return grpc.StatusCode.INVALID_ARGUMENT

        def details(self):
            return "Model grok-4.5 is not supported for batch processing."

    stub = mock.MagicMock()
    stub.AddBatchRequests = mock.AsyncMock(side_effect=FakeRpcError())
    client = aio_batch.Client.__new__(aio_batch.Client)
    client._stub = stub

    request = batch_pb2.BatchRequest(
        batch_request_id="req_0",
        completion_request=chat_pb2.GetCompletionsRequest(model="grok-4.5"),
    )
    with pytest.raises(BatchUnsupportedModelError) as exc_info:
        await client.add("batch_id", [request])
    assert exc_info.value.model == "grok-4.5"
