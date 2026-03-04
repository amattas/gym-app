# Issues Found - Code Review Audit

Tracked issues from comprehensive codebase review. Each entry links to a GitHub issue.

## Critical

| # | Title | Category | File(s) | GH Issue |
|---|-------|----------|---------|----------|
| 1 | Stripe webhook bypasses signature verification when secret is empty | Security | `backend/src/gym_api/routers/stripe_webhooks.py:24-25` | [#222](https://github.com/amattas/gym-app/issues/222) |
| 2 | GraphQL client query missing gym_id tenant isolation | Security | `backend/src/gym_api/graphql/schema.py:107-127` | [#223](https://github.com/amattas/gym-app/issues/223) |
| 3 | JWT tokens stored in localStorage (XSS vulnerable) | Security | `frontend/src/lib/api.ts:26-28`, `frontend/src/lib/auth.tsx:46` | [#224](https://github.com/amattas/gym-app/issues/224) |
| 4 | Hardcoded database credentials in docker-compose.yml | Security | `docker-compose.yml:8,19-20` | [#225](https://github.com/amattas/gym-app/issues/225) |
| 5 | Insecure default JWT secret with weak production validation | Security | `backend/src/gym_api/config.py:11,24-35` | [#226](https://github.com/amattas/gym-app/issues/226) |
| 40 | Check-in endpoints missing user authentication (5 endpoints) | Security | `backend/src/gym_api/routers/check_ins.py` | [#261](https://github.com/amattas/gym-app/issues/261) |
| 41 | Calendar/analytics endpoints missing user authentication | Security | `backend/src/gym_api/routers/calendar.py` | [#262](https://github.com/amattas/gym-app/issues/262) |
| 42 | Schedule management endpoints missing user authentication (6+) | Security | `backend/src/gym_api/routers/schedules.py:63-148` | [#263](https://github.com/amattas/gym-app/issues/263) |
| 43 | Notes update/delete missing ALL auth guards | Security | `backend/src/gym_api/routers/notes.py:105-127` | [#264](https://github.com/amattas/gym-app/issues/264) |
| 73 | No FK constraints on any model — referential integrity not enforced at DB level | Bug | `backend/src/gym_api/models/*.py` | [#294](https://github.com/amattas/gym-app/issues/294) |
| 74 | Billing checkout passes user_id as account_id creating orphaned invoices | Bug | `backend/src/gym_api/routers/billing.py:141,188` | [#295](https://github.com/amattas/gym-app/issues/295) |
| 75 | Stripe handle_payment_success missing gym_id enables cross-tenant payment manipulation | Security | `backend/src/gym_api/services/stripe_service.py:222-253` | [#296](https://github.com/amattas/gym-app/issues/296) |
| 133 | Frontend auth calls non-existent /v1/auth/me endpoint — app broken on refresh | Integration | `frontend/src/lib/auth.tsx:49` ↔ `backend/src/gym_api/routers/auth.py` | [#354](https://github.com/amattas/gym-app/issues/354) |
| 134 | Login response shape mismatch — frontend expects {data: {access_token, user}} | Integration | `frontend/src/lib/auth.tsx:72-84` ↔ `backend/src/gym_api/routers/auth.py:144-151` | [#355](https://github.com/amattas/gym-app/issues/355) |
| 135 | Token refresh response shape mismatch — refresh always fails | Integration | `frontend/src/lib/api.ts:103-106` ↔ `backend/src/gym_api/routers/auth.py:154-161` | [#356](https://github.com/amattas/gym-app/issues/356) |
| 136 | Workout creation sends nested exercises but backend discards them silently | Integration | `frontend/src/app/(app)/workouts/new/page.tsx:128-147` ↔ `backend/src/gym_api/schemas/workout.py` | [#357](https://github.com/amattas/gym-app/issues/357) |
| 137 | Passkey service has no challenge persistence — replay attacks possible | Security | `backend/src/gym_api/services/passkey_service.py:13-54,89-118` | [#358](https://github.com/amattas/gym-app/issues/358) |
| 138 | Client CRUD endpoints (7 routes) missing auth guard entirely | Security | `backend/src/gym_api/routers/clients.py:21-122` | [#359](https://github.com/amattas/gym-app/issues/359) |
| 296 | Webhook sign_payload hmac.new crash -- all webhook signatures broken | Bug | `backend/src/gym_api/webhooks/webhook_service.py:17` | [#517](https://github.com/amattas/gym-app/issues/517) |
| 383 | Stripe webhook passes string payment_id to service expecting UUID -- payment success handler broken | Bug | `backend/src/gym_api/routers/stripe_webhooks.py:80-92` | [#604](https://github.com/amattas/gym-app/issues/604) |
| 384 | Stripe webhook string payment_id to handle_payment_failure -- same UUID mismatch | Bug | `backend/src/gym_api/routers/stripe_webhooks.py:93-104` | [#605](https://github.com/amattas/gym-app/issues/605) |
| 385 | PaymentMethodCreate missing required type field -- NOT NULL violation on every add | Bug | `backend/src/gym_api/schemas/billing.py:25-30` | [#606](https://github.com/amattas/gym-app/issues/606) |
| 450 | JWT tokens missing iss/aud/nbf claims -- no issuer or audience validation | Security | `backend/src/gym_api/services/auth_service.py:24-38` | [#671](https://github.com/amattas/gym-app/issues/671) |
| 451 | Stripe SDK imported but never used -- entire payment processing is mocked/fake | Bug | `backend/src/gym_api/services/stripe_service.py:1-270` | [#672](https://github.com/amattas/gym-app/issues/672) |
| 452 | Zero refund functionality -- no refund service, endpoint, or webhook handler exists | Bug | `backend/src/gym_api/services/stripe_service.py`, `billing.py` | [#673](https://github.com/amattas/gym-app/issues/673) |
| 453 | Stripe Connect onboarding uses fake placeholder account IDs -- never syncs with Stripe | Bug | `backend/src/gym_api/services/stripe_service.py:47-59` | [#674](https://github.com/amattas/gym-app/issues/674) |
| 507 | No cryptographic signature verification for signed e-sign envelopes | Security | `backend/src/gym_api/services/esign_service.py:68-80` | [#728](https://github.com/amattas/gym-app/issues/728) |
| 508 | No state machine validation on agreement envelopes -- signed docs can be reverted | Security | `backend/src/gym_api/services/esign_service.py:117-123` | [#729](https://github.com/amattas/gym-app/issues/729) |
| 555 | Client invitation router endpoints missing entirely -- service is dead code | Bug | `backend/src/gym_api/routers/invitations.py` | [#776](https://github.com/amattas/gym-app/issues/776) |
| 556 | Invitation accept creates user without transaction boundaries -- partial state on failure | Bug | `backend/src/gym_api/routers/invitations.py:54-78` | [#777](https://github.com/amattas/gym-app/issues/777) |
| 557 | No deactivation cleanup cascades -- deactivated users retain API access via cached tokens | Security | `backend/src/gym_api/models/user.py:31`, `auth_service.py:110` | [#778](https://github.com/amattas/gym-app/issues/778) |
| 642 | audit_service.log_event never called anywhere -- entire audit logging system is dead code | Bug | `backend/src/gym_api/services/audit_service.py:10-33` | [#863](https://github.com/amattas/gym-app/issues/863) |
| 643 | deliver_webhook never called -- custom webhook delivery system entirely disconnected | Bug | `backend/src/gym_api/webhooks/webhook_service.py:26-75` | [#864](https://github.com/amattas/gym-app/issues/864) |
| 644 | Check-in does not trigger membership visit deduction -- visits_used never incremented | Bug | `backend/src/gym_api/services/check_in_service.py:16-52` | [#865](https://github.com/amattas/gym-app/issues/865) |
| 696 | handle_payment_success has no idempotency guard -- re-processes succeeded payments | Bug | `backend/src/gym_api/services/stripe_service.py:222-253` | [#917](https://github.com/amattas/gym-app/issues/917) |
| 740 | WebhookCreate missing secret field -- IntegrityError on every webhook creation | Bug | `backend/src/gym_api/routers/webhook_endpoints.py:15-18` | [#961](https://github.com/amattas/gym-app/issues/961) |
| 790 | process_pending_deletions never scheduled -- GDPR deletion requests never execute | Bug | `backend/src/gym_api/jobs/scheduler.py:13-31` | [#1011](https://github.com/amattas/gym-app/issues/1011) |
| 970 | Measurements page sends measurement_type but backend expects type -- every create 422s | Integration | `frontend/src/app/(app)/measurements/page.tsx:94` ↔ `backend/src/gym_api/schemas/measurement.py:9` | [#1191](https://github.com/amattas/gym-app/issues/1191) |
| 1101 | No signing endpoint -- envelopes can never be signed via API | Missing Functionality | `backend/src/gym_api/services/esign_service.py`, `backend/src/gym_api/routers/agreements.py` | [#1330](https://github.com/amattas/gym-app/issues/1330) |
| 1140 | Test fixture uses invalid enum 'qr' for CheckInMethod | Testing | `backend/tests/test_routers/test_check_ins.py:61` | [#1361](https://github.com/amattas/gym-app/issues/1361) |

## High

| # | Title | Category | File(s) | GH Issue |
|---|-------|----------|---------|----------|
| 6 | Missing rate limiting on forgot-password endpoint | Security | `backend/src/gym_api/middleware/rate_limiter.py:14-19` | [#227](https://github.com/amattas/gym-app/issues/227) |
| 7 | CORS allows wildcard headers with credentials enabled | Security | `backend/src/gym_api/middleware/cors.py:25` | [#228](https://github.com/amattas/gym-app/issues/228) |
| 8 | Missing authentication on unassign-trainer endpoint | Security | `backend/src/gym_api/routers/clients.py:156-167` | [#229](https://github.com/amattas/gym-app/issues/229) |
| 9 | N+1 query in AI summary generation causes severe perf degradation | Performance | `backend/src/gym_api/services/ai_summary_service.py:109-130` | [#230](https://github.com/amattas/gym-app/issues/230) |
| 10 | N+1 query in data export service (GDPR compliance risk) | Performance | `backend/src/gym_api/services/data_export_service.py:88-104` | [#231](https://github.com/amattas/gym-app/issues/231) |
| 11 | N+1 query in measurement service | Performance | `backend/src/gym_api/services/measurement_service.py:83-101` | [#232](https://github.com/amattas/gym-app/issues/232) |
| 12 | Race condition: multiple default payment methods allowed | Bug | `backend/src/gym_api/models/payment_method.py:26` | [#233](https://github.com/amattas/gym-app/issues/233) |
| 13 | Token refresh race condition with concurrent requests | Bug | `frontend/src/lib/api.ts:60-73` | [#234](https://github.com/amattas/gym-app/issues/234) |
| 14 | Missing confirmation dialogs for destructive actions (memberships) | Usability | `frontend/src/app/(app)/memberships/page.tsx:71-104` | [#235](https://github.com/amattas/gym-app/issues/235) |
| 15 | Kubernetes deployment missing security context | Infra | `k8s/deployment.yaml:16-56` | [#236](https://github.com/amattas/gym-app/issues/236) |
| 16 | K8s deployment uses floating "latest" image tag | Infra | `k8s/deployment.yaml:19` | [#237](https://github.com/amattas/gym-app/issues/237) |
| 17 | Payment model missing updated_at timestamp | Bug | `backend/src/gym_api/models/invoice.py:63-87` | [#238](https://github.com/amattas/gym-app/issues/238) |
| 18 | Rate limiter parses JWT without signature verification | Security | `backend/src/gym_api/middleware/rate_limiter.py:100-117` | [#239](https://github.com/amattas/gym-app/issues/239) |
| 19 | CORS hardcodes localhost origins (included in production) | Security | `backend/src/gym_api/middleware/cors.py:3-6` | [#240](https://github.com/amattas/gym-app/issues/240) |
| 20 | Missing client-side UUID validation on form inputs | Bug | `frontend/src/app/(app)/workouts/new/page.tsx:176-183` | [#241](https://github.com/amattas/gym-app/issues/241) |
| 44 | IDOR: agreements, data privacy, AI summary, notification endpoints missing gym isolation | Security | Multiple routers | [#265](https://github.com/amattas/gym-app/issues/265) |
| 45 | IDOR: Goals/programs endpoints accessible cross-gym (6+) | Security | `backend/src/gym_api/routers/goals.py` | [#266](https://github.com/amattas/gym-app/issues/266) |
| 46 | IDOR: Billing, location, webhook endpoints missing gym validation | Security | Multiple routers | [#267](https://github.com/amattas/gym-app/issues/267) |
| 47 | IDOR: Trainer availability/exception endpoints accessible cross-gym | Security | `backend/src/gym_api/routers/schedules.py:151-196` | [#268](https://github.com/amattas/gym-app/issues/268) |
| 48 | S3Storage uses blocking boto3 calls in async methods | Performance | `backend/src/gym_api/storage/s3_storage.py:30-62` | [#269](https://github.com/amattas/gym-app/issues/269) |
| 49 | LocalStorage path traversal vulnerability | Security | `backend/src/gym_api/storage/local_storage.py:16-18` | [#270](https://github.com/amattas/gym-app/issues/270) |
| 50 | Discount code race condition on times_used allows limit bypass | Bug | `backend/src/gym_api/services/discount_service.py:106-128` | [#271](https://github.com/amattas/gym-app/issues/271) |
| 51 | Membership visit deduction race condition allows over-use | Bug | `backend/src/gym_api/services/membership_service.py:256-272` | [#272](https://github.com/amattas/gym-app/issues/272) |
| 52 | Schedule double-booking race condition | Bug | `backend/src/gym_api/services/schedule_service.py:163-179` | [#273](https://github.com/amattas/gym-app/issues/273) |
| 53 | Missing /auth/logout endpoint (in API spec but not implemented) | Bug | `backend/src/gym_api/routers/auth.py` | [#274](https://github.com/amattas/gym-app/issues/274) |
| 54 | Missing /auth/password/change endpoint (in API spec) | Bug | `backend/src/gym_api/routers/auth.py` | [#275](https://github.com/amattas/gym-app/issues/275) |
| 62 | Missing confirmation dialog on exercise deletion | Usability | `frontend/src/app/(app)/exercises/page.tsx:131-139` | [#283](https://github.com/amattas/gym-app/issues/283) |
| 63 | Missing confirmation dialog on domain deletion | Usability | `frontend/src/app/(app)/domains/page.tsx:81-89` | [#284](https://github.com/amattas/gym-app/issues/284) |
| 69 | Missing test coverage for 14+ critical auth endpoints | Testing | `backend/tests/test_auth/` | [#290](https://github.com/amattas/gym-app/issues/290) |
| 76 | Scheduler runs on every pod replica causing duplicate job execution | Bug | `backend/src/gym_api/jobs/scheduler.py:10-31` | [#297](https://github.com/amattas/gym-app/issues/297) |
| 77 | Login endpoint allows unverified email accounts to authenticate | Security | `backend/src/gym_api/routers/auth.py:132-151` | [#298](https://github.com/amattas/gym-app/issues/298) |
| 78 | Progress photos list/delete endpoints missing authentication | Security | `backend/src/gym_api/routers/progress_photos.py:57-83` | [#299](https://github.com/amattas/gym-app/issues/299) |
| 79 | Invitation accept bypasses password validation rules | Security | `backend/src/gym_api/routers/invitations.py:43-66` | [#300](https://github.com/amattas/gym-app/issues/300) |
| 80 | apply_discount() ignores max_uses, valid_from, valid_until constraints | Bug | `backend/src/gym_api/services/discount_service.py:106-128` | [#301](https://github.com/amattas/gym-app/issues/301) |
| 81 | Stripe webhook missing timestamp replay protection | Security | `backend/src/gym_api/routers/stripe_webhooks.py:23-33` | [#302](https://github.com/amattas/gym-app/issues/302) |
| 82 | MFA secret stored as plaintext in database | Security | `backend/src/gym_api/models/user.py:33` | [#303](https://github.com/amattas/gym-app/issues/303) |
| 83 | GraphQL _require_gym_access silently permits access when no gym_id in token | Security | `backend/src/gym_api/graphql/schema.py:17-20` | [#304](https://github.com/amattas/gym-app/issues/304) |
| 84 | Seed script creates platform admin with hardcoded weak password | Security | `backend/src/gym_api/scripts/seed.py:170` | [#305](https://github.com/amattas/gym-app/issues/305) |
| 85 | Dockerfile missing alembic directory — cannot run migrations in container | Infra | `backend/Dockerfile:5-6,15` | [#306](https://github.com/amattas/gym-app/issues/306) |
| 86 | Busyness service executes 192 sequential DB queries per request | Performance | `backend/src/gym_api/services/busyness_service.py:20-52` | [#307](https://github.com/amattas/gym-app/issues/307) |
| 87 | Idempotency middleware uses in-memory store — not shared across replicas | Bug | `backend/src/gym_api/middleware/idempotency.py:17` | [#308](https://github.com/amattas/gym-app/issues/308) |
| 88 | Client.email has no unique constraint per gym — duplicate clients | Bug | `backend/src/gym_api/models/client.py:42` | [#309](https://github.com/amattas/gym-app/issues/309) |
| 89 | Trainer.email has no unique constraint per gym — duplicate trainers | Bug | `backend/src/gym_api/models/trainer.py:23` | [#310](https://github.com/amattas/gym-app/issues/310) |
| 90 | Membership expiry job has no error handling — single failure aborts batch | Bug | `backend/src/gym_api/jobs/membership_expiry.py:10-25` | [#311](https://github.com/amattas/gym-app/issues/311) |
| 91 | Workout set update/delete operations lack gym_id scoping (IDOR) | Security | `backend/src/gym_api/services/workout_service.py:121-147` | [#312](https://github.com/amattas/gym-app/issues/312) |
| 92 | Webhook create/list endpoints accept arbitrary gym_id from URL path | Security | `backend/src/gym_api/routers/webhook_endpoints.py:37-57` | [#313](https://github.com/amattas/gym-app/issues/313) |
| 93 | Device unregister allows any authenticated user to delete any device | Security | `backend/src/gym_api/routers/notifications.py:32-40` | [#314](https://github.com/amattas/gym-app/issues/314) |
| 94 | Health readiness probe returns HTTP 200 even when database is down | Infra | `backend/src/gym_api/routers/health.py:17-43` | [#315](https://github.com/amattas/gym-app/issues/315) |
| 95 | Missing skip navigation link in app layout (WCAG 2.4.1) | Accessibility | `frontend/src/app/(app)/layout.tsx:37-53` | [#316](https://github.com/amattas/gym-app/issues/316) |
| 96 | Payment method deletion has no ownership verification (cross-tenant) | Security | `backend/src/gym_api/routers/billing.py:105-114` | [#317](https://github.com/amattas/gym-app/issues/317) |
| 97 | Cleanup job has no error handling — unhandled exception kills job | Bug | `backend/src/gym_api/jobs/cleanup.py:14-47` | [#318](https://github.com/amattas/gym-app/issues/318) |
| 139 | Workout detail page expects nested exercises but backend returns flat workout | Integration | `frontend/src/app/(app)/workouts/[workoutId]/page.tsx:39-48` | [#360](https://github.com/amattas/gym-app/issues/360) |
| 140 | Workout set field names mismatch (set_number/weight vs set_index/weight_kg) | Integration | `frontend/src/app/(app)/workouts/[workoutId]/page.tsx:21-29` | [#361](https://github.com/amattas/gym-app/issues/361) |
| 141 | Client detail page calls non-existent /v1/clients/{id}/measurements endpoint | Integration | `frontend/src/app/(app)/clients/[clientId]/page.tsx:65` | [#362](https://github.com/amattas/gym-app/issues/362) |
| 142 | Billing invoices fetch missing required membership_id query parameter | Integration | `frontend/src/app/(app)/billing/page.tsx:79` | [#363](https://github.com/amattas/gym-app/issues/363) |
| 143 | Billing invoice amount_cents field doesnt exist in backend response | Integration | `frontend/src/app/(app)/billing/page.tsx:36-43` | [#364](https://github.com/amattas/gym-app/issues/364) |
| 144 | Frontend X-Gym-ID header is ignored — backend derives gym_id from JWT only | Integration | `frontend/src/lib/api.ts:51-53` | [#365](https://github.com/amattas/gym-app/issues/365) |
| 145 | Add-set operation missing required set_index field — always returns 422 | Integration | `frontend/src/app/(app)/workouts/[workoutId]/page.tsx:134-141` | [#366](https://github.com/amattas/gym-app/issues/366) |
| 146 | client_program_service entirely missing gym_id — no tenant isolation | Security | `backend/src/gym_api/services/client_program_service.py:1-75` | [#367](https://github.com/amattas/gym-app/issues/367) |
| 147 | gym_admin can view/update any gym without ownership check | Security | `backend/src/gym_api/routers/gyms.py:45-75` | [#368](https://github.com/amattas/gym-app/issues/368) |
| 148 | Measurement delete_measurement service lacks gym_id scoping (IDOR) | Security | `backend/src/gym_api/routers/measurements.py:66-79` | [#369](https://github.com/amattas/gym-app/issues/369) |
| 149 | WorkoutSet model missing RPE, distance, notes, set_type fields per MVP spec | Spec Compliance | `backend/src/gym_api/models/workout.py:57-70` | [#370](https://github.com/amattas/gym-app/issues/370) |
| 150 | Missing client program lifecycle endpoints per spec | Spec Compliance | `backend/src/gym_api/routers/goals.py:96-170` | [#371](https://github.com/amattas/gym-app/issues/371) |
| 151 | Missing measurement types CRUD endpoints per MVP spec | Spec Compliance | `backend/src/gym_api/routers/measurements.py` | [#372](https://github.com/amattas/gym-app/issues/372) |
| 152 | Missing progress photo signed upload URL endpoint per spec | Spec Compliance | `backend/src/gym_api/routers/progress_photos.py` | [#373](https://github.com/amattas/gym-app/issues/373) |
| 153 | Missing 4 workout endpoint tests (start, complete, update_set, delete_set) | Testing | `backend/tests/test_routers/test_workouts.py` | [#374](https://github.com/amattas/gym-app/issues/374) |
| 154 | Missing billing checkout/payment/fee tests (critical financial endpoints) | Testing | `backend/tests/test_routers/test_billing.py` | [#375](https://github.com/amattas/gym-app/issues/375) |
| 174 | Data export stores full client data as base64 data URI in database column | Bug | `backend/src/gym_api/services/data_export_service.py:144` | [#395](https://github.com/amattas/gym-app/issues/395) |
| 175 | Data export generate_export_data missing gym_id scoping on 5 of 6 entity types | Security | `backend/src/gym_api/services/data_export_service.py:78-126` | [#396](https://github.com/amattas/gym-app/issues/396) |
| 176 | Data deletion _anonymize_client_data omits workouts, check-ins, schedules, billing (GDPR incomplete) | Bug | `backend/src/gym_api/services/data_deletion_service.py:81-126` | [#397](https://github.com/amattas/gym-app/issues/397) |
| 177 | Data deletion partial commit causes irrecoverable state on mid-anonymization failure | Bug | `backend/src/gym_api/services/data_deletion_service.py:67-77,126` | [#398](https://github.com/amattas/gym-app/issues/398) |
| 178 | Data export status/download endpoints lack gym_id tenant scoping (IDOR) | Security | `backend/src/gym_api/routers/data_privacy.py:60-83` | [#399](https://github.com/amattas/gym-app/issues/399) |
| 179 | Calendar token generate/rotate endpoints missing auth -- anyone can issue tokens for arbitrary users | Security | `backend/src/gym_api/routers/calendar.py:38-84` | [#400](https://github.com/amattas/gym-app/issues/400) |
| 180 | iCal generate_ics query has no gym_id scoping -- exposes cross-tenant schedule data | Security | `backend/src/gym_api/services/ical_service.py:58-85` | [#401](https://github.com/amattas/gym-app/issues/401) |
| 190 | Migration missing trial enum value in membershipstatus -- inserts fail | Bug | `backend/alembic/versions/001_initial_schema.py:74-77` | [#411](https://github.com/amattas/gym-app/issues/411) |
| 191 | Migration missing session_pack enum value in plantype -- inserts fail | Bug | `backend/alembic/versions/001_initial_schema.py:92-94` | [#412](https://github.com/amattas/gym-app/issues/412) |
| 192 | Password reset does not invalidate existing sessions or refresh tokens | Security | `backend/src/gym_api/routers/auth.py:237-262` | [#413](https://github.com/amattas/gym-app/issues/413) |
| 193 | Checkout creates invoice and payment in separate commits -- partial failure orphans invoice | Bug | `backend/src/gym_api/services/stripe_service.py:180-219` | [#414](https://github.com/amattas/gym-app/issues/414) |
| 194 | handle_payment_success lacks SELECT FOR UPDATE -- lost update on concurrent webhook retries | Bug | `backend/src/gym_api/services/stripe_service.py:222-253` | [#415](https://github.com/amattas/gym-app/issues/415) |
| 1168 | apply_discount() bypasses all validation — expired/maxed-out codes still applied | Bug | `backend/src/gym_api/services/discount_service.py` | [#1389](https://github.com/amattas/gym-app/issues/1389) |
| 1169 | GraphQL _require_gym_access silently permits access when token gym_id is null | Security | `backend/src/gym_api/graphql/schema.py:17-20` | [#1390](https://github.com/amattas/gym-app/issues/1390) |

## High

| # | Title | Category | File(s) | GH Issue |
|---|-------|----------|---------|----------|
| 195 | Missing client columns (account_id, member_role, login_enabled) in migration | Bug | `backend/alembic/versions/001_initial_schema.py:171-195` | [#416](https://github.com/amattas/gym-app/issues/416) |
| 196 | payments.invoice_id nullability mismatch -- migration NOT NULL vs model nullable | Bug | `backend/alembic/versions/001_initial_schema.py:939` | [#417](https://github.com/amattas/gym-app/issues/417) |
| 197 | Missing stripe_accounts.gym_id UNIQUE constraint in migration | Bug | `backend/alembic/versions/001_initial_schema.py:868-885` | [#418](https://github.com/amattas/gym-app/issues/418) |
| 198 | No ON DELETE behavior on any FK constraint in migration -- deletes fail | Bug | `backend/alembic/versions/001_initial_schema.py` (throughout) | [#419](https://github.com/amattas/gym-app/issues/419) |
| 199 | Access tokens lack jti claim -- no individual token revocation possible | Security | `backend/src/gym_api/services/auth_service.py:24-34` | [#420](https://github.com/amattas/gym-app/issues/420) |
| 200 | TOTP verification has no replay protection for used codes | Security | `backend/src/gym_api/services/mfa_service.py:17` | [#421](https://github.com/amattas/gym-app/issues/421) |
| 201 | No rate limiting on MFA verification endpoint -- brute-force 6-digit codes | Security | `backend/src/gym_api/middleware/rate_limiter.py:14-19` | [#422](https://github.com/amattas/gym-app/issues/422) |
| 202 | MFA code in same login request leaks credential validity via 403 vs 401 | Security | `backend/src/gym_api/routers/auth.py:37-40,132-151` | [#423](https://github.com/amattas/gym-app/issues/423) |
| 203 | No per-account lockout after repeated failed login attempts | Security | `backend/src/gym_api/routers/auth.py:132-136` | [#424](https://github.com/amattas/gym-app/issues/424) |
| 204 | UserSession records created but never validated on API requests | Security | `backend/src/gym_api/dependencies/auth.py:15-30` | [#425](https://github.com/amattas/gym-app/issues/425) |
| 205 | Refresh tokens not bound to sessions -- session revocation ineffective | Security | `backend/src/gym_api/services/auth_service.py:79-122` | [#426](https://github.com/amattas/gym-app/issues/426) |
| 206 | Logout does not call backend to invalidate tokens server-side | Security | `frontend/src/lib/auth.tsx:97-103` | [#427](https://github.com/amattas/gym-app/issues/427) |
| 207 | No pagination on any frontend list page -- unbounded dataset fetch (systemic) | Performance | Multiple frontend pages | [#428](https://github.com/amattas/gym-app/issues/428) |
| 208 | Invitation acceptance race condition -- same invitation accepted twice | Bug | `backend/src/gym_api/services/invitation_service.py:40-63` | [#429](https://github.com/amattas/gym-app/issues/429) |
| 209 | get_or_create_stripe_account TOCTOU race creates duplicate rows | Bug | `backend/src/gym_api/services/stripe_service.py:11-24` | [#430](https://github.com/amattas/gym-app/issues/430) |
| 210 | Discount consumed but payment may fail -- non-atomic cross-service checkout | Bug | `backend/src/gym_api/routers/billing.py:117-147` | [#431](https://github.com/amattas/gym-app/issues/431) |
| 211 | get_db yields session without transaction wrapper -- no auto-rollback on multi-step failures | Bug | `backend/src/gym_api/database.py:14-16` | [#432](https://github.com/amattas/gym-app/issues/432) |
| 212 | Membership batch jobs load all rows without locking or batching with split commits | Bug | `backend/src/gym_api/services/membership_service.py:291-373` | [#433](https://github.com/amattas/gym-app/issues/433) |
| 213 | GraphQL clients/trainers/locations queries have zero result limit (DoS) | Security | `backend/src/gym_api/graphql/schema.py:84-105,129-147,238-259` | [#434](https://github.com/amattas/gym-app/issues/434) |
| 214 | GraphQL has no query depth or complexity limit -- alias amplification DoS | Security | `backend/src/gym_api/graphql/schema.py:262` | [#435](https://github.com/amattas/gym-app/issues/435) |
| 215 | GraphQL context does not verify user exists or is_active in database | Security | `backend/src/gym_api/routers/graphql_router.py:14-27` | [#436](https://github.com/amattas/gym-app/issues/436) |
| 216 | Invitation accept endpoint has no rate limiting -- brute-force token guessing | Security | `backend/src/gym_api/routers/invitations.py:43-86` | [#437](https://github.com/amattas/gym-app/issues/437) |
| 217 | Agreement send_envelope does not validate template_id/client_id belong to gym | Security | `backend/src/gym_api/services/esign_service.py:68-80` | [#438](https://github.com/amattas/gym-app/issues/438) |
| 218 | Stripe webhook invoice handlers have no gym_id scoping -- cross-tenant manipulation | Security | `backend/src/gym_api/routers/stripe_webhooks.py:95-125` | [#439](https://github.com/amattas/gym-app/issues/439) |
| 219 | Stripe webhook subscription.deleted uses unvalidated membership_id from metadata | Security | `backend/src/gym_api/routers/stripe_webhooks.py:130-149` | [#440](https://github.com/amattas/gym-app/issues/440) |
| 220 | Stripe webhook account.updated trusts arbitrary payload fields -- privilege escalation | Security | `backend/src/gym_api/routers/stripe_webhooks.py:54-73` | [#441](https://github.com/amattas/gym-app/issues/441) |
| 221 | Invitation accept creates user+trainer+accept in separate commits -- partial state | Bug | `backend/src/gym_api/routers/invitations.py:55-78` | [#442](https://github.com/amattas/gym-app/issues/442) |
| 222 | Agreement get_envelope endpoint missing gym_id tenant scoping (IDOR) | Security | `backend/src/gym_api/services/esign_service.py:83-91` | [#443](https://github.com/amattas/gym-app/issues/443) |
| 223 | Custom webhook delivery has no receiver-side replay protection | Security | `backend/src/gym_api/webhooks/webhook_service.py:33-42` | [#444](https://github.com/amattas/gym-app/issues/444) |
| 261 | Membership expiration date truncates day to 28 even when target month has 30-31 days | Bug | `backend/src/gym_api/services/membership_service.py:148-160` | [#482](https://github.com/amattas/gym-app/issues/482) |
| 262 | deduct_visit allows deductions from non-active memberships (no status check) | Bug | `backend/src/gym_api/services/membership_service.py:256-272` | [#483](https://github.com/amattas/gym-app/issues/483) |
| 263 | Schedule update uses 'or' fallback -- midnight times and explicit None defeated | Bug | `backend/src/gym_api/services/schedule_service.py:56-73` | [#484](https://github.com/amattas/gym-app/issues/484) |
| 264 | No schedule status transition validation -- completed/cancelled can be re-activated | Bug | `backend/src/gym_api/services/schedule_service.py:75-95` | [#485](https://github.com/amattas/gym-app/issues/485) |
| 265 | apply_discount fixed_amount multiplies by 100 creating ambiguous cents/dollars semantics | Bug | `backend/src/gym_api/services/discount_service.py:106-128` | [#486](https://github.com/amattas/gym-app/issues/486) |
| 266 | get_client_measurement_trend missing gym_id scoping -- cross-tenant data leak | Security | `backend/src/gym_api/services/analytics_service.py:85-110` | [#487](https://github.com/amattas/gym-app/issues/487) |
| 267 | note_service update_note and delete_note lack gym_id tenant scoping | Security | `backend/src/gym_api/services/note_service.py:45-75` | [#488](https://github.com/amattas/gym-app/issues/488) |
| 268 | pr_service.list_prs missing gym_id scoping -- cross-tenant PR data leakage | Security | `backend/src/gym_api/services/pr_service.py:30-45` | [#489](https://github.com/amattas/gym-app/issues/489) |
| 269 | Analytics router does not validate client belongs to requesting gym | Security | `backend/src/gym_api/routers/analytics.py:20-55` | [#490](https://github.com/amattas/gym-app/issues/490) |
| 270 | No Next.js middleware for auth -- protected pages served before client check | Security | `frontend/src/` (missing middleware.ts) | [#491](https://github.com/amattas/gym-app/issues/491) |
| 271 | Delete operation tests never verify the delete service function was called | Testing | `backend/tests/test_routers/test_billing.py` | [#492](https://github.com/amattas/gym-app/issues/492) |
| 272 | Filter/query parameter tests don't verify parameters forwarded to service | Testing | `backend/tests/test_routers/test_workouts.py`, `test_programs.py` | [#493](https://github.com/amattas/gym-app/issues/493) |
| 273 | Status transition tests don't verify correct status passed to service | Testing | `backend/tests/test_routers/test_schedules.py` | [#494](https://github.com/amattas/gym-app/issues/494) |
| 297 | user_sessions.last_used_at nullable mismatch -- model NOT NULL vs migration allows NULL | Bug | `backend/src/gym_api/models/session.py:20-21` | [#518](https://github.com/amattas/gym-app/issues/518) |
| 298 | client_memberships.base_membership_id missing FK and index -- addons unenforceable | Bug | `backend/src/gym_api/models/client_membership.py:47-48` | [#519](https://github.com/amattas/gym-app/issues/519) |
| 299 | rotate_refresh_token does not revoke on expiry -- token family stays active | Security | `backend/src/gym_api/services/auth_service.py:93-104` | [#520](https://github.com/amattas/gym-app/issues/520) |
| 300 | data_export/deletion compare UUID notable_id to string -- Notes never exported/anonymized | Bug | `backend/src/gym_api/services/data_export_service.py:124` | [#521](https://github.com/amattas/gym-app/issues/521) |
| 301 | pr_service.detect_rep_prs logic inverted -- 1-rep set records all PR thresholds | Bug | `backend/src/gym_api/services/pr_service.py:17-24` | [#522](https://github.com/amattas/gym-app/issues/522) |
| 302 | account_service.add_member/remove_member missing gym_id -- cross-tenant reassignment | Security | `backend/src/gym_api/services/account_service.py:43-73` | [#523](https://github.com/amattas/gym-app/issues/523) |
| 303 | trainer_client_service.assign_trainer missing gym_id -- cross-tenant assignment | Security | `backend/src/gym_api/services/trainer_client_service.py:12-39` | [#524](https://github.com/amattas/gym-app/issues/524) |
| 304 | process_pending_cancellations addon commit before parent -- inconsistent state on crash | Bug | `backend/src/gym_api/services/membership_service.py:331-355` | [#525](https://github.com/amattas/gym-app/issues/525) |
| 305 | Workout detail set rows onClick without keyboard accessibility (WCAG 2.1.1) | Accessibility | `frontend/src/app/(app)/workouts/[workoutId]/page.tsx:254-258` | [#526](https://github.com/amattas/gym-app/issues/526) |
| 306 | Goal delete button missing confirmation dialog | Usability | `frontend/src/app/(app)/goals/page.tsx:141-151` | [#527](https://github.com/amattas/gym-app/issues/527) |
| 307 | Schedule action buttons (cancel/complete/no-show) missing confirmation | Usability | `frontend/src/app/(app)/schedules/page.tsx:293-328` | [#528](https://github.com/amattas/gym-app/issues/528) |
| 308 | Goals Abandon button missing confirmation dialog | Usability | `frontend/src/app/(app)/goals/page.tsx:334-339` | [#529](https://github.com/amattas/gym-app/issues/529) |
| 309 | Missing PodDisruptionBudget -- voluntary disruptions can evict all pods | Infra | `k8s/` (missing PDB resource) | [#530](https://github.com/amattas/gym-app/issues/530) |
| 310 | K8s Deployment missing rolling update strategy -- stalls with 2 replicas | Infra | `k8s/deployment.yaml:7-11` | [#531](https://github.com/amattas/gym-app/issues/531) |
| 311 | K8s Deployment missing startupProbe -- slow cold starts cause CrashLoopBackOff | Infra | `k8s/deployment.yaml:38-49` | [#532](https://github.com/amattas/gym-app/issues/532) |
| 312 | Ingress missing ssl-redirect, rate-limit, proxy-body-size security annotations | Security | `k8s/ingress.yaml:5-7` | [#533](https://github.com/amattas/gym-app/issues/533) |
| 313 | Docker Compose missing JWT_SECRET -- api crashes immediately on startup | Config | `docker-compose.yml:7-9` | [#534](https://github.com/amattas/gym-app/issues/534) |
| 314 | CI pip-audit suppressed with \|\| true -- vulnerable deps never block merges | Security | `.github/workflows/ci.yml:66` | [#535](https://github.com/amattas/gym-app/issues/535) |
| 315 | NetworkPolicy blocks kubelet health probes -- pods stuck in NotReady | Infra | `k8s/network-policy.yaml:12-19` | [#536](https://github.com/amattas/gym-app/issues/536) |
| 316 | K8s missing ENFORCE_HTTPS and CORS_ALLOWED_ORIGINS -- HTTP served, CORS blocks frontend | Security | `k8s/deployment.yaml:22-37` | [#537](https://github.com/amattas/gym-app/issues/537) |
| 317 | Idempotency cache key no user identity -- cross-user cache poisoning | Security | `backend/src/gym_api/middleware/idempotency.py:62-70` | [#538](https://github.com/amattas/gym-app/issues/538) |
| 318 | PlanTemplateCreate/Update accept unvalidated dicts for critical config fields | Bug | `backend/src/gym_api/schemas/plan_template.py:12-15` | [#539](https://github.com/amattas/gym-app/issues/539) |
| 319 | StripeConnectCreate return_url/refresh_url have no URL validation | Security | `backend/src/gym_api/schemas/billing.py:8-9` | [#540](https://github.com/amattas/gym-app/issues/540) |
| 320 | CheckoutResponse exposes Stripe PaymentIntent client_secret in API response | Security | `backend/src/gym_api/schemas/billing.py:72` | [#543](https://github.com/amattas/gym-app/issues/543) |
| 321 | get_gym_context does not verify gym exists or is_active in database | Security | `backend/src/gym_api/dependencies/gym_scope.py:9-22` | [#541](https://github.com/amattas/gym-app/issues/541) |
| 322 | ClientUpdate allows arbitrary status string -- bypasses enum validation | Security | `backend/src/gym_api/schemas/client.py:31` | [#542](https://github.com/amattas/gym-app/issues/542) |
| 386 | ScheduleCreate model_dump passes status=None overriding SQLAlchemy default -- IntegrityError | Bug | `backend/src/gym_api/routers/schedules.py:34-36` | [#607](https://github.com/amattas/gym-app/issues/607) |
| 387 | Stripe webhook tests exercise zero handler logic -- all event branches untested | Testing | `backend/tests/test_routers/test_stripe_webhooks.py` | [#608](https://github.com/amattas/gym-app/issues/608) |
| 388 | Notes router missing update_note and delete_note test coverage | Testing | `backend/tests/test_routers/test_notes.py` | [#609](https://github.com/amattas/gym-app/issues/609) |
| 389 | GraphQL router and schema have zero test coverage -- no test file exists | Testing | `backend/tests/` (missing file) | [#610](https://github.com/amattas/gym-app/issues/610) |
| 390 | 34 of 43 service modules have zero direct unit tests -- all business logic untested | Testing | `backend/tests/test_services/` | [#611](https://github.com/amattas/gym-app/issues/611) |
| 391 | audit_logs test require_role override creates non-matching function object -- RBAC untested | Testing | `backend/tests/test_routers/test_audit_logs.py` | [#612](https://github.com/amattas/gym-app/issues/612) |
| 392 | Conftest provides no get_db override -- missing service mock causes real DB connection attempt | Testing | `backend/tests/conftest.py` | [#613](https://github.com/amattas/gym-app/issues/613) |
| 393 | Separate AuthProvider instances between app and login layouts -- auth state not shared | Bug | `frontend/src/app/(app)/layout.tsx`, `frontend/src/app/(auth)/layout.tsx` | [#614](https://github.com/amattas/gym-app/issues/614) |
| 394 | Login response missing expires_in and mfa_required fields per API spec | Spec Compliance | `backend/src/gym_api/routers/auth.py:144-151` | [#615](https://github.com/amattas/gym-app/issues/615) |
| 395 | MFA login uses inline code instead of spec's two-step session flow | Spec Compliance | `backend/src/gym_api/routers/auth.py:37-40,132-151` | [#616](https://github.com/amattas/gym-app/issues/616) |
| 396 | Check-in endpoint path uses /v1/check-ins instead of spec's /locations/{id}/check-in | Spec Compliance | `backend/src/gym_api/routers/check_ins.py:26-50` | [#617](https://github.com/amattas/gym-app/issues/617) |
| 397 | Active check-ins list endpoint not implemented per spec | Spec Compliance | `backend/src/gym_api/routers/check_ins.py` | [#618](https://github.com/amattas/gym-app/issues/618) |
| 398 | Exercises list missing category and muscle_group query filters per spec | Spec Compliance | `backend/src/gym_api/routers/exercises.py:42-52` | [#619](https://github.com/amattas/gym-app/issues/619) |
| 399 | Workout start spec endpoint not matched -- implementation splits into two calls | Spec Compliance | `backend/src/gym_api/routers/workouts.py` | [#620](https://github.com/amattas/gym-app/issues/620) |
| 400 | Account management endpoints substantially missing per spec (4+ endpoints) | Spec Compliance | `backend/src/gym_api/routers/accounts.py` | [#621](https://github.com/amattas/gym-app/issues/621) |
| 454 | Timing attack in authenticate_user leaks account existence via response latency | Security | `backend/src/gym_api/services/auth_service.py:69-76` | [#675](https://github.com/amattas/gym-app/issues/675) |
| 455 | Refresh token hashes use SHA256 without HMAC or salt -- rainbow table vulnerable | Security | `backend/src/gym_api/services/auth_service.py:20-21` | [#676](https://github.com/amattas/gym-app/issues/676) |
| 456 | subscription.updated webhook handler is empty -- subscription changes silently ignored | Bug | `backend/src/gym_api/routers/stripe_webhooks.py:127-128` | [#677](https://github.com/amattas/gym-app/issues/677) |
| 457 | No payment failure retry logic -- single decline permanently fails payment | Bug | `backend/src/gym_api/services/stripe_service.py:256-269` | [#678](https://github.com/amattas/gym-app/issues/678) |
| 458 | No currency validation or multi-currency support -- cross-currency charges possible | Bug | `backend/src/gym_api/models/invoice.py:50`, `stripe_service.py:180-219` | [#679](https://github.com/amattas/gym-app/issues/679) |
| 459 | Invoice.line_items field never populated -- all invoices lack itemized detail | Bug | `backend/src/gym_api/services/stripe_service.py:180-219` | [#680](https://github.com/amattas/gym-app/issues/680) |
| 460 | Soft-deleted clients still referenced by child records -- orphaned data accumulates | Bug | `backend/src/gym_api/services/client_service.py:82-85` | [#681](https://github.com/amattas/gym-app/issues/681) |
| 461 | Timezone-aware datetimes converted to naive dates in analytics -- DST misalignment | Bug | `backend/src/gym_api/services/analytics_service.py:139`, `check_in_service.py:85-88` | [#682](https://github.com/amattas/gym-app/issues/682) |
| 462 | Missing 'use client' directive in auth layout -- SSR hydration mismatch | Bug | `frontend/src/app/(auth)/layout.tsx` | [#683](https://github.com/amattas/gym-app/issues/683) |
| 463 | Date formatting uses browser locale without timezone -- inconsistent across users | Usability | Multiple frontend pages (workouts, memberships, billing, schedules) | [#684](https://github.com/amattas/gym-app/issues/684) |
| 464 | Filter state not persisted in URL params -- back button loses filters | Usability | `frontend/src/app/(app)/clients/page.tsx:31`, `exercises/page.tsx:51-52` | [#685](https://github.com/amattas/gym-app/issues/685) |
| 465 | Membership batch jobs N+1 on addon cascade -- connection pool exhaustion risk | Bug | `backend/src/gym_api/services/membership_service.py:225-244,331-355` | [#686](https://github.com/amattas/gym-app/issues/686) |
| 484 | Email send failures silently ignored in register/reset/resend endpoints | Bug | `backend/src/gym_api/routers/auth.py:127,232,291` | [#705](https://github.com/amattas/gym-app/issues/705) |
| 485 | Data export missing critical PII categories -- incomplete GDPR portability | Bug | `backend/src/gym_api/services/data_export_service.py:66-128` | [#706](https://github.com/amattas/gym-app/issues/706) |
| 486 | No audit logging of PII read access -- only mutations tracked | Security | `backend/src/gym_api/services/audit_service.py:10-62` | [#707](https://github.com/amattas/gym-app/issues/707) |
| 487 | Uvicorn has no explicit request timeout -- slowloris/resource exhaustion | Security | `backend/Dockerfile:21` | [#708](https://github.com/amattas/gym-app/issues/708) |
| 488 | Idempotency middleware cache lacks max size -- unbounded memory growth to OOM | Security | `backend/src/gym_api/middleware/idempotency.py:14-17,49-53` | [#709](https://github.com/amattas/gym-app/issues/709) |
| 489 | Deletion process orphans AI summaries and signed agreements -- incomplete erasure | Bug | `backend/src/gym_api/services/data_deletion_service.py:81-126` | [#710](https://github.com/amattas/gym-app/issues/710) |
| 509 | Signed documents lack tampering detection -- no content hash or checksum | Security | `backend/src/gym_api/models/agreement.py:30,60` | [#730](https://github.com/amattas/gym-app/issues/730) |
| 510 | No cryptographic commitment to signer identity -- email/name unverified | Security | `backend/src/gym_api/routers/agreements.py:95-105` | [#731](https://github.com/amattas/gym-app/issues/731) |
| 511 | Agreement template injection risk -- content rendered without sanitization | Security | `backend/src/gym_api/schemas/agreement.py:10-11` | [#732](https://github.com/amattas/gym-app/issues/732) |
| 512 | No audit trail for envelope signing operations | Security | `backend/src/gym_api/services/esign_service.py` | [#733](https://github.com/amattas/gym-app/issues/733) |
| 513 | GraphQL field-level authorization missing -- email/phone exposed to all roles | Security | `backend/src/gym_api/graphql/schema.py:24-127` | [#734](https://github.com/amattas/gym-app/issues/734) |
| 514 | GraphQL query batching DoS -- unlimited queries per single request | Security | `backend/src/gym_api/routers/graphql_router.py:30-34` | [#735](https://github.com/amattas/gym-app/issues/735) |
| 515 | Cache stampede -- no lock or stale-while-revalidate on cache expiry | Performance | `backend/src/gym_api/cache/cache_service.py:25-35` | [#736](https://github.com/amattas/gym-app/issues/736) |
| 516 | Seed script lacks production environment safeguards | Security | `backend/src/gym_api/scripts/seed.py:196-208` | [#737](https://github.com/amattas/gym-app/issues/737) |
| 517 | Cache key missing tenant/gym_id scoping -- cross-gym cache poisoning | Bug | `backend/src/gym_api/routers/programs.py:54`, `gyms.py:51` | [#738](https://github.com/amattas/gym-app/issues/738) |
| 518 | Loading spinners across 15+ pages have no accessible text or aria-busy | Accessibility | `frontend/src/app/(app)/layout.tsx:25`, 15+ pages | [#739](https://github.com/amattas/gym-app/issues/739) |
| 519 | Search input icons not labeled for screen readers | Accessibility | `frontend/src/app/(app)/clients/page.tsx:72-78` | [#740](https://github.com/amattas/gym-app/issues/740) |
| 533 | Pydantic model_validate() ValidationError not caught by middleware -- 500 instead of 422 | Bug | `backend/src/gym_api/routers/*.py` (130+ endpoints) | [#754](https://github.com/amattas/gym-app/issues/754) |
| 534 | Stripe webhook malformed JSON body not caught -- crashes with 500 | Bug | `backend/src/gym_api/routers/stripe_webhooks.py:50` | [#755](https://github.com/amattas/gym-app/issues/755) |
| 535 | Database commit failures unhandled in auth endpoints -- IntegrityError crashes | Bug | `backend/src/gym_api/routers/auth.py:170,186,261,278` | [#756](https://github.com/amattas/gym-app/issues/756) |
| 536 | Database commit failures unhandled across all stripe service operations | Bug | `backend/src/gym_api/services/stripe_service.py:22,42,54,69,79,97,114,154` | [#757](https://github.com/amattas/gym-app/issues/757) |
| 537 | PUT endpoints use partial update semantics -- HTTP method confusion | Bug | `backend/src/gym_api/routers/clients.py:106`, `goals.py:68`, `notes.py:105` | [#758](https://github.com/amattas/gym-app/issues/758) |
| 538 | Auth login/refresh endpoints return bare objects instead of {data:...} envelope | Bug | `backend/src/gym_api/routers/auth.py:132-161` | [#759](https://github.com/amattas/gym-app/issues/759) |
| 539 | Frontend next.config.ts completely empty -- no headers, domains, or output config | Bug | `frontend/next.config.ts:3-5` | [#760](https://github.com/amattas/gym-app/issues/760) |
| 558 | Usage metering period range filtering is backwards -- partial overlaps excluded | Bug | `backend/src/gym_api/services/usage_metering_service.py:59-62` | [#779](https://github.com/amattas/gym-app/issues/779) |
| 559 | AI summary date range calculation causes incorrect workout frequency | Bug | `backend/src/gym_api/services/ai_summary_service.py:152-155` | [#780](https://github.com/amattas/gym-app/issues/780) |
| 560 | Analytics volume trend treats NULL completed as True -- inflates stats | Bug | `backend/src/gym_api/services/analytics_service.py:157` | [#781](https://github.com/amattas/gym-app/issues/781) |
| 561 | No gym_id isolation in client invitation acceptance | Security | `backend/src/gym_api/services/client_invitation_service.py:38-53` | [#782](https://github.com/amattas/gym-app/issues/782) |
| 562 | Missing email verification during trainer onboarding via invitation | Security | `backend/src/gym_api/routers/invitations.py:43-86` | [#783](https://github.com/amattas/gym-app/issues/783) |
| 563 | Dialog forms don't reset state on close -- stale data on reopen (4 dialogs) | Bug | Multiple frontend dialog components | [#784](https://github.com/amattas/gym-app/issues/784) |
| 564 | Invoice/Payment monetary model fields allow negative values -- no check constraints | Bug | `backend/src/gym_api/models/invoice.py:45-49,77` | [#785](https://github.com/amattas/gym-app/issues/785) |
| 565 | StripeAccount.processing_fee_percentage has no bounds -- allows negative or >100% | Bug | `backend/src/gym_api/models/stripe_account.py:35` | [#786](https://github.com/amattas/gym-app/issues/786) |
| 566 | Trainer deactivation doesn't cascade to user -- deactivated trainers retain login | Bug | `backend/src/gym_api/models/trainer.py:25`, `trainer_service.py:42-48` | [#787](https://github.com/amattas/gym-app/issues/787) |
| 582 | Idempotency middleware TOCTOU race -- concurrent duplicate requests both execute | Bug | `backend/src/gym_api/middleware/idempotency.py:30-38` | [#803](https://github.com/amattas/gym-app/issues/803) |
| 583 | Exercise cache serves cross-tenant data -- cached response bypasses gym_id auth check | Security | `backend/src/gym_api/routers/exercises.py:53-56` | [#804](https://github.com/amattas/gym-app/issues/804) |
| 584 | Program cached response returned before gym_id authorization check | Security | `backend/src/gym_api/routers/programs.py:54-57` | [#805](https://github.com/amattas/gym-app/issues/805) |
| 585 | Gym cached response returned to any gym_admin without ownership verification | Security | `backend/src/gym_api/routers/gyms.py:51-54` | [#806](https://github.com/amattas/gym-app/issues/806) |
| 586 | Cursor pagination timestamp collision -- duplicates and skips when created_at values match | Bug | `backend/src/gym_api/utils/pagination.py:41-44` | [#807](https://github.com/amattas/gym-app/issues/807) |
| 587 | Cursor decode unhandled ValueError -- invalid cursor causes 500 instead of 400 | Bug | `backend/src/gym_api/utils/pagination.py:28-39` | [#808](https://github.com/amattas/gym-app/issues/808) |
| 588 | Cursor timezone-aware vs naive datetime mismatch in fromisoformat | Bug | `backend/src/gym_api/utils/pagination.py:35` | [#809](https://github.com/amattas/gym-app/issues/809) |
| 589 | Batch jobs load ALL memberships across ALL gyms without LIMIT -- OOM risk | Performance | `backend/src/gym_api/services/membership_service.py:291-373` | [#810](https://github.com/amattas/gym-app/issues/810) |
| 590 | get_client_volume_trend loads all workouts unbounded then N+1 loops | Performance | `backend/src/gym_api/services/analytics_service.py:118-166` | [#811](https://github.com/amattas/gym-app/issues/811) |
| 591 | generate_export_data loads ALL client data across 6 entity types -- OOM risk | Performance | `backend/src/gym_api/services/data_export_service.py:66-128` | [#812](https://github.com/amattas/gym-app/issues/812) |
| 592 | Storage backend implementations never wired in -- all upload/download dead code | Bug | `backend/src/gym_api/storage/s3_storage.py`, `local_storage.py`, `storage_service.py` | [#813](https://github.com/amattas/gym-app/issues/813) |
| 593 | Progress photo storage_key accepts arbitrary path -- path traversal vulnerability | Security | `backend/src/gym_api/routers/progress_photos.py:18` | [#814](https://github.com/amattas/gym-app/issues/814) |
| 594 | Progress photo create does not verify client_id belongs to requesting gym | Security | `backend/src/gym_api/routers/progress_photos.py:42-54` | [#815](https://github.com/amattas/gym-app/issues/815) |
| 595 | S3Storage upload missing server-side encryption and private ACL | Security | `backend/src/gym_api/storage/s3_storage.py:30-44` | [#816](https://github.com/amattas/gym-app/issues/816) |
| 596 | Frontend progress photo delete calls wrong URL -- every delete 404 | Integration | `frontend/src/app/(app)/progress-photos/page.tsx:93-94` | [#817](https://github.com/amattas/gym-app/issues/817) |
| 597 | Frontend progress photos page has no file input -- metadata-only form | Bug | `frontend/src/app/(app)/progress-photos/page.tsx:149-193` | [#818](https://github.com/amattas/gym-app/issues/818) |
| 598 | Storage backends accept unlimited upload data size -- no file size validation | Security | `backend/src/gym_api/storage/storage_service.py:5-8`, `s3_storage.py:30-44` | [#819](https://github.com/amattas/gym-app/issues/819) |
| 599 | No logging for auth-critical operations -- logins, resets, MFA untraced | Security | `backend/src/gym_api/routers/auth.py:132-262` | [#820](https://github.com/amattas/gym-app/issues/820) |
| 645 | Webhook/job/cache async tests missing pytest.mark.asyncio -- 19 tests may silently not execute | Testing | `backend/tests/test_services/test_webhook_service.py`, `test_jobs.py`, `test_cache_service.py` | [#866](https://github.com/amattas/gym-app/issues/866) |
| 646 | Auth override always uses gym_admin role -- entire RBAC system untested per-endpoint | Testing | `backend/tests/test_routers/test_workouts.py:62-66` and 15+ files | [#867](https://github.com/amattas/gym-app/issues/867) |
| 647 | All test factories use SimpleNamespace -- Pydantic model_validate and response shape untested | Testing | `backend/tests/test_routers/helpers.py:7-23`, all _make_* factories | [#868](https://github.com/amattas/gym-app/issues/868) |
| 648 | Migration missing server_default for 25+ boolean NOT NULL columns -- non-ORM inserts fail | Data Integrity | `backend/alembic/versions/001_initial_schema.py` (25+ lines) | [#869](https://github.com/amattas/gym-app/issues/869) |
| 649 | Migration missing server_default for integer NOT NULL columns -- visits_used and times_used | Data Integrity | `backend/alembic/versions/001_initial_schema.py:506,968` | [#870](https://github.com/amattas/gym-app/issues/870) |
| 650 | client_goals.created_by_trainer_id missing FK constraint in migration | Data Integrity | `backend/alembic/versions/001_initial_schema.py:623` | [#871](https://github.com/amattas/gym-app/issues/871) |
| 651 | client_programs.assigned_by_trainer_id missing FK constraint in migration | Data Integrity | `backend/alembic/versions/001_initial_schema.py:640` | [#872](https://github.com/amattas/gym-app/issues/872) |
| 652 | client_memberships.base_membership_id missing self-referential FK in migration | Data Integrity | `backend/alembic/versions/001_initial_schema.py:512` | [#873](https://github.com/amattas/gym-app/issues/873) |
| 653 | AuthGuard useEffect race condition -- child pages fire API calls before auth check | Security | `frontend/src/app/(app)/layout.tsx:16-20` | [#874](https://github.com/amattas/gym-app/issues/874) |
| 654 | No role-based route protection -- all authenticated users access all admin pages | Security | `frontend/src/app/(app)/layout.tsx:12-33` | [#875](https://github.com/amattas/gym-app/issues/875) |
| 655 | Memberships sub-routes (/plans, /assign) not linked from UI -- unreachable pages | Bug | `frontend/src/app/(app)/memberships/plans/page.tsx`, `assign/page.tsx` | [#876](https://github.com/amattas/gym-app/issues/876) |
| 656 | Stripe webhook handlers bypass service layer -- direct model manipulation | Bug | `backend/src/gym_api/routers/stripe_webhooks.py:54-73,130-149` | [#877](https://github.com/amattas/gym-app/issues/877) |
| 657 | Billing checkout partial commits -- orphaned pending membership on failure | Bug | `backend/src/gym_api/routers/billing.py:150-195` | [#878](https://github.com/amattas/gym-app/issues/878) |
| 658 | No notification/email on membership state changes -- pause, cancel, expire silent | Bug | `backend/src/gym_api/services/membership_service.py:150-222` | [#879](https://github.com/amattas/gym-app/issues/879) |
| 659 | Trainer invitation never sends email -- setup link only in API response | Bug | `backend/src/gym_api/routers/invitations.py:22-40` | [#880](https://github.com/amattas/gym-app/issues/880) |
| 697 | handle_payment_failure no terminal-state guard -- overwrites succeeded payments | Bug | `backend/src/gym_api/services/stripe_service.py:256-269` | [#918](https://github.com/amattas/gym-app/issues/918) |
| 698 | subscription.deleted webhook cancels membership regardless of current status | Bug | `backend/src/gym_api/routers/stripe_webhooks.py:130-149` | [#919](https://github.com/amattas/gym-app/issues/919) |
| 699 | Paused memberships never expire -- process_expired only checks active status | Bug | `backend/src/gym_api/services/membership_service.py:314-328` | [#920](https://github.com/amattas/gym-app/issues/920) |
| 700 | Exercises/sets can be added to completed or cancelled workouts -- no status guard | Bug | `backend/src/gym_api/routers/workouts.py:84-134` | [#921](https://github.com/amattas/gym-app/issues/921) |
| 701 | WorkoutUpdate PATCH bypasses start/complete lifecycle via direct status injection | Security | `backend/src/gym_api/routers/workouts.py:67-81` | [#922](https://github.com/amattas/gym-app/issues/922) |
| 702 | Reporting dashboard 'today' metrics use UTC midnight -- wrong for non-UTC gyms | Bug | `backend/src/gym_api/services/reporting_service.py:23,50-56,76-83` | [#923](https://github.com/amattas/gym-app/issues/923) |
| 703 | Busyness service day boundaries use UTC midnight -- slots misaligned for local gyms | Bug | `backend/src/gym_api/services/busyness_service.py:18,60-61` | [#924](https://github.com/amattas/gym-app/issues/924) |
| 704 | Schedule list date filter uses UTC midnight -- sessions near day boundaries on wrong day | Bug | `backend/src/gym_api/services/schedule_service.py:59-64` | [#925](https://github.com/amattas/gym-app/issues/925) |
| 705 | GraphQL resolvers bypass service layer -- all 7 queries use direct DB access | Bug | `backend/src/gym_api/graphql/schema.py:82-259` | [#926](https://github.com/amattas/gym-app/issues/926) |
| 706 | GraphQL trainers query returns deactivated trainers -- missing is_active filter | Bug | `backend/src/gym_api/graphql/schema.py:129-147` | [#927](https://github.com/amattas/gym-app/issues/927) |
| 707 | GraphQL resolvers create independent DB sessions -- bypass per-request management | Bug | `backend/src/gym_api/graphql/schema.py:88,111,134,157,184,211,243` | [#928](https://github.com/amattas/gym-app/issues/928) |
| 708 | GraphQL user_id never validated in resolvers -- any JWT can query any gym | Security | `backend/src/gym_api/routers/graphql_router.py:24-25` | [#929](https://github.com/amattas/gym-app/issues/929) |
| 709 | GraphQL client (singular) query returns soft-deleted clients | Bug | `backend/src/gym_api/graphql/schema.py:107-127` | [#930](https://github.com/amattas/gym-app/issues/930) |
| 710 | Stripe webhook router has no error handling -- exceptions cause 500 triggering retries | Bug | `backend/src/gym_api/routers/stripe_webhooks.py:75-149` | [#931](https://github.com/amattas/gym-app/issues/931) |
| 741 | Middleware stack ordering -- ErrorHandler inside RateLimiter/Idempotency produces raw 500 | Bug | `backend/src/gym_api/main.py:108-112` | [#962](https://github.com/amattas/gym-app/issues/962) |
| 742 | HTTPSRedirectMiddleware blocks K8s health probes behind TLS-terminating proxies | Integration | `backend/src/gym_api/middleware/https_redirect.py:7-9` | [#963](https://github.com/amattas/gym-app/issues/963) |
| 743 | Rate limiter Redis INCR/EXPIRE non-atomic -- key can persist without TTL permanently | Bug | `backend/src/gym_api/middleware/rate_limiter.py:73-76` | [#964](https://github.com/amattas/gym-app/issues/964) |
| 744 | AI summary update endpoint missing gym_id tenant scoping (IDOR) | Security | `backend/src/gym_api/routers/ai_summaries.py:57-68` | [#965](https://github.com/amattas/gym-app/issues/965) |
| 745 | AI summary generation queries 5 tables without gym_id -- cross-tenant data leak | Security | `backend/src/gym_api/services/ai_summary_service.py:87-171` | [#966](https://github.com/amattas/gym-app/issues/966) |
| 746 | Payment method add/list endpoints accept arbitrary account_id without gym verification | Security | `backend/src/gym_api/routers/billing.py:82-102` | [#967](https://github.com/amattas/gym-app/issues/967) |
| 747 | handle_payment_failure missing gym_id -- cross-tenant payment manipulation | Security | `backend/src/gym_api/services/stripe_service.py:256-269` | [#968](https://github.com/amattas/gym-app/issues/968) |
| 748 | Deletion request get/cancel missing gym_id -- cross-tenant deletion manipulation | Security | `backend/src/gym_api/services/data_deletion_service.py:36-54` | [#969](https://github.com/amattas/gym-app/issues/969) |
| 749 | Programs detail page race condition -- rapid day selection overwrites exercises | Bug | `frontend/src/app/(app)/programs/[programId]/page.tsx:58-70` | [#970](https://github.com/amattas/gym-app/issues/970) |
| 791 | Scheduler shutdown(wait=False) kills running jobs mid-execution -- partial state | Bug | `backend/src/gym_api/main.py:83` | [#1012](https://github.com/amattas/gym-app/issues/1012) |
| 792 | Export/deletion requests stuck in processing state permanently after process crash | Bug | `services/data_export_service.py:138-139`, `data_deletion_service.py:68-69` | [#1013](https://github.com/amattas/gym-app/issues/1013) |
| 793 | detect_prs executes 2N+1 sequential queries per workout completion | Performance | `backend/src/gym_api/services/workout_service.py:150-201` | [#1014](https://github.com/amattas/gym-app/issues/1014) |
| 794 | stripe_service list_invoices and list_payments have no LIMIT -- unbounded | Performance | `backend/src/gym_api/services/stripe_service.py:130-147,167-177` | [#1015](https://github.com/amattas/gym-app/issues/1015) |
| 795 | UserNav avatar button missing accessible label | Accessibility | `frontend/src/components/user-nav.tsx:26-29` | [#1016](https://github.com/amattas/gym-app/issues/1016) |
| 796 | Exercise card edit/delete icon-only buttons missing aria-label | Accessibility | `frontend/src/app/(app)/exercises/page.tsx:230-245` | [#1017](https://github.com/amattas/gym-app/issues/1017) |
| 797 | New workout set inputs (Weight, Reps) have no label or aria-label | Accessibility | `frontend/src/app/(app)/workouts/new/page.tsx:235-254` | [#1018](https://github.com/amattas/gym-app/issues/1018) |
| 798 | 10+ backend list endpoints missing cursor pagination -- unbounded arrays | Spec Compliance | `routers/custom_domains.py`, `billing.py`, `accounts.py`, `goals.py`, `workouts.py`, `schedules.py`, `analytics.py` | [#1019](https://github.com/amattas/gym-app/issues/1019) |
| 837 | Email service tests missing pytest.mark.asyncio -- 3 async tests silently skip | Testing | `backend/tests/test_services/test_email_service.py:28,37,46` | [#1058](https://github.com/amattas/gym-app/issues/1058) |
| 838 | Local storage tests missing pytest.mark.asyncio -- 6 async tests silently skip | Testing | `backend/tests/test_services/test_local_storage.py:13,22,27,33,38,43` | [#1059](https://github.com/amattas/gym-app/issues/1059) |
| 839 | test_path_traversal_prevented has flawed assertions -- traversal could pass | Testing | `backend/tests/test_services/test_local_storage.py:43-50` | [#1060](https://github.com/amattas/gym-app/issues/1060) |
| 840 | Zero Pydantic 422 validation tests across entire router test suite | Testing | All `backend/tests/test_routers/test_*.py` | [#1061](https://github.com/amattas/gym-app/issues/1061) |
| 841 | test_readiness does not assert HTTP status code -- 200-on-degraded undetected | Testing | `backend/tests/test_routers/test_health.py:36-52` | [#1062](https://github.com/amattas/gym-app/issues/1062) |
| 852 | Dockerfile missing alembic.ini and pyproject.toml in runtime image | Infra | `backend/Dockerfile:15,17-18` | [#1063](https://github.com/amattas/gym-app/issues/1063) |
| 853 | CI backend-test never runs Alembic migrations -- migration correctness untested | Config | `.github/workflows/ci.yml:96-105` | [#1064](https://github.com/amattas/gym-app/issues/1064) |
| 854 | Alembic env.py no advisory lock -- concurrent pod startups race on migrations | Config | `backend/alembic/env.py:33-47` | [#1065](https://github.com/amattas/gym-app/issues/1065) |
| 855 | CI missing aggregation gate job for conditional workflows | Config | `.github/workflows/ci.yml` | [#1066](https://github.com/amattas/gym-app/issues/1066) |
| 891 | unpause_membership destroys trial metadata by setting pause_info=None | Bug | `backend/src/gym_api/services/membership_service.py:183` | [#1067](https://github.com/amattas/gym-app/issues/1067) |
| 902 | GraphQL _require_gym_access raises bare PermissionError -- not HTTP 403 | Security | `backend/src/gym_api/graphql/schema.py:20` | [#1123](https://github.com/amattas/gym-app/issues/1123) |
| 907 | Rate limiter uses request.client.host behind reverse proxy -- rate-limits proxy IP | Security | `backend/src/gym_api/middleware/rate_limiter.py:29` | [#1128](https://github.com/amattas/gym-app/issues/1128) |
| 914 | Passkey service entirely dead code -- no router imports or invokes it | Integration | `backend/src/gym_api/services/passkey_service.py:1-118` | [#1135](https://github.com/amattas/gym-app/issues/1135) |
| 915 | Passkey service missing verify_authentication_response -- login impossible | Bug | `backend/src/gym_api/services/passkey_service.py:57-86` | [#1136](https://github.com/amattas/gym-app/issues/1136) |
| 928 | Session pack creates committed membership before payment -- orphaned on failure | Bug | `backend/src/gym_api/routers/billing.py:168-194` | [#1149](https://github.com/amattas/gym-app/issues/1149) |
| 929 | Session pack purchase no client_id-to-gym verification -- cross-tenant creation | Security | `backend/src/gym_api/routers/billing.py:150-177` | [#1150](https://github.com/amattas/gym-app/issues/1150) |
| 930 | All 17 billing endpoints missing RBAC -- any role can manage Stripe/discounts | Security | `backend/src/gym_api/routers/billing.py:38-322` | [#1151](https://github.com/amattas/gym-app/issues/1151) |
| 932 | Checkout/session-pack never verify Stripe onboarding or charges_enabled | Bug | `backend/src/gym_api/routers/billing.py:117-195` | [#1153](https://github.com/amattas/gym-app/issues/1153) |
| 945 | Stripe webhook subscription.deleted string membership_id -- UUID compare fails | Bug | `backend/src/gym_api/routers/stripe_webhooks.py:130-149` | [#1166](https://github.com/amattas/gym-app/issues/1166) |
| 955 | PaymentMethod model has no gym_id column -- tenant isolation impossible | Security | `backend/src/gym_api/models/payment_method.py:11-29` | [#1176](https://github.com/amattas/gym-app/issues/1176) |
| 958 | ClientProgram model missing gym_id column -- no tenant isolation for programs | Data Integrity | `backend/src/gym_api/models/client_program.py` | [#1179](https://github.com/amattas/gym-app/issues/1179) |
| 962 | stripe_connect_id missing UNIQUE constraint -- duplicate Stripe accounts | Data Integrity | `backend/src/gym_api/models/stripe_connect_account.py` | [#1183](https://github.com/amattas/gym-app/issues/1183) |
| 963 | stripe_payment_intent_id missing UNIQUE constraint -- duplicate payments | Data Integrity | `backend/src/gym_api/models/payment.py` | [#1184](https://github.com/amattas/gym-app/issues/1184) |
| 971 | Measurements page reads measurement_type but response has type -- display broken | Integration | `frontend/src/app/(app)/measurements/page.tsx:37,114` | [#1192](https://github.com/amattas/gym-app/issues/1192) |
| 972 | Settings page field mismatch: email/phone vs contact_email/contact_phone | Integration | `frontend/src/app/(app)/settings/page.tsx:15-16,50-51` ↔ `backend/src/gym_api/schemas/gym.py:17-23` | [#1193](https://github.com/amattas/gym-app/issues/1193) |
| 973 | Trainers page field mismatch: specialties (array) vs specializations (string) | Integration | `frontend/src/app/(app)/trainers/page.tsx:21` ↔ `backend/src/gym_api/schemas/trainer.py:27` | [#1194](https://github.com/amattas/gym-app/issues/1194) |
| 974 | Client detail page reads measurement_type but response has type | Integration | `frontend/src/app/(app)/clients/[clientId]/page.tsx:37,196` | [#1195](https://github.com/amattas/gym-app/issues/1195) |
| 975 | Schedule create form requires raw UUID text input for Client/Trainer/Location | Usability | `frontend/src/app/(app)/schedules/page.tsx:147-168` | [#1197](https://github.com/amattas/gym-app/issues/1197) |
| 976 | Schedules/programs show truncated UUIDs instead of human-readable names | Usability | `frontend/src/app/(app)/schedules/page.tsx:277-281`, `programs/[programId]/page.tsx:185` | [#1198](https://github.com/amattas/gym-app/issues/1198) |
| 977 | get_active_occupancy counts all-time unchecked-out entries -- stale check-ins inflate count | Bug | `backend/src/gym_api/services/check_in_service.py:107-117` | [#1217](https://github.com/amattas/gym-app/issues/1217) |
| 978 | create_schedule skips double-booking check when trainer_id/start/end is missing | Bug | `backend/src/gym_api/services/schedule_service.py:17-23` | [#1223](https://github.com/amattas/gym-app/issues/1223) |
| 979 | _check_double_booking does not consult TrainerException records | Bug | `backend/src/gym_api/services/schedule_service.py:163-179` | [#1224](https://github.com/amattas/gym-app/issues/1224) |
| 980 | get_device has no user_id ownership check -- any device token readable by ID | Security | `backend/src/gym_api/services/notification_service.py:24-28` | [#1226](https://github.com/amattas/gym-app/issues/1226) |
| 981 | _anonymize_client_data does not clear address/DOB/emergency_contact PII fields | Bug (GDPR) | `backend/src/gym_api/services/data_deletion_service.py:89-95` | [#1232](https://github.com/amattas/gym-app/issues/1232) |
| 982 | _anonymize_client_data inner commit flushes outer dirty state prematurely | Bug | `backend/src/gym_api/services/data_deletion_service.py:126,67-77` | [#1234](https://github.com/amattas/gym-app/issues/1234) |
| 983 | Test route pollution -- app.include_router at import time permanently adds routes | Testing | Multiple `backend/tests/test_routers/test_*.py` files | [#1235](https://github.com/amattas/gym-app/issues/1235) |
| 984 | No integration tests exist -- all router tests mock entire service layer | Testing | All `backend/tests/test_routers/` files | [#1237](https://github.com/amattas/gym-app/issues/1237) |
| 985 | All backend dependencies unpinned -- no lock file for deterministic builds | Infra | `backend/pyproject.toml` | [#1239](https://github.com/amattas/gym-app/issues/1239) |
| 1037 | CORS middleware registered first runs last -- error responses lack CORS headers | Bug | `backend/src/gym_api/main.py:98-112` | [#1258](https://github.com/amattas/gym-app/issues/1258) |
| 1038 | APScheduler >=3.10.0 allows v4 install -- incompatible API crashes on import | Config | `backend/pyproject.toml:20`, `backend/src/gym_api/jobs/scheduler.py:3` | [#1259](https://github.com/amattas/gym-app/issues/1259) |
| 1102 | Webhook delivery retry blocks request path with up to 36s synchronous sleep | Performance | `backend/src/gym_api/webhooks/webhook_service.py` | [#1322](https://github.com/amattas/gym-app/issues/1322) |
| 1103 | No signing token/link security mechanism for external signers | Security | `backend/src/gym_api/services/esign_service.py`, `backend/src/gym_api/routers/agreements.py` | [#1331](https://github.com/amattas/gym-app/issues/1331) |
| 1104 | No signature capture or storage mechanism in e-sign model | Missing Functionality | `backend/src/gym_api/models/agreement.py`, `backend/src/gym_api/services/esign_service.py` | [#1332](https://github.com/amattas/gym-app/issues/1332) |
| 1105 | No role-based access control on agreement endpoints | Security | `backend/src/gym_api/routers/agreements.py` | [#1334](https://github.com/amattas/gym-app/issues/1334) |
| 1106 | Dark mode CSS fully defined but ThemeProvider never wired up | Bug | `frontend/src/app/layout.tsx`, `frontend/src/app/globals.css` | [#1341](https://github.com/amattas/gym-app/issues/1341) |
| 1107 | Complete workout + PR detection spans multiple commits -- partial PRs on failure | Data Integrity | `backend/src/gym_api/routers/workouts.py:167-188`, `backend/src/gym_api/services/pr_service.py` | [#1353](https://github.com/amattas/gym-app/issues/1353) |
| 1141 | response_model=dict on all endpoints bypasses Pydantic response validation | Testing | All backend routers | [#1365](https://github.com/amattas/gym-app/issues/1365) |
| 1142 | All created_at/updated_at columns missing nullable=False in migration | Data Integrity | `backend/alembic/versions/001_initial_schema.py` | [#1367](https://github.com/amattas/gym-app/issues/1367) |
| 1143 | No ON DELETE CASCADE rules on any of 50+ foreign key constraints | Data Integrity | `backend/alembic/versions/001_initial_schema.py` | [#1368](https://github.com/amattas/gym-app/issues/1368) |
| 1144 | No cross-tab auth state synchronization -- stale sessions in other tabs | Security | `frontend/src/lib/auth.tsx` | [#1371](https://github.com/amattas/gym-app/issues/1371) |
| 1145 | No file type validation or MIME type verification in storage | Security | `backend/src/gym_api/storage/storage_service.py` | [#1380](https://github.com/amattas/gym-app/issues/1380) |
| 1146 | Stored files not cleaned up on photo deletion -- GDPR violation | Bug | `backend/src/gym_api/services/progress_photo_service.py:40-42` | [#1381](https://github.com/amattas/gym-app/issues/1381) |
| 1147 | Rate limiter path mismatch -- /v1/auth/password-reset vs actual /v1/auth/reset-password | Security | `backend/src/gym_api/middleware/rate_limiter.py:14-19` | [#1388](https://github.com/amattas/gym-app/issues/1388) |
| 1170 | Rate limiter extracts JWT identity without verifying signature | Security | `backend/src/gym_api/middleware/rate_limiter.py` | [#1391](https://github.com/amattas/gym-app/issues/1391) |
| 1171 | Discount application can produce negative invoice total — no floor at zero | Bug | `backend/src/gym_api/services/discount_service.py` | [#1392](https://github.com/amattas/gym-app/issues/1392) |
| 1172 | Data export queries lack gym_id filter on child tables — cross-tenant data leak | Security | `backend/src/gym_api/services/data_export_service.py` | [#1393](https://github.com/amattas/gym-app/issues/1393) |
| 1173 | Data deletion _anonymize can destroy records across tenant boundaries | Security | `backend/src/gym_api/services/data_deletion_service.py` | [#1394](https://github.com/amattas/gym-app/issues/1394) |
| 1174 | Workout set delete/update endpoints lack ownership verification | Security | `backend/src/gym_api/services/workout_service.py` | [#1395](https://github.com/amattas/gym-app/issues/1395) |
| 1194 | 8 update_* services block clearing nullable fields to NULL | Bug | `backend/src/gym_api/services/*.py` | [#1415](https://github.com/amattas/gym-app/issues/1415) |
| 1195 | Note update/delete has no author ownership check | Security | `backend/src/gym_api/services/note_service.py:55-67` | [#1416](https://github.com/amattas/gym-app/issues/1416) |
| 1196 | GoalUpdate.status accepts arbitrary strings — not constrained to enum | Bug | `backend/src/gym_api/schemas/goal.py:21` | [#1417](https://github.com/amattas/gym-app/issues/1417) |
| 1197 | AccountCreate/Update account_type accepts arbitrary string — bypasses enum | Security | `backend/src/gym_api/schemas/account.py:7-10` | [#1418](https://github.com/amattas/gym-app/issues/1418) |
| 1198 | ProgramCreate/Update template_scope unvalidated — invalid enum causes 500 | Bug | `backend/src/gym_api/schemas/program.py:10` | [#1419](https://github.com/amattas/gym-app/issues/1419) |
| 1199 | Child resource creation (goals/notes/photos) does not verify client_id | Bug | `backend/src/gym_api/routers/goals.py:23-34` | [#1420](https://github.com/amattas/gym-app/issues/1420) |
| 1200 | Location soft-delete does not cascade to schedules/check-ins | Bug | `backend/src/gym_api/services/location_service.py:56-58` | [#1421](https://github.com/amattas/gym-app/issues/1421) |
| 1201 | 6 schedule mutation endpoints don't capture user identity for audit | Security | `backend/src/gym_api/routers/schedules.py:63-148` | [#1422](https://github.com/amattas/gym-app/issues/1422) |
| 1202 | 6 client-program endpoints missing get_gym_context at router level | Security | `backend/src/gym_api/routers/goals.py:96-170` | [#1423](https://github.com/amattas/gym-app/issues/1423) |
| 1203 | 4 trainer availability/exception endpoints missing get_gym_context | Security | `backend/src/gym_api/routers/schedules.py:151-196` | [#1424](https://github.com/amattas/gym-app/issues/1424) |
| 1204 | get_envelope is only agreement endpoint without get_gym_context — IDOR | Security | `backend/src/gym_api/routers/agreements.py:127-136` | [#1426](https://github.com/amattas/gym-app/issues/1426) |
| 1205 | delete_measurement router has gym_id but never passes to service | Security | `backend/src/gym_api/routers/measurements.py:73-74` | [#1427](https://github.com/amattas/gym-app/issues/1427) |
| 1206 | Exercises page handleDelete uses stale closure — data loss | Bug | `frontend/src/app/(app)/exercises/page.tsx:131-135` | [#1429](https://github.com/amattas/gym-app/issues/1429) |
| 1207 | 8 business-critical timestamp columns missing nullable=False in migration | Data Integrity | `backend/alembic/versions/001_initial_schema.py` | [#1435](https://github.com/amattas/gym-app/issues/1435) |
| 1208 | client_programs table has no gym_id column — multi-tenancy gap | Security | `backend/src/gym_api/models/client_program.py` | [#1436](https://github.com/amattas/gym-app/issues/1436) |

## Medium

| # | Title | Category | File(s) | GH Issue |
|---|-------|----------|---------|----------|
| 21 | Silent exception swallowing in data deletion job | Bug | `backend/src/gym_api/services/data_deletion_service.py:70-77` | [#242](https://github.com/amattas/gym-app/issues/242) |
| 22 | Silent exception in data export job | Bug | `backend/src/gym_api/services/data_export_service.py:141-148` | [#243](https://github.com/amattas/gym-app/issues/243) |
| 23 | GraphQL plan_type.value called on string field (AttributeError) | Bug | `backend/src/gym_api/graphql/schema.py:224-227` | [#244](https://github.com/amattas/gym-app/issues/244) |
| 24 | GraphQL queries hardcode limit(100) with no pagination | Bug | `backend/src/gym_api/graphql/schema.py:161,188,219` | [#245](https://github.com/amattas/gym-app/issues/245) |
| 25 | Dashboard silently swallows API errors showing zero stats | Usability | `frontend/src/app/(app)/dashboard/page.tsx:20-34` | [#246](https://github.com/amattas/gym-app/issues/246) |
| 26 | Missing accessible label associations on check-in filters | Accessibility | `frontend/src/app/(app)/check-ins/page.tsx:185-210` | [#247](https://github.com/amattas/gym-app/issues/247) |
| 27 | Non-keyboard-accessible day selection in programs | Accessibility | `frontend/src/app/(app)/programs/[programId]/page.tsx:142-157` | [#248](https://github.com/amattas/gym-app/issues/248) |
| 28 | Missing aria-labels on icon-only buttons | Accessibility | `frontend/src/components/app-sidebar.tsx:98-101` | [#249](https://github.com/amattas/gym-app/issues/249) |
| 29 | Database engine missing connection pool configuration | Infra | `backend/src/gym_api/database.py:1-6` | [#250](https://github.com/amattas/gym-app/issues/250) |
| 30 | Next.js missing security headers and CSP configuration | Security | `frontend/next.config.ts:3-4` | [#251](https://github.com/amattas/gym-app/issues/251) |
| 31 | Exposed database and Redis ports in docker-compose | Security | `docker-compose.yml:22-35` | [#252](https://github.com/amattas/gym-app/issues/252) |
| 32 | Backup/restore scripts expose credentials in process list | Security | `scripts/backup_db.sh:26`, `scripts/restore_db.sh:37` | [#253](https://github.com/amattas/gym-app/issues/253) |
| 33 | Client detail page shows infinite spinner on fetch error | Usability | `frontend/src/app/(app)/clients/[clientId]/page.tsx:72-78` | [#254](https://github.com/amattas/gym-app/issues/254) |
| 34 | HPA missing scale-down stabilization window | Infra | `k8s/hpa.yaml:12-24` | [#255](https://github.com/amattas/gym-app/issues/255) |
| 35 | Missing useEffect cleanup causes memory leak warnings | Bug | `frontend/src/app/(app)/check-ins/page.tsx:56-61,86-97` | [#256](https://github.com/amattas/gym-app/issues/256) |
| 55 | Auth service token revocation gap during refresh rotation | Bug | `backend/src/gym_api/services/auth_service.py:93-122` | [#276](https://github.com/amattas/gym-app/issues/276) |
| 56 | DeviceToken missing unique constraint allows duplicate registrations | Bug | `backend/src/gym_api/models/notification.py:19` | [#277](https://github.com/amattas/gym-app/issues/277) |
| 57 | DiscountCode missing unique constraint per gym | Bug | `backend/src/gym_api/models/discount_code.py:24` | [#278](https://github.com/amattas/gym-app/issues/278) |
| 58 | Cache service fails silently with no retry or circuit breaker | Bug | `backend/src/gym_api/cache/cache_service.py:13-22` | [#279](https://github.com/amattas/gym-app/issues/279) |
| 59 | Cache invalidation after commit causes stale reads | Bug | `backend/src/gym_api/services/program_service.py:56-63` | [#280](https://github.com/amattas/gym-app/issues/280) |
| 60 | Alembic downgrade references undefined ALL_ENUMS variable | Bug | `backend/alembic/versions/001_initial_schema.py:1123-1125` | [#281](https://github.com/amattas/gym-app/issues/281) |
| 61 | Error response format doesn't match API specification | Bug | `backend/src/gym_api/middleware/error_handler.py` | [#282](https://github.com/amattas/gym-app/issues/282) |
| 64 | Workout detail page infinite spinner on fetch error | Usability | `frontend/src/app/(app)/workouts/[workoutId]/page.tsx:63-73` | [#285](https://github.com/amattas/gym-app/issues/285) |
| 65 | Multiple pages show silent errors or infinite spinners on fetch failure | Usability | Multiple frontend pages | [#286](https://github.com/amattas/gym-app/issues/286) |
| 66 | Missing loading state and double-submit protection on action buttons | Usability | `frontend goals/page.tsx`, `schedules/page.tsx` | [#287](https://github.com/amattas/gym-app/issues/287) |
| 67 | Memberships page potential null pointer on client_id.slice() | Bug | `frontend/src/app/(app)/memberships/page.tsx:168-170` | [#288](https://github.com/amattas/gym-app/issues/288) |
| 68 | Audit logs page missing pagination for large datasets | Usability | `frontend/src/app/(app)/audit-logs/page.tsx:34-40` | [#289](https://github.com/amattas/gym-app/issues/289) |
| 70 | No auth failure/negative tests across router test suite | Testing | `backend/tests/test_routers/` | [#291](https://github.com/amattas/gym-app/issues/291) |
| 71 | Flaky test: global state mutation in test_idempotency.py | Testing | `backend/tests/test_middleware/test_idempotency.py:8` | [#292](https://github.com/amattas/gym-app/issues/292) |
| 98 | Checkout allows negative invoice totals when discount exceeds subtotal | Bug | `backend/src/gym_api/services/stripe_service.py:191` | [#319](https://github.com/amattas/gym-app/issues/319) |
| 99 | auth_service email case not normalized — duplicate accounts possible | Bug | `backend/src/gym_api/services/auth_service.py:51-53` | [#320](https://github.com/amattas/gym-app/issues/320) |
| 100 | Verification tokens not invalidated when new ones created | Security | `backend/src/gym_api/services/verification_service.py:15-26` | [#321](https://github.com/amattas/gym-app/issues/321) |
| 101 | Trial membership info overwritten when pause_info is set | Bug | `backend/src/gym_api/services/membership_service.py:64-68,157-159` | [#322](https://github.com/amattas/gym-app/issues/322) |
| 102 | Revoke-all-sessions also revokes caller's own session | Bug | `backend/src/gym_api/routers/auth.py:218-222` | [#323](https://github.com/amattas/gym-app/issues/323) |
| 103 | Data export processed synchronously in request handler | Performance | `backend/src/gym_api/routers/data_privacy.py:46-57` | [#324](https://github.com/amattas/gym-app/issues/324) |
| 104 | MFA setup persists TOTP secret before user verification | Security | `backend/src/gym_api/routers/auth.py:164-172` | [#325](https://github.com/amattas/gym-app/issues/325) |
| 105 | RegisterRequest missing max_length on password field (bcrypt DoS) | Security | `backend/src/gym_api/routers/auth.py:30-34` | [#326](https://github.com/amattas/gym-app/issues/326) |
| 106 | Webhook endpoint URL not validated — SSRF vulnerability | Security | `backend/src/gym_api/routers/webhook_endpoints.py:16` | [#327](https://github.com/amattas/gym-app/issues/327) |
| 107 | Schema status fields use bare str instead of Enum types | Bug | `backend/src/gym_api/schemas/workout.py:15` + multiple | [#328](https://github.com/amattas/gym-app/issues/328) |
| 108 | DiscountCode percentage type has no upper bound (allows >100%) | Bug | `backend/src/gym_api/models/discount_code.py:27` | [#329](https://github.com/amattas/gym-app/issues/329) |
| 109 | CustomDomain.domain missing unique constraint | Bug | `backend/src/gym_api/models/custom_domain.py:31` | [#330](https://github.com/amattas/gym-app/issues/330) |
| 110 | WebhookEndpoint.secret stored as plaintext | Security | `backend/src/gym_api/models/webhook_endpoint.py:19` | [#331](https://github.com/amattas/gym-app/issues/331) |
| 111 | Usage metering race condition on read-then-increment | Bug | `backend/src/gym_api/services/usage_metering_service.py:10-48` | [#332](https://github.com/amattas/gym-app/issues/332) |
| 112 | TrainerException.exception_date type mismatch (datetime vs Date) | Bug | `backend/src/gym_api/models/schedule.py:71` | [#333](https://github.com/amattas/gym-app/issues/333) |
| 113 | No check constraint on schedule ensuring end > start | Bug | `backend/src/gym_api/models/schedule.py:37-38` | [#334](https://github.com/amattas/gym-app/issues/334) |
| 114 | Rate limiter in-memory fallback not shared across replicas | Bug | `backend/src/gym_api/middleware/rate_limiter.py:26,86-98` | [#335](https://github.com/amattas/gym-app/issues/335) |
| 115 | Metrics middleware unbounded per-path counters (memory leak) | Performance | `backend/src/gym_api/metrics/prometheus.py:10-12,25-31` | [#336](https://github.com/amattas/gym-app/issues/336) |
| 116 | Spinner loading indicators missing accessible text (all pages) | Accessibility | Multiple frontend pages | [#337](https://github.com/amattas/gym-app/issues/337) |
| 117 | Pervasive missing form label-input associations (12+ dialogs) | Accessibility | Multiple frontend pages | [#338](https://github.com/amattas/gym-app/issues/338) |
| 118 | Error boundary missing role="alert" for screen readers | Accessibility | `frontend/src/components/error-boundary.tsx:31-39` | [#339](https://github.com/amattas/gym-app/issues/339) |
| 119 | Billing page silently discards individual API fetch errors | Usability | `frontend/src/app/(app)/billing/page.tsx:76-85` | [#340](https://github.com/amattas/gym-app/issues/340) |
| 120 | Locations page stuck loading if gym_id missing from localStorage | Usability | `frontend/src/app/(app)/locations/page.tsx:25-36` | [#341](https://github.com/amattas/gym-app/issues/341) |
| 121 | Redis get_redis() connection race condition under concurrent access | Bug | `backend/src/gym_api/cache/cache_service.py:13-22` | [#342](https://github.com/amattas/gym-app/issues/342) |
| 122 | K8s network policy overly permissive egress rule | Security | `k8s/network-policy.yaml:35-42` | [#343](https://github.com/amattas/gym-app/issues/343) |
| 123 | TrainerClientAssignment and TrainerAvailability missing gym_id column | Security | `backend/src/gym_api/models/trainer_client.py`, `schedule.py` | [#344](https://github.com/amattas/gym-app/issues/344) |
| 124 | Backup codes defined in User model but never generated or stored | Bug | `backend/src/gym_api/models/user.py:35` | [#345](https://github.com/amattas/gym-app/issues/345) |
| 125 | No ORM relationships defined — root cause of N+1 query issues | Performance | `backend/src/gym_api/models/*.py` | [#346](https://github.com/amattas/gym-app/issues/346) |
| 126 | UserSession missing expires_at — sessions never expire at DB level | Security | `backend/src/gym_api/models/session.py:11-25` | [#347](https://github.com/amattas/gym-app/issues/347) |
| 127 | UsageMetricRollup missing unique constraint on business key | Bug | `backend/src/gym_api/models/usage_metric.py:14-21` | [#348](https://github.com/amattas/gym-app/issues/348) |
| 155 | Workout model missing location_id, check_in_id, program_day_id per spec | Spec Compliance | `backend/src/gym_api/models/workout.py:19-42` | [#376](https://github.com/amattas/gym-app/issues/376) |
| 156 | custom_domain_service verify_domain performs no actual DNS verification | Bug | `backend/src/gym_api/services/custom_domain_service.py:43-49` | [#377](https://github.com/amattas/gym-app/issues/377) |
| 157 | passkey_service silently returns None on all verification exceptions | Security | `backend/src/gym_api/services/passkey_service.py:116-118` | [#378](https://github.com/amattas/gym-app/issues/378) |
| 158 | exercise_service get_exercise cache bypasses gym_id scoping | Security | `backend/src/gym_api/services/exercise_service.py:25-27` | [#379](https://github.com/amattas/gym-app/issues/379) |
| 159 | All service update functions cant clear optional fields (systemic) | Bug | Multiple service files | [#380](https://github.com/amattas/gym-app/issues/380) |
| 160 | assign_trainer endpoint accepts raw dict instead of Pydantic schema | Bug | `backend/src/gym_api/routers/clients.py:125-153` | [#381](https://github.com/amattas/gym-app/issues/381) |
| 161 | Program cache not invalidated on update/delete — stale data for 5 min | Bug | `backend/src/gym_api/routers/programs.py:47-94` | [#382](https://github.com/amattas/gym-app/issues/382) |
| 162 | WorkoutSetCreate allows negative weight_kg, reps, and duration_seconds | Bug | `backend/src/gym_api/schemas/workout.py:28-33` | [#383](https://github.com/amattas/gym-app/issues/383) |
| 163 | ClientCreate.email has no format validation (accepts arbitrary strings) | Bug | `backend/src/gym_api/schemas/client.py:10` | [#384](https://github.com/amattas/gym-app/issues/384) |
| 164 | Workout start/complete has no state machine validation | Bug | `backend/src/gym_api/services/workout_service.py:95-118` | [#385](https://github.com/amattas/gym-app/issues/385) |
| 165 | Missing client analytics endpoints (summary, PRs, exercises) per spec | Spec Compliance | `backend/src/gym_api/routers/analytics.py` | [#386](https://github.com/amattas/gym-app/issues/386) |
| 166 | Missing goal abandon and progress endpoints per spec | Spec Compliance | `backend/src/gym_api/routers/goals.py` | [#387](https://github.com/amattas/gym-app/issues/387) |
| 167 | Schedules date filter type mismatch (date string vs datetime param) | Integration | `frontend/src/app/(app)/schedules/page.tsx:68` | [#388](https://github.com/amattas/gym-app/issues/388) |
| 168 | audit_service log_event uses separate commit — orphaned audit logs | Bug | `backend/src/gym_api/services/audit_service.py:10-33` | [#389](https://github.com/amattas/gym-app/issues/389) |
| 169 | plan_template_service hard-deletes templates referenced by active memberships | Bug | `backend/src/gym_api/services/plan_template_service.py:64-66` | [#390](https://github.com/amattas/gym-app/issues/390) |
| 170 | Email service tests only exercise SMTP not configured fallback path | Testing | `backend/tests/test_services/test_email_service.py:28-51` | [#391](https://github.com/amattas/gym-app/issues/391) |
| 224 | Alembic env.py missing compare_type=True -- autogenerate misses type changes | Config | `backend/alembic/env.py:34` | [#445](https://github.com/amattas/gym-app/issues/445) |
| 225 | user_sessions.last_used_at missing server_default in migration | Bug | `backend/alembic/versions/001_initial_schema.py:408` | [#446](https://github.com/amattas/gym-app/issues/446) |
| 226 | Forgot-password rate limit key doesnt match actual endpoint path -- limit bypassed | Security | `backend/src/gym_api/middleware/rate_limiter.py:18` | [#447](https://github.com/amattas/gym-app/issues/447) |
| 227 | Resend-verification endpoint has no rate limiting -- email bombing vector | Security | `backend/src/gym_api/routers/auth.py:282-294` | [#448](https://github.com/amattas/gym-app/issues/448) |
| 228 | HIBP password breach check fails open -- breached passwords accepted when API down | Security | `backend/src/gym_api/services/hibp_service.py:19-21` | [#449](https://github.com/amattas/gym-app/issues/449) |
| 229 | Notification preferences optimistic rollback uses stale closure | Bug | `frontend/src/app/(app)/notifications/page.tsx:35-44` | [#450](https://github.com/amattas/gym-app/issues/450) |
| 230 | Check-ins all location value sent as literal query param causing 422 | Bug | `frontend/src/app/(app)/check-ins/page.tsx:67,87-96` | [#451](https://github.com/amattas/gym-app/issues/451) |
| 231 | Exercise muscle group all filter causes zero results shown | Bug | `frontend/src/app/(app)/exercises/page.tsx:79-86` | [#452](https://github.com/amattas/gym-app/issues/452) |
| 232 | parseFloat accepts NaN without validation -- NaN sent to API on multiple forms | Bug | `frontend/src/app/(app)/billing/page.tsx:95`, `goals/page.tsx:88` | [#453](https://github.com/amattas/gym-app/issues/453) |
| 233 | PR detection read-then-insert race allows duplicate personal records | Bug | `backend/src/gym_api/services/pr_service.py:37-107` | [#454](https://github.com/amattas/gym-app/issues/454) |
| 234 | GraphQL introspection enabled in all environments -- schema disclosure | Security | `backend/src/gym_api/graphql/schema.py:262` | [#455](https://github.com/amattas/gym-app/issues/455) |
| 235 | Security headers missing Content-Security-Policy; deprecated X-XSS-Protection | Security | `backend/src/gym_api/middleware/security_headers.py:5-13` | [#456](https://github.com/amattas/gym-app/issues/456) |
| 236 | cancel_membership commits base before addon cancellations -- crash leaves inconsistent state | Bug | `backend/src/gym_api/services/membership_service.py:189-222` | [#457](https://github.com/amattas/gym-app/issues/457) |
| 237 | get_occupancy_history runs 24 sequential queries without gym_id scoping | Bug | `backend/src/gym_api/services/check_in_service.py:120-137` | [#458](https://github.com/amattas/gym-app/issues/458) |
| 238 | register_user TOCTOU race on email uniqueness -- concurrent duplicate accounts | Bug | `backend/src/gym_api/services/auth_service.py:41-66` | [#459](https://github.com/amattas/gym-app/issues/459) |
| 239 | Stripe webhook invoice status updates bypass service layer -- no transition validation | Bug | `backend/src/gym_api/routers/stripe_webhooks.py:95-125` | [#460](https://github.com/amattas/gym-app/issues/460) |
| 240 | set_trainer_availability delete-recreate causes phantom empty reads during update | Bug | `backend/src/gym_api/services/schedule_service.py:117-134` | [#461](https://github.com/amattas/gym-app/issues/461) |
| 241 | Invitation accept leaks ValueError messages -- account enumeration | Security | `backend/src/gym_api/routers/invitations.py:55-66` | [#462](https://github.com/amattas/gym-app/issues/462) |
| 242 | Agreement content field has no size limit -- memory/storage exhaustion | Security | `backend/src/gym_api/schemas/agreement.py:10-11` | [#463](https://github.com/amattas/gym-app/issues/463) |
| 243 | Invitation email field has no email format validation | Bug | `backend/src/gym_api/schemas/invitation.py:8` | [#464](https://github.com/amattas/gym-app/issues/464) |
| 244 | Notification device token response exposes raw FCM/APNs tokens | Security | `backend/src/gym_api/schemas/notification.py:12-20` | [#465](https://github.com/amattas/gym-app/issues/465) |
| 245 | Stripe webhook handler has no event deduplication -- redeliveries cause duplicate mutations | Bug | `backend/src/gym_api/routers/stripe_webhooks.py:36-151` | [#466](https://github.com/amattas/gym-app/issues/466) |
| 246 | Password reset/email verification token TOCTOU gap allowing double-use | Security | `backend/src/gym_api/services/verification_service.py:29-50` | [#467](https://github.com/amattas/gym-app/issues/467) |
| 247 | Schedules page filter inputs fire API call per keystroke (no debounce) | Performance | `frontend/src/app/(app)/schedules/page.tsx:62-84` | [#468](https://github.com/amattas/gym-app/issues/468) |
| 248 | Analytics clientDays useEffect uses stale clientId from closure | Bug | `frontend/src/app/(app)/analytics/page.tsx:74-88` | [#469](https://github.com/amattas/gym-app/issues/469) |
| 249 | gym_id not cleared from localStorage on auth failure -- persists across sessions | Security | `frontend/src/lib/api.ts:74-78` | [#470](https://github.com/amattas/gym-app/issues/470) |
| 250 | Token refresh path may lose original 401 error message (body consumed) | Bug | `frontend/src/lib/api.ts:60-83` | [#471](https://github.com/amattas/gym-app/issues/471) |
| 251 | Invitation accept password has no max_length (bcrypt DoS on unauthenticated endpoint) | Security | `backend/src/gym_api/schemas/invitation.py:23` | [#472](https://github.com/amattas/gym-app/issues/472) |
| 252 | Agreement signer_email/signer_name have no validation or size limits | Bug | `backend/src/gym_api/schemas/agreement.py:39-43` | [#473](https://github.com/amattas/gym-app/issues/473) |
| 253 | Custom domain input has no domain name format validation | Bug | `backend/src/gym_api/schemas/custom_domain.py:8` | [#474](https://github.com/amattas/gym-app/issues/474) |
| 274 | Combined months+days membership duration only applies months, silently discards days | Bug | `backend/src/gym_api/services/membership_service.py:148-160` | [#495](https://github.com/amattas/gym-app/issues/495) |
| 275 | Per-period visit limit never enforced -- counter incremented but never compared | Bug | `backend/src/gym_api/services/membership_service.py:256-272` | [#496](https://github.com/amattas/gym-app/issues/496) |
| 276 | Period resets exclude perpetual memberships (no expires_at) -- visit counter never resets | Bug | `backend/src/gym_api/services/membership_service.py:291-320` | [#497](https://github.com/amattas/gym-app/issues/497) |
| 277 | Trial conversion crashes on naive vs tz-aware datetime comparison | Bug | `backend/src/gym_api/services/membership_service.py:205-230` | [#498](https://github.com/amattas/gym-app/issues/498) |
| 278 | handle_payment_success only activates pending memberships -- misses trial status | Bug | `backend/src/gym_api/services/stripe_service.py:222-253` | [#499](https://github.com/amattas/gym-app/issues/499) |
| 279 | handle_payment_success never sets invoice.paid_at -- timestamp always NULL | Bug | `backend/src/gym_api/services/stripe_service.py:222-253` | [#500](https://github.com/amattas/gym-app/issues/500) |
| 280 | update_invoice_status allows arbitrary status transitions (paid->draft, void->paid) | Bug | `backend/src/gym_api/services/invoice_service.py:40-55` | [#501](https://github.com/amattas/gym-app/issues/501) |
| 281 | Goal update has no status transition validation and no auto-completion | Bug | `backend/src/gym_api/services/goal_service.py:45-65` | [#502](https://github.com/amattas/gym-app/issues/502) |
| 282 | Checkout never applies configured processing fees -- always 0 | Bug | `backend/src/gym_api/routers/billing.py:117-147` | [#503](https://github.com/amattas/gym-app/issues/503) |
| 283 | Addon membership creation doesn't validate base membership exists or is active | Bug | `backend/src/gym_api/services/membership_service.py:80-120` | [#504](https://github.com/amattas/gym-app/issues/504) |
| 284 | trainer_service.get_trainer returns deactivated (is_active=False) trainers | Bug | `backend/src/gym_api/services/trainer_service.py:25-35` | [#505](https://github.com/amattas/gym-app/issues/505) |
| 285 | location_service.get_location returns soft-deleted (is_active=False) locations | Bug | `backend/src/gym_api/services/location_service.py:20-30` | [#506](https://github.com/amattas/gym-app/issues/506) |
| 286 | analytics crash on invalid measurement_type enum -- unhandled 500 | Bug | `backend/src/gym_api/services/analytics_service.py:85-110` | [#507](https://github.com/amattas/gym-app/issues/507) |
| 287 | Locations create/list accept arbitrary gym_id from URL path bypassing tenant check | Security | `backend/src/gym_api/routers/locations.py:37-57` | [#508](https://github.com/amattas/gym-app/issues/508) |
| 288 | PR detect_rep_prs stores threshold value as reps instead of actual reps performed | Bug | `backend/src/gym_api/services/pr_service.py:60-85` | [#509](https://github.com/amattas/gym-app/issues/509) |
| 289 | exercise_service.delete_exercise hard-deletes without handling FK constraint violations | Bug | `backend/src/gym_api/services/exercise_service.py:40-50` | [#510](https://github.com/amattas/gym-app/issues/510) |
| 290 | client_invitation_service.accept_invitation TOCTOU race allows double acceptance | Bug | `backend/src/gym_api/services/client_invitation_service.py:30-60` | [#511](https://github.com/amattas/gym-app/issues/511) |
| 291 | Missing not-found.tsx and error.tsx -- no custom 404 or route-level error recovery | Bug | `frontend/src/app/` (missing files) | [#512](https://github.com/amattas/gym-app/issues/512) |
| 292 | Sonner Toaster uses useTheme() without ThemeProvider wrapper | Bug | `frontend/src/components/ui/sonner.tsx` | [#513](https://github.com/amattas/gym-app/issues/513) |
| 293 | Root page unconditional redirect causes double-redirect for unauthenticated users | Bug | `frontend/src/app/page.tsx` | [#514](https://github.com/amattas/gym-app/issues/514) |
| 294 | Progress photos delete button missing confirmation dialog | Usability | `frontend/src/app/(app)/progress-photos/page.tsx` | [#515](https://github.com/amattas/gym-app/issues/515) |
| 295 | Deferred cancellation of trial memberships never processed by batch job | Bug | `backend/src/gym_api/services/membership_service.py:340-373` | [#516](https://github.com/amattas/gym-app/issues/516) |
| 323 | Migration missing index on clients.status declared in model | Performance | `backend/src/gym_api/models/client.py:52` | [#544](https://github.com/amattas/gym-app/issues/544) |
| 324 | Migration missing index on payments.account_id declared in model | Performance | `backend/src/gym_api/models/invoice.py:73-74` | [#545](https://github.com/amattas/gym-app/issues/545) |
| 325 | invoices.membership_id missing FK constraint and index in migration | Bug | `backend/alembic/versions/001_initial_schema.py:905-931` | [#546](https://github.com/amattas/gym-app/issues/546) |
| 326 | Trainer table missing updated_at column -- inconsistent with all other mutable entities | Bug | `backend/src/gym_api/models/trainer.py:11-28` | [#547](https://github.com/amattas/gym-app/issues/547) |
| 327 | trainer_invitations.token_hash String(64) while all others use String(128) | Bug | `backend/src/gym_api/models/trainer_invitation.py:21` | [#548](https://github.com/amattas/gym-app/issues/548) |
| 328 | check_in_service.create_check_in allows check-in with no active membership | Bug | `backend/src/gym_api/services/check_in_service.py:26-52` | [#549](https://github.com/amattas/gym-app/issues/549) |
| 329 | detect_prs creates spurious PR records when best set has reps=None | Bug | `backend/src/gym_api/services/workout_service.py:184-196` | [#550](https://github.com/amattas/gym-app/issues/550) |
| 330 | check_in_service.checkout allows double checkout -- corrupts duration data | Bug | `backend/src/gym_api/services/check_in_service.py:100-104` | [#551](https://github.com/amattas/gym-app/issues/551) |
| 331 | schedule_service.get_trainer_exception missing gym_id scoping | Security | `backend/src/gym_api/services/schedule_service.py:152-160` | [#552](https://github.com/amattas/gym-app/issues/552) |
| 332 | analytics volume_trend executes N+1+1 nested queries | Performance | `backend/src/gym_api/services/analytics_service.py:118-166` | [#553](https://github.com/amattas/gym-app/issues/553) |
| 333 | unpause_membership crashes on naive vs tz-aware datetime subtraction | Bug | `backend/src/gym_api/services/membership_service.py:166-186` | [#554](https://github.com/amattas/gym-app/issues/554) |
| 334 | gym_service.create_gym TOCTOU on slug raises unhandled IntegrityError | Bug | `backend/src/gym_api/services/gym_service.py:15-23` | [#555](https://github.com/amattas/gym-app/issues/555) |
| 335 | add_exercise_to_workout and add_set do not validate parent entity exists | Bug | `backend/src/gym_api/services/workout_service.py:59-66,78-83` | [#556](https://github.com/amattas/gym-app/issues/556) |
| 336 | cancel_deletion_request returns request without indicating cancellation failed | Bug | `backend/src/gym_api/services/data_deletion_service.py:45-54` | [#557](https://github.com/amattas/gym-app/issues/557) |
| 337 | ai_summary filters by nullable started_at -- completed workouts without timestamps excluded | Bug | `backend/src/gym_api/services/ai_summary_service.py:92-99` | [#558](https://github.com/amattas/gym-app/issues/558) |
| 338 | notification_service.register_device creates duplicates on repeated calls | Bug | `backend/src/gym_api/services/notification_service.py:9-16` | [#559](https://github.com/amattas/gym-app/issues/559) |
| 339 | Login error message missing role=alert for screen readers | Accessibility | `frontend/src/app/(auth)/login/page.tsx:53-56` | [#560](https://github.com/amattas/gym-app/issues/560) |
| 340 | Notification switch toggles missing label association | Accessibility | `frontend/src/app/(app)/notifications/page.tsx:78-84` | [#561](https://github.com/amattas/gym-app/issues/561) |
| 341 | Icon-only back buttons across 6 detail pages missing aria-label | Accessibility | Multiple frontend pages | [#562](https://github.com/amattas/gym-app/issues/562) |
| 342 | Audit log filter fires API call per keystroke (no debounce) | Performance | `frontend/src/app/(app)/audit-logs/page.tsx:33-40` | [#563](https://github.com/amattas/gym-app/issues/563) |
| 343 | Exercises page fetch error silently swallowed with no toast | Usability | `frontend/src/app/(app)/exercises/page.tsx:63-72` | [#564](https://github.com/amattas/gym-app/issues/564) |
| 344 | User nav Profile dropdown menu item is non-functional | Usability | `frontend/src/components/user-nav.tsx:42-45` | [#565](https://github.com/amattas/gym-app/issues/565) |
| 345 | Usage page badge uses color alone to indicate limit breach (WCAG 1.4.1) | Accessibility | `frontend/src/app/(app)/usage/page.tsx:68-70` | [#566](https://github.com/amattas/gym-app/issues/566) |
| 346 | Error boundary Try again does not retry failed data fetch | Usability | `frontend/src/components/error-boundary.tsx:34-37` | [#567](https://github.com/amattas/gym-app/issues/567) |
| 347 | Client detail silently redirects on any fetch error (not just 404) | Usability | `frontend/src/app/(app)/clients/[clientId]/page.tsx:54-55` | [#568](https://github.com/amattas/gym-app/issues/568) |
| 348 | Ingress uses deprecated kubernetes.io/ingress.class annotation | Infra | `k8s/ingress.yaml:6` | [#569](https://github.com/amattas/gym-app/issues/569) |
| 349 | Docker COPY entire /usr/local/bin from builder increases attack surface | Security | `backend/Dockerfile:14` | [#570](https://github.com/amattas/gym-app/issues/570) |
| 350 | Docker Compose api service has no healthcheck | Infra | `docker-compose.yml:2-14` | [#571](https://github.com/amattas/gym-app/issues/571) |
| 351 | CI installs pytest-cov but never uses it -- no coverage gating | Config | `.github/workflows/ci.yml:100,105` | [#572](https://github.com/amattas/gym-app/issues/572) |
| 352 | CI backend-test missing Redis service -- Redis code paths untested | Config | `.github/workflows/ci.yml:68-105` | [#573](https://github.com/amattas/gym-app/issues/573) |
| 353 | CI web-test job is duplicate of web-lint -- no actual tests run | Config | `.github/workflows/ci.yml:154-174` | [#574](https://github.com/amattas/gym-app/issues/574) |
| 354 | CI no K8s manifest validation step | Config | `.github/workflows/ci.yml` | [#575](https://github.com/amattas/gym-app/issues/575) |
| 355 | No .dockerignore -- build context includes tests, caches, secrets | Security | `backend/` (missing file) | [#576](https://github.com/amattas/gym-app/issues/576) |
| 356 | Backup script pg_dump incompatible with asyncpg DATABASE_URL format | Infra | `scripts/backup_db.sh:26` | [#577](https://github.com/amattas/gym-app/issues/577) |
| 357 | Restore script psql incompatible with asyncpg DATABASE_URL format | Infra | `scripts/restore_db.sh:37` | [#578](https://github.com/amattas/gym-app/issues/578) |
| 358 | K8s Deployment missing pod anti-affinity -- both replicas on same node | Infra | `k8s/deployment.yaml:12-16` | [#579](https://github.com/amattas/gym-app/issues/579) |
| 359 | K8s Deployment missing SMTP env vars -- emails silently dropped in production | Config | `k8s/deployment.yaml:22-37` | [#580](https://github.com/amattas/gym-app/issues/580) |
| 360 | CI Trivy action pinned to @master -- supply chain risk | Security | `.github/workflows/ci.yml:118` | [#581](https://github.com/amattas/gym-app/issues/581) |
| 361 | CI pipeline no final gate job -- partial failures can be merged | Config | `.github/workflows/ci.yml` | [#582](https://github.com/amattas/gym-app/issues/582) |
| 362 | Alembic asyncio.run() fails from existing event loop | Config | `backend/alembic/env.py:50-51` | [#583](https://github.com/amattas/gym-app/issues/583) |
| 363 | ScheduleCreate accepts scheduled_end before scheduled_start | Bug | `backend/src/gym_api/schemas/schedule.py:7-14` | [#584](https://github.com/amattas/gym-app/issues/584) |
| 364 | TrainerAvailability day_of_week allows values outside 0-6 range | Bug | `backend/src/gym_api/schemas/schedule.py:42` | [#585](https://github.com/amattas/gym-app/issues/585) |
| 365 | TrainerAvailability allows end_time before or equal to start_time | Bug | `backend/src/gym_api/schemas/schedule.py:41-45` | [#586](https://github.com/amattas/gym-app/issues/586) |
| 366 | Idempotency middleware drops original response headers on cache hit | Bug | `backend/src/gym_api/middleware/idempotency.py:49-56` | [#587](https://github.com/amattas/gym-app/issues/587) |
| 367 | RequestIDMiddleware accepts client X-Request-ID without validation -- log injection | Security | `backend/src/gym_api/middleware/request_id.py:12` | [#588](https://github.com/amattas/gym-app/issues/588) |
| 368 | Rate limiter applies to ALL paths including health checks | Performance | `backend/src/gym_api/middleware/rate_limiter.py:28` | [#589](https://github.com/amattas/gym-app/issues/589) |
| 369 | Rate limiter memory fallback never evicts entries -- unbounded growth | Bug | `backend/src/gym_api/middleware/rate_limiter.py:26` | [#590](https://github.com/amattas/gym-app/issues/590) |
| 370 | GymUpdate settings accepts unvalidated arbitrary dict -- JSON injection | Security | `backend/src/gym_api/schemas/gym.py:24` | [#591](https://github.com/amattas/gym-app/issues/591) |
| 371 | GymCreate.slug has no pattern validation -- allows spaces and special chars | Bug | `backend/src/gym_api/schemas/gym.py:9` | [#592](https://github.com/amattas/gym-app/issues/592) |
| 372 | Pagination decode_cursor does not handle malformed base64 -- unhandled crash | Bug | `backend/src/gym_api/utils/pagination.py:12-13` | [#593](https://github.com/amattas/gym-app/issues/593) |
| 373 | Multiple enum schemas accept arbitrary strings instead of enum types (7 schemas) | Bug | Multiple schema files | [#594](https://github.com/amattas/gym-app/issues/594) |
| 374 | Multiple email fields across schemas lack format validation (3 schemas) | Bug | `schemas/trainer.py`, `schemas/gym.py`, `schemas/account.py` | [#595](https://github.com/amattas/gym-app/issues/595) |
| 375 | ExerciseCreate.description and GoalCreate.notes have no size limit | Bug | `backend/src/gym_api/schemas/exercise.py:9`, `schemas/goal.py:12` | [#596](https://github.com/amattas/gym-app/issues/596) |
| 376 | AgreementEnvelopeResponse exposes signed_document_url in list | Security | `backend/src/gym_api/schemas/agreement.py:58` | [#597](https://github.com/amattas/gym-app/issues/597) |
| 377 | ErrorHandlerMiddleware catches asyncio.CancelledError -- suppresses shutdown | Bug | `backend/src/gym_api/middleware/error_handler.py:3-15` | [#598](https://github.com/amattas/gym-app/issues/598) |
| 378 | Cache service json.dumps(default=str) silently corrupts complex types | Bug | `backend/src/gym_api/cache/cache_service.py:43` | [#599](https://github.com/amattas/gym-app/issues/599) |
| 379 | LocalStorage.get_url returns predictable file paths -- unauthorized download | Security | `backend/src/gym_api/storage/local_storage.py:45-48` | [#600](https://github.com/amattas/gym-app/issues/600) |
| 380 | AccountResponse exposes stripe_customer_id to client | Security | `backend/src/gym_api/schemas/account.py:19` | [#601](https://github.com/amattas/gym-app/issues/601) |
| 381 | get_current_user doesn't handle UUID ValueError from malformed JWT | Bug | `backend/src/gym_api/dependencies/auth.py:19-26` | [#602](https://github.com/amattas/gym-app/issues/602) |
| 382 | Email send_email subject vulnerable to header injection | Security | `backend/src/gym_api/email/email_service.py:44` | [#603](https://github.com/amattas/gym-app/issues/603) |
| 401 | record_visit service silently discards user-provided notes parameter | Bug | `backend/src/gym_api/services/membership_service.py:256-272` | [#622](https://github.com/amattas/gym-app/issues/622) |
| 402 | update_set/delete_set endpoints ignore workout_exercise_id path parameter | Bug | `backend/src/gym_api/routers/workouts.py:121-147` | [#623](https://github.com/amattas/gym-app/issues/623) |
| 403 | get_gym_context blocks platform_admin with no gym_id override mechanism | Bug | `backend/src/gym_api/dependencies/gym_scope.py:9-22` | [#624](https://github.com/amattas/gym-app/issues/624) |
| 404 | Checkout endpoints return raw dict without CheckoutResponse validation | Bug | `backend/src/gym_api/routers/billing.py:117-147` | [#625](https://github.com/amattas/gym-app/issues/625) |
| 405 | Workout detail handleSaveSet sends NaN when editReps is empty | Bug | `frontend/src/app/(app)/workouts/[workoutId]/page.tsx:134-141` | [#626](https://github.com/amattas/gym-app/issues/626) |
| 406 | Schedules page handleAction has no loading state -- duplicate status transitions possible | Bug | `frontend/src/app/(app)/schedules/page.tsx:293-328` | [#627](https://github.com/amattas/gym-app/issues/627) |
| 407 | Exercises page create/edit forms lack loading state -- double-submit possible | Bug | `frontend/src/app/(app)/exercises/page.tsx:131-145` | [#628](https://github.com/amattas/gym-app/issues/628) |
| 408 | Goals page refreshGoals has no error handling -- misleading error messages | Bug | `frontend/src/app/(app)/goals/page.tsx:50-60` | [#629](https://github.com/amattas/gym-app/issues/629) |
| 409 | Billing page window.open for Stripe fires in async context -- popup blocked | Bug | `frontend/src/app/(app)/billing/page.tsx:92-100` | [#630](https://github.com/amattas/gym-app/issues/630) |
| 410 | Check-ins page checkout button has no loading state -- double-click double-checkout | Bug | `frontend/src/app/(app)/check-ins/page.tsx:120-128` | [#631](https://github.com/amattas/gym-app/issues/631) |
| 411 | POST /v1/schedules response envelope uses {data:...} but spec requires {schedule:...} | Spec Compliance | `backend/src/gym_api/routers/schedules.py:39` | [#632](https://github.com/amattas/gym-app/issues/632) |
| 412 | POST /v1/check-ins response missing location and member expansion per spec | Spec Compliance | `backend/src/gym_api/routers/check_ins.py:26-50` | [#633](https://github.com/amattas/gym-app/issues/633) |
| 413 | GET /v1/workouts missing status query filter per spec | Spec Compliance | `backend/src/gym_api/routers/workouts.py:42-52` | [#634](https://github.com/amattas/gym-app/issues/634) |
| 414 | Workout response missing duration_minutes computed field per spec | Spec Compliance | `backend/src/gym_api/schemas/workout.py:15-25` | [#635](https://github.com/amattas/gym-app/issues/635) |
| 415 | Invoice response missing line_items array per spec | Spec Compliance | `backend/src/gym_api/schemas/billing.py:50-65` | [#636](https://github.com/amattas/gym-app/issues/636) |
| 416 | Membership response missing visit_count and visit_limit fields per spec | Spec Compliance | `backend/src/gym_api/schemas/membership.py` | [#637](https://github.com/amattas/gym-app/issues/637) |
| 417 | Client response missing membership_status and last_check_in fields per spec | Spec Compliance | `backend/src/gym_api/schemas/client.py` | [#638](https://github.com/amattas/gym-app/issues/638) |
| 418 | Trainer response missing specializations and certifications arrays per spec | Spec Compliance | `backend/src/gym_api/schemas/trainer.py` | [#639](https://github.com/amattas/gym-app/issues/639) |
| 419 | Schedule conflict detection not implemented -- double-bookings accepted | Spec Compliance | `backend/src/gym_api/services/schedule_service.py` | [#640](https://github.com/amattas/gym-app/issues/640) |
| 420 | Goal progress endpoint returns wrong shape -- spec requires progress_entries array | Spec Compliance | `backend/src/gym_api/routers/goals.py` | [#641](https://github.com/amattas/gym-app/issues/641) |
| 421 | Membership router tests missing pause/unpause/cancel/renew coverage | Testing | `backend/tests/test_routers/test_memberships.py` | [#642](https://github.com/amattas/gym-app/issues/642) |
| 422 | Check-in router tests missing checkout and occupancy endpoint coverage | Testing | `backend/tests/test_routers/test_check_ins.py` | [#643](https://github.com/amattas/gym-app/issues/643) |
| 423 | Client router tests missing search and trainer-assignment coverage | Testing | `backend/tests/test_routers/test_clients.py` | [#644](https://github.com/amattas/gym-app/issues/644) |
| 424 | Invitation router tests missing accept-invitation flow coverage | Testing | `backend/tests/test_routers/test_invitations.py` | [#645](https://github.com/amattas/gym-app/issues/645) |
| 425 | Data privacy router tests missing export download and deletion coverage | Testing | `backend/tests/test_routers/test_data_privacy.py` | [#646](https://github.com/amattas/gym-app/issues/646) |
| 426 | Calendar and iCal router tests missing token validation coverage | Testing | `backend/tests/test_routers/test_calendar.py` | [#647](https://github.com/amattas/gym-app/issues/647) |
| 427 | Analytics router tests missing trend and measurement endpoints coverage | Testing | `backend/tests/test_routers/test_analytics.py` | [#648](https://github.com/amattas/gym-app/issues/648) |
| 428 | Agreement and esign router tests missing envelope CRUD coverage | Testing | `backend/tests/test_routers/test_agreements.py` | [#649](https://github.com/amattas/gym-app/issues/649) |
| 429 | Discount router tests missing apply_discount and validation coverage | Testing | `backend/tests/test_routers/test_discounts.py` | [#650](https://github.com/amattas/gym-app/issues/650) |
| 430 | Frontend workout detail fetchWorkout uses stale workoutId from closure | Bug | `frontend/src/app/(app)/workouts/[workoutId]/page.tsx:39-48` | [#651](https://github.com/amattas/gym-app/issues/651) |
| 431 | Frontend workout detail uses array index as React key -- reorder bugs | Bug | `frontend/src/app/(app)/workouts/[workoutId]/page.tsx:240-260` | [#652](https://github.com/amattas/gym-app/issues/652) |
| 432 | Frontend schedules page uses array index as React key | Bug | `frontend/src/app/(app)/schedules/page.tsx:200-250` | [#653](https://github.com/amattas/gym-app/issues/653) |
| 433 | Frontend goals page uses array index as React key | Bug | `frontend/src/app/(app)/goals/page.tsx:200-250` | [#654](https://github.com/amattas/gym-app/issues/654) |
| 434 | Location response missing current_occupancy computed field per spec | Spec Compliance | `backend/src/gym_api/schemas/location.py` | [#655](https://github.com/amattas/gym-app/issues/655) |
| 435 | Notification preferences endpoint missing per-category toggle per spec | Spec Compliance | `backend/src/gym_api/routers/notifications.py` | [#656](https://github.com/amattas/gym-app/issues/656) |
| 436 | Program response missing total_duration_weeks and exercises_count per spec | Spec Compliance | `backend/src/gym_api/schemas/program.py` | [#657](https://github.com/amattas/gym-app/issues/657) |
| 437 | Missing /v1/gyms/{gym_id}/stats aggregate stats endpoint per spec | Spec Compliance | `backend/src/gym_api/routers/gyms.py` | [#658](https://github.com/amattas/gym-app/issues/658) |
| 438 | Missing /v1/reports/revenue and /v1/reports/retention endpoints per spec | Spec Compliance | `backend/src/gym_api/routers/` | [#659](https://github.com/amattas/gym-app/issues/659) |
| 439 | Frontend members/trainers pages fetch without cursor pagination -- only first page shown | Bug | `frontend/src/app/(app)/clients/page.tsx`, `trainers/page.tsx` | [#660](https://github.com/amattas/gym-app/issues/660) |
| 466 | JWT iat claim included but never validated -- old tokens accepted indefinitely | Security | `backend/src/gym_api/services/auth_service.py:24-38` | [#687](https://github.com/amattas/gym-app/issues/687) |
| 467 | Registration endpoint leaks account existence via 201 vs 409 status codes | Security | `backend/src/gym_api/routers/auth.py:101-129` | [#688](https://github.com/amattas/gym-app/issues/688) |
| 468 | Token hash comparisons use SQL equality instead of constant-time comparison | Security | `backend/src/gym_api/services/auth_service.py:95`, `verification_service.py:34` | [#689](https://github.com/amattas/gym-app/issues/689) |
| 469 | No proration logic for membership plan changes mid-cycle | Bug | `backend/src/gym_api/services/membership_service.py`, `stripe_service.py` | [#690](https://github.com/amattas/gym-app/issues/690) |
| 470 | tax_amount field exists in Invoice model but never calculated or applied | Bug | `backend/src/gym_api/models/invoice.py:47`, `stripe_service.py:180-219` | [#691](https://github.com/amattas/gym-app/issues/691) |
| 471 | No invoice PDF generation endpoint or service | Bug | `backend/src/gym_api/routers/billing.py:211-221` | [#692](https://github.com/amattas/gym-app/issues/692) |
| 472 | Missing charge.refunded, charge.dispute, charge.failed Stripe webhook handlers | Bug | `backend/src/gym_api/routers/stripe_webhooks.py:36-151` | [#693](https://github.com/amattas/gym-app/issues/693) |
| 473 | Cascade delete undefined for gym deletion -- orphaned data on gym removal | Bug | `backend/src/gym_api/models/*.py` | [#694](https://github.com/amattas/gym-app/issues/694) |
| 474 | Frontend setState after unmount across 20+ pages -- no AbortController in fetch calls | Bug | `frontend/src/app/(app)/dashboard/page.tsx:20-35`, 20+ pages | [#695](https://github.com/amattas/gym-app/issues/695) |
| 475 | Dashboard page has no route-level error boundary -- API failure shows infinite spinner | Bug | `frontend/src/app/(app)/dashboard/page.tsx` | [#696](https://github.com/amattas/gym-app/issues/696) |
| 476 | Billing page Stripe popup blocked -- window.open in async context | Bug | `frontend/src/app/(app)/billing/page.tsx:112-118` | [#697](https://github.com/amattas/gym-app/issues/697) |
| 477 | Memberships page fetchMemberships recreated on render -- potential infinite loop | Bug | `frontend/src/app/(app)/memberships/page.tsx:67-69` | [#698](https://github.com/amattas/gym-app/issues/698) |
| 478 | Programs detail page silently fails on fetch error -- empty state forever | Bug | `frontend/src/app/(app)/programs/[programId]/page.tsx:45-56` | [#699](https://github.com/amattas/gym-app/issues/699) |
| 490 | Email templates missing CAN-SPAM List-Unsubscribe header | Bug | `backend/src/gym_api/email/email_service.py:25-99` | [#711](https://github.com/amattas/gym-app/issues/711) |
| 491 | send_trainer_invitation function defined but never called -- dead code | Bug | `backend/src/gym_api/email/email_service.py:62-74` | [#712](https://github.com/amattas/gym-app/issues/712) |
| 492 | Log redaction filter missing IP address patterns | Security | `backend/src/gym_api/utils/log_redaction.py:4-30` | [#713](https://github.com/amattas/gym-app/issues/713) |
| 493 | No consent tracking model or endpoints for analytics/marketing | Security | `backend/src/gym_api/models/`, `data_privacy.py` | [#714](https://github.com/amattas/gym-app/issues/714) |
| 494 | S3 storage bucket region not validated against data residency requirements | Security | `backend/src/gym_api/storage/s3_storage.py:15-28` | [#715](https://github.com/amattas/gym-app/issues/715) |
| 495 | TrainerInvitation missing email index in migration | Bug | `backend/src/gym_api/models/trainer_invitation.py:20` | [#716](https://github.com/amattas/gym-app/issues/716) |
| 496 | ClientInvitation missing invited_by_user_id index in migration | Bug | `backend/src/gym_api/models/client_invitation.py:21-22` | [#717](https://github.com/amattas/gym-app/issues/717) |
| 497 | ClientGoal missing created_by_trainer_id index in migration | Bug | `backend/src/gym_api/models/goal.py:34-35` | [#718](https://github.com/amattas/gym-app/issues/718) |
| 498 | PersonalRecord missing pr_type index in migration | Bug | `backend/src/gym_api/models/personal_record.py:35` | [#719](https://github.com/amattas/gym-app/issues/719) |
| 499 | Idempotency cache key header accepts unbounded input -- CPU amplification | Security | `backend/src/gym_api/middleware/idempotency.py:23-27` | [#720](https://github.com/amattas/gym-app/issues/720) |
| 500 | No request body size limit middleware -- relies on Starlette implicit default | Performance | `backend/src/gym_api/main.py` | [#721](https://github.com/amattas/gym-app/issues/721) |
| 501 | No response compression middleware -- all responses sent uncompressed | Performance | `backend/src/gym_api/main.py` | [#722](https://github.com/amattas/gym-app/issues/722) |
| 502 | Sidebar cookie set without Secure/HttpOnly/SameSite flags | Security | `frontend/src/components/ui/sidebar.tsx:86` | [#723](https://github.com/amattas/gym-app/issues/723) |
| 503 | Data export embedded as base64 data URI -- PII exposed in URL/logs | Security | `backend/src/gym_api/services/data_export_service.py:144` | [#724](https://github.com/amattas/gym-app/issues/724) |
| 520 | Agreement envelope expiry not enforced -- expired envelopes can still be signed | Bug | `backend/src/gym_api/models/agreement.py:59` | [#741](https://github.com/amattas/gym-app/issues/741) |
| 521 | Seed script multiple commits creates partial-seed atomicity gap | Bug | `backend/src/gym_api/scripts/seed.py:160,176,192` | [#742](https://github.com/amattas/gym-app/issues/742) |
| 522 | Restore script uses --quiet flag suppressing all errors including constraint violations | Bug | `scripts/restore_db.sh:37` | [#743](https://github.com/amattas/gym-app/issues/743) |
| 523 | Clickable Card divs lack keyboard accessibility and button semantics | Accessibility | `frontend/src/app/(app)/programs/[programId]/page.tsx:143-155` | [#744](https://github.com/amattas/gym-app/issues/744) |
| 524 | No aria-live regions for dynamic content updates (toasts, data refresh) | Accessibility | `frontend/src/components/ui/sonner.tsx`, multiple pages | [#745](https://github.com/amattas/gym-app/issues/745) |
| 525 | Data table loading state not announced to screen readers | Accessibility | `frontend/src/components/data-table.tsx:47-49` | [#746](https://github.com/amattas/gym-app/issues/746) |
| 526 | Job monitoring missing -- no duration/success metrics for background jobs | Bug | `backend/src/gym_api/jobs/membership_expiry.py:18-25`, `cleanup.py:42-47` | [#747](https://github.com/amattas/gym-app/issues/747) |
| 540 | Model validation errors in list comprehensions crash entire list endpoint | Bug | `backend/src/gym_api/routers/workouts.py:49` and 50+ endpoints | [#761](https://github.com/amattas/gym-app/issues/761) |
| 541 | POST action endpoints missing status_code=201 -- return 200 implicitly | Bug | `backend/src/gym_api/routers/workouts.py:152-164`, `memberships.py:94-112` | [#762](https://github.com/amattas/gym-app/issues/762) |
| 542 | Billing endpoints return unstructured data outside {data:...} envelope | Bug | `backend/src/gym_api/routers/billing.py:38-51,117-147` | [#763](https://github.com/amattas/gym-app/issues/763) |
| 543 | Webhooks list endpoint missing pagination structure | Bug | `backend/src/gym_api/routers/webhook_endpoints.py:50-57` | [#764](https://github.com/amattas/gym-app/issues/764) |
| 544 | Frontend API response types not validated at runtime -- silent shape mismatches | Bug | `frontend/src/lib/api.ts:103`, `billing/page.tsx:112` | [#765](https://github.com/amattas/gym-app/issues/765) |
| 545 | Frontend dynamic route params not validated -- invalid UUIDs cause loading spinners | Bug | `frontend/src/app/(app)/workouts/[workoutId]/page.tsx:50-53` | [#766](https://github.com/amattas/gym-app/issues/766) |
| 546 | All 34 frontend pages marked 'use client' -- prevents server-side rendering | Bug | `frontend/src/app/(app)/` (all page.tsx files) | [#767](https://github.com/amattas/gym-app/issues/767) |
| 547 | No page-level metadata exports -- all 34 pages missing title/description | Bug | `frontend/src/app/(app)/` (all page.tsx files) | [#768](https://github.com/amattas/gym-app/issues/768) |
| 548 | Auth context initialization race -- brief loading flash on every page load | Bug | `frontend/src/lib/auth.tsx:44-68` | [#769](https://github.com/amattas/gym-app/issues/769) |
| 549 | Frontend Record<string, unknown> types lose type safety on settings/domains/plans | Bug | `frontend/src/app/(app)/settings/page.tsx:18`, `domains/page.tsx:39` | [#770](https://github.com/amattas/gym-app/issues/770) |
| 567 | Reporting adherence rate returns 0 instead of null when no scheduled data | Bug | `backend/src/gym_api/services/reporting_service.py:176-180` | [#788](https://github.com/amattas/gym-app/issues/788) |
| 568 | WorkoutExercise/Set/ProgramDay order_index missing uniqueness constraints | Bug | `backend/src/gym_api/models/workout.py:52,66`, `program.py:45,58` | [#789](https://github.com/amattas/gym-app/issues/789) |
| 569 | Numeric input fields accept negative values -- workout sets, goals, discounts | Bug | `frontend workouts/new, goals, billing pages` | [#790](https://github.com/amattas/gym-app/issues/790) |
| 570 | PersonalRecord/Measurement/Client physical fields allow negative values | Bug | `backend/src/gym_api/models/personal_record.py:36-38`, `measurement.py:32` | [#791](https://github.com/amattas/gym-app/issues/791) |
| 571 | PlanTemplate.addon_discount_percentage unconstrained -- allows negative or >100% | Bug | `backend/src/gym_api/models/plan_template.py:44` | [#792](https://github.com/amattas/gym-app/issues/792) |
| 572 | No audit log on invitation acceptance -- critical lifecycle event untracked | Bug | `backend/src/gym_api/routers/invitations.py:43-86` | [#793](https://github.com/amattas/gym-app/issues/793) |
| 573 | Password validation inconsistent -- register strict, invitation accepts weak passwords | Bug | `backend/src/gym_api/routers/invitations.py:56-59` | [#794](https://github.com/amattas/gym-app/issues/794) |
| 574 | UsageMetricRollup period_end before period_start allowed -- no check constraint | Bug | `backend/src/gym_api/models/usage_metric.py:19-20` | [#795](https://github.com/amattas/gym-app/issues/795) |
| 575 | Workout started_at can be after ended_at -- no check constraint | Bug | `backend/src/gym_api/models/workout.py:36-37` | [#796](https://github.com/amattas/gym-app/issues/796) |
| 576 | Program.num_days allows 0 or negative values -- no check constraint | Bug | `backend/src/gym_api/models/program.py:32` | [#797](https://github.com/amattas/gym-app/issues/797) |
| 577 | NotificationPreference missing updated_at timestamp | Bug | `backend/src/gym_api/models/notification.py:26-39` | [#798](https://github.com/amattas/gym-app/issues/798) |
| 578 | ClientMembership.total_visits_remaining can go negative -- no check constraint | Bug | `backend/src/gym_api/models/client_membership.py:38` | [#799](https://github.com/amattas/gym-app/issues/799) |
| 600 | Idempotency middleware caches 4xx errors -- retries with fixed payload return stale error | Bug | `backend/src/gym_api/middleware/idempotency.py:40` | [#821](https://github.com/amattas/gym-app/issues/821) |
| 601 | Membership expiry job runs all sub-operations in one session -- no error isolation | Bug | `backend/src/gym_api/jobs/membership_expiry.py:12-16` | [#822](https://github.com/amattas/gym-app/issues/822) |
| 602 | Scheduler missing misfire_grace_time -- missed jobs silently skipped after restart | Bug | `backend/src/gym_api/jobs/scheduler.py:15-30` | [#823](https://github.com/amattas/gym-app/issues/823) |
| 603 | Cleanup job doesn't clean expired email verification tokens or client invitations | Bug | `backend/src/gym_api/jobs/cleanup.py:14-47` | [#824](https://github.com/amattas/gym-app/issues/824) |
| 604 | Redis connection in cache_service has no timeout or pool configuration | Performance | `backend/src/gym_api/cache/cache_service.py:17` | [#825](https://github.com/amattas/gym-app/issues/825) |
| 605 | Idempotency eviction runs full store scan on every request -- O(n) overhead | Performance | `backend/src/gym_api/middleware/idempotency.py:28,66-70` | [#826](https://github.com/amattas/gym-app/issues/826) |
| 606 | Idempotency response body fully consumed -- streaming responses broken | Bug | `backend/src/gym_api/middleware/idempotency.py:41-58` | [#827](https://github.com/amattas/gym-app/issues/827) |
| 607 | Health readiness creates new Redis connection per probe -- connection leak | Bug | `backend/src/gym_api/routers/health.py:29-36` | [#828](https://github.com/amattas/gym-app/issues/828) |
| 608 | Background job exceptions not propagated to any alerting system | Bug | `backend/src/gym_api/jobs/membership_expiry.py`, `cleanup.py` | [#829](https://github.com/amattas/gym-app/issues/829) |
| 609 | list_invoices/payments_for_membership have no LIMIT -- unbounded results | Performance | `backend/src/gym_api/services/invoice_service.py:20-40` | [#830](https://github.com/amattas/gym-app/issues/830) |
| 610 | get_usage_summary no LIMIT -- unbounded result set for long-lived gyms | Performance | `backend/src/gym_api/services/usage_metering_service.py:51-67` | [#831](https://github.com/amattas/gym-app/issues/831) |
| 611 | _check_double_booking uses scalar_one_or_none -- MultipleResultsFound on multiple conflicts | Bug | `backend/src/gym_api/services/schedule_service.py:170-179` | [#832](https://github.com/amattas/gym-app/issues/832) |
| 612 | Missing composite index schedules(trainer_id, scheduled_start) for double-booking | Performance | `backend/src/gym_api/models/schedule.py:33,37` | [#833](https://github.com/amattas/gym-app/issues/833) |
| 613 | Missing composite index check_ins(location_id, checked_in_at) for busyness queries | Performance | `backend/src/gym_api/models/check_in.py:26-27,38-39` | [#834](https://github.com/amattas/gym-app/issues/834) |
| 614 | Missing index client_memberships.status -- 8+ queries filter without index | Performance | `backend/src/gym_api/models/client_membership.py:31-32` | [#835](https://github.com/amattas/gym-app/issues/835) |
| 615 | Pagination metadata has no total_count -- frontend cannot display result totals | Performance | `backend/src/gym_api/utils/pagination.py:50-69` | [#836](https://github.com/amattas/gym-app/issues/836) |
| 616 | get_trainer_busyness has no gym_id filter -- cross-tenant schedule exposure | Security | `backend/src/gym_api/services/busyness_service.py:55-80` | [#837](https://github.com/amattas/gym-app/issues/837) |
| 617 | Progress photo content_type accepts arbitrary strings -- no MIME allowlist | Security | `backend/src/gym_api/routers/progress_photos.py:19` | [#838](https://github.com/amattas/gym-app/issues/838) |
| 618 | Photo/data deletion never removes actual files from storage -- orphaned blobs | Bug | `backend/src/gym_api/services/progress_photo_service.py:40-42`, `data_deletion_service.py:114-118` | [#839](https://github.com/amattas/gym-app/issues/839) |
| 619 | S3 presigned URL has no maximum expiry enforcement | Security | `backend/src/gym_api/storage/s3_storage.py:56-62` | [#840](https://github.com/amattas/gym-app/issues/840) |
| 620 | Data export download returns PII without Content-Disposition or streaming | Security | `backend/src/gym_api/routers/data_privacy.py:72-83` | [#841](https://github.com/amattas/gym-app/issues/841) |
| 621 | S3Storage._get_client creates new boto3 per operation -- no reuse | Performance | `backend/src/gym_api/storage/s3_storage.py:20-28` | [#842](https://github.com/amattas/gym-app/issues/842) |
| 622 | ProgressPhotoCreate.notes and tags have no size limits | Security | `backend/src/gym_api/routers/progress_photos.py:20-21` | [#843](https://github.com/amattas/gym-app/issues/843) |
| 623 | No storage configuration in Settings -- S3/backend selection absent | Config | `backend/src/gym_api/config.py:8-22` | [#844](https://github.com/amattas/gym-app/issues/844) |
| 624 | No structured/JSON logging format -- plain text unusable in aggregators | Observability | `backend/src/gym_api/main.py:64-72` | [#845](https://github.com/amattas/gym-app/issues/845) |
| 625 | Request ID not propagated to log records -- correlation impossible | Observability | `backend/src/gym_api/middleware/request_id.py:10-16` | [#846](https://github.com/amattas/gym-app/issues/846) |
| 626 | Metrics endpoint not exposed -- in-memory metrics inaccessible to Prometheus | Observability | `backend/src/gym_api/metrics/prometheus.py:36-41` | [#847](https://github.com/amattas/gym-app/issues/847) |
| 627 | Config secrets bypass Settings -- STRIPE_WEBHOOK_SECRET/WEBAUTHN use os.getenv | Config | `backend/src/gym_api/routers/stripe_webhooks.py:20`, `passkey_service.py:8-10` | [#848](https://github.com/amattas/gym-app/issues/848) |
| 628 | OpenAPI/Swagger UI exposed in all environments including production | Security | `backend/src/gym_api/main.py:88-96` | [#849](https://github.com/amattas/gym-app/issues/849) |
| 629 | SMTP password and JWT secret not using SecretStr -- exposed in repr | Security | `backend/src/gym_api/config.py:11,18` | [#850](https://github.com/amattas/gym-app/issues/850) |
| 660 | API client hard-redirects via window.location.href on auth failure -- destroys SPA state | Bug | `frontend/src/lib/api.ts:77` | [#881](https://github.com/amattas/gym-app/issues/881) |
| 661 | Module-level uuid constants in tests mask gym_id validation bugs | Testing | `backend/tests/test_routers/test_workouts.py:13-14` and 8+ files | [#882](https://github.com/amattas/gym-app/issues/882) |
| 662 | Rate limiter test never tests actual 429 enforcement | Testing | `backend/tests/test_middleware/test_rate_limiter.py:20-26` | [#883](https://github.com/amattas/gym-app/issues/883) |
| 663 | Auth endpoint tests never verify service functions receive correct arguments | Testing | `backend/tests/test_auth/test_auth_endpoints.py:10-33,119-136` | [#884](https://github.com/amattas/gym-app/issues/884) |
| 664 | Migration missing server_default for string NOT NULL columns -- currency, format | Data Integrity | `backend/alembic/versions/001_initial_schema.py:877,919,943,841` | [#885](https://github.com/amattas/gym-app/issues/885) |
| 665 | Neither migration is idempotent -- re-running causes ProgrammingError | Bug | `backend/alembic/versions/001_initial_schema.py`, `002_add_missing_fk_indexes.py` | [#886](https://github.com/amattas/gym-app/issues/886) |
| 666 | Payment model missing updated_at but migration creates it -- ORM ignores column | Bug | `backend/alembic/versions/001_initial_schema.py:948` | [#887](https://github.com/amattas/gym-app/issues/887) |
| 667 | Migration env.py missing compare_server_default=True | Config | `backend/alembic/env.py:23-28,33-36` | [#888](https://github.com/amattas/gym-app/issues/888) |
| 668 | schedules.created_by_user_id missing FK constraint to users | Data Integrity | `backend/alembic/versions/001_initial_schema.py:548` | [#889](https://github.com/amattas/gym-app/issues/889) |
| 669 | gym_check_ins.checked_in_by_user_id missing FK constraint to users | Data Integrity | `backend/alembic/versions/001_initial_schema.py:598` | [#890](https://github.com/amattas/gym-app/issues/890) |
| 670 | calendar_tokens.owner_type missing CHECK constraint on polymorphic values | Data Integrity | `backend/alembic/versions/001_initial_schema.py:807-808` | [#891](https://github.com/amattas/gym-app/issues/891) |
| 671 | notes.notable_type missing CHECK constraint on polymorphic values | Data Integrity | `backend/alembic/versions/001_initial_schema.py:705` | [#892](https://github.com/amattas/gym-app/issues/892) |
| 672 | workout_summaries.gym_id missing index despite model index=True | Performance | `backend/src/gym_api/models/ai_summary.py:18` | [#893](https://github.com/amattas/gym-app/issues/893) |
| 673 | Back button on detail pages uses router.push -- destroys browser history | Usability | `frontend/src/app/(app)/clients/[clientId]/page.tsx:83` and 5 more pages | [#894](https://github.com/amattas/gym-app/issues/894) |
| 674 | Tab state not in URL -- browser back/forward loses selected tab on 5 pages | Usability | `frontend/src/app/(app)/analytics/page.tsx:102`, billing, memberships | [#895](https://github.com/amattas/gym-app/issues/895) |
| 675 | Login page doesn't redirect authenticated users | Bug | `frontend/src/app/(auth)/login/page.tsx:19-38` | [#896](https://github.com/amattas/gym-app/issues/896) |
| 676 | Dashboard/analytics/settings read gym_id from localStorage without auth context | Bug | `frontend/src/app/(app)/dashboard/page.tsx:21` and 3 more pages | [#897](https://github.com/amattas/gym-app/issues/897) |
| 677 | New workout page uses array index as React key for exercise entries | Bug | `frontend/src/app/(app)/workouts/new/page.tsx:197` | [#898](https://github.com/amattas/gym-app/issues/898) |
| 678 | No unsaved changes warning on form pages -- data lost without confirmation | Usability | `frontend/src/app/(app)/clients/new/page.tsx` and 3 more pages | [#899](https://github.com/amattas/gym-app/issues/899) |
| 679 | Dynamic route params no runtime UUID validation -- malformed URLs cause 500s | Bug | `frontend/src/app/(app)/workouts/[workoutId]/page.tsx:53` and 2 more | [#900](https://github.com/amattas/gym-app/issues/900) |
| 680 | ErrorBoundary doesn't reset on route change -- stale error persists | Bug | `frontend/src/app/(app)/layout.tsx:48`, `components/error-boundary.tsx` | [#901](https://github.com/amattas/gym-app/issues/901) |
| 681 | client_service.delete_client doesn't cancel memberships or future schedules | Bug | `backend/src/gym_api/services/client_service.py:82-85` | [#902](https://github.com/amattas/gym-app/issues/902) |
| 682 | discount_service apply_discount and validate_discount_code enforce different rules | Bug | `backend/src/gym_api/services/discount_service.py:69-128` | [#903](https://github.com/amattas/gym-app/issues/903) |
| 683 | Agreement send_envelope sends no email to client signer | Bug | `backend/src/gym_api/routers/agreements.py:95-105` | [#904](https://github.com/amattas/gym-app/issues/904) |
| 684 | Auth router directly queries User model -- bypasses auth_service layer | Bug | `backend/src/gym_api/routers/auth.py:225-294` | [#905](https://github.com/amattas/gym-app/issues/905) |
| 685 | PR detection commits independently of workout completion -- PRs persist on failure | Bug | `backend/src/gym_api/services/pr_service.py:102-103` | [#906](https://github.com/amattas/gym-app/issues/906) |
| 686 | Reporting service accesses 5 models directly -- bypasses service layer filters | Bug | `backend/src/gym_api/services/reporting_service.py:15-104` | [#907](https://github.com/amattas/gym-app/issues/907) |
| 687 | Stripe subscription.deleted missing cancellation_info metadata | Bug | `backend/src/gym_api/routers/stripe_webhooks.py:130-149` | [#908](https://github.com/amattas/gym-app/issues/908) |
| 688 | Billing checkout doesn't verify client_id owns membership -- cross-user payment | Security | `backend/src/gym_api/routers/billing.py:117-147` | [#909](https://github.com/amattas/gym-app/issues/909) |
| 711 | process_pending_deletions infinite retry loop -- no attempt counter or backoff | Bug | `backend/src/gym_api/services/data_deletion_service.py:66-78` | [#932](https://github.com/amattas/gym-app/issues/932) |
| 712 | complete_onboarding skips status validation -- restricted accounts can complete | Bug | `backend/src/gym_api/services/stripe_service.py:62-71` | [#933](https://github.com/amattas/gym-app/issues/933) |
| 713 | Custom domain activate/verify have no status transition guards | Bug | `backend/src/gym_api/services/custom_domain_service.py:43-58` | [#934](https://github.com/amattas/gym-app/issues/934) |
| 714 | ScheduleCreate accepts arbitrary status string -- callers can inject terminal states | Security | `backend/src/gym_api/schemas/schedule.py:13` | [#935](https://github.com/amattas/gym-app/issues/935) |
| 715 | create_membership accepts arbitrary initial_status parameter -- bypass trial/payment | Security | `backend/src/gym_api/services/membership_service.py:20-21,75` | [#936](https://github.com/amattas/gym-app/issues/936) |
| 716 | GoalUpdate PATCH allows setting status to any arbitrary string via service passthrough | Security | `backend/src/gym_api/schemas/goal.py:21` | [#937](https://github.com/amattas/gym-app/issues/937) |
| 717 | Discount code discount_type not validated as enum -- misinterpreted as fixed amount | Bug | `backend/src/gym_api/schemas/billing.py:119` | [#938](https://github.com/amattas/gym-app/issues/938) |
| 718 | iCal VEVENT missing mandatory DTSTAMP property (RFC 5545 violation) | Integration | `backend/src/gym_api/services/ical_service.py:94-103` | [#939](https://github.com/amattas/gym-app/issues/939) |
| 719 | Check-in occupancy histogram misaligned for non-UTC timezones | Bug | `backend/src/gym_api/services/check_in_service.py:121-137` | [#940](https://github.com/amattas/gym-app/issues/940) |
| 720 | Frontend schedule creation sends datetime-local without timezone offset | Usability | `frontend/src/app/(app)/schedules/page.tsx:172-183,90-96` | [#941](https://github.com/amattas/gym-app/issues/941) |
| 721 | process_pending_cancellations compares naive datetime to tz-aware now | Bug | `backend/src/gym_api/services/membership_service.py:344-347` | [#942](https://github.com/amattas/gym-app/issues/942) |
| 722 | GraphQL workouts query returns all statuses including cancelled -- no filter | Bug | `backend/src/gym_api/graphql/schema.py:149-174` | [#943](https://github.com/amattas/gym-app/issues/943) |
| 723 | GraphQL schedules query returns all statuses including cancelled/completed/no-show | Bug | `backend/src/gym_api/graphql/schema.py:176-201` | [#944](https://github.com/amattas/gym-app/issues/944) |
| 724 | GraphQL memberships query returns all statuses including cancelled/expired | Bug | `backend/src/gym_api/graphql/schema.py:203-236` | [#945](https://github.com/amattas/gym-app/issues/945) |
| 725 | GraphQL schema is read-only -- no mutation support | Bug | `backend/src/gym_api/graphql/schema.py:262` | [#946](https://github.com/amattas/gym-app/issues/946) |
| 726 | GraphQL get_graphql_context UUID parsing unhandled -- malformed sub/gym_id causes 500 | Bug | `backend/src/gym_api/routers/graphql_router.py:25-26` | [#947](https://github.com/amattas/gym-app/issues/947) |
| 727 | Registration endpoint ignores email sending failure -- no partial success indicator | Bug | `backend/src/gym_api/routers/auth.py:125-129` | [#948](https://github.com/amattas/gym-app/issues/948) |
| 728 | Stripe webhook falls through to success for unrecognized events with no logging | Bug | `backend/src/gym_api/routers/stripe_webhooks.py:36-151` | [#949](https://github.com/amattas/gym-app/issues/949) |
| 729 | Forgot-password wastes reset token when email send fails -- user cannot retry easily | Bug | `backend/src/gym_api/routers/auth.py:229-234` | [#950](https://github.com/amattas/gym-app/issues/950) |
| 730 | Calendar token endpoints accept arbitrary trainer_id/client_id without entity validation | Bug | `backend/src/gym_api/routers/calendar.py:38-84` | [#951](https://github.com/amattas/gym-app/issues/951) |
| 731 | Webhook delivery retries 4xx client errors -- non-retryable failures trigger full backoff | Bug | `backend/src/gym_api/webhooks/webhook_service.py:44-72` | [#952](https://github.com/amattas/gym-app/issues/952) |
| 732 | ErrorHandlerMiddleware returns generic 500 for all exceptions -- no type differentiation | Bug | `backend/src/gym_api/middleware/error_handler.py:28-42` | [#953](https://github.com/amattas/gym-app/issues/953) |
| 733 | Rate limiter silently swallows malformed token errors with no logging or size limit | Security | `backend/src/gym_api/middleware/rate_limiter.py:100-117` | [#954](https://github.com/amattas/gym-app/issues/954) |
| 750 | RequestIDMiddleware innermost -- request_id unknown on error/rate-limit responses | Bug | `backend/src/gym_api/main.py:108` | [#971](https://github.com/amattas/gym-app/issues/971) |
| 751 | Security headers missing on error and rate-limit response paths | Security | `backend/src/gym_api/middleware/security_headers.py:17-21` | [#972](https://github.com/amattas/gym-app/issues/972) |
| 752 | Database engine never disposed on shutdown -- connection pool leaked | Bug | `backend/src/gym_api/main.py:75-85`, `database.py:6` | [#973](https://github.com/amattas/gym-app/issues/973) |
| 753 | Module-level engine creation at import time prevents test database isolation | Bug | `backend/src/gym_api/database.py:6-7`, `config.py:38` | [#974](https://github.com/amattas/gym-app/issues/974) |
| 754 | WebhookResponse.created_at is str instead of datetime -- serialization mismatch | Bug | `backend/src/gym_api/routers/webhook_endpoints.py:32` | [#975](https://github.com/amattas/gym-app/issues/975) |
| 755 | WebhookResponse missing secret field -- created webhook secrets unrecoverable | Bug | `backend/src/gym_api/routers/webhook_endpoints.py:26-34` | [#976](https://github.com/amattas/gym-app/issues/976) |
| 756 | PaginatedResponse.data is untyped list -- OpenAPI loses all type information | Bug | `backend/src/gym_api/schemas/common.py:31` | [#977](https://github.com/amattas/gym-app/issues/977) |
| 757 | 7 additional schemas use str instead of Enum (measurement, gender, template_scope, domain_type, plan_type, check_in_method, account_type) | Bug | `schemas/measurement.py:9`, `client.py:13`, `program.py:10`, `custom_domain.py:9`, `plan_template.py:10`, `check_in.py:11`, `account.py:8` | [#978](https://github.com/amattas/gym-app/issues/978) |
| 758 | PlanTemplate addon_discount_percentage has no bounds -- allows negative or >100% | Bug | `backend/src/gym_api/schemas/plan_template.py:18` | [#979](https://github.com/amattas/gym-app/issues/979) |
| 759 | DiscountCodeCreate.amount no upper bound -- percentage discounts can exceed 100% | Bug | `backend/src/gym_api/schemas/billing.py:120` | [#980](https://github.com/amattas/gym-app/issues/980) |
| 760 | MembershipCreate.started_at accepts naive datetime -- timezone info lost | Bug | `backend/src/gym_api/schemas/membership.py:9` | [#981](https://github.com/amattas/gym-app/issues/981) |
| 761 | ScheduleUpdate empty body produces needless DB commit -- applies to 17 endpoints | Bug | `backend/src/gym_api/routers/schedules.py:86` | [#982](https://github.com/amattas/gym-app/issues/982) |
| 762 | ResetPasswordRequest/LoginRequest password no max_length -- bcrypt DoS vector | Security | `backend/src/gym_api/routers/auth.py:67-68,44` | [#983](https://github.com/amattas/gym-app/issues/983) |
| 763 | TrainerExceptionCreate.exception_date datetime vs Date type mismatch -- time silently truncated | Bug | `backend/src/gym_api/schemas/schedule.py:59` | [#984](https://github.com/amattas/gym-app/issues/984) |
| 764 | _check_double_booking queries across all tenants -- false conflicts and cross-tenant leak | Security | `backend/src/gym_api/services/schedule_service.py:163-179` | [#985](https://github.com/amattas/gym-app/issues/985) |
| 765 | Trainer availability get/set/exception service functions missing gym_id | Security | `backend/src/gym_api/services/schedule_service.py:106-144` | [#986](https://github.com/amattas/gym-app/issues/986) |
| 766 | check_and_record_prs existing PR lookup missing gym_id -- cross-tenant comparison | Security | `backend/src/gym_api/services/pr_service.py:53-58,79-84` | [#987](https://github.com/amattas/gym-app/issues/987) |
| 767 | _cancel_addon_memberships queries addons without gym_id filter | Security | `backend/src/gym_api/services/membership_service.py:225-244` | [#988](https://github.com/amattas/gym-app/issues/988) |
| 768 | get_occupancy_history router no gym_id and no location ownership verification | Security | `backend/src/gym_api/routers/check_ins.py:98-113` | [#989](https://github.com/amattas/gym-app/issues/989) |
| 769 | Audit logs page isLoading never reset on filter changes -- stale data shown | Bug | `frontend/src/app/(app)/audit-logs/page.tsx:30-40` | [#990](https://github.com/amattas/gym-app/issues/990) |
| 770 | Exercises page optimistic delete stale closure -- concurrent ops can lose data | Bug | `frontend/src/app/(app)/exercises/page.tsx:131-139` | [#991](https://github.com/amattas/gym-app/issues/991) |
| 771 | Memberships page Pause/Unpause/Cancel no loading state -- double-click possible | Bug | `frontend/src/app/(app)/memberships/page.tsx:71-105` | [#992](https://github.com/amattas/gym-app/issues/992) |
| 772 | Check-ins page fetchCheckIns not awaited -- occupancy races with list refresh | Bug | `frontend/src/app/(app)/check-ins/page.tsx:112-120` | [#993](https://github.com/amattas/gym-app/issues/993) |
| 773 | Settings page save silently no-ops when gym failed to load -- no user feedback | Usability | `frontend/src/app/(app)/settings/page.tsx:43-57` | [#994](https://github.com/amattas/gym-app/issues/994) |
| 774 | Frontend 5 pages refetch-after-mutation in same try/catch -- misleading error messages | Bug | `measurements/page.tsx`, `progress-photos/page.tsx`, `memberships/plans/page.tsx`, `billing/page.tsx`, `agreements/page.tsx` | [#995](https://github.com/amattas/gym-app/issues/995) |
| 799 | Cleanup job unbounded DELETE -- long-running transaction lock on large tables | Performance | `backend/src/gym_api/jobs/cleanup.py:18-38` | [#1020](https://github.com/amattas/gym-app/issues/1020) |
| 800 | Trial/cancellation batch loads all rows then filters in Python -- dates in JSON columns | Performance | `backend/src/gym_api/services/membership_service.py:291-311,331-355` | [#1021](https://github.com/amattas/gym-app/issues/1021) |
| 801 | select(func.count()).where() missing select_from() -- fragile FROM inference in 17+ queries | Bug | `services/reporting_service.py`, `analytics_service.py`, `check_in_service.py`, `busyness_service.py` | [#1022](https://github.com/amattas/gym-app/issues/1022) |
| 802 | list_prs query has no LIMIT -- returns all personal records unbounded | Performance | `backend/src/gym_api/services/pr_service.py:110-123` | [#1023](https://github.com/amattas/gym-app/issues/1023) |
| 803 | list_payments drops payments with NULL invoice_id when filtering by membership | Bug | `backend/src/gym_api/services/stripe_service.py:170-177` | [#1024](https://github.com/amattas/gym-app/issues/1024) |
| 804 | Invoice.membership_id missing index -- frequently filtered/joined | Performance | `backend/src/gym_api/models/invoice.py:38-40` | [#1025](https://github.com/amattas/gym-app/issues/1025) |
| 805 | Payment.invoice_id missing index -- used in JOIN queries | Performance | `backend/src/gym_api/models/invoice.py:70-72` | [#1026](https://github.com/amattas/gym-app/issues/1026) |
| 806 | Service-layer queries filter enum columns with bare strings -- silent empty results | Bug | `services/stripe_service.py:144`, `membership_service.py:116`, `esign_service.py:107`, `schedule_service.py:66` | [#1027](https://github.com/amattas/gym-app/issues/1027) |
| 807 | Auth layout missing main landmark -- screen readers cannot identify content | Accessibility | `frontend/src/app/(auth)/layout.tsx:7-9` | [#1028](https://github.com/amattas/gym-app/issues/1028) |
| 808 | Forgot-password error message missing role=alert for screen readers | Accessibility | `frontend/src/app/(auth)/forgot-password/page.tsx:74-76` | [#1029](https://github.com/amattas/gym-app/issues/1029) |
| 809 | Forgot-password success state change not announced to assistive technology | Accessibility | `frontend/src/app/(auth)/forgot-password/page.tsx:40-58` | [#1030](https://github.com/amattas/gym-app/issues/1030) |
| 810 | SidebarTrigger in app header lacks descriptive aria-label | Accessibility | `frontend/src/app/(app)/layout.tsx:42` | [#1031](https://github.com/amattas/gym-app/issues/1031) |
| 811 | Analytics day-range filter buttons lack group semantics and aria-pressed | Accessibility | `frontend/src/app/(app)/analytics/page.tsx:109-119` | [#1032](https://github.com/amattas/gym-app/issues/1032) |
| 812 | New workout remove buttons and Select components missing aria-label/label | Accessibility | `frontend/src/app/(app)/workouts/new/page.tsx:202-280` | [#1033](https://github.com/amattas/gym-app/issues/1033) |
| 813 | Goals/photos delete buttons and Goals Progress bar missing aria-label | Accessibility | `goals/page.tsx:312,343-349`, `progress-photos/page.tsx:208-215` | [#1034](https://github.com/amattas/gym-app/issues/1034) |
| 814 | Audit logs filter input missing label -- placeholder insufficient for WCAG | Accessibility | `frontend/src/app/(app)/audit-logs/page.tsx:53-57` | [#1035](https://github.com/amattas/gym-app/issues/1035) |
| 815 | All 31 app pages share same document title -- WCAG 2.4.2 violation | Accessibility | All pages under `frontend/src/app/(app)/` | [#1036](https://github.com/amattas/gym-app/issues/1036) |
| 816 | Schedules/check-ins filter labels text-muted-foreground potential contrast failure | Accessibility | `schedules/page.tsx:206`, `check-ins/page.tsx:187` | [#1037](https://github.com/amattas/gym-app/issues/1037) |
| 817 | Dynamic search results on 4+ pages not announced to screen readers | Accessibility | `accounts/page.tsx`, `measurements/page.tsx`, `goals/page.tsx`, `progress-photos/page.tsx` | [#1038](https://github.com/amattas/gym-app/issues/1038) |
| 818 | complete_workout response mixes new_prs outside the {data:...} envelope | Spec Compliance | `backend/src/gym_api/routers/workouts.py:185-188` | [#1039](https://github.com/amattas/gym-app/issues/1039) |
| 819 | POST /v1/invitations/accept returns 200 instead of 201 for new resource creation | Spec Compliance | `backend/src/gym_api/routers/invitations.py:43` | [#1040](https://github.com/amattas/gym-app/issues/1040) |
| 820 | PUT locations/notifications/webhooks use partial-update semantics -- HTTP method confusion | Bug | `routers/locations.py:57`, `notifications.py:54`, `webhook_endpoints.py:60` | [#1041](https://github.com/amattas/gym-app/issues/1041) |
| 821 | All 25+ POST 201 endpoints missing Location header | Spec Compliance | All router files with status_code=201 | [#1042](https://github.com/amattas/gym-app/issues/1042) |
| 822 | Starlette 404/405 responses bypass custom error handler -- bare {detail} envelope | Spec Compliance | `backend/src/gym_api/main.py:115-116` | [#1043](https://github.com/amattas/gym-app/issues/1043) |
| 823 | Billing list_invoices/list_payments router endpoints lack pagination parameters | Spec Compliance | `backend/src/gym_api/routers/billing.py:198-234` | [#1044](https://github.com/amattas/gym-app/issues/1044) |
| 824 | Analytics endpoints accept gym_id as both path param and dependency -- double source | Bug | `backend/src/gym_api/routers/calendar.py:100-130` | [#1045](https://github.com/amattas/gym-app/issues/1045) |
| 842 | test_gyms.py no autouse fixture -- manual override cleanup leaks on failure | Testing | `backend/tests/test_routers/test_gyms.py:34-137` | [#1068](https://github.com/amattas/gym-app/issues/1068) |
| 843 | Idempotency and error handler tests register routes on global app at import | Testing | `test_idempotency.py:6-23`, `test_error_handler.py:6-24` | [#1069](https://github.com/amattas/gym-app/issues/1069) |
| 844 | test_register_success doesn't verify email verification functions called | Testing | `backend/tests/test_auth/test_auth_endpoints.py:11-33` | [#1070](https://github.com/amattas/gym-app/issues/1070) |
| 845 | test_login_success doesn't verify create_session called | Testing | `backend/tests/test_auth/test_auth_endpoints.py:118-136` | [#1071](https://github.com/amattas/gym-app/issues/1071) |
| 846 | Passkey test sys.modules patch ineffective -- module already imported | Testing | `backend/tests/test_services/test_passkey_service.py:9-26` | [#1072](https://github.com/amattas/gym-app/issues/1072) |
| 847 | test_create_stripe_connect asserts onboarding_url outside data envelope | Testing | `backend/tests/test_routers/test_billing.py:134` | [#1073](https://github.com/amattas/gym-app/issues/1073) |
| 848 | Module-level entity ID constants reused across factory calls -- duplicates masked | Testing | `test_schedules.py:16`, `test_check_ins.py:16`, `test_goals.py:15` | [#1074](https://github.com/amattas/gym-app/issues/1074) |
| 849 | Cache service tests mutate module-level _redis without isolation | Testing | `backend/tests/test_services/test_cache_service.py:9-13` | [#1075](https://github.com/amattas/gym-app/issues/1075) |
| 850 | test_schedule_conflict only tests ValueError -- other exception types untested | Testing | `backend/tests/test_routers/test_schedules.py:92-108` | [#1076](https://github.com/amattas/gym-app/issues/1076) |
| 856 | CI all GitHub Actions pinned by mutable tag not SHA -- supply chain risk | Security | `.github/workflows/ci.yml` | [#1077](https://github.com/amattas/gym-app/issues/1077) |
| 857 | K8s Deployment uses default service account with auto-mounted token | Security | `k8s/deployment.yaml:16-56` | [#1078](https://github.com/amattas/gym-app/issues/1078) |
| 858 | K8s NetworkPolicy egress to port 443 unrestricted to any IP | Security | `k8s/network-policy.yaml:35-42` | [#1079](https://github.com/amattas/gym-app/issues/1079) |
| 859 | Settings validate_jwt_secret called too late -- insecure secret usable before lifespan | Security | `config.py:24-35`, `main.py:77` | [#1080](https://github.com/amattas/gym-app/issues/1080) |
| 860 | Docker Compose api service has no restart policy | Infra | `docker-compose.yml:2-14` | [#1081](https://github.com/amattas/gym-app/issues/1081) |
| 861 | Docker Compose Redis no persistence -- rate-limit state lost on restart | Config | `docker-compose.yml:32-40` | [#1082](https://github.com/amattas/gym-app/issues/1082) |
| 862 | CI missing concurrency control -- parallel runs waste resources | Config | `.github/workflows/ci.yml:1-6` | [#1083](https://github.com/amattas/gym-app/issues/1083) |
| 863 | K8s Deployment missing terminationGracePeriodSeconds | Infra | `k8s/deployment.yaml:16-56` | [#1084](https://github.com/amattas/gym-app/issues/1084) |
| 864 | K8s manifests missing namespace declarations | Infra | `k8s/*.yaml` (all 5 files) | [#1085](https://github.com/amattas/gym-app/issues/1085) |
| 865 | Docker Compose has no migration service | Config | `docker-compose.yml:2-14` | [#1086](https://github.com/amattas/gym-app/issues/1086) |
| 871 | Schedule create form allows end datetime before start | Bug | `frontend/src/app/(app)/schedules/page.tsx:170-186` | [#1087](https://github.com/amattas/gym-app/issues/1087) |
| 872 | Goals progress bar breaks with negative target_value | Bug | `frontend/src/app/(app)/goals/page.tsx:288-294` | [#1088](https://github.com/amattas/gym-app/issues/1088) |
| 873 | refreshGoals() has no try/catch -- unhandled rejection | Bug | `frontend/src/app/(app)/goals/page.tsx:56-62` | [#1089](https://github.com/amattas/gym-app/issues/1089) |
| 874 | Workout detail Edit Set dialog uses div not form | Usability | `frontend/src/app/(app)/workouts/[workoutId]/page.tsx:296-320` | [#1090](https://github.com/amattas/gym-app/issues/1090) |
| 875 | parseInt(editReps) no radix + NaN guard in workout detail | Bug | `frontend/src/app/(app)/workouts/[workoutId]/page.tsx:118-119` | [#1091](https://github.com/amattas/gym-app/issues/1091) |
| 876 | Settings page save button no loading/disabled state | Usability | `frontend/src/app/(app)/settings/page.tsx:108` | [#1092](https://github.com/amattas/gym-app/issues/1092) |
| 877 | Membership action buttons no loading state -- double-submit | Usability | `frontend/src/app/(app)/memberships/page.tsx:71-105` | [#1093](https://github.com/amattas/gym-app/issues/1093) |
| 878 | Agreements page cannot view template content after creation | Usability | `frontend/src/app/(app)/agreements/page.tsx:142-174` | [#1094](https://github.com/amattas/gym-app/issues/1094) |
| 879 | Analytics page duplicate API call on clientDays change | Bug | `frontend/src/app/(app)/analytics/page.tsx:57-88` | [#1095](https://github.com/amattas/gym-app/issues/1095) |
| 880 | Billing invoice amount_cents division assumes cents | Integration | `frontend/src/app/(app)/billing/page.tsx:220` | [#1096](https://github.com/amattas/gym-app/issues/1096) |
| 881 | Notifications preference toggle lost-update on rapid clicks | Bug | `frontend/src/app/(app)/notifications/page.tsx:35-44` | [#1097](https://github.com/amattas/gym-app/issues/1097) |
| 889 | Inconsistent completed set filtering across AI summary, PRs, analytics | Bug | `ai_summary_service.py:123`, `workout_service.py:184`, `analytics_service.py:157` | [#1098](https://github.com/amattas/gym-app/issues/1098) |
| 890 | AI summary skips bodyweight exercises via weight_kg truthiness | Bug | `backend/src/gym_api/services/ai_summary_service.py:129-130` | [#1099](https://github.com/amattas/gym-app/issues/1099) |
| 892 | get_current_period_usage crashes with MultipleResultsFound | Bug | `backend/src/gym_api/services/usage_metering_service.py:70-82` | [#1100](https://github.com/amattas/gym-app/issues/1100) |
| 893 | check_limit off-by-one allows exceeding limit by 1 | Bug | `backend/src/gym_api/services/usage_metering_service.py:93-94` | [#1101](https://github.com/amattas/gym-app/issues/1101) |
| 894 | reset_period_visits per-item commit in batch loop | Bug | `backend/src/gym_api/services/membership_service.py:286,370-372` | [#1102](https://github.com/amattas/gym-app/issues/1102) |
| 895 | process_trial_conversions no gym_id filter -- cross-tenant batch | Security | `backend/src/gym_api/services/membership_service.py:293-297` | [#1103](https://github.com/amattas/gym-app/issues/1103) |
| 896 | workout_analytics_preview N+1 queries on exercises/sets | Performance | `backend/src/gym_api/routers/analytics.py:32-43` | [#1104](https://github.com/amattas/gym-app/issues/1104) |
| 897 | generate_ics crashes on NULL scheduled_end | Bug | `backend/src/gym_api/services/ical_service.py:98` | [#1105](https://github.com/amattas/gym-app/issues/1105) |
| 898 | list_workout_exercises and list_sets no gym_id scoping | Security | `backend/src/gym_api/services/workout_service.py:69-75,86-92` | [#1106](https://github.com/amattas/gym-app/issues/1106) |
| 899 | delete_discount_code hard-deletes used codes -- orphans records | Data Integrity | `backend/src/gym_api/services/discount_service.py:64-66` | [#1107](https://github.com/amattas/gym-app/issues/1107) |
| 900 | add_exercise_to_workout no exercise_id validation | Bug | `backend/src/gym_api/services/workout_service.py:59-66` | [#1108](https://github.com/amattas/gym-app/issues/1108) |
| 903 | GraphQL trainers resolver hardcodes specializations=None -- discards real data | Bug | `backend/src/gym_api/graphql/schema.py:144` | [#1124](https://github.com/amattas/gym-app/issues/1124) |
| 904 | GraphQL ScheduleType declares client_id/trainer_id as nullable but DB is NOT NULL | Bug | `backend/src/gym_api/graphql/schema.py:55-56` | [#1125](https://github.com/amattas/gym-app/issues/1125) |
| 905 | CORS expose_headers missing X-RateLimit-Reset, Retry-After, X-Idempotent-Replayed | Integration | `backend/src/gym_api/middleware/cors.py:26` | [#1126](https://github.com/amattas/gym-app/issues/1126) |
| 908 | GraphQL context getter KeyError on missing JWT sub claim -- unhandled 500 | Bug | `backend/src/gym_api/routers/graphql_router.py:25` | [#1129](https://github.com/amattas/gym-app/issues/1129) |
| 909 | Metrics middleware inside ErrorHandler/RateLimiter -- 500s and 429s invisible | Observability | `backend/src/gym_api/main.py:102,108-112` | [#1130](https://github.com/amattas/gym-app/issues/1130) |
| 912 | Lifespan does not validate database connectivity on startup | Config | `backend/src/gym_api/main.py:76-82` | [#1133](https://github.com/amattas/gym-app/issues/1133) |
| 916 | RegistrationCredential.parse_raw() uses deprecated Pydantic v1 API | Bug | `backend/src/gym_api/services/passkey_service.py:101` | [#1137](https://github.com/amattas/gym-app/issues/1137) |
| 917 | get_current_user KeyError when JWT payload lacks sub claim | Security | `backend/src/gym_api/dependencies/auth.py:26` | [#1138](https://github.com/amattas/gym-app/issues/1138) |
| 918 | No MFA disable endpoint -- users cannot turn off MFA once enabled | Bug | `backend/src/gym_api/routers/auth.py` | [#1139](https://github.com/amattas/gym-app/issues/1139) |
| 919 | MFA setup allows overwriting pending TOTP secret -- attacker can hijack MFA | Security | `backend/src/gym_api/routers/auth.py:164-172` | [#1140](https://github.com/amattas/gym-app/issues/1140) |
| 920 | Password reset/email verification tokens not invalidated on new request | Security | `backend/src/gym_api/services/verification_service.py:15-26,53-64` | [#1141](https://github.com/amattas/gym-app/issues/1141) |
| 921 | Login creates session but discards session_id -- client can't identify session | Bug | `backend/src/gym_api/routers/auth.py:147-151` | [#1142](https://github.com/amattas/gym-app/issues/1142) |
| 926 | Self-registered users get gym_id=None -- locked out of all gym features | Bug | `backend/src/gym_api/routers/auth.py:101-129`, `backend/src/gym_api/services/auth_service.py:41-66` | [#1147](https://github.com/amattas/gym-app/issues/1147) |
| 931 | update_stripe_account None guard blocks clearing processing_fee_percentage | Bug | `backend/src/gym_api/services/stripe_service.py:36-44` | [#1152](https://github.com/amattas/gym-app/issues/1152) |
| 933 | CheckoutCreate.payment_method_id accepted but silently discarded | Bug | `backend/src/gym_api/routers/billing.py:117-147` | [#1154](https://github.com/amattas/gym-app/issues/1154) |
| 934 | list_payments_for_membership INNER JOIN drops payments with NULL invoice_id | Bug | `backend/src/gym_api/services/invoice_service.py:31-40` | [#1155](https://github.com/amattas/gym-app/issues/1155) |
| 935 | Discount code lookup is case-sensitive -- users must match exact case | Bug | `backend/src/gym_api/services/discount_service.py:72-78,109-116` | [#1156](https://github.com/amattas/gym-app/issues/1156) |
| 936 | DiscountCodeUpdate cannot clear valid_from/valid_until -- None guard blocks | Bug | `backend/src/gym_api/services/discount_service.py:53-61` | [#1157](https://github.com/amattas/gym-app/issues/1157) |
| 937 | validate_discount_code returns amount in ambiguous units -- no cents/dollars | Bug | `backend/src/gym_api/services/discount_service.py:98-103` | [#1158](https://github.com/amattas/gym-app/issues/1158) |
| 938 | Stripe webhook invoice.paid does not set paid_at timestamp | Bug | `backend/src/gym_api/routers/stripe_webhooks.py:95-109` | [#1159](https://github.com/amattas/gym-app/issues/1159) |
| 939 | Stripe webhook invoice.payment_failed sets uncollectible without state check | Bug | `backend/src/gym_api/routers/stripe_webhooks.py:111-125` | [#1160](https://github.com/amattas/gym-app/issues/1160) |
| 940 | Usage check endpoint accepts arbitrary metric_name with no allowlist | Security | `backend/src/gym_api/routers/usage.py:42-52` | [#1161](https://github.com/amattas/gym-app/issues/1161) |
| 942 | Duplicate discount codes within gym cause MultipleResultsFound crash | Bug | `backend/src/gym_api/services/discount_service.py:11-18,72-78` | [#1163](https://github.com/amattas/gym-app/issues/1163) |
| 946 | invoice_service and stripe_service contain duplicate CRUD functions | Bug | `backend/src/gym_api/services/invoice_service.py`, `backend/src/gym_api/services/stripe_service.py` | [#1167](https://github.com/amattas/gym-app/issues/1167) |
| 947 | get_metric_totals func.max(limit_value) returns historical max not current | Bug | `backend/src/gym_api/services/usage_metering_service.py:100-115` | [#1168](https://github.com/amattas/gym-app/issues/1168) |
| 948 | All 3 usage router endpoints missing RBAC -- any role views business metrics | Security | `backend/src/gym_api/routers/usage.py:16-52` | [#1169](https://github.com/amattas/gym-app/issues/1169) |
| 949 | Frontend billing discount form missing max_uses, valid_from, valid_until fields | Usability | `frontend/src/app/(app)/billing/page.tsx:88-107` | [#1170](https://github.com/amattas/gym-app/issues/1170) |
| 950 | Frontend billing invoices tab always empty -- no membership selector UI | Usability | `frontend/src/app/(app)/billing/page.tsx:79,194-248` | [#1171](https://github.com/amattas/gym-app/issues/1171) |
| 951 | Frontend billing page has no payment methods management UI | Usability | `frontend/src/app/(app)/billing/page.tsx` | [#1172](https://github.com/amattas/gym-app/issues/1172) |
| 952 | DiscountCodeUpdate cannot modify discount_type, amount, or code after creation | Bug | `backend/src/gym_api/schemas/billing.py:127-132` | [#1173](https://github.com/amattas/gym-app/issues/1173) |
| 959 | Mapped[float] on Numeric columns causes silent precision loss | Bug | `backend/src/gym_api/models/body_measurement.py:32-34`, `backend/src/gym_api/models/discount_code.py:27` | [#1180](https://github.com/amattas/gym-app/issues/1180) |
| 960 | onupdate=func.now() is ORM-only -- no DB trigger, raw SQL leaves stale timestamps | Bug | `backend/src/gym_api/models/*.py`, `backend/alembic/versions/` | [#1181](https://github.com/amattas/gym-app/issues/1181) |
| 961 | client_memberships.plan_type is String(50) not Enum -- inconsistent with plan_templates | Bug | `backend/src/gym_api/models/client_membership.py`, `backend/src/gym_api/models/plan_template.py` | [#1182](https://github.com/amattas/gym-app/issues/1182) |
| 986 | Trainers page entirely read-only -- no create/edit/delete capability | Usability | `frontend/src/app/(app)/trainers/page.tsx` | [#1196](https://github.com/amattas/gym-app/issues/1196) |
| 987 | Client detail page has no edit or delete capability | Usability | `frontend/src/app/(app)/clients/[clientId]/page.tsx:80-219` | [#1199](https://github.com/amattas/gym-app/issues/1199) |
| 988 | Programs list page has no delete or edit actions | Usability | `frontend/src/app/(app)/programs/page.tsx:39-107` | [#1200](https://github.com/amattas/gym-app/issues/1200) |
| 989 | Program detail page has no ability to add exercises to a day | Usability | `frontend/src/app/(app)/programs/[programId]/page.tsx:160-205` | [#1201](https://github.com/amattas/gym-app/issues/1201) |
| 990 | Client detail fires 3 parallel API calls with no loading coordination | Bug | `frontend/src/app/(app)/clients/[clientId]/page.tsx:51-70` | [#1202](https://github.com/amattas/gym-app/issues/1202) |
| 991 | Analytics page shows misleading No analytics data when gym_id is missing | Usability | `frontend/src/app/(app)/analytics/page.tsx:39-43,182-184` | [#1203](https://github.com/amattas/gym-app/issues/1203) |
| 992 | All Dialog components missing DialogDescription -- Radix accessibility warning | Accessibility | `frontend/src/app/(app)/schedules/page.tsx`, `programs/[programId]/page.tsx` | [#1205](https://github.com/amattas/gym-app/issues/1205) |
| 993 | Trainers page shows deactivated trainers with no filter option | Usability | `frontend/src/app/(app)/trainers/page.tsx:29-34` | [#1207](https://github.com/amattas/gym-app/issues/1207) |
| 994 | Settings page gym_id interpolated in URL without encodeURIComponent | Security | `frontend/src/app/(app)/settings/page.tsx:33,48` | [#1208](https://github.com/amattas/gym-app/issues/1208) |
| 995 | Settings page shows empty form with no select-a-gym message when gym_id missing | Usability | `frontend/src/app/(app)/settings/page.tsx:28-41` | [#1210](https://github.com/amattas/gym-app/issues/1210) |
| 996 | record_visit dual counter mutation not atomic -- partial state on session error | Bug | `backend/src/gym_api/services/membership_service.py:247-261` | [#1211](https://github.com/amattas/gym-app/issues/1211) |
| 997 | Deferred cancel_membership does not update status field -- invisible to queries | Bug | `backend/src/gym_api/services/membership_service.py:208-214` | [#1212](https://github.com/amattas/gym-app/issues/1212) |
| 998 | process_pending_cancellations inner commit breaks batch atomicity | Bug | `backend/src/gym_api/services/membership_service.py:348-354` | [#1213](https://github.com/amattas/gym-app/issues/1213) |
| 999 | reset_period_visits no guard against premature invocation mid-period | Bug | `backend/src/gym_api/services/membership_service.py:275-288` | [#1214](https://github.com/amattas/gym-app/issues/1214) |
| 1000 | create_check_in membership check excludes trial status -- false warning | Bug | `backend/src/gym_api/services/check_in_service.py:27-39` | [#1215](https://github.com/amattas/gym-app/issues/1215) |
| 1001 | list_check_ins date filter timezone-offset produces wrong UTC day range | Bug | `backend/src/gym_api/services/check_in_service.py:85-86` | [#1216](https://github.com/amattas/gym-app/issues/1216) |
| 1002 | list_workouts WorkoutStatus(status) raises unhandled ValueError for invalid strings | Bug | `backend/src/gym_api/services/workout_service.py:40` | [#1218](https://github.com/amattas/gym-app/issues/1218) |
| 1003 | update_program cache_delete failure propagates exception after successful DB commit | Bug | `backend/src/gym_api/services/program_service.py:60-63` | [#1219](https://github.com/amattas/gym-app/issues/1219) |
| 1004 | delete_program does not check for active ClientProgram references | Bug | `backend/src/gym_api/services/program_service.py:66-70` | [#1220](https://github.com/amattas/gym-app/issues/1220) |
| 1005 | set_trainer_availability no flush between delete and insert -- PK collision | Bug | `backend/src/gym_api/services/schedule_service.py:117-134` | [#1221](https://github.com/amattas/gym-app/issues/1221) |
| 1006 | create_trainer_exception allows duplicate exceptions for same trainer and date | Bug | `backend/src/gym_api/services/schedule_service.py:137-144` | [#1222](https://github.com/amattas/gym-app/issues/1222) |
| 1007 | update_preferences concurrent INSERT race -- unhandled IntegrityError | Bug | `backend/src/gym_api/services/notification_service.py:40-53` | [#1225](https://github.com/amattas/gym-app/issues/1225) |
| 1008 | compute_workout_analytics treats None weight_kg as 0 -- bodyweight excluded | Bug | `backend/src/gym_api/services/analytics_service.py:28-33` | [#1227](https://github.com/amattas/gym-app/issues/1227) |
| 1009 | completion_rate returns 0.0-1.0 fraction not percentage -- display ambiguity | Bug | `backend/src/gym_api/services/analytics_service.py:104-108` | [#1228](https://github.com/amattas/gym-app/issues/1228) |
| 1010 | Volume trend groups by UTC date not gym-local date -- wrong day boundaries | Bug | `backend/src/gym_api/services/analytics_service.py:139` | [#1230](https://github.com/amattas/gym-app/issues/1230) |
| 1011 | _row_to_dict does not serialize nested JSONB UUID/datetime values -- export crash | Bug | `backend/src/gym_api/services/data_export_service.py:53-63` | [#1231](https://github.com/amattas/gym-app/issues/1231) |
| 1012 | _anonymize_client_data N+1 DELETE loop for photos/measurements | Performance | `backend/src/gym_api/services/data_deletion_service.py:114-124` | [#1233](https://github.com/amattas/gym-app/issues/1233) |
| 1013 | Delete operations never verified in 11+ test files -- mock delete never asserted | Testing | Multiple `backend/tests/test_routers/test_*.py` files | [#1236](https://github.com/amattas/gym-app/issues/1236) |
| 1014 | Missing npm audit in CI -- frontend dependencies never scanned | Security | `.github/workflows/ci.yml` | [#1238](https://github.com/amattas/gym-app/issues/1238) |
| 1015 | Check-in router tests missing exception/checkout-already-done test cases | Testing | `backend/tests/test_routers/test_check_ins.py` | [#1242](https://github.com/amattas/gym-app/issues/1242) |
| 1016 | Router-service signature mismatches invisible -- all tests mock service layer | Testing | All `backend/tests/test_routers/` files | [#1243](https://github.com/amattas/gym-app/issues/1243) |
| 1017 | No test for get_current_user when is_active=False -- deactivated access untested | Testing | `backend/tests/test_auth/test_dependencies.py` | [#1244](https://github.com/amattas/gym-app/issues/1244) |
| 1018 | NoteResponse created_at/updated_at typed as str instead of datetime | Bug | `backend/src/gym_api/routers/notes.py:27-28` | [#1247](https://github.com/amattas/gym-app/issues/1247) |
| 1019 | SummaryResponse generated_at typed as str instead of datetime | Bug | `backend/src/gym_api/routers/ai_summaries.py:21` | [#1248](https://github.com/amattas/gym-app/issues/1248) |
| 1020 | CheckoutResponse missing model_config from_attributes | Bug | `backend/src/gym_api/schemas/billing.py:69-76` | [#1249](https://github.com/amattas/gym-app/issues/1249) |
| 1021 | NoteCreate missing max_length on content -- unbounded input | Security | `backend/src/gym_api/routers/notes.py:17` | [#1251](https://github.com/amattas/gym-app/issues/1251) |
| 1022 | SummaryUpdate missing max_length on content -- unbounded input | Security | `backend/src/gym_api/routers/ai_summaries.py:28` | [#1252](https://github.com/amattas/gym-app/issues/1252) |
| 1023 | API base path uses /v1/ instead of spec-required /api/v1/ | Spec Compliance | All router files | [#1253](https://github.com/amattas/gym-app/issues/1253) |
| 1024 | Client detail page expects notes field but ClientResponse has fitness_goals | Integration | `frontend/src/app/(app)/clients/[clientId]/page.tsx:23` ↔ `backend/src/gym_api/schemas/client.py:50` | [#1254](https://github.com/amattas/gym-app/issues/1254) |
| 1025 | Accounts page Member role field not in ClientResponse -- always shows member | Integration | `frontend/src/app/(app)/accounts/page.tsx:47,292` | [#1255](https://github.com/amattas/gym-app/issues/1255) |
| 1026 | ProgramDayExerciseCreate missing ge=0 on default_sets/default_reps/rest_seconds | Bug | `backend/src/gym_api/schemas/client_program.py:40-42` | [#1256](https://github.com/amattas/gym-app/issues/1256) |
| 1027 | WorkoutExerciseCreate target_sets/target_reps missing ge=0 constraint | Bug | `backend/src/gym_api/schemas/workout.py:24-25` | [#1257](https://github.com/amattas/gym-app/issues/1257) |
| 1039 | AuthProvider load() useEffect missing AbortController -- stale auth state | Bug | `frontend/src/lib/auth.tsx:44-68` | [#1260](https://github.com/amattas/gym-app/issues/1260) |
| 1040 | Login page stale tokens interfere with new login request flow | Bug | `frontend/src/app/(auth)/login/page.tsx:26-37` | [#1261](https://github.com/amattas/gym-app/issues/1261) |
| 1041 | Schedule create form allows end before start with no validation | Bug | `frontend/src/app/(app)/schedules/page.tsx:170-186` | [#1262](https://github.com/amattas/gym-app/issues/1262) |
| 1042 | Goals page progress percentage incorrect for inverse goals and zero-target | Bug | `frontend/src/app/(app)/goals/page.tsx:288-294` | [#1263](https://github.com/amattas/gym-app/issues/1263) |
| 1043 | Billing discount creation accepts out-of-range amount | Bug | `frontend/src/app/(app)/billing/page.tsx:88-108` | [#1264](https://github.com/amattas/gym-app/issues/1264) |
| 1044 | Agreements page no way to view/edit template content after creation | Usability | `frontend/src/app/(app)/agreements/page.tsx:142-174` | [#1265](https://github.com/amattas/gym-app/issues/1265) |
| 1045 | Domains page verify/delete buttons no loading state -- double-click | Usability | `frontend/src/app/(app)/domains/page.tsx:81-99,196-212` | [#1266](https://github.com/amattas/gym-app/issues/1266) |
| 1046 | New workout page set rows use array index as React key | Bug | `frontend/src/app/(app)/workouts/new/page.tsx:231` | [#1267](https://github.com/amattas/gym-app/issues/1267) |
| 1047 | Client detail 3 parallel fetches with no coordinated error handling | Bug | `frontend/src/app/(app)/clients/[clientId]/page.tsx:51-70` | [#1268](https://github.com/amattas/gym-app/issues/1268) |
| 1048 | get_db return type annotation declares AsyncSession but is generator | Bug | `backend/src/gym_api/database.py:14-16` | [#1275](https://github.com/amattas/gym-app/issues/1275) |
| 1049 | Metrics middleware misses responses from outer middleware layers | Bug | `backend/src/gym_api/main.py:101-102` | [#1276](https://github.com/amattas/gym-app/issues/1276) |
| 1050 | Idempotency replay coerces Content-Type to application/json | Bug | `backend/src/gym_api/middleware/idempotency.py:54-58` | [#1277](https://github.com/amattas/gym-app/issues/1277) |
| 1051 | Rate limiter Redis-to-memory fallback double-counts request | Bug | `backend/src/gym_api/middleware/rate_limiter.py:69-84` | [#1278](https://github.com/amattas/gym-app/issues/1278) |
| 1052 | Scheduler module-level singleton retains stale event loop | Bug | `backend/src/gym_api/jobs/scheduler.py:10` | [#1279](https://github.com/amattas/gym-app/issues/1279) |
| 1053 | Config Settings() instantiated at module level triggers DB at import | Config | `backend/src/gym_api/config.py:38` | [#1281](https://github.com/amattas/gym-app/issues/1281) |
| 1054 | stripe_accounts.processing_fee_percentage uses Float not Numeric | Data Integrity | `backend/src/gym_api/models/stripe_account.py:35` | [#1282](https://github.com/amattas/gym-app/issues/1282) |
| 1055 | workouts.status index=True in model but no index in migration | Performance | `backend/src/gym_api/models/workout.py:34` | [#1283](https://github.com/amattas/gym-app/issues/1283) |
| 1056 | workout_exercises.exercise_id FK column missing index | Performance | `backend/src/gym_api/models/workout.py:51` | [#1284](https://github.com/amattas/gym-app/issues/1284) |
| 1057 | Exercise model missing updated_at column | Bug | `backend/src/gym_api/models/exercise.py:11-25` | [#1285](https://github.com/amattas/gym-app/issues/1285) |
| 1058 | Workout model missing updated_at column | Bug | `backend/src/gym_api/models/workout.py:19-41` | [#1286](https://github.com/amattas/gym-app/issues/1286) |
| 1059 | gym_check_ins missing updated_at column | Bug | `backend/src/gym_api/models/check_in.py:18-43` | [#1287](https://github.com/amattas/gym-app/issues/1287) |
| 1060 | trainer_invitations.token_hash String(64) vs others String(128) | Data Integrity | `backend/src/gym_api/models/trainer_invitation.py:21` | [#1288](https://github.com/amattas/gym-app/issues/1288) |
| 1061 | schedules.created_by_user_id missing FK constraint | Data Integrity | `backend/src/gym_api/models/schedule.py:43-45` | [#1289](https://github.com/amattas/gym-app/issues/1289) |
| 1062 | gym_check_ins.checked_in_by_user_id missing FK constraint | Data Integrity | `backend/src/gym_api/models/check_in.py:35-37` | [#1290](https://github.com/amattas/gym-app/issues/1290) |
| 1063 | trainer_client_assignments.assigned_by missing FK constraint | Data Integrity | `backend/src/gym_api/models/trainer_client.py:23` | [#1291](https://github.com/amattas/gym-app/issues/1291) |
| 1064 | progress_photos.measurement_id missing FK constraint | Data Integrity | `backend/src/gym_api/models/progress_photo.py:23-25` | [#1292](https://github.com/amattas/gym-app/issues/1292) |
| 1065 | progress_photos.uploaded_by_user_id missing FK constraint | Data Integrity | `backend/src/gym_api/models/progress_photo.py:26-28` | [#1293](https://github.com/amattas/gym-app/issues/1293) |
| 1066 | discount_codes.amount missing CHECK constraint >= 0 | Data Integrity | `backend/src/gym_api/models/discount_code.py:27` | [#1294](https://github.com/amattas/gym-app/issues/1294) |
| 1067 | trainer_availability.day_of_week missing CHECK 0-6 | Data Integrity | `backend/src/gym_api/models/schedule.py:58` | [#1295](https://github.com/amattas/gym-app/issues/1295) |
| 1068 | trainer_availability missing CHECK end_time > start_time | Data Integrity | `backend/src/gym_api/models/schedule.py:60-61` | [#1296](https://github.com/amattas/gym-app/issues/1296) |
| 1069 | audit_logs.user_id missing FK constraint | Data Integrity | `backend/src/gym_api/models/audit_log.py:18` | [#1297](https://github.com/amattas/gym-app/issues/1297) |
| 1070 | accounts.stripe_customer_id missing UNIQUE constraint | Data Integrity | `backend/src/gym_api/models/account.py:29` | [#1298](https://github.com/amattas/gym-app/issues/1298) |
| 1071 | payment_methods.stripe_payment_method_id missing UNIQUE | Data Integrity | `backend/src/gym_api/models/payment_method.py:20` | [#1299](https://github.com/amattas/gym-app/issues/1299) |
| 1072 | invoices.stripe_invoice_id missing UNIQUE constraint | Data Integrity | `backend/src/gym_api/models/invoice.py:41` | [#1300](https://github.com/amattas/gym-app/issues/1300) |
| 1073 | client_memberships missing partial unique preventing duplicate active | Data Integrity | `backend/src/gym_api/models/client_membership.py:21-55` | [#1301](https://github.com/amattas/gym-app/issues/1301) |
| 1074 | Missing entire OAuth2 authorization server per spec | Spec Compliance | `backend/src/gym_api/routers/auth.py` | [#1307](https://github.com/amattas/gym-app/issues/1307) |
| 1075 | Missing MFA subsystem endpoints per spec | Spec Compliance | `backend/src/gym_api/routers/auth.py` | [#1308](https://github.com/amattas/gym-app/issues/1308) |
| 1076 | Missing DELETE /v1/trainers/{id} for soft-delete | Spec Compliance | `backend/src/gym_api/routers/trainers.py` | [#1309](https://github.com/amattas/gym-app/issues/1309) |
| 1077 | Missing POST /clients/{id}/grant-login | Spec Compliance | `backend/src/gym_api/routers/clients.py` | [#1310](https://github.com/amattas/gym-app/issues/1310) |
| 1078 | Missing gym analytics revenue/clients/engagement/realtime | Spec Compliance | `backend/src/gym_api/routers/calendar.py` | [#1311](https://github.com/amattas/gym-app/issues/1311) |
| 1079 | Account add_member links client_id vs spec creates person | Spec Compliance | `backend/src/gym_api/routers/accounts.py:60-75` | [#1312](https://github.com/amattas/gym-app/issues/1312) |
| 1108 | No webhook delivery logging model or audit trail | Integration | `backend/src/gym_api/models/webhook_endpoint.py` | [#1323](https://github.com/amattas/gym-app/issues/1323) |
| 1109 | No circuit breaker for persistently failing webhook endpoints | Integration | `backend/src/gym_api/webhooks/webhook_service.py` | [#1324](https://github.com/amattas/gym-app/issues/1324) |
| 1110 | No event type validation for webhook subscriptions | Bug | `backend/src/gym_api/routers/webhook_endpoints.py`, `backend/src/gym_api/models/webhook_endpoint.py` | [#1325](https://github.com/amattas/gym-app/issues/1325) |
| 1111 | Stripe webhook handler lacks idempotency -- duplicate events reprocessed | Bug | `backend/src/gym_api/routers/stripe_webhooks.py` | [#1326](https://github.com/amattas/gym-app/issues/1326) |
| 1112 | Stripe webhook handler does not validate event payload structure | Security | `backend/src/gym_api/routers/stripe_webhooks.py` | [#1327](https://github.com/amattas/gym-app/issues/1327) |
| 1113 | No role-based access control on webhook management endpoints | Security | `backend/src/gym_api/routers/webhook_endpoints.py` | [#1328](https://github.com/amattas/gym-app/issues/1328) |
| 1114 | Agreement template content not snapshotted at envelope creation | Bug | `backend/src/gym_api/models/agreement.py`, `backend/src/gym_api/services/esign_service.py` | [#1335](https://github.com/amattas/gym-app/issues/1335) |
| 1115 | Envelope concurrent status update has no locking -- race conditions | Bug | `backend/src/gym_api/services/esign_service.py:117-123` | [#1336](https://github.com/amattas/gym-app/issues/1336) |
| 1116 | Hard delete of agreement templates orphans envelopes | Data Integrity | `backend/src/gym_api/services/esign_service.py:63-65` | [#1337](https://github.com/amattas/gym-app/issues/1337) |
| 1117 | No webhook endpoint for external e-sign providers (DocuSign) | Integration | `backend/src/gym_api/routers/agreements.py` | [#1338](https://github.com/amattas/gym-app/issues/1338) |
| 1118 | Workout set entry row layout breaks on mobile | Responsive Design | `frontend/src/app/(app)/workouts/new/page.tsx:231-282` | [#1342](https://github.com/amattas/gym-app/issues/1342) |
| 1119 | PageHeader component exists but never used -- dead code | Design Consistency | `frontend/src/components/page-header.tsx` | [#1343](https://github.com/amattas/gym-app/issues/1343) |
| 1120 | DataTable component exists but never used -- dead code | Design Consistency | `frontend/src/components/data-table.tsx` | [#1344](https://github.com/amattas/gym-app/issues/1344) |
| 1121 | Loading state patterns inconsistent -- Skeleton component unused | Design Consistency | Multiple frontend pages, `frontend/src/components/ui/skeleton.tsx` | [#1345](https://github.com/amattas/gym-app/issues/1345) |
| 1122 | useIsMobile hook returns false during SSR causing desktop-to-mobile flash | Bug | `frontend/src/hooks/use-mobile.ts` | [#1346](https://github.com/amattas/gym-app/issues/1346) |
| 1123 | Select 'All' filter option uses value 'all' which matches no records | Bug | `frontend/src/app/(app)/exercises/page.tsx:208`, `frontend/src/app/(app)/check-ins/page.tsx:193` | [#1347](https://github.com/amattas/gym-app/issues/1347) |
| 1124 | Exercise deletion orphans WorkoutExercise and PersonalRecord records | Data Integrity | `backend/src/gym_api/services/exercise_service.py:58-62` | [#1354](https://github.com/amattas/gym-app/issues/1354) |
| 1125 | Program deletion orphans ClientProgram, ProgramDay, and ProgramDayExercise records | Data Integrity | `backend/src/gym_api/services/program_service.py:66-70` | [#1355](https://github.com/amattas/gym-app/issues/1355) |
| 1126 | No optimistic locking anywhere in codebase -- concurrent updates last-writer-wins | Data Integrity | All backend service files | [#1356](https://github.com/amattas/gym-app/issues/1356) |
| 1127 | Workout set CRUD has no authorization check on exercise/workout ownership | Security | `backend/src/gym_api/services/workout_service.py:121-130` | [#1357](https://github.com/amattas/gym-app/issues/1357) |
| 1128 | Stripe handle_payment_success silently ignores missing invoice/membership | Bug | `backend/src/gym_api/services/stripe_service.py:222-253` | [#1358](https://github.com/amattas/gym-app/issues/1358) |
| 1129 | Trainer-client assignment uniqueness check has TOCTOU race | Race Condition | `backend/src/gym_api/services/trainer_client_service.py:12-38` | [#1359](https://github.com/amattas/gym-app/issues/1359) |
| 1130 | Gym slug uniqueness check has TOCTOU race | Race Condition | `backend/src/gym_api/services/gym_service.py:15-23` | [#1360](https://github.com/amattas/gym-app/issues/1360) |
| 1131 | Page header flex layout breaks on small screens | Responsive Design | `frontend/src/app/(app)/clients/page.tsx:55`, `workouts/page.tsx:52` | [#1351](https://github.com/amattas/gym-app/issues/1351) |
| 1148 | Router tests never verify service call arguments -- wrong params pass silently | Testing | `backend/tests/test_routers/*.py` | [#1362](https://github.com/amattas/gym-app/issues/1362) |
| 1149 | Client test fixture missing required fields -- tests pass with incomplete data | Testing | `backend/tests/test_routers/test_clients.py` | [#1363](https://github.com/amattas/gym-app/issues/1363) |
| 1150 | Pagination metadata never verified in tests -- cursor logic untested | Testing | `backend/tests/test_routers/*.py` | [#1364](https://github.com/amattas/gym-app/issues/1364) |
| 1151 | Response envelope verified inconsistently across test files | Testing | `backend/tests/test_routers/*.py` | [#1366](https://github.com/amattas/gym-app/issues/1366) |
| 1152 | progress_photos FK to measurements missing -- orphan photos possible | Data Integrity | `backend/src/gym_api/models/progress_photo.py` | [#1370](https://github.com/amattas/gym-app/issues/1370) |
| 1153 | No redirect to originally requested page after login | Usability | `frontend/src/lib/auth.tsx` | [#1372](https://github.com/amattas/gym-app/issues/1372) |
| 1154 | No CSRF protection on state-changing endpoints | Security | `backend/src/gym_api/main.py` | [#1373](https://github.com/amattas/gym-app/issues/1373) |
| 1155 | Refresh token response parsing expects wrong format -- sends Bearer undefined | Integration | `frontend/src/lib/api.ts:103-106` | [#1374](https://github.com/amattas/gym-app/issues/1374) |
| 1156 | No verify-email or reset-password pages in frontend | Missing Functionality | `frontend/src/app/` | [#1375](https://github.com/amattas/gym-app/issues/1375) |
| 1157 | No register page in frontend -- only login exists | Missing Functionality | `frontend/src/app/` | [#1376](https://github.com/amattas/gym-app/issues/1376) |
| 1158 | window.location.href bypass destroys React state on login redirect | Bug | `frontend/src/lib/auth.tsx` | [#1377](https://github.com/amattas/gym-app/issues/1377) |
| 1159 | No filename sanitization for storage keys -- null bytes pass through | Security | `backend/src/gym_api/storage/storage_service.py` | [#1382](https://github.com/amattas/gym-app/issues/1382) |
| 1160 | Concurrent uploads can silently overwrite files with same key | Race Condition | `backend/src/gym_api/storage/storage_service.py` | [#1383](https://github.com/amattas/gym-app/issues/1383) |
| 1161 | No cleanup on DB failure after successful file upload -- orphaned blobs | Data Integrity | `backend/src/gym_api/storage/storage_service.py` | [#1384](https://github.com/amattas/gym-app/issues/1384) |
| 1162 | Email silently succeeds when SMTP not configured in production | Bug | `backend/src/gym_api/services/email_service.py` | [#1386](https://github.com/amattas/gym-app/issues/1386) |
| 1163 | STARTTLS email sending without certificate verification | Security | `backend/src/gym_api/services/email_service.py` | [#1387](https://github.com/amattas/gym-app/issues/1387) |
| 1175 | No RBAC enforcement on GraphQL resolvers — any authenticated user queries any data | Security | `backend/src/gym_api/graphql/schema.py` | [#1396](https://github.com/amattas/gym-app/issues/1396) |
| 1176 | No database connection pool configuration — defaults may cause pool exhaustion | Performance | `backend/src/gym_api/database.py` | [#1397](https://github.com/amattas/gym-app/issues/1397) |
| 1177 | CORS allow_headers=['*'] wildcard permits credential exfiltration | Security | `backend/src/gym_api/main.py` | [#1398](https://github.com/amattas/gym-app/issues/1398) |
| 1178 | Rate limiter in-memory buckets never expire — unbounded memory growth | Performance | `backend/src/gym_api/middleware/rate_limiter.py` | [#1399](https://github.com/amattas/gym-app/issues/1399) |
| 1179 | Idempotency middleware strips response headers from cached responses | Bug | `backend/src/gym_api/middleware/idempotency.py` | [#1400](https://github.com/amattas/gym-app/issues/1400) |
| 1180 | BaseHTTPMiddleware buffers entire request/response body in memory | Performance | `backend/src/gym_api/middleware/` | [#1401](https://github.com/amattas/gym-app/issues/1401) |
| 1181 | Audit logs page fires API call on every keystroke — no debounce | Usability | `frontend/src/app/(app)/audit-logs/page.tsx` | [#1402](https://github.com/amattas/gym-app/issues/1402) |
| 1182 | Audit logs loading state not reset between searches | Bug | `frontend/src/app/(app)/audit-logs/page.tsx` | [#1403](https://github.com/amattas/gym-app/issues/1403) |
| 1183 | Notification preferences save handler uses stale closure | Bug | `frontend/src/app/(app)/settings/notifications/page.tsx` | [#1404](https://github.com/amattas/gym-app/issues/1404) |
| 1184 | Analytics dashboard fires duplicate API calls on mount | Bug | `frontend/src/app/(app)/analytics/page.tsx` | [#1405](https://github.com/amattas/gym-app/issues/1405) |
| 1185 | Client detail page redirects on 404 without showing error | Usability | `frontend/src/app/(app)/clients/[id]/page.tsx` | [#1406](https://github.com/amattas/gym-app/issues/1406) |
| 1186 | Membership renewal clamps day to 28 — members lose up to 3 days per cycle | Bug | `backend/src/gym_api/services/membership_service.py` | [#1407](https://github.com/amattas/gym-app/issues/1407) |
| 1187 | handle_payment_success does not verify payment amount matches invoice | Bug | `backend/src/gym_api/services/stripe_service.py` | [#1408](https://github.com/amattas/gym-app/issues/1408) |
| 1188 | GDPR anonymize retries infinitely on persistent DB errors | Bug | `backend/src/gym_api/services/data_deletion_service.py` | [#1409](https://github.com/amattas/gym-app/issues/1409) |
| 1189 | cancel_membership ignores trial and pending statuses — silently does nothing | Bug | `backend/src/gym_api/services/membership_service.py` | [#1410](https://github.com/amattas/gym-app/issues/1410) |
| 1209 | mfa_setup returns bare MFASetupResponse without data envelope | Bug | `backend/src/gym_api/routers/auth.py:172` | [#1425](https://github.com/amattas/gym-app/issues/1425) |
| 1210 | add_set and list_sets don't verify workout_exercise_id belongs to workout | Bug | `backend/src/gym_api/routers/workouts.py:119-149` | [#1428](https://github.com/amattas/gym-app/issues/1428) |
| 1211 | Falsy-zero rendering bug on usage and locations pages | Bug | `frontend/src/app/(app)/usage/page.tsx:63` | [#1430](https://github.com/amattas/gym-app/issues/1430) |
| 1212 | Check-in occupancy fetch races on rapid location switch | Bug | `frontend/src/app/(app)/check-ins/page.tsx:86-97` | [#1431](https://github.com/amattas/gym-app/issues/1431) |
| 1213 | Agreements page swallows Promise.allSettled rejections | Bug | `frontend/src/app/(app)/agreements/page.tsx:56-64` | [#1433](https://github.com/amattas/gym-app/issues/1433) |
| 1214 | calendar_tokens.gym_id index declared in model but missing from migrations | Performance | `backend/alembic/versions/001_initial_schema.py` | [#1437](https://github.com/amattas/gym-app/issues/1437) |
| 1215 | Migration uses gen_random_uuid() without PG extension or version guard | Config/DevEx | `backend/alembic/versions/001_initial_schema.py:19` | [#1438](https://github.com/amattas/gym-app/issues/1438) |
| 1216 | calculate_volume defaults missing completed key to True — false PRs | Bug | `backend/src/gym_api/services/pr_service.py:27-34` | [#1440](https://github.com/amattas/gym-app/issues/1440) |
| 1217 | get_gym returns inactive gyms — no is_active filter | Bug | `backend/src/gym_api/services/gym_service.py:26-28` | [#1441](https://github.com/amattas/gym-app/issues/1441) |
| 1218 | Program cache key not scoped by gym_id — cross-tenant cache poisoning | Security | `backend/src/gym_api/routers/programs.py:54-57` | [#1442](https://github.com/amattas/gym-app/issues/1442) |
| 1219 | Workout note create/list does not verify workout_id belongs to gym | Security | `backend/src/gym_api/routers/notes.py:69-102` | [#1443](https://github.com/amattas/gym-app/issues/1443) |
| 1220 | Client list status filter uses raw string — case mismatch returns empty | Bug | `backend/src/gym_api/services/client_service.py:53-54` | [#1444](https://github.com/amattas/gym-app/issues/1444) |

## Low

| # | Title | Category | File(s) | GH Issue |
|---|-------|----------|---------|----------|
| 36 | data-table String() renders "undefined" for missing values | Bug | `frontend/src/components/data-table.tsx:64` | [#257](https://github.com/amattas/gym-app/issues/257) |
| 37 | Missing .env.example for backend environment variables | DevEx | `backend/` (missing file) | [#258](https://github.com/amattas/gym-app/issues/258) |
| 38 | CORS default empty string may reject all origins | Config | `backend/src/gym_api/config.py:20` | [#259](https://github.com/amattas/gym-app/issues/259) |
| 39 | Inconsistent empty state messages across frontend pages | Usability | Multiple frontend pages | [#260](https://github.com/amattas/gym-app/issues/260) |
| 72 | Measurements page allows negative weight/body values | Usability | `frontend/src/app/(app)/measurements/page.tsx:192-198` | [#293](https://github.com/amattas/gym-app/issues/293) |
| 128 | Scheduler cron job has no timezone configuration | Config | `backend/src/gym_api/jobs/scheduler.py:15-22` | [#349](https://github.com/amattas/gym-app/issues/349) |
| 129 | PII redaction filter mutates LogRecord args, corrupting other handlers | Bug | `backend/src/gym_api/utils/log_redaction.py:33-41` | [#350](https://github.com/amattas/gym-app/issues/350) |
| 130 | Tables across multiple pages missing accessible captions | Accessibility | Multiple frontend pages | [#351](https://github.com/amattas/gym-app/issues/351) |
| 131 | client_service.search LIKE pattern doesn't escape wildcards | Bug | `backend/src/gym_api/services/client_service.py:42` | [#352](https://github.com/amattas/gym-app/issues/352) |
| 132 | Security headers apply Cache-Control no-store to all responses | Performance | `backend/src/gym_api/middleware/security_headers.py:12,17-21` | [#353](https://github.com/amattas/gym-app/issues/353) |
| 171 | test_schedules uses invalid enum day_off that doesnt exist in ExceptionType | Testing | `backend/tests/test_routers/test_schedules.py:55,202` | [#392](https://github.com/amattas/gym-app/issues/392) |
| 172 | LocationCreate capacity allows negative values | Bug | `backend/src/gym_api/schemas/location.py:15,26` | [#393](https://github.com/amattas/gym-app/issues/393) |
| 173 | Router tests only check status code without verifying response body | Testing | Multiple test files | [#394](https://github.com/amattas/gym-app/issues/394) |
| 254 | Missing indexes: workouts.program_id, workouts.status, personal_records.gym_id/pr_type | Performance | `backend/alembic/versions/001_initial_schema.py` | [#475](https://github.com/amattas/gym-app/issues/475) |
| 255 | UserSession.last_used_at never updated -- session activity tracking broken | Bug | `backend/src/gym_api/models/session.py:20-21` | [#476](https://github.com/amattas/gym-app/issues/476) |
| 256 | Settings page save button has no loading/disabled state during submission | Usability | `frontend/src/app/(app)/settings/page.tsx:43-57` | [#477](https://github.com/amattas/gym-app/issues/477) |
| 257 | Sidebar active state startsWith causes false positive highlighting | Bug | `frontend/src/components/app-sidebar.tsx:113` | [#478](https://github.com/amattas/gym-app/issues/478) |
| 258 | parseInt without radix parameter across workout pages | Bug | Multiple frontend workout pages | [#479](https://github.com/amattas/gym-app/issues/479) |
| 259 | DeviceToken platform field has no enum validation -- arbitrary values stored | Bug | `backend/src/gym_api/schemas/notification.py:7-9` | [#480](https://github.com/amattas/gym-app/issues/480) |
| 260 | Redundant ix_gyms_slug index alongside unique constraint | Config | `backend/alembic/versions/001_initial_schema.py:142-144` | [#481](https://github.com/amattas/gym-app/issues/481) |
| 181 | Cache service get_redis never recovers after Redis connection drops post-initialization | Bug | `backend/src/gym_api/cache/cache_service.py:13-22` | [#402](https://github.com/amattas/gym-app/issues/402) |
| 182 | Data deletion _anonymize_client_data has no gym_id scoping | Security | `backend/src/gym_api/services/data_deletion_service.py:81-87` | [#403](https://github.com/amattas/gym-app/issues/403) |
| 183 | Email service send_email returns True when SMTP not configured -- caller believes email was delivered | Bug | `backend/src/gym_api/email/email_service.py:34-36` | [#404](https://github.com/amattas/gym-app/issues/404) |
| 184 | Reporting service get_gym_dashboard executes 8 sequential COUNT queries | Performance | `backend/src/gym_api/services/reporting_service.py:15-104` | [#405](https://github.com/amattas/gym-app/issues/405) |
| 185 | CalendarToken has no expiration -- tokens are valid forever once generated | Security | `backend/src/gym_api/models/calendar_token.py:11-24` | [#406](https://github.com/amattas/gym-app/issues/406) |
| 186 | iCal validate_token does not verify owner_type matches the endpoint being accessed | Security | `backend/src/gym_api/services/ical_service.py:45-55` | [#407](https://github.com/amattas/gym-app/issues/407) |
| 187 | LocalStorage path traversal fix is bypassable with recursive encoded sequences | Security | `backend/src/gym_api/storage/local_storage.py:17` | [#408](https://github.com/amattas/gym-app/issues/408) |
| 188 | Webhook delivery has no response body size limit -- malicious endpoint can OOM service | Security | `backend/src/gym_api/webhooks/webhook_service.py:47` | [#409](https://github.com/amattas/gym-app/issues/409) |
| 189 | Webhook delivery retries block calling coroutine for up to 36 seconds inline | Performance | `backend/src/gym_api/webhooks/webhook_service.py:44-72` | [#410](https://github.com/amattas/gym-app/issues/410) |
| 440 | API error responses use {detail:...} instead of spec's {error:{code,message}} envelope | Spec Compliance | `backend/src/gym_api/middleware/error_handler.py` | [#661](https://github.com/amattas/gym-app/issues/661) |
| 441 | Pagination response uses {pagination:{next_cursor}} instead of spec's {meta:{cursor,has_more}} | Spec Compliance | `backend/src/gym_api/utils/pagination.py` | [#662](https://github.com/amattas/gym-app/issues/662) |
| 442 | Missing HATEOAS _links in resource responses per spec | Spec Compliance | Multiple router files | [#663](https://github.com/amattas/gym-app/issues/663) |
| 443 | Missing ETags and conditional request support per spec | Spec Compliance | `backend/src/gym_api/middleware/` | [#664](https://github.com/amattas/gym-app/issues/664) |
| 444 | Missing bulk operation endpoints (bulk-create exercises, bulk-update sets) per spec | Spec Compliance | `backend/src/gym_api/routers/exercises.py`, `workouts.py` | [#665](https://github.com/amattas/gym-app/issues/665) |
| 445 | Missing webhook event types for membership, check-in, and workout events per spec | Spec Compliance | `backend/src/gym_api/webhooks/webhook_service.py` | [#666](https://github.com/amattas/gym-app/issues/666) |
| 446 | Missing /v1/health/ready Redis connectivity check per spec | Spec Compliance | `backend/src/gym_api/routers/health.py` | [#667](https://github.com/amattas/gym-app/issues/667) |
| 447 | Router test conftest does not test 401 for unauthenticated requests | Testing | `backend/tests/conftest.py` | [#668](https://github.com/amattas/gym-app/issues/668) |
| 448 | Frontend auth context refreshUser function never called after token refresh | Bug | `frontend/src/lib/auth.tsx:49-55` | [#669](https://github.com/amattas/gym-app/issues/669) |
| 449 | Frontend check-ins page interval timer not cleared on unmount -- memory leak | Bug | `frontend/src/app/(app)/check-ins/page.tsx:56-61` | [#670](https://github.com/amattas/gym-app/issues/670) |
| 479 | Missing composite index on client_memberships(gym_id, client_id) for list operations | Performance | `backend/src/gym_api/models/client_membership.py:27-28` | [#700](https://github.com/amattas/gym-app/issues/700) |
| 480 | stripe_payment_method_id accepts arbitrary strings -- no pm_ prefix validation | Bug | `backend/src/gym_api/schemas/billing.py:52-53` | [#701](https://github.com/amattas/gym-app/issues/701) |
| 481 | Frontend discount display shows 'undefined' for null amount_cents/max_uses | Bug | `frontend/src/app/(app)/billing/page.tsx:320-326` | [#702](https://github.com/amattas/gym-app/issues/702) |
| 482 | Frontend check-in page has duplicated occupancy refresh logic | Bug | `frontend/src/app/(app)/check-ins/page.tsx:113-120,135-142` | [#703](https://github.com/amattas/gym-app/issues/703) |
| 483 | Check-in input accepts malformed UUID without client-side validation | Bug | `frontend/src/app/(app)/check-ins/page.tsx:223-228` | [#704](https://github.com/amattas/gym-app/issues/704) |
| 504 | No push notification delivery implementation exists -- DeviceToken registration is dead-end | Bug | `backend/src/gym_api/services/notification_service.py:1-54` | [#725](https://github.com/amattas/gym-app/issues/725) |
| 505 | No data retention policy or auto-deletion for export/deletion requests | Bug | `backend/src/gym_api/models/data_request.py:27-63` | [#726](https://github.com/amattas/gym-app/issues/726) |
| 506 | Sidebar state cookie persists 7 days -- not strictly necessary per GDPR | Bug | `frontend/src/components/ui/sidebar.tsx:29` | [#727](https://github.com/amattas/gym-app/issues/727) |
| 527 | No prefers-reduced-motion support for animations | Accessibility | `frontend/src/app/globals.css`, all components | [#748](https://github.com/amattas/gym-app/issues/748) |
| 528 | Touch target sizes below 44x44px for small icon button variants | Accessibility | `frontend/src/components/ui/button.tsx:28-31` | [#749](https://github.com/amattas/gym-app/issues/749) |
| 529 | GraphQL error responses may leak stack traces and internal paths | Security | `backend/src/gym_api/routers/graphql_router.py` | [#750](https://github.com/amattas/gym-app/issues/750) |
| 530 | Alembic downgrade lacks error handling for partial table drop failures | Bug | `backend/alembic/versions/001_initial_schema.py:1071-1125` | [#751](https://github.com/amattas/gym-app/issues/751) |
| 531 | Backup script does not verify backup file integrity -- no checksum | Bug | `scripts/backup_db.sh:26,45` | [#752](https://github.com/amattas/gym-app/issues/752) |
| 532 | Backup script does not handle GCS upload failures | Bug | `scripts/backup_db.sh:32-35` | [#753](https://github.com/amattas/gym-app/issues/753) |
| 550 | Database connection errors return 500 instead of 503 Service Unavailable | Bug | `backend/src/gym_api/middleware/error_handler.py:32-42` | [#771](https://github.com/amattas/gym-app/issues/771) |
| 551 | No robots.txt or sitemap.xml for search engine crawlers | Bug | `frontend/src/app/` (missing files) | [#772](https://github.com/amattas/gym-app/issues/772) |
| 552 | Unused SVG assets in public directory -- bundle bloat | Bug | `frontend/public/*.svg` | [#773](https://github.com/amattas/gym-app/issues/773) |
| 553 | Frontend statusColors lookup returns undefined for unknown statuses | Bug | `frontend/src/app/(app)/workouts/page.tsx:29` | [#774](https://github.com/amattas/gym-app/issues/774) |
| 554 | No frontend environment variable validation at build time | Bug | `frontend/.env.local.example` | [#775](https://github.com/amattas/gym-app/issues/775) |
| 579 | Password schema min_length=8 conflicts with validator requiring 12+ chars | Bug | `backend/src/gym_api/schemas/invitation.py:23` | [#800](https://github.com/amattas/gym-app/issues/800) |
| 580 | DeviceToken.token String(500) may be too short for Firebase/APNs tokens | Bug | `backend/src/gym_api/models/notification.py:19` | [#801](https://github.com/amattas/gym-app/issues/801) |
| 581 | Token expiry inconsistency -- password reset 1hr vs invitation 7 days | Bug | `backend/src/gym_api/services/verification_service.py:11-12` | [#802](https://github.com/amattas/gym-app/issues/802) |
| 630 | No rate limiting on data export endpoints -- resource exhaustion vector | Security | `backend/src/gym_api/routers/data_privacy.py:46-57` | [#851](https://github.com/amattas/gym-app/issues/851) |
| 631 | Cache invalidation after commit creates stale-read window across cached services | Bug | `backend/src/gym_api/services/exercise_service.py:52-54`, `program_service.py`, `gym_service.py` | [#852](https://github.com/amattas/gym-app/issues/852) |
| 632 | Idempotency replay returns JSONResponse for non-JSON content types | Bug | `backend/src/gym_api/middleware/idempotency.py:32-36,54-58` | [#853](https://github.com/amattas/gym-app/issues/853) |
| 633 | LocalStorage creates files with default umask permissions -- world-readable | Security | `backend/src/gym_api/storage/local_storage.py:28` | [#854](https://github.com/amattas/gym-app/issues/854) |
| 634 | Data export format parameter accepts arbitrary string -- only JSON implemented | Bug | `backend/src/gym_api/services/data_export_service.py:18-33` | [#855](https://github.com/amattas/gym-app/issues/855) |
| 635 | Uvicorn CMD missing --workers and --log-config flags | Infra | `backend/Dockerfile:21` | [#856](https://github.com/amattas/gym-app/issues/856) |
| 636 | No graceful shutdown for in-flight requests -- lifespan yields without draining | Bug | `backend/src/gym_api/main.py:75-85` | [#857](https://github.com/amattas/gym-app/issues/857) |
| 637 | K8s deployment missing STRIPE/WEBAUTHN/FRONTEND_URL env vars | Config | `k8s/deployment.yaml:22-37` | [#858](https://github.com/amattas/gym-app/issues/858) |
| 638 | JWT access token includes user email -- PII in every Authorization header | Security | `backend/src/gym_api/services/auth_service.py:28` | [#859](https://github.com/amattas/gym-app/issues/859) |
| 639 | Missing composite index workouts(gym_id, created_at) for pagination | Performance | `backend/src/gym_api/models/workout.py:25,39-41` | [#860](https://github.com/amattas/gym-app/issues/860) |
| 640 | 40+ service modules have zero logging -- all business operations silent | Bug | `backend/src/gym_api/services/` (40+ files) | [#861](https://github.com/amattas/gym-app/issues/861) |
| 641 | Metrics counters not thread-safe and meaningless across uvicorn workers | Bug | `backend/src/gym_api/metrics/prometheus.py:10-12,25-31` | [#862](https://github.com/amattas/gym-app/issues/862) |
| 689 | BMI test lacks edge cases -- zero height, negative values, extreme inputs | Testing | `backend/tests/test_services/test_measurement_service.py:4-19` | [#910](https://github.com/amattas/gym-app/issues/910) |
| 690 | Passkey tests tautological -- isinstance(dict) passes on any dict including errors | Testing | `backend/tests/test_services/test_passkey_service.py:9-26` | [#911](https://github.com/amattas/gym-app/issues/911) |
| 691 | Tampered token test catches bare Exception -- masks JWT failure mode | Testing | `backend/tests/test_auth/test_auth_service.py:73-78` | [#912](https://github.com/amattas/gym-app/issues/912) |
| 692 | Missing MetaData naming_convention -- autogenerate constraint names unpredictable | Config | `backend/src/gym_api/database.py:10-11` | [#913](https://github.com/amattas/gym-app/issues/913) |
| 693 | notes.notable_id model index=True but migration creates composite index only | Performance | `backend/src/gym_api/models/note.py:19` | [#914](https://github.com/amattas/gym-app/issues/914) |
| 694 | Programs detail page selectedDay not persisted in URL -- lost on refresh | Usability | `frontend/src/app/(app)/programs/[programId]/page.tsx:40` | [#915](https://github.com/amattas/gym-app/issues/915) |
| 695 | Auth token early return path may leave isLoading stuck true permanently | Bug | `frontend/src/lib/auth.tsx:44-67` | [#916](https://github.com/amattas/gym-app/issues/916) |
| 734 | MembershipUpdate schema has bare str status field -- available for future exploitation | Bug | `backend/src/gym_api/schemas/membership.py:13-14` | [#955](https://github.com/amattas/gym-app/issues/955) |
| 735 | TrainerExceptionCreate.exception_type accepts arbitrary string -- bypasses ExceptionType enum | Bug | `backend/src/gym_api/schemas/schedule.py:60` | [#956](https://github.com/amattas/gym-app/issues/956) |
| 736 | iCal STATUS uses non-RFC values (COMPLETED, NO_SHOW, CANCELED instead of CANCELLED) | Integration | `backend/src/gym_api/services/ical_service.py:100-102` | [#957](https://github.com/amattas/gym-app/issues/957) |
| 737 | iCal strftime appends Z suffix without explicit UTC conversion -- fragile assumption | Bug | `backend/src/gym_api/services/ical_service.py:97-98` | [#958](https://github.com/amattas/gym-app/issues/958) |
| 738 | iCal VCALENDAR missing CALSCALE property | Integration | `backend/src/gym_api/services/ical_service.py:87-91` | [#959](https://github.com/amattas/gym-app/issues/959) |
| 739 | Resend-verification creates token before email send without checking result | Bug | `backend/src/gym_api/routers/auth.py:288-294` | [#960](https://github.com/amattas/gym-app/issues/960) |
| 775 | Test dependency_overrides.clear() on global app singleton -- cross-test contamination | Testing | `backend/tests/test_routers/test_invitations.py:31-36` | [#996](https://github.com/amattas/gym-app/issues/996) |
| 776 | SessionResponse timestamp fields str instead of datetime -- inconsistent serialization | Bug | `backend/src/gym_api/routers/auth.py:79-84` | [#997](https://github.com/amattas/gym-app/issues/997) |
| 777 | 10+ schema Text fields missing max_length -- unbounded input on description/notes/address | Security | `schemas/program.py:9`, `agreement.py:9`, `plan_template.py:9`, `schedule.py:14`, `client.py:16`, `gym.py:14` | [#998](https://github.com/amattas/gym-app/issues/998) |
| 778 | ExerciseCreate.muscle_groups and WebhookCreate.events lists have no size limit | Security | `schemas/exercise.py:10`, `routers/webhook_endpoints.py:17` | [#999](https://github.com/amattas/gym-app/issues/999) |
| 779 | GoalCreate target_value/current_value and order_index fields missing numeric constraints | Bug | `schemas/goal.py:9-10`, `client_program.py:25,39`, `workout.py:23-25` | [#1000](https://github.com/amattas/gym-app/issues/1000) |
| 780 | InvitationResponse missing invited_by_user_id and created_at fields | Bug | `backend/src/gym_api/schemas/invitation.py:11-18` | [#1001](https://github.com/amattas/gym-app/issues/1001) |
| 781 | 3 response schemas use str instead of Enum for status/type (export, deletion, PR) | Bug | `routers/data_privacy.py:20,37`, `schemas/personal_record.py:12` | [#1002](https://github.com/amattas/gym-app/issues/1002) |
| 782 | DiscountCodeCreate.applicable_plan_types bare str -- no format or value validation | Bug | `backend/src/gym_api/schemas/billing.py:122` | [#1003](https://github.com/amattas/gym-app/issues/1003) |
| 783 | detect_prs Exercise lookup missing gym_id -- cross-tenant exercise name leak | Security | `backend/src/gym_api/services/workout_service.py:163-166` | [#1004](https://github.com/amattas/gym-app/issues/1004) |
| 784 | Accounts page double toast on concurrent account+members fetch failure | Usability | `frontend/src/app/(app)/accounts/page.tsx:86-101` | [#1005](https://github.com/amattas/gym-app/issues/1005) |
| 785 | Billing discount form discountType state not reset on dialog close | Bug | `frontend/src/app/(app)/billing/page.tsx:69-107` | [#1006](https://github.com/amattas/gym-app/issues/1006) |
| 786 | api.ts sends Content-Type: application/json on bodyless DELETE/GET requests | Bug | `frontend/src/lib/api.ts:43-46` | [#1007](https://github.com/amattas/gym-app/issues/1007) |
| 787 | MeasurementCreate.value and ClientCreate.height_cm/weight_kg no constraints -- negative values | Bug | `schemas/measurement.py:10`, `client.py:14-15` | [#1008](https://github.com/amattas/gym-app/issues/1008) |
| 788 | Exercises edit dialog state not cleared on dismiss -- stale values briefly visible | Usability | `frontend/src/app/(app)/exercises/page.tsx:107-112` | [#1009](https://github.com/amattas/gym-app/issues/1009) |
| 789 | Workout detail event handlers capture stale workoutId from closure after navigation | Bug | `frontend/src/app/(app)/workouts/[workoutId]/page.tsx:63-68` | [#1010](https://github.com/amattas/gym-app/issues/1010) |
| 825 | list_payment_methods in stripe_service has no LIMIT -- unbounded result set | Performance | `backend/src/gym_api/services/stripe_service.py:84-92` | [#1046](https://github.com/amattas/gym-app/issues/1046) |
| 826 | _build_summary_text uses dict(Row.all()) relying on legacy Row tuple structure | Bug | `backend/src/gym_api/services/ai_summary_service.py:142` | [#1047](https://github.com/amattas/gym-app/issues/1047) |
| 827 | AgreementEnvelope.template_id missing index | Performance | `backend/src/gym_api/models/agreement.py:49` | [#1048](https://github.com/amattas/gym-app/issues/1048) |
| 828 | ClientMembership.plan_template_id missing index | Performance | `backend/src/gym_api/models/client_membership.py:29` | [#1049](https://github.com/amattas/gym-app/issues/1049) |
| 829 | Decorative Lucide icons exposed to accessibility tree across 12+ pages | Accessibility | `login/page.tsx:44`, `forgot-password/page.tsx:65`, `dashboard/page.tsx:76` | [#1050](https://github.com/amattas/gym-app/issues/1050) |
| 830 | Progress photos placeholder image area not accessible to screen readers | Accessibility | `frontend/src/app/(app)/progress-photos/page.tsx:201-203` | [#1051](https://github.com/amattas/gym-app/issues/1051) |
| 831 | Billing Stripe connect button opens new window without indication (WCAG 3.2.5) | Accessibility | `frontend/src/app/(app)/billing/page.tsx:117` | [#1052](https://github.com/amattas/gym-app/issues/1052) |
| 832 | POST /v1/ai-summary/regenerate returns 200 instead of 201 for resource creation | Spec Compliance | `backend/src/gym_api/routers/ai_summaries.py:44` | [#1053](https://github.com/amattas/gym-app/issues/1053) |
| 833 | POST /v1/discount-codes/validate is a read-only query using POST -- should be GET | Spec Compliance | `backend/src/gym_api/routers/billing.py:311` | [#1054](https://github.com/amattas/gym-app/issues/1054) |
| 834 | X-RateLimit-Reset header missing on successful (non-429) responses | Spec Compliance | `backend/src/gym_api/middleware/rate_limiter.py:56-59` | [#1055](https://github.com/amattas/gym-app/issues/1055) |
| 835 | Stripe Connect onboarding_url response field sits outside {data:...} envelope | Spec Compliance | `backend/src/gym_api/routers/billing.py:48-51` | [#1056](https://github.com/amattas/gym-app/issues/1056) |
| 836 | Calendar token generate/rotate endpoints return 200 instead of 201 for new tokens | Spec Compliance | `backend/src/gym_api/routers/calendar.py:38-47,63-72,75-84` | [#1057](https://github.com/amattas/gym-app/issues/1057) |
| 851 | Inconsistent mock user factories across test directories | Testing | `test_auth_service.py:15`, `test_auth/helpers.py`, `test_routers/helpers.py` | [#1109](https://github.com/amattas/gym-app/issues/1109) |
| 866 | Dockerfile base image not pinned to patch version -- non-reproducible builds | Infra | `backend/Dockerfile:2,10` | [#1110](https://github.com/amattas/gym-app/issues/1110) |
| 867 | Config.py database_url default has no credentials -- confusing startup error | Config | `backend/src/gym_api/config.py:9` | [#1111](https://github.com/amattas/gym-app/issues/1111) |
| 868 | Backup script retention cleanup vulnerable to filename issues | Security | `scripts/backup_db.sh:39-42` | [#1112](https://github.com/amattas/gym-app/issues/1112) |
| 869 | CI backend jobs missing pip dependency caching -- slow builds | Config | `.github/workflows/ci.yml:53-57` | [#1113](https://github.com/amattas/gym-app/issues/1113) |
| 870 | Alembic 002 downgrade drops indexes without IF EXISTS | Config | `backend/alembic/versions/002_add_missing_fk_indexes.py:79-104` | [#1114](https://github.com/amattas/gym-app/issues/1114) |
| 882 | String.replace only replaces first underscore on measurements/exercises | Bug | `frontend/src/app/(app)/measurements/page.tsx:184,217,259` | [#1115](https://github.com/amattas/gym-app/issues/1115) |
| 883 | Progress photos interpolates clientId without encodeURIComponent | Bug | `frontend/src/app/(app)/progress-photos/page.tsx:51-53` | [#1116](https://github.com/amattas/gym-app/issues/1116) |
| 884 | Login form inputs missing autocomplete attributes for password managers | Accessibility | `frontend/src/app/(auth)/login/page.tsx:60-77` | [#1117](https://github.com/amattas/gym-app/issues/1117) |
| 885 | Check-ins empty state says 'No check-ins today' even with date filter | Usability | `frontend/src/app/(app)/check-ins/page.tsx:258-260` | [#1118](https://github.com/amattas/gym-app/issues/1118) |
| 886 | page-header.tsx component defined but never imported -- dead code | Bug | `frontend/src/components/page-header.tsx` | [#1119](https://github.com/amattas/gym-app/issues/1119) |
| 887 | Accounts create dialog does not reset accountType on close | Bug | `frontend/src/app/(app)/accounts/page.tsx:63-79` | [#1120](https://github.com/amattas/gym-app/issues/1120) |
| 888 | New workout exercise dropdown doesn't indicate already-added exercises | Usability | `frontend/src/app/(app)/workouts/new/page.tsx:212-226` | [#1121](https://github.com/amattas/gym-app/issues/1121) |
| 901 | Reporting date range inclusive upper bound -- boundary double-counting | Bug | `backend/src/gym_api/services/reporting_service.py:131,160-171` | [#1122](https://github.com/amattas/gym-app/issues/1122) |
| 906 | SecurityHeaders sends HSTS unconditionally even when HTTPS not enforced | Security | `backend/src/gym_api/middleware/security_headers.py:11` | [#1127](https://github.com/amattas/gym-app/issues/1127) |
| 910 | Idempotency/RateLimiter run outside HTTPS redirect -- HTTP processed first | Security | `backend/src/gym_api/main.py:105,111-112` | [#1131](https://github.com/amattas/gym-app/issues/1131) |
| 911 | GraphQL router uses path= kwarg instead of standard prefix= pattern | Config | `backend/src/gym_api/routers/graphql_router.py:32` | [#1132](https://github.com/amattas/gym-app/issues/1132) |
| 913 | _setup_logging PII filter per-handler misses handlers added after startup | Security | `backend/src/gym_api/main.py:64-72` | [#1134](https://github.com/amattas/gym-app/issues/1134) |
| 922 | list_sessions returns unbounded result set -- no pagination or limit | Performance | `backend/src/gym_api/services/auth_service.py:146-152` | [#1143](https://github.com/amattas/gym-app/issues/1143) |
| 923 | RegisterRequest.first_name/last_name have no max_length -- DB truncation error | Bug | `backend/src/gym_api/routers/auth.py:30-34` | [#1144](https://github.com/amattas/gym-app/issues/1144) |
| 924 | Login session user_agent not truncated -- oversized UA crashes insert | Bug | `backend/src/gym_api/routers/auth.py:148`, `backend/src/gym_api/models/session.py:19` | [#1145](https://github.com/amattas/gym-app/issues/1145) |
| 925 | consume_password_reset_token mid-function commit flushes caller dirty state | Bug | `backend/src/gym_api/routers/auth.py:259-261`, `backend/src/gym_api/services/verification_service.py:46-50` | [#1146](https://github.com/amattas/gym-app/issues/1146) |
| 927 | RefreshRequest.refresh_token has no max_length -- memory pressure attacks | Security | `backend/src/gym_api/routers/auth.py:43-44` | [#1148](https://github.com/amattas/gym-app/issues/1148) |
| 941 | get_metric_totals returns raw dicts bypassing Pydantic validation | Bug | `backend/src/gym_api/routers/usage.py:32-39` | [#1162](https://github.com/amattas/gym-app/issues/1162) |
| 943 | ProcessingFeeUpdate allows pass_fees_to_client=true with null fee percentage | Bug | `backend/src/gym_api/schemas/billing.py:32-34` | [#1164](https://github.com/amattas/gym-app/issues/1164) |
| 944 | Session pack checkout returns inconsistent response shape with extra field | Bug | `backend/src/gym_api/routers/billing.py:194` | [#1165](https://github.com/amattas/gym-app/issues/1165) |
| 953 | record_metric does not validate period_start < period_end -- inverted accepted | Bug | `backend/src/gym_api/services/usage_metering_service.py:10-48` | [#1174](https://github.com/amattas/gym-app/issues/1174) |
| 954 | DiscountCodeCreate allows valid_from after valid_until -- permanently invalid | Bug | `backend/src/gym_api/schemas/billing.py:116-124` | [#1175](https://github.com/amattas/gym-app/issues/1175) |
| 956 | StripeConnectResponse exposes stripe_connect_id to all authenticated users | Security | `backend/src/gym_api/schemas/billing.py:12-25` | [#1177](https://github.com/amattas/gym-app/issues/1177) |
| 957 | DiscountCodeCreate.description has no max_length -- unbounded storage | Security | `backend/src/gym_api/schemas/billing.py:118` | [#1178](https://github.com/amattas/gym-app/issues/1178) |
| 964 | Location.capacity has no CHECK constraint -- negative capacity accepted | Data Integrity | `backend/src/gym_api/models/location.py` | [#1185](https://github.com/amattas/gym-app/issues/1185) |
| 965 | DiscountCode.times_used has no CHECK constraint -- can go negative | Data Integrity | `backend/src/gym_api/models/discount_code.py` | [#1186](https://github.com/amattas/gym-app/issues/1186) |
| 966 | ClientMembership.visits_used_this_period no CHECK constraint -- negative visits | Data Integrity | `backend/src/gym_api/models/client_membership.py` | [#1187](https://github.com/amattas/gym-app/issues/1187) |
| 967 | Invoice monetary columns lack server_default -- non-ORM inserts get NULL | Data Integrity | `backend/src/gym_api/models/invoice.py` | [#1188](https://github.com/amattas/gym-app/issues/1188) |
| 968 | Alembic migration downgrade drops all tables -- asymmetric with upgrade | Infra | `backend/alembic/versions/` | [#1189](https://github.com/amattas/gym-app/issues/1189) |
| 969 | WorkoutSet.completed Python default=True but no server_default -- NULL on non-ORM | Bug | `backend/src/gym_api/models/workout.py` | [#1190](https://github.com/amattas/gym-app/issues/1190) |
| 1028 | Client new form phone input missing type=tel attribute | Bug | `frontend/src/app/(app)/clients/new/page.tsx:91-96` | [#1204](https://github.com/amattas/gym-app/issues/1204) |
| 1029 | AppSidebar People section uses duplicate Users icon for Clients and Accounts | Usability | `frontend/src/components/app-sidebar.tsx:48-51` | [#1206](https://github.com/amattas/gym-app/issues/1206) |
| 1030 | Settings page does not refresh gym state after successful save | Bug | `frontend/src/app/(app)/settings/page.tsx:43-57` | [#1209](https://github.com/amattas/gym-app/issues/1209) |
| 1031 | get_client_measurement_trend datetime vs volume_trend ISO strings -- inconsistent date type | Bug | `backend/src/gym_api/services/analytics_service.py:187-190` | [#1229](https://github.com/amattas/gym-app/issues/1229) |
| 1032 | aiosqlite listed as dev dependency but never used -- dead dependency | Config/DevEx | `backend/pyproject.toml:32` | [#1240](https://github.com/amattas/gym-app/issues/1240) |
| 1033 | Frontend @tailwindcss/postcss uses extremely wide ^4 caret range | Config/DevEx | `frontend/package.json` | [#1241](https://github.com/amattas/gym-app/issues/1241) |
| 1034 | test_gym_context_platform_admin_rejected codifies bug #624 as expected behavior | Testing | `backend/tests/test_auth/test_dependencies.py:66-71` | [#1245](https://github.com/amattas/gym-app/issues/1245) |
| 1035 | _make_gym factory timezone variable shadows datetime.timezone import | Testing | `backend/tests/test_routers/test_gyms.py:26-27` | [#1246](https://github.com/amattas/gym-app/issues/1246) |
| 1036 | DiscountValidationResponse and OccupancyResponse missing model_config | Bug | `backend/src/gym_api/schemas/billing.py:163-167`, `backend/src/gym_api/schemas/check_in.py:28-30` | [#1250](https://github.com/amattas/gym-app/issues/1250) |
| 1080 | Domains page fetchDomains never re-sets isLoading on refetches | Bug | `frontend/src/app/(app)/domains/page.tsx:51-63` | [#1269](https://github.com/amattas/gym-app/issues/1269) |
| 1081 | Measurements page addType not reset on dialog close | Bug | `frontend/src/app/(app)/measurements/page.tsx:65-109` | [#1270](https://github.com/amattas/gym-app/issues/1270) |
| 1082 | Accounts page double error toasts from Promise.all inner+outer catch | Bug | `frontend/src/app/(app)/accounts/page.tsx:86-101` | [#1271](https://github.com/amattas/gym-app/issues/1271) |
| 1083 | Login/forgot-password pages don't trim email input | Usability | `frontend/src/app/(auth)/login/page.tsx:32` | [#1272](https://github.com/amattas/gym-app/issues/1272) |
| 1084 | New client email validation relies solely on HTML5 type=email | Bug | `frontend/src/app/(app)/clients/new/page.tsx:84` | [#1273](https://github.com/amattas/gym-app/issues/1273) |
| 1085 | Forgot-password page not in AuthProvider -- useAuth() would crash | Bug | `frontend/src/app/(auth)/forgot-password/page.tsx` | [#1274](https://github.com/amattas/gym-app/issues/1274) |
| 1086 | PII redaction filter converts numeric log args to strings | Bug | `backend/src/gym_api/utils/log_redaction.py:40-41` | [#1280](https://github.com/amattas/gym-app/issues/1280) |
| 1087 | PersonalRecord missing updated_at -- superseded records untracked | Bug | `backend/src/gym_api/models/personal_record.py:20-42` | [#1302](https://github.com/amattas/gym-app/issues/1302) |
| 1088 | WorkoutSummary missing updated_at -- stale mutation untracked | Bug | `backend/src/gym_api/models/ai_summary.py:11-24` | [#1303](https://github.com/amattas/gym-app/issues/1303) |
| 1089 | locations.capacity missing CHECK >= 0 | Data Integrity | `backend/src/gym_api/models/location.py:25` | [#1304](https://github.com/amattas/gym-app/issues/1304) |
| 1090 | programs.num_days missing CHECK >= 1 | Data Integrity | `backend/src/gym_api/models/program.py:32` | [#1305](https://github.com/amattas/gym-app/issues/1305) |
| 1091 | payment_methods.exp_month missing CHECK 1-12 | Data Integrity | `backend/src/gym_api/models/payment_method.py:24` | [#1306](https://github.com/amattas/gym-app/issues/1306) |
| 1092 | Missing GET /trainers/{id}/exceptions list endpoint | Spec Compliance | `backend/src/gym_api/routers/schedules.py` | [#1313](https://github.com/amattas/gym-app/issues/1313) |
| 1093 | Missing passkey management endpoints per spec | Spec Compliance | `backend/src/gym_api/routers/auth.py` | [#1314](https://github.com/amattas/gym-app/issues/1314) |
| 1094 | Missing DELETE calendar token revoke endpoints | Spec Compliance | `backend/src/gym_api/routers/calendar.py` | [#1315](https://github.com/amattas/gym-app/issues/1315) |
| 1095 | Missing order query parameter on paginated endpoints | Spec Compliance | `backend/src/gym_api/utils/pagination.py` | [#1316](https://github.com/amattas/gym-app/issues/1316) |
| 1096 | Missing q search parameter on client/exercise endpoints | Spec Compliance | `backend/src/gym_api/routers/clients.py`, `exercises.py` | [#1317](https://github.com/amattas/gym-app/issues/1317) |
| 1097 | Missing GET /clients/{id}/qr-code endpoint | Spec Compliance | `backend/src/gym_api/routers/check_ins.py` | [#1318](https://github.com/amattas/gym-app/issues/1318) |
| 1098 | Missing GET /clients/{id}/deletion-status endpoint | Spec Compliance | `backend/src/gym_api/routers/data_privacy.py` | [#1319](https://github.com/amattas/gym-app/issues/1319) |
| 1099 | Missing DELETE /gyms/{id} for gym soft-delete | Spec Compliance | `backend/src/gym_api/routers/gyms.py` | [#1320](https://github.com/amattas/gym-app/issues/1320) |
| 1100 | Missing POST /trainers/{id}/resend-invitation | Spec Compliance | `backend/src/gym_api/routers/trainers.py` | [#1321](https://github.com/amattas/gym-app/issues/1321) |
| 1132 | Stripe webhook tests have zero coverage for signature/event processing | Testing | `backend/tests/test_routers/test_stripe_webhooks.py` | [#1329](https://github.com/amattas/gym-app/issues/1329) |
| 1133 | No PDF generation capability for signed agreement documents | Missing Functionality | `backend/src/gym_api/services/esign_service.py` | [#1338](https://github.com/amattas/gym-app/issues/1338) |
| 1134 | Agreement test fixture uses wrong field 'metadata' instead of 'extra_data' | Testing | `backend/tests/test_routers/test_agreements.py:24` | [#1339](https://github.com/amattas/gym-app/issues/1339) |
| 1135 | Envelope status query parameter not validated against enum values | Bug | `backend/src/gym_api/routers/agreements.py:111` | [#1340](https://github.com/amattas/gym-app/issues/1340) |
| 1136 | Weight displayed as 'lbs' in workout detail but 'kg' in measurements | Design Consistency | `frontend/src/app/(app)/workouts/[workoutId]/page.tsx:263`, `measurements/page.tsx:55` | [#1348](https://github.com/amattas/gym-app/issues/1348) |
| 1137 | zod + react-hook-form + Form component installed but entirely unused | Config/DevEx | `frontend/package.json`, `frontend/src/components/ui/form.tsx` | [#1349](https://github.com/amattas/gym-app/issues/1349) |
| 1138 | Duplicate sidebar icons for multiple navigation items | Usability | `frontend/src/components/app-sidebar.tsx:48-78` | [#1350](https://github.com/amattas/gym-app/issues/1350) |
| 1139 | date-fns dependency installed but never imported anywhere | Config/DevEx | `frontend/package.json:17` | [#1352](https://github.com/amattas/gym-app/issues/1352) |
| 1164 | Duplicate token_hash indexes in migration -- redundant index waste | Config/DevEx | `backend/alembic/versions/` | [#1369](https://github.com/amattas/gym-app/issues/1369) |
| 1165 | No password visibility toggle on login/auth forms | Usability | `frontend/src/app/login/page.tsx` | [#1378](https://github.com/amattas/gym-app/issues/1378) |
| 1166 | Login error messages reveal MFA enrollment status | Security | `backend/src/gym_api/routers/auth.py` | [#1379](https://github.com/amattas/gym-app/issues/1379) |
| 1167 | S3 client recreated on every storage operation -- expensive setup per call | Performance | `backend/src/gym_api/storage/storage_service.py` | [#1385](https://github.com/amattas/gym-app/issues/1385) |
| 1190 | Request ID middleware uses client-provided X-Request-Id without validation | Security | `backend/src/gym_api/middleware/` | [#1411](https://github.com/amattas/gym-app/issues/1411) |
| 1191 | Profile dropdown menu items do nothing — no navigation handlers | Bug | `frontend/src/components/app-sidebar.tsx` | [#1412](https://github.com/amattas/gym-app/issues/1412) |
| 1192 | Membership sub-pages (payments, invoices) unreachable — no navigation links | Usability | `frontend/src/app/(app)/memberships/` | [#1413](https://github.com/amattas/gym-app/issues/1413) |
| 1193 | Membership unpause uses integer division for remaining days — rounds to zero | Bug | `backend/src/gym_api/services/membership_service.py` | [#1414](https://github.com/amattas/gym-app/issues/1414) |
| 1221 | Schedule action toast shows 'completeed' and 'no-showed' | Bug | `frontend/src/app/(app)/schedules/page.tsx:117` | [#1432](https://github.com/amattas/gym-app/issues/1432) |
| 1222 | Trainers page empty specialties array renders blank instead of '---' | Bug | `frontend/src/app/(app)/trainers/page.tsx:76-80` | [#1434](https://github.com/amattas/gym-app/issues/1434) |
| 1223 | 4 FK columns missing indexes — slow cascading deletes | Performance | `backend/alembic/versions/001_initial_schema.py` | [#1439](https://github.com/amattas/gym-app/issues/1439) |

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 47 |
| High | 340 |
| Medium | 647 |
| Low | 189 |
| **Total** | **1223** |

*Note: Counts include original (1-72), iteration 1 (73-132), iteration 2 (133-173), iteration 3 (174-189), iteration 4 (190-260), iteration 5 (261-295), iteration 6 (296-382), iteration 7 (383-449), iteration 8 (450-483), iteration 9 (484-506), iteration 10 (507-532), iteration 11 (533-554), iteration 12 (555-581), iteration 13 (582-641), iteration 14 (642-695), iteration 15 (696-739), iteration 16 (740-789), iteration 17 (790-836), iteration 18 (837-901), iteration 19 (902-969), iteration 20 (970-1036), iteration 21 (1037-1100), iteration 22 (1101-1139), iteration 23 (1140-1167), iteration 24 (1168-1193), and iteration 25 (1194-1223) issues.*

### By Category
| Category | Count |
|----------|-------|
| Security | 245 |
| Bug | 536 |
| Integration | 31 |
| Usability | 61 |
| Performance | 60 |
| Accessibility | 39 |
| Spec Compliance | 61 |
| Infra | 23 |
| Testing | 68 |
| Config/DevEx | 38 |
| Observability | 4 |
| Data Integrity | 44 |
| Missing Functionality | 5 |
| Responsive Design | 3 |
| Design Consistency | 3 |
| Race Condition | 3 |

### Priority Fix Order
1. **BLOCKER**: Frontend-backend integration — app non-functional (#133-136, #139-145)
2. **BLOCKER**: Migration schema — missing enums trial/session_pack (#190-191), missing client columns (#195)
3. **Immediate**: Password reset doesn't invalidate sessions (#192), session management ineffective (#204-205)
4. **Immediate**: Missing auth guards (#40-43, #8, #78, #93, #138, #179), unverified login (#77)
5. **Immediate**: IDOR/tenant isolation (#44-47, #2, #75, #91, #92, #96, #123, #146-148, #175, #178, #180, #217-222)
6. **Immediate**: Stripe webhook security — no gym_id scoping (#218-220), unvalidated metadata (#219)
7. **Immediate**: No FK constraints (#73), orphaned invoice data (#74), no ON DELETE (#198)
8. **Urgent**: Transaction integrity — checkout non-atomic (#193-194, #210), invitation partial state (#221)
9. **Urgent**: Passkey replay attacks (#137), Stripe webhook bypass (#1) + replay (#81)
10. **Urgent**: Race conditions with financial impact (#50-52, #12, #80, #111, #208-209)
11. **Urgent**: MFA bypass vectors — no replay protection (#200), no rate limit (#201), credential leak (#202)
12. **Urgent**: No account lockout (#203), no jti for token revocation (#199)
13. **Urgent**: Scheduler duplicate execution (#76), job error handling (#90, #97)
14. **Urgent**: GDPR compliance — incomplete data deletion (#176), partial commit corruption (#177)
15. **Urgent**: get_db no transaction wrapper — systemic root cause of split commits (#211)
16. **High**: GraphQL DoS — no limits (#213-214), no user validation (#215), introspection (#234)
17. **High**: MFA stored plaintext (#82), GraphQL gym bypass (#83), seed password (#84)
18. **High**: MVP spec gaps — WorkoutSet fields (#149), measurement types (#151), program lifecycle (#150)
19. **High**: Performance — N+1 queries (#9-11, #86), no pagination on frontend (#207), no ORM rels (#125)
20. **High**: Infra — idempotency in-memory (#87), readiness probe (#94), Dockerfile (#85)
21. **Medium**: Rate limiting gaps — forgot-password path mismatch (#226), resend-verification (#227)
22. **Medium**: Concurrency — PR duplicates (#233), availability phantom reads (#240), batch jobs (#212)
23. **Medium**: Data integrity, schema validation, cache invalidation (#88, #89, #108, #159-163, #181)
24. **Medium**: Frontend bugs — filter values (#230-231), NaN inputs (#232), stale closures (#229, #248)
25. **Medium**: Accessibility — skip nav (#95), spinners (#116), labels (#117)
26. **High**: Business logic -- membership date truncation (#261), deduct_visit no status check (#262), discount ambiguity (#265)
27. **High**: Schedule integrity -- no transition validation (#264), 'or' fallback defeats explicit values (#263)
28. **High**: Missing tenant scoping -- measurement trends (#266), notes (#267), PRs (#268), analytics (#269)
29. **High**: Frontend auth gap -- no Next.js middleware, protected pages served unauthed (#270)
30. **High**: Test quality -- delete assertions missing (#271), filter params unverified (#272), status args unverified (#273)
31. **Medium**: Payment logic -- invoice.paid_at never set (#279), arbitrary status transitions (#280), processing fees always 0 (#282)
32. **Medium**: Membership edge cases -- months+days discards days (#274), visit limit never enforced (#275), perpetual never resets (#276), trial datetime crash (#277)
33. **Medium**: Entity lifecycle -- deactivated trainers returned (#284), soft-deleted locations returned (#285), enum crash (#286)
34. **Medium**: Frontend robustness -- missing error pages (#291), Sonner theme crash (#292), double redirect (#293)
35. **Critical**: Webhook signature crash -- all webhook deliveries broken (#296)
36. **High**: Cross-tenant escalation -- account_service no gym_id (#302), trainer_client no gym_id (#303)
37. **High**: Token security -- refresh token family not revoked on expiry (#299), client_secret exposed (#320)
38. **High**: GDPR -- data export/deletion UUID vs string means Notes never processed (#300)
39. **High**: PR logic inverted -- 1-rep records all thresholds (#301), addon cancellation commit ordering (#304)
40. **High**: K8s production readiness -- missing PDB (#309), strategy (#310), startupProbe (#311), NetworkPolicy blocks probes (#315)
41. **High**: K8s security -- ingress annotations (#312), ENFORCE_HTTPS/CORS missing (#316), JWT_SECRET missing (#313)
42. **High**: CI security -- pip-audit suppressed (#314), idempotency cross-user poisoning (#317)
43. **High**: Schema validation gaps -- unvalidated plan configs (#318), Stripe URLs (#319), gym_id not verified (#321), arbitrary client status (#322)
44. **High**: Missing confirmation dialogs -- goal delete (#306), goal abandon (#308), schedule actions (#307)
45. **Medium**: Service bugs -- check-in without membership (#328), double checkout (#330), spurious PRs (#329)
46. **Medium**: Schema validation -- 7 enum fields accept strings (#373), email format missing (#374), no size limits (#375)
47. **Medium**: Infra gaps -- backup/restore asyncpg URL (#356-357), no .dockerignore (#355), no pod anti-affinity (#358)
48. **Medium**: CI gaps -- no coverage (#351), no Redis in test (#352), no frontend tests (#353), no K8s validation (#354)
49. **Low**: Code quality, configuration, test improvements, missing indexes (#254)
50. **Critical**: Stripe webhook UUID type mismatch -- payment success/failure handlers both broken (#383-384)
51. **Critical**: PaymentMethodCreate missing type field -- every add-payment-method call fails (#385)
52. **High**: Schedule creation passes status=None -- IntegrityError on every create (#386)
53. **High**: Test infrastructure gaps -- webhook handlers untested (#387), notes CRUD (#388), GraphQL zero coverage (#389), 34/43 services untested (#390)
54. **High**: Test correctness -- audit_logs RBAC effectively untested (#391), conftest missing DB override (#392)
55. **High**: Frontend dual AuthProvider -- auth state not shared between app and login layouts (#393)
56. **High**: API spec compliance -- login response shape (#394-395), check-in paths (#396-397), exercises filters (#398), workouts split (#399), accounts missing (#400)
57. **Medium**: Service contract issues -- record_visit discards notes (#401), update_set ignores path param (#402), platform_admin blocked (#403)
58. **Medium**: Frontend double-submit risks -- schedules (#406), exercises (#407), check-ins (#410), NaN saves (#405)
59. **Medium**: Spec response shape mismatches -- all major resource types missing fields (#411-420, #434-438)
60. **Medium**: Test coverage gaps -- 9 router test files missing critical endpoint coverage (#421-429)
61. **Medium**: Frontend React key anti-pattern -- array index keys on 3 list pages (#431-433)
62. **Low**: Spec aspirational features -- HATEOAS (#442), ETags (#443), bulk ops (#444), webhook events (#445)
63. **Critical**: Stripe integration entirely mocked -- no actual API calls (#451), fake Connect accounts (#453)
64. **Critical**: Zero refund functionality -- no service, no endpoint, no webhook handler (#452)
65. **Critical**: JWT missing issuer/audience validation -- token substitution attacks (#450)
66. **High**: Auth security -- timing attack on login (#454), SHA256 token hashes without salt (#455)
67. **High**: Stripe subscription.updated handler empty -- plan changes silently ignored (#456)
68. **High**: Payment lifecycle gaps -- no retry on failure (#457), no currency validation (#458), line_items empty (#459)
69. **High**: Data integrity -- soft-deleted clients orphan child records (#460), timezone date grouping wrong (#461)
70. **High**: Frontend architecture -- missing 'use client' in auth layout (#462), date formatting without timezone (#463), filter state lost on back (#464)
71. **High**: Batch job performance -- addon cascade N+1 exhausts connection pool (#465)
72. **Medium**: Financial logic gaps -- no proration (#469), tax never calculated (#470), no invoice PDF (#471), missing webhook handlers (#472)
73. **Medium**: Auth timing/enumeration -- registration leaks existence (#467), non-constant-time hash comparison (#468)
74. **Medium**: Frontend robustness -- unmount setState across 20+ pages (#474), dashboard no error boundary (#475), popup blocked (#476)
75. **High**: Email delivery -- send failures silently ignored on register/reset/resend (#484), incomplete data export (#485)
76. **High**: GDPR compliance -- no PII read audit logging (#486), deletion orphans AI summaries/agreements (#489)
77. **High**: DoS vectors -- Uvicorn no request timeout (#487), idempotency cache unbounded to OOM (#488)
78. **Medium**: Privacy gaps -- no consent tracking (#493), S3 region not validated (#494), log redaction missing IPs (#492)
79. **Medium**: Migration index gaps -- TrainerInvitation email (#495), ClientInvitation user_id (#496), Goal trainer_id (#497), PR type (#498)
80. **Medium**: Compliance -- CAN-SPAM unsubscribe header missing (#490), data export as base64 URI leaks PII (#503), sidebar cookie insecure (#502)
81. **Critical**: E-sign security -- no cryptographic signature verification (#507), no state machine (#508), docs can be reverted
82. **High**: E-sign integrity -- no content hash (#509), unverified signer identity (#510), template XSS injection (#511), no audit trail (#512)
83. **High**: GraphQL security -- field-level auth missing exposes PII (#513), query batching DoS (#514)
84. **High**: Cache/performance -- stampede on expiry (#515), cache keys missing gym_id (#517)
85. **High**: Seed script can run in production (#516), loading spinners inaccessible (#518), search icons unlabeled (#519)
86. **Medium**: Agreement lifecycle -- expiry not enforced (#520), seed atomicity gap (#521), restore errors suppressed (#522)
87. **Medium**: Accessibility -- clickable divs not keyboard accessible (#523), no aria-live for toasts (#524), data table loading unannounced (#525), job monitoring (#526)
88. **High**: Error handling systemic -- model_validate crashes 130+ endpoints as 500 (#533), unhandled db.commit in auth (#535) and stripe (#536)
89. **High**: Webhook robustness -- malformed JSON crashes (#534), auth envelope inconsistency (#538)
90. **High**: HTTP method confusion -- PUT endpoints use partial update semantics (#537), next.config.ts empty (#539)
91. **Medium**: API contract -- POST actions return 200 not 201 (#541), billing unstructured (#542), webhooks no pagination (#543)
92. **Medium**: Frontend architecture -- all pages 'use client' (#546), no page metadata (#547), auth loading flash (#548), unvalidated route params (#545)
93. **Medium**: Type safety -- runtime shape mismatches (#544), Record<string, unknown> loses types (#549), model_validate list crashes (#540)
94. **Critical**: Client invitation endpoints entirely missing -- service dead code (#555), invitation no transactions (#556)
95. **Critical**: Deactivation no cleanup cascade -- cached tokens retain access (#557)
96. **High**: Usage metering period filtering backwards (#558), AI summary frequency error (#559), analytics NULL inflation (#560)
97. **High**: Invitation security -- no gym_id isolation (#561), no email verification (#562), no audit logging (#572)
98. **High**: Monetary constraints missing -- invoice negatives (#564), processing fee unbounded (#565), addon discount unbounded (#571)
99. **High**: Deactivation cascade incomplete -- trainer deactivation doesn't cascade to user (#566)
100. **Medium**: Dialog forms don't reset on close (#563), numeric inputs accept negatives (#569)
101. **Medium**: Data integrity constraints -- order_index uniqueness (#568), temporal ordering (#574-575), physical fields negative (#570)
102. **Medium**: Model constraints -- Program.num_days allows 0 (#576), visits_remaining negative (#578), reporting returns 0 vs null (#567)
103. **Low**: Password schema conflict (#579), device token length (#580), token expiry inconsistency (#581)
104. **High**: Cache-based tenant isolation bypass -- exercise (#583), program (#584), gym (#585) cached responses skip auth checks
105. **High**: Idempotency TOCTOU race -- concurrent duplicate financial operations (#582)
106. **High**: Cursor pagination systemic bugs -- timestamp collision (#586), unhandled ValueError (#587), timezone mismatch (#588)
107. **High**: Unbounded queries -- batch jobs OOM (#589), volume trend (#590), data export (#591)
108. **High**: Storage completely non-functional -- backends never wired in (#592), no file upload UI (#597)
109. **High**: Storage security -- path traversal (#593), no client_id verification (#594), no encryption (#595), unlimited upload size (#598)
110. **High**: Frontend progress photo integration broken -- wrong delete URL (#596), no auth logging (#599)
111. **Medium**: Idempotency bugs -- caches 4xx (#600), O(n) eviction (#605), streaming broken (#606)
112. **Medium**: Background job reliability -- no error isolation (#601), missed jobs (#602), no alerting (#608)
113. **Medium**: Missing indexes -- schedules composite (#612), check_ins composite (#613), membership status (#614)
114. **Medium**: Storage gaps -- no config (#623), MIME validation (#617), orphaned blobs (#618), S3 reuse (#621)
115. **Medium**: Observability gaps -- no structured logging (#624), no request ID correlation (#625), metrics unexposed (#626)
116. **Medium**: Config management -- secrets bypass Settings (#627), OpenAPI in production (#628), SecretStr missing (#629)
117. **Low**: Graceful shutdown (#636), K8s env vars (#637), JWT email PII (#638), service logging (#640)
118. **Critical**: Dead infrastructure -- audit_service.log_event never called (#642), deliver_webhook never called (#643)
119. **Critical**: Check-in doesn't deduct membership visits -- unlimited check-ins for limited plans (#644)
120. **High**: Test infrastructure -- 19 async tests may not execute (#645), RBAC untested (#646), SimpleNamespace factories (#647)
121. **High**: Migration server_defaults -- 25+ boolean (#648), integer (#649) columns break non-ORM inserts
122. **High**: Migration missing FKs -- goals trainer (#650), programs trainer (#651), membership self-ref (#652)
123. **High**: Frontend security -- AuthGuard race condition (#653), no role-based routing (#654)
124. **High**: Service bypasses -- Stripe webhook direct model access (#656), billing partial commits (#657)
125. **High**: Missing notifications -- membership changes (#658), trainer invitation email (#659)
126. **Medium**: Migration integrity -- string defaults (#664), non-idempotent (#665), env.py config (#667)
127. **Medium**: Missing FK constraints -- schedules (#668), check_ins (#669), polymorphic types (#670-671)
128. **Medium**: Frontend UX -- router.push back (#673), tab state (#674), unsaved changes (#678)
129. **Medium**: Service contracts -- discount apply vs validate (#682), auth bypasses service (#684), reporting bypasses service (#686)
130. **Low**: Test quality -- BMI edges (#689), passkey tautological (#690), token test (#691)
131. **Critical**: Payment success handler no idempotency -- re-processes succeeded payments, resurrects failed payments (#696)
132. **High**: Payment state machine gaps -- failure overwrites succeeded (#697), subscription.deleted cancels any status (#698), paused never expires (#699)
133. **High**: Workout status guards missing -- exercises/sets added to completed workouts (#700), PATCH bypasses lifecycle (#701)
134. **High**: UTC midnight day boundaries -- reporting (#702), busyness (#703), schedule list (#704) all wrong for non-UTC gyms
135. **High**: GraphQL architecture -- resolvers bypass service layer (#705), independent sessions (#707), user_id unused (#708)
136. **High**: GraphQL data quality -- deactivated trainers (#706), soft-deleted clients (#709), all-status returns (#722-724)
137. **High**: Stripe webhook error handling -- no try/except around service calls, 500s trigger retries (#710)
138. **Medium**: Status injection -- ScheduleCreate (#714), GoalUpdate (#716), create_membership (#715), discount_type (#717)
139. **Medium**: Status transition guards missing -- complete_onboarding (#712), custom domain (#713), deletion retry (#711)
140. **Medium**: Date/time bugs -- occupancy histogram (#719), frontend datetime-local (#720), pending_cancellations tz (#721)
141. **Medium**: GraphQL gaps -- no mutations (#725), UUID parsing (#726), no status filters (#722-724)
142. **Medium**: Error handling -- registration partial success (#727), Stripe fallthrough (#728), forgot-password token waste (#729)
143. **Medium**: Validation gaps -- calendar entity validation (#730), webhook 4xx retries (#731), error middleware (#732), rate limiter (#733)
144. **Medium**: iCal RFC violations -- missing DTSTAMP (#718)
145. **Low**: Schema str fields -- MembershipUpdate (#734), TrainerExceptionCreate (#735)
146. **Low**: iCal spec -- non-RFC STATUS (#736), Z suffix (#737), CALSCALE (#738), resend-verification (#739)
147. **Critical**: WebhookCreate missing secret field -- IntegrityError on every webhook creation (#740)
148. **High**: Middleware stack ordering -- ErrorHandler inside outer middleware, raw 500s bypass structured error handling (#741)
149. **High**: HTTPSRedirectMiddleware blocks K8s health probes behind TLS proxy (#742)
150. **High**: Rate limiter Redis INCR/EXPIRE non-atomic -- permanent rate limit possible (#743)
151. **High**: Multi-tenancy gaps -- AI summary IDOR (#744), AI summary cross-tenant data (#745), payment methods no gym check (#746)
152. **High**: Cross-tenant manipulation -- handle_payment_failure no gym_id (#747), deletion request no gym_id (#748)
153. **High**: Programs detail page race condition -- out-of-order responses overwrite exercises (#749)
154. **Medium**: Middleware lifecycle -- RequestID innermost (#750), security headers missing on errors (#751), engine not disposed (#752)
155. **Medium**: Schema validation -- 7 more str-vs-enum fields (#757), discount bounds (#758-759), naive datetime (#760)
156. **Medium**: Webhook schema -- WebhookResponse type mismatches (#754-755), PaginatedResponse untyped (#756)
157. **Medium**: Multi-tenancy service gaps -- double_booking (#764), availability (#765), PRs (#766), addons (#767), occupancy (#768)
158. **Medium**: Auth input validation -- password no max_length bcrypt DoS (#762), exception_date type mismatch (#763)
159. **Medium**: Frontend state -- audit logs no reload indicator (#769), exercises stale closure (#770), memberships no loading (#771)
160. **Medium**: Frontend data flow -- check-ins race (#772), settings silent no-op (#773), refetch misleading errors (#774)
161. **Low**: Schema gaps -- 10+ fields no max_length (#777), lists no size limit (#778), numeric no bounds (#779)
162. **Low**: Response schemas -- invitation missing fields (#780), 3 str-vs-enum responses (#781), discount format (#782)
163. **Low**: Frontend UX -- double toast (#784), discount form not reset (#785), edit dialog stale (#788), stale workoutId (#789)
164. **Critical**: GDPR deletion never executes -- process_pending_deletions never scheduled (#790)
165. **High**: Background job reliability -- scheduler shutdown race (#791), stuck processing never reset (#792), scheduler single-process (#793)
166. **High**: Query performance -- detect_prs 2N+1 queries (#794), list_invoices/list_payments no LIMIT (#795)
167. **High**: Frontend accessibility -- avatar button no aria-label (#796), workout set inputs no labels (#797), sidebar nav no landmarks (#798)
168. **Medium**: Background job integrity -- cleanup unbounded DELETE (#799), trial batch no time window (#800)
169. **Medium**: ORM patterns -- select_from instead of joins (#801), list_prs filter bypass (#802), detect_prs missing indexes (#803-805)
170. **Medium**: Accessibility -- 12 pages missing labels, landmarks, live regions (#810-821)
171. **Medium**: API contract compliance -- POST 200 vs 201 (#822-823), PATCH vs PUT (#824), pagination cursor (#806-809)
172. **Low**: Performance -- list_payment_methods unbounded (#825), missing indexes (#827-828)
173. **Low**: Accessibility -- decorative icons in a11y tree (#829), photos placeholder (#830), Stripe connect window (#831)
174. **Low**: Spec compliance -- ai-summary 201 (#832), validate POST→GET (#833), rate limit header (#834), envelope (#835), calendar 201 (#836)
175. **High**: Test execution -- 19+ async tests never awaited, silently pass without running (#837), path traversal test tautological (#838)
176. **High**: Test correctness -- Pydantic ValidationError untested in routers (#839), RBAC assertions use wrong field (#840), empty-body PATCH returns 422 not tested (#841)
177. **High**: Config/Deployment -- Dockerfile missing Alembic directory (#852), CI skips migration check (#853), Alembic env.py no advisory lock (#854), backup script no encryption (#855)
178. **Medium**: Test gaps -- filter param assertions missing (#842-843), status transition tests missing (#844-845), error path coverage (#846-850)
179. **Medium**: Config gaps -- K8s resource limits (#856), no graceful shutdown (#857), missing env vars (#858), missing composite index (#860)
180. **Medium**: Frontend UX -- String.replace first-only (#882), progress photos no encodeURIComponent (#883), check-ins wrong empty state (#885), accounts dialog reset (#887)
181. **Medium**: Service logic -- membership start_date override (#889), metering ceiling vs round (#892), AI summary race (#893), analytics None crash (#894)
182. **Medium**: Service edge cases -- iCal None fields (#895), discount concurrent redeem (#896), reporting boundary double-count (#901), workout negative reps (#899-900)
183. **Low**: Testing -- inconsistent mock factories (#851), Dockerfile not pinned (#866), config default confusing (#867), CI no caching (#869)
184. **Low**: Frontend -- login autocomplete (#884), page-header dead code (#886), workout dropdown no indicator (#888)
185. **High**: Billing RBAC -- all 17 billing endpoints missing role checks (#930), usage endpoints no RBAC (#948), cross-tenant session pack (#929)
186. **High**: Stripe integration -- subscription.deleted UUID mismatch (#945), session pack orphans (#928), no onboarding check (#932)
187. **High**: Tenant isolation -- PaymentMethod no gym_id (#955), ClientProgram no gym_id (#958), rate limiter proxy IP (#907)
188. **High**: Data integrity -- stripe_connect_id no UNIQUE (#962), stripe_payment_intent_id no UNIQUE (#963), GraphQL PermissionError leak (#902)
189. **High**: Auth gaps -- passkey service dead code (#914), passkey missing verify auth (#915), MFA no disable (#918)
190. **Medium**: Auth security -- MFA overwrite (#919), token accumulation (#920), KeyError on missing sub claim (#908, #917), self-register gym_id=None (#926)
191. **Medium**: Billing logic -- discount case-sensitive (#935), discount update can't clear dates (#936), invoice.paid no timestamp (#938), invoice.payment_failed no state check (#939)
192. **Medium**: Service bugs -- INNER JOIN drops payments (#934), duplicate CRUD (#946), metric historical max (#947), payment_method_id discarded (#933)
193. **Medium**: Model integrity -- Mapped[float] precision loss (#959), onupdate ORM-only (#960), plan_type String vs Enum (#961)
194. **Medium**: Frontend billing -- discount form incomplete (#949), invoices tab empty (#950), no payment methods UI (#951), discount code immutable (#952)
195. **Medium**: Middleware/config -- metrics invisible to monitoring (#909), DB connectivity not checked (#912), CORS missing headers (#905)
196. **Low**: Auth edge cases -- list_sessions unbounded (#922), first_name no max_length (#923), user_agent truncation (#924), commit coupling (#925)
197. **Low**: Billing edge cases -- raw dicts bypass Pydantic (#941), fee null check (#943), response shape (#944), period validation (#953), dates inverted (#954)
198. **Low**: Security minor -- HSTS unconditional (#906), HTTPS redirect order (#910), PII filter late handlers (#913), token no max_length (#927), stripe_connect_id exposed (#956), description unbounded (#957)
199. **Low**: Data integrity -- capacity CHECK (#964), times_used CHECK (#965), visits CHECK (#966), Invoice server_default (#967), migration downgrade (#968), WorkoutSet default (#969)
200. **Critical**: Measurements page sends measurement_type but backend expects type -- every create 422s (#1191)
201. **High**: Frontend-backend field mismatches -- measurements type (#1192, #1195), settings email/phone (#1193), trainers specializations (#1194)
202. **High**: Schedule UX -- raw UUID input (#1197), truncated UUIDs instead of names (#1198)
203. **High**: Service bugs -- stale occupancy (#1217), skip double-booking check (#1223), booking during TrainerException (#1224)
204. **High**: Security -- device ownership missing (#1226), GDPR anonymize incomplete (#1232), double-commit dirty state (#1234)
205. **High**: Testing infra -- route pollution (#1235), no integration tests (#1237), unpinned deps (#1239)
206. **Medium**: Frontend CRUD gaps -- trainers read-only (#1196), client detail no edit (#1199), programs no edit/delete (#1200), no add exercises (#1201)
207. **Medium**: Frontend UX -- analytics misleading empty (#1203), deactivated trainers no filter (#1207), settings no gym message (#1210)
208. **Medium**: Service edge cases -- record_visit non-atomic (#1211), cancel_membership status (#1212), batch atomicity (#1213), period reset guard (#1214)
209. **Medium**: Service bugs -- trial check-in (#1215), check-in timezone (#1216), workout enum ValueError (#1218), cache delete propagation (#1219)
210. **Medium**: Service data -- delete_program refs (#1220), availability PK collision (#1221), duplicate exceptions (#1222), preferences race (#1225)
211. **Medium**: Analytics -- bodyweight 0 volume (#1227), completion_rate 0-1 (#1228), volume UTC grouping (#1230), export JSONB serialize (#1231)
212. **Medium**: Schema/validation -- NoteResponse str dates (#1247-#1248), CheckoutResponse model_config (#1249), unbounded content (#1251-#1252), API path mismatch (#1253), ge=0 constraints (#1256-#1257)
213. **Medium**: Integration -- client notes vs fitness_goals (#1254), accounts role always member (#1255), npm audit missing (#1238)
214. **Medium**: Testing gaps -- delete never verified (#1236), check-in tests (#1242), signature mismatch (#1243), deactivated user (#1244), DialogDescription (#1205)
215. **Low**: Frontend minor -- phone type=tel (#1204), duplicate sidebar icons (#1206), settings no refresh (#1209), N+1 delete (#1233)
216. **Low**: Testing/config -- test codifies bug (#1245), timezone shadow (#1246), dead aiosqlite (#1240), wide tailwind range (#1241), model_config (#1250), date type inconsistency (#1229)
217. **High**: CORS middleware last -- error responses invisible to browser (#1258), APScheduler v4 import crash (#1259)
218. **Medium**: Frontend auth/UX -- AuthProvider race (#1260), stale login tokens (#1261), schedule end<start (#1262), goals inverse progress (#1263)
219. **Medium**: Frontend bugs -- discount out-of-range (#1264), domains loading (#1266, #1269), set array keys (#1267), client detail races (#1268)
220. **Medium**: Middleware -- get_db type annotation (#1275), metrics mispositioned (#1276), idempotency Content-Type (#1277), rate limiter double-count (#1278)
221. **Medium**: Config/startup -- scheduler singleton (#1279), Settings() eager (#1281), processing_fee Float (#1282)
222. **Medium**: Missing indexes -- workouts.status (#1283), workout_exercises.exercise_id (#1284)
223. **Medium**: Missing updated_at -- Exercise (#1285), Workout (#1286), CheckIn (#1287)
224. **Medium**: Missing FK constraints -- schedule created_by (#1289), check_in by_user (#1290), assignment by (#1291), photo measurement_id (#1292), photo user_id (#1293)
225. **Medium**: Missing DB constraints -- discount amount>=0 (#1294), day_of_week 0-6 (#1295), availability end>start (#1296), audit_logs FK (#1297)
226. **Medium**: Missing UNIQUE constraints -- stripe_customer_id (#1298), stripe_payment_method_id (#1299), stripe_invoice_id (#1300), active memberships (#1301)
227. **Medium**: Spec gaps -- OAuth2 server (#1307), MFA endpoints (#1308), trainer soft-delete (#1309), client grant-login (#1310), analytics endpoints (#1311), add_member semantics (#1312)
228. **Low**: Frontend minor -- agreements no content view (#1265), measurements addType reset (#1270), accounts double toast (#1271), email trim (#1272), email validation (#1273), forgot-password provider (#1274)
229. **Low**: Data integrity minor -- PersonalRecord updated_at (#1302), WorkoutSummary updated_at (#1303), capacity CHECK (#1304), num_days CHECK (#1305), exp_month CHECK (#1306), token_hash length (#1288), PII redaction (#1280)
230. **Low**: Spec compliance deferred -- trainer exceptions list (#1313), passkey endpoints (#1314), calendar revoke (#1315), order param (#1316), search param (#1317), qr-code (#1318), deletion-status (#1319), gym delete (#1320), resend-invitation (#1321)
231. **Critical**: E-sign non-functional -- no signing endpoint (#1101/1330), no signing tokens (#1103/1331), no signature capture (#1104/1332)
232. **High**: E-sign security -- no RBAC on agreements (#1105/1334), content not snapshotted (#1114/1335), no locking (#1115/1336)
233. **High**: Webhook infrastructure -- delivery blocks request path 36s (#1102/1322), no RBAC (#1113/1328), no event validation (#1110/1325)
234. **High**: Dark mode CSS dead code -- ThemeProvider never wired up (#1106/1341)
235. **High**: Transaction integrity -- workout+PR multi-commit (#1107/1353), exercise/program delete orphans (#1124-1125/1354-1355)
236. **Medium**: Stripe webhook -- no idempotency (#1111/1326), no payload validation (#1112/1327), silent failures (#1128/1358)
237. **Medium**: Race conditions -- trainer-client assign (#1129/1359), gym slug (#1130/1360), no optimistic locking (#1126/1356)
238. **Medium**: Frontend UX -- workout set mobile overflow (#1118/1342), page header mobile break (#1131/1351), select All filter bug (#1123/1347)
239. **Medium**: Dead frontend code -- PageHeader (#1119/1343), DataTable (#1120/1344), Skeleton (#1121/1345), useIsMobile SSR flash (#1122/1346)
240. **Low**: Dead dependencies -- zod/react-hook-form unused (#1137/1349), date-fns unused (#1139/1352), duplicate sidebar icons (#1138/1350)
241. **Critical**: Test fixture invalid enum -- CheckInMethod 'qr' doesn't exist, tests pass with wrong data (#1140)
242. **High**: response_model=dict bypasses Pydantic validation -- 130+ endpoints return unvalidated data (#1141)
243. **High**: Migration timestamps nullable -- created_at/updated_at allow NULL across all tables (#1142)
244. **High**: No ON DELETE CASCADE on 50+ FKs -- orphaned rows on any parent deletion (#1143)
245. **High**: Cross-tab auth desync -- logout/token refresh not propagated to other tabs (#1144)
246. **High**: Storage accepts any file type -- no MIME validation enables XSS via upload (#1145)
247. **High**: Photo deletion doesn't remove stored files -- GDPR violation (#1146)
248. **High**: Rate limiter wrong path -- password-reset not rate limited (#1147)
249. **Medium**: Test quality -- service args unverified (#1148), fixture incomplete (#1149), pagination untested (#1150), envelope inconsistent (#1151)
250. **Medium**: Auth UX -- no post-login redirect (#1153), no CSRF (#1154), refresh token parsing broken (#1155)
251. **Medium**: Missing frontend pages -- no verify-email (#1156), no register (#1157)
252. **Medium**: Storage robustness -- no filename sanitization (#1159), concurrent overwrite (#1160), no cleanup on DB failure (#1161)
253. **Medium**: Email -- silently succeeds without SMTP (#1162), STARTTLS no cert verification (#1163)
254. **Low**: Minor -- duplicate indexes (#1164), no password toggle (#1165), MFA status leak (#1166), S3 client per-call (#1167)
255. **Critical**: Discount validation bypass -- apply_discount accepts expired/maxed-out codes (#1168/1389), GraphQL null gym_id bypass (#1169/1390)
256. **High**: Rate limiter unsigned JWT identity (#1170/1391), discount negative total (#1171/1392), data export cross-tenant (#1172/1393)
257. **High**: Data deletion cross-tenant (#1173/1394), workout set ownership bypass (#1174/1395)
258. **Medium**: GraphQL no RBAC (#1175/1396), CORS wildcard headers (#1177/1398), rate limiter memory leak (#1178/1399)
259. **Medium**: Middleware -- idempotency strips headers (#1179/1400), BaseHTTPMiddleware buffering (#1180/1401), DB pool config (#1176/1397)
260. **Medium**: Frontend bugs -- audit logs debounce (#1181/1402), audit logs loading (#1182/1403), notification stale closure (#1183/1404)
261. **Medium**: Frontend bugs -- analytics duplicate calls (#1184/1405), client detail redirect (#1185/1406)
262. **Medium**: Service bugs -- membership day clamping (#1186/1407), payment amount verification (#1187/1408), anonymize retry loop (#1188/1409), trial cancellation (#1189/1410)
263. **Low**: Minor -- request ID spoofing (#1190/1411), profile menu broken (#1191/1412), membership sub-pages (#1192/1413), unpause rounding (#1193/1414)
264. **High**: Schema enum bypass -- GoalUpdate.status (#1196/1417), AccountType (#1197/1418), template_scope (#1198/1419) accept arbitrary strings
265. **High**: Service layer gaps -- 8 update_* services can't clear nullable fields (#1194/1415), note ownership missing (#1195/1416), client_id not verified (#1199/1420)
266. **High**: Location soft-delete no cascade (#1200/1421), client_programs has no gym_id column (#1208/1436)
267. **High**: Router auth -- schedule mutations no audit (#1201/1422), program endpoints no gym_id (#1202/1423), availability no gym_id (#1203/1424)
268. **High**: Router IDOR -- get_envelope (#1204/1426), delete_measurement (#1205/1427), exercises stale closure (#1206/1429)
269. **High**: Migration -- 8 timestamps nullable (#1207/1435)
270. **Medium**: Router/envelope -- mfa_setup (#1209/1425), add_set IDOR (#1210/1428), program cache poisoning (#1218/1442)
271. **Medium**: Frontend bugs -- falsy-zero (#1211/1430), occupancy race (#1212/1431), agreements errors swallowed (#1213/1433)
272. **Medium**: Backend edge cases -- volume PR inflation (#1216/1440), get_gym inactive (#1217/1441), workout note cross-tenant (#1219/1443), client status filter (#1220/1444)
273. **Medium**: Migration -- calendar_tokens index (#1214/1437), gen_random_uuid compat (#1215/1438)
274. **Low**: Minor -- schedule toast grammar (#1221/1432), trainers empty specialties (#1222/1434), FK indexes (#1223/1439)
