"""OpenTelemetry setup (R-OBS-06)."""

from __future__ import annotations

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import AppConfig


def setup_otel(config: AppConfig, engine: object | None = None) -> None:
    if engine is not None:
        sync_engine = getattr(engine, "sync_engine", engine)
        SQLAlchemyInstrumentor().instrument(engine=sync_engine)
    if not config.otel_exporter_otlp_endpoint:
        return
    resource = Resource.create({"service.name": config.otel_service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=config.otel_exporter_otlp_endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    HTTPXClientInstrumentor().instrument()
    RedisInstrumentor().instrument()


def instrument_fastapi(app: object) -> None:
    FastAPIInstrumentor.instrument_app(app)  # type: ignore[arg-type]
