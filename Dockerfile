FROM python:3.12-slim AS build
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip wheel --no-cache-dir --wheel-dir /wheels .

FROM python:3.12-slim
RUN useradd --create-home --uid 10001 appuser
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels
USER appuser
EXPOSE 8000
CMD ["uvicorn", "copilot_insights.api:app", "--host", "0.0.0.0", "--port", "8000"]

