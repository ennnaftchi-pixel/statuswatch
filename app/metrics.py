from prometheus_client import Counter, Gauge, Histogram

# 1. Counter: Total checks performed, split by service name and status
CHECKS_TOTAL = Counter(
    "statuswatch_checks_total",
    "Total number of checks performed",
    ["service_name", "status"]
)

# 2. Gauge: Is the service up (1) or down (0)?
SERVICE_UP = Gauge(
    "statuswatch_service_up",
    "Whether the service is up (1) or down (0)",
    ["service_name"]
)

# 3. Histogram: How long do the requests take?
RESPONSE_TIME = Histogram(
    "statuswatch_response_time_seconds",
    "Response time of the service check",
    ["service_name"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)
