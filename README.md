# AI News Agentic System -- 6-Layer Architecture

A modular, event-driven, production-ready system for collecting,
filtering, analyzing and delivering AI news at scale.

## Mục lục

1.  Giới thiệu
2.  Các Layer Kiến Trúc
3.  Luồng Hoạt Động
4.  Yêu cầu hệ thống
5.  Cách cài đặt & chạy
6.  Mở rộng sang Microservices
7.  Monitoring & Observability
8.  CI/CD
9.  Roadmap
10. License

## Giới thiệu

Hệ thống này được xây dựng để thu thập tin tức AI từ hàng trăm nguồn,
lọc và xếp hạng tin quan trọng bằng AI, tóm tắt bằng mô hình AI tuỳ
chọn, lưu trữ dữ liệu lâu dài, xuất tin tức sang nhiều kênh, theo dõi
hoạt động real-time và hỗ trợ xử lý hàng trăm nghìn bài mỗi ngày. Kiến
trúc 6 layer giúp dự án dễ mở rộng, bảo trì và tái sử dụng.

## Các Layer Kiến Trúc

-   **Input Layer**: nhận RSS, HTTP fetch, Google News API, chuẩn hóa dữ
    liệu, chống trùng.
-   **Processing Layer**: điều phối pipeline, lọc, validate schema, gửi
    job sang AI layer.
-   **AI Layer**: tóm tắt, phân loại, tạo embedding, semantic ranking.
-   **Database Layer**: PostgreSQL, MongoDB, Redis, MinIO/S3.
-   **Output Layer**: xuất tin tức qua Email, Slack, Telegram, HTML
    template.
-   **Observability Layer**: logs, metrics Prometheus, traces
    OpenTelemetry, alerts.

## Luồng Hoạt Động

Input → Processing → AI → Database → Output → Observability

## Yêu cầu hệ thống

-   Python 3.11
-   Thư viện mới nhất tới 15-11-2025: requests, feedparser, bs4,
    pydantic, openai, google-generativeai, ollama, sqlalchemy, pymongo,
    redis, boto3, minio, opentelemetry, prometheus-client, dotenv,
    fastapi, jinja2...

## Cách cài đặt & chạy

``` bash
git clone https://github.com/<your-repo>/ai-news-agent.git
cd ai-news-agent
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Tạo `.env`:

    POSTGRES_URL=...
    MONGO_URL=...
    REDIS_URL=...
    OPENAI_API_KEY=...
    SLACK_WEBHOOK=...

Chạy:

``` bash
python main.py --mode=full
```

## Mở rộng sang Microservices

-   Input Layer ➝ FastAPI service
-   Processing Layer ➝ Kafka/Redis Streams consumer
-   AI Layer ➝ GPU worker cluster
-   Output Layer ➝ Event-driven service
-   Observability ➝ Prometheus + Grafana + Jaeger

## Monitoring & Observability

-   Metrics: throughput, latency, failures
-   Logging JSON: correlation_id, layer_name, duration_ms
-   Tracing: toàn pipeline
-   Dashboard: latency heatmap, error alerts

## CI/CD

GitHub Actions: lint → test → build → deploy, Docker image per layer.

## Roadmap

-   v1.1: sentiment analysis
-   v1.2: real-time streaming dashboard
-   v1.3: multi-language summarization
-   v2.0: microservice version

## License

MIT License
