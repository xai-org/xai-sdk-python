"""Tests for the protobuf runtime dispatch in ``xai_sdk.proto``."""

import importlib

import google.protobuf
import pytest

import xai_sdk.proto


@pytest.fixture
def reload_proto_with_version(monkeypatch: pytest.MonkeyPatch):
    """Re-import ``xai_sdk.proto`` as if the installed protobuf runtime had the given version.

    The real module is reloaded again on teardown so later tests see the modules that match
    the runtime actually installed.
    """

    def _reload(fake_version: str):
        monkeypatch.setattr(google.protobuf, "__version__", fake_version)
        return importlib.reload(xai_sdk.proto)

    yield _reload

    monkeypatch.undo()
    importlib.reload(xai_sdk.proto)


@pytest.mark.parametrize("fake_version", ["7.0.0", "7.36.0", "8.1.0"])
def test_runtime_newer_than_v6_gencode_uses_the_v6_modules(reload_proto_with_version, fake_version):
    # protobuf only refuses a runtime that is older than the gencode it loads, so the modules
    # generated with 6.x are the right ones for every later major version.
    proto = reload_proto_with_version(fake_version)

    assert proto.chat_pb2.__name__ == "xai_sdk.proto.v6.chat_pb2"
    assert proto.shared_pb2.__name__ == "xai_sdk.proto.v6.shared_pb2"


def test_runtime_6_uses_the_v6_modules(reload_proto_with_version):
    proto = reload_proto_with_version("6.31.1")

    assert proto.chat_pb2.__name__ == "xai_sdk.proto.v6.chat_pb2"


# Loading the v5 modules under the installed 6.x runtime makes protobuf warn once per file
# about the gencode being one major older; that is the expected cross-version path here.
@pytest.mark.filterwarnings("ignore:Protobuf gencode version .* older than the runtime:UserWarning")
def test_runtime_5_uses_the_v5_modules(reload_proto_with_version):
    proto = reload_proto_with_version("5.29.4")

    assert proto.chat_pb2.__name__ == "xai_sdk.proto.v5.chat_pb2"


def test_runtime_older_than_any_gencode_is_rejected(reload_proto_with_version):
    with pytest.raises(ValueError, match="Unsupported protobuf version: 4.25.0"):
        reload_proto_with_version("4.25.0")
