# Event-Driven Order Service - Fault-Tolerant System

**YuvaIntern Certificate No: YI/2026/186210/440517**
**Name: G. Devi Prasanna**

Online grocery platform (Kochi) - Monolith to Microservices migration using Event-Driven Architecture.

### Architecture
- **Producer:** Order Service (Flask - Port 5001)
- **Consumers:** Inventory Service, Notification Service
- **Broker:** RabbitMQ Topic Exchange `grocery.events`
- **DB:** Postgres
- **Pattern:** Transactional Outbox + Idempotent Consumers

### Key Features Implemented (As per requirements)

1.  **Guaranteed Delivery (Outbox Pattern):** `orders` and `outbox` tables inserted in single ACID transaction. Poller uses `SELECT ... FOR UPDATE SKIP LOCKED` to publish pending events with persistent delivery_mode=2.
2.  **Idempotency:** `processed_events(event_id PK)` table. Before processing, consumer checks if event_id exists. Duplicate -> ack as no-op. No double stock deduction.
3.  **Retries & DLQ:** On failure, message NACKed. Retry queues with TTL 5s, 25s, 125s (exponential backoff). After 3 retries -> `dlx.exchange` -> `inventory.dlq`. Poison messages logged with reason.
4.  **Validation & Compensation:** Invalid item -> reject to DLQ. Out-of-stock item -> publish `inventory.failed` -> Order Service marks order CANCELLED (compensation event).
5.  **Observability:** JSON logs `{"correlation_id": "...", "event_id": "..."}`. Correlation ID from HTTP Header `X-Correlation-Id` propagated to RabbitMQ `correlation_id` property.
6.  **Per-Order Sequencing:** Version check on stock row to ensure order events processed in order.
7.  **Load & Chaos Test:** `load_test.py` generates 200 orders/min with 10% duplicates, 5% invalid, 5% OOS. Chaos: kill inventory consumer 30s, verify zero data loss on recovery.
8.  **Edge Cases (8):** Duplicate delivery, empty cart, invalid product, OOS, consumer down, broker restart, clock skew, out-of-order.

### Run Locally
```bash
docker-compose up -d
curl -X POST http://localhost:5001/orders -H "X-Correlation-Id: test-123" -H "Content-Type: application/json" -d '{"product":"rice","qty":1}'# event-driven-order-service
YuvaIntern project - Fault tolerant order service with RabbitMQ
