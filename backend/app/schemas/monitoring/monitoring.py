from pydantic import BaseModel, ConfigDict


class BenchmarkRequest(BaseModel):
    """基准测试请求"""
    model_config = ConfigDict(from_attributes=True)

    name: str
    iterations: int = 100
    warmup: int = 10


class BenchmarkResult(BaseModel):
    """基准测试结果"""
    model_config = ConfigDict(from_attributes=True)

    name: str
    iterations: int
    warmup: int
    min_ms: float
    max_ms: float
    avg_ms: float
    median_ms: float
    std_dev_ms: float
    p95_ms: float
    p99_ms: float
