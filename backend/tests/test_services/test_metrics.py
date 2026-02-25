from gym_api.metrics.prometheus import (
    _metric_key,
    get_metrics_summary,
    reset_metrics,
)


def test_metric_key_format():
    key = _metric_key("GET", "/v1/health", 200)
    assert key == "GET:/v1/health:200"


def test_reset_metrics():
    from gym_api.metrics.prometheus import _request_count

    _request_count["test:key:200"] = 5
    reset_metrics()
    summary = get_metrics_summary()
    assert summary["request_count"] == {}
    assert summary["request_duration_sum"] == {}
    assert summary["request_errors"] == {}


def test_get_metrics_summary_empty():
    reset_metrics()
    summary = get_metrics_summary()
    assert "request_count" in summary
    assert "request_duration_sum" in summary
    assert "request_errors" in summary
