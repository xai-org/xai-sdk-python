import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from xai_sdk import Client
from tests import server

@pytest.fixture(scope="module")
def bench_client():
    with server.run_test_server() as port:
        yield Client(api_key=server.API_KEY, api_host=f"localhost:{port}")

def test_auth_get_api_key_info_benchmark(benchmark, bench_client):
    """Benchmark the get_api_key_info API call."""
    result = benchmark(bench_client.auth.get_api_key_info)
    assert result is not None

def test_auth_concurrent_requests(benchmark, bench_client):
    """Benchmark concurrent get_api_key_info calls."""
    import concurrent.futures
    
    def make_request(_):
        return bench_client.auth.get_api_key_info()
    
    results = benchmark(
        lambda: list(concurrent.futures.ThreadPoolExecutor().map(
            make_request, range(10)
        ))
    )
    assert len(results) == 10
    assert all(r is not None for r in results)

@pytest.mark.parametrize("num_requests", [10, 100, 1000])
def test_auth_throughput(benchmark, bench_client, num_requests):
    """Benchmark throughput for multiple sequential requests."""
    def run_requests():
        for _ in range(num_requests):
            bench_client.auth.get_api_key_info()
    
    benchmark.pedantic(run_requests, iterations=1, rounds=3)
