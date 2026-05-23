# PL-400 Develop Integrations — Concept Study Guide

> Exam weight: 10–15%. Based on synthesis of 42 practice questions.

---

## 1. Dataverse Azure Integration: Service Endpoints & Contract Types

### Key Facts

The **Plug-in Registration Tool** is used to register both **service endpoints** (Azure Service Bus, Event Hubs) and **webhooks**. For Azure Service Bus, a **step** must also be registered to bind the Dataverse event (message + table) to the endpoint — two separate registrations are always required.

### Contract Types

| Contract | Listener Required? | Fan-out | Typical Use |
|---|---|---|---|
| **One-way** | Yes (active listener) | No | Simple fire-and-forget to a relay; fails if listener offline |
| **Queue** | No (brokered) | No (single consumer) | Durable delivery; consumer reads later; listener can be offline |
| **Topic** | No (brokered) | Yes (multiple subscribers) | Multiple downstream consumers for the same event stream |
| **Event Hub** | No | Yes (streaming) | High-volume analytics ingestion; millions of events/sec |
| **Two-way** | Yes | No | Synchronous round-trip; response returned to Dataverse |

**Decision rule:**
- Listener is sometimes offline → **Queue**
- Multiple independent downstream consumers → **Topic**
- High-throughput streaming / analytics → **Event Hub**
- Simple direct HTTP callback to external app → **Webhook**

### Event Hub Specifics
- Contract type must be **Event Hub** (not Queue or One-way)
- Only **SAS authorization** is supported for Event Hub registrations
- Message body format can be **XML or JSON**
- Must supply the Event Hub connection string

### Common Distractors
- "Switch to Two-way" does not solve listener-downtime problems — it still needs an active listener.
- "Register a WebHook instead" is not a fix for listener downtime within the Service Bus model.
- REST contract is similar to two-way on a REST endpoint, not a durable queue.

---

## 2. Webhooks vs Azure Service Bus

| Dimension | Webhook | Azure Service Bus |
|---|---|---|
| Transport | HTTP POST with JSON | Service Bus brokered messaging |
| Registration tool | Plug-in Registration Tool | Plug-in Registration Tool |
| Execution mode | Synchronous or asynchronous | Asynchronous only |
| Security model | HttpHeader, HttpQueryString, WebhookKey | SAS |
| Response body parsing | Not parsed (only HTTP status code matters) | N/A |
| Listener requirement | Active listener at endpoint | Depends on contract (queue = no active listener needed) |
| Best for | Notifying an external web app via HTTP | Durable, decoupled enterprise messaging |

> **Plain English — Async vs Active Listener:** These two columns measure different things. "Execution mode" describes whether Dataverse waits for the response before finishing the user's operation. "Listener requirement" describes whether the destination must be a live HTTP server. For webhooks, even in async mode, your HTTP endpoint must exist and be reachable — async just means Dataverse sends the call in the background without blocking the user. The listener still has to pick up eventually. With Service Bus Queue, the message sits in the queue indefinitely — your consumer can come back online a week later and still process it. Think of webhook as a phone call (someone must answer eventually) vs Service Bus Queue as a mailbox (message waits as long as needed).

### Webhook Authentication Options

| Option | When to Use |
|---|---|
| **WebhookKey** | Endpoint expects auth value as `?code=<key>` query string — specifically designed for **Azure Functions** |
| **HttpHeader** | Custom HTTP header-based auth |
| **HttpQueryString** | Custom query string key/value (not the `code` pattern) |
| SharedAccessSignature | Not applicable for webhook registrations |

**Decision rule:** Azure Function endpoint using `?code=` → **WebhookKey** always.

### Webhook Response Body Behavior
Dataverse **does not parse the response body** from a webhook call. It only reads the HTTP status code. A 200 with a JSON body instructing Dataverse to alter behavior will be ignored. Use synchronous plug-ins if you need in-transaction control.

> **Plain English:** Dataverse only cares about "did it succeed or fail" — not "what the response said." Your endpoint can return `200 OK` with a JSON body saying `{ "action": "cancel_save" }` and Dataverse will completely ignore that JSON. It sees `200` and moves on. If you want to control what Dataverse does based on external logic (block a save, throw an error to the user), you need a synchronous plug-in — not a webhook.

---

## 3. Listener Option Selection: Plug-in vs Webhook vs Flow vs Event Hub

| Requirement | Best Listener |
|---|---|
| Block/cancel a save and show error to user | **Synchronous plug-in step** |
| Notify external HTTP endpoint asynchronously | **Webhook** (asynchronous step) |
| Low-code asynchronous response, no custom code | **Power Automate cloud flow** (Dataverse "When an action is performed" trigger) |
| High-throughput streaming to analytics systems | **Azure Event Hubs** |
| Enterprise pub/sub with multiple subscribers | **Service Bus Topic** |
| Durable delivery when listener may be offline | **Service Bus Queue** |

**Key distinction — synchronous plug-in vs all others:**
Only a synchronous plug-in step participates directly in the Dataverse transaction pipeline and can cancel the operation and surface an error to the user. All other listeners (webhook, flow, Event Hub) are external or asynchronous and cannot block the save.

---

## 4. Custom Azure-Aware Plug-ins (IServiceEndpointNotificationService)

### Key Facts

A **custom Azure-aware plug-in** is a plug-in that manually calls `IServiceEndpointNotificationService.Execute()` to publish the execution context to a registered service endpoint (Azure Service Bus).

### Required Registration Model
- Must be registered as **asynchronous** (the notification service returns `null` on synchronous steps)
- Must run in the **sandbox**
- Service endpoint ID is passed via **unsecure configuration** at step registration

### Correct Code Pattern
```csharp
IServiceEndpointNotificationService cloudService =
    (IServiceEndpointNotificationService)serviceProvider
        .GetService(typeof(IServiceEndpointNotificationService));

cloudService.Execute(
    new EntityReference("serviceendpoint", serviceEndpointId),  // correct logical name
    context);
```

**Critical:** The `EntityReference` logical name must be `"serviceendpoint"` — NOT the business table name (e.g., `"account"`).

### Retry Safety Rule
For asynchronous plug-ins, if the Service Bus post fails and is retried, the **entire plug-in executes again**. Therefore:
- The Azure-aware plug-in should do **nothing except** modify the context (if needed) and post to Service Bus
- Adding extra business logic creates duplicate side effects on retry
- **Publish-only design** is the Microsoft-documented best practice

### Common Distractors
- "Register outside sandbox for direct network access" — wrong; sandbox is required
- "Notification service works on synchronous steps" — wrong; returns null on sync
- Using `"account"` or another table name in the EntityReference — wrong; must be `"serviceendpoint"`

---

## 5. UpsertRequest and Alternate Keys for Data Synchronization

### UpsertRequest

`UpsertRequest` is the standard message for integration scenarios where you need to **create or update** without a preliminary existence check. The `UpsertResponse.RecordCreated` property indicates whether the operation inserted (`true`) or updated (`false`) the row.

**Use when:**
- Source system has a business identifier but not the Dataverse GUID
- Integration must avoid a retrieve-first pattern
- Downstream logging needs to distinguish new vs updated rows

> **Plain English — why no GUID:** The source system (e.g., SAP, Salesforce) has its own ID for a record (e.g., `CUST-1001`), but Dataverse assigns its own internal GUID when it stores the record. The source system has never seen that GUID and doesn't store it. So the integration maps the source system's ID to an **alternate key** in Dataverse, and Upsert uses that as the lookup key — find or create by `erp_customerid = CUST-1001` without ever needing the Dataverse GUID.

### Alternate Keys

Alternate keys let Dataverse rows be identified by **business columns** instead of GUIDs. Essential for integration with external systems that have their own identifiers.

**Valid column types for alternate keys:** Single line of text, Whole number, Decimal, Date/Time, Lookup, Option Set.

**Invalid types:** Multi-line text, File column, columns with field security enabled (on their own).

### SDK Pattern for Alternate-Key Update/Upsert

```csharp
// CORRECT: use Entity(String, KeyAttributeCollection) constructor
var keys = new KeyAttributeCollection();
keys.Add("accountnumber", "AC-1007");
Entity account = new Entity("account", keys);
account["name"] = "Contoso North";
service.Execute(new UpsertRequest { Target = account });
```

**Wrong pattern:** Setting `account["accountnumber"] = "AC-1007"` as a regular attribute does NOT identify the row by alternate key — it just sets the field value.

### Web API Pattern

```
PATCH /api/data/v9.2/accounts(accountnumber='AC-1007')
```

This performs an upsert using the alternate key in the URL.

### Unsupported Characters in Alternate Key Values

If an alternate key column value contains any of: `/ < > * % & : \ ? +`, then Web API and SDK retrieve, update, and upsert operations using that key **will not work**. The key can still enforce uniqueness, but cannot be used in integration API calls.

**Example of failing key value:** `EU/2026/0042` (contains `/`), `EU+44` (contains `+`)

---

## 6. Change Tracking for Incremental Synchronization

### Key Facts

**Change tracking** is the Dataverse feature for efficiently synchronizing data with external systems. It detects what changed since the last successful sync, avoiding expensive full-table comparisons.

### Correct Setup Sequence
1. **Enable "Track changes"** on the table
2. **Send initial request** with `Prefer: odata.track-changes` header
3. **Process returned rows** including deleted-entity entries
4. **Persist the `@odata.deltaLink`** for the next incremental cycle

### Delta Link

The `@odata.deltaLink` is the opaque, service-generated continuation token returned in the response. It must be persisted after each successful cycle to drive the next incremental request.

**Wrong things to persist:** `@odata.context`, `Preference-Applied` header, a specific record ID.

> **Plain English — persist the delta link:** Save the delta link to a database, file, or config store after each successful sync. It acts as a bookmark — next run you read it back and pass it to Dataverse, which then returns only what changed since that point. Without persisting it you have no bookmark and must do a full sync every time.

### Deleted Rows

The delta response includes **deleted-entity entries** that must be processed to keep the external store consistent. Ignoring them causes drift.

> **Plain English:** When someone deletes a record in Dataverse, the delta response includes a notification about that deletion. You must act on it in your external system too — otherwise your external database still has the record and the two systems slowly diverge. Always handle both: normal records (create or update externally) and `@odata.deletedEntity` entries (delete from external system). Always check if the record exists locally before deleting — you may receive a deletion for a record you never saw (phantom delete, explained below).

### Token Expiry

Change tracking tokens have a **default 7-day retention window** (controlled by `ExpireChangeTrackingInDays` organization setting). If a sync is paused longer than this window, the stored token becomes invalid and Dataverse throws an exception. The fix is to **reinitialize the sync baseline** — not retry with the same token.

### Common Distractors
- "Add `$orderby` to change requests" — not part of the change tracking pattern
- "Re-enable Track changes before each run" — only needs to be done once
- "Switch to auditing for deltas" — audit log is not the supported incremental sync mechanism
- "Retry the same delta link" after expiry — won't work; baseline must be reinitialized

---

## 7. Dataverse Event Publishing: Registration Steps

### Two Required Steps (Azure Service Bus / Event Hub)

1. **Register a service endpoint** — defines the Azure target (Service Bus, Event Hub), contract type, and authorization
2. **Register a step** — binds the Dataverse event (message + primary entity table) to the endpoint

No custom plug-in assembly is needed for the out-of-box Azure-aware integration.

### Webhook Step Best Practices
- Use **filtering attributes** to limit firing to relevant column changes (e.g., `firstname,lastname`) — Microsoft prompts for this as a performance best practice
- Use **asynchronous execution** to avoid blocking the user's save and to allow failures to be reviewed in System Jobs
- Synchronous webhook steps surface endpoint failures directly to the user

---

## 8. Recommended Integration Pattern (Full Lifecycle)

For a robust integration between an external system and Dataverse:

1. Define an **alternate key** on the business identifier column
2. Use **UpsertRequest** (SDK) or **PATCH by alternate key URL** (Web API) for inbound writes
3. Enable **change tracking** on the table for outbound deltas
4. Persist the **`@odata.deltaLink`** after each cycle
5. Handle **deleted-entity entries** in delta responses
6. Handle **429 (throttling)** responses with Retry-After backoff

---

## Quick-Fire Facts

- **Queue contract** = listener does NOT need to be actively running; messages are held until consumed
- **Topic contract** = multiple subscribers can receive the same event (fan-out)
- **Event Hub contract** = SAS auth only; XML or JSON body; used for high-throughput streaming
- **WebhookKey** = specifically for Azure Functions `?code=` pattern
- **Webhook response body** is never parsed by Dataverse; only HTTP status code matters
- **Synchronous plug-in** is the only option that can block a save and show the user an error
- **IServiceEndpointNotificationService** returns null on synchronous steps — must be async + sandbox
- **EntityReference** in Azure-aware plug-in must use logical name `"serviceendpoint"` not a table name
- **Azure-aware plug-in** should contain no business logic beyond publishing — retries replay entire plug-in
- **UpsertResponse.RecordCreated** = true if row was created, false if updated
- **Alternate key column types**: single line text, whole number, decimal, date/time, lookup, option set
- **Unsupported alt-key characters**: `/ < > * % & : \ ? +` — breaks Web API and SDK key-based operations
- **Change tracking token** expires after 7 days (default) — expired token requires baseline reinit, not retry
- **@odata.deltaLink** is the value to persist for incremental sync; not `@odata.context`
- Power Automate "When an action is performed" trigger = low-code asynchronous Dataverse event listener
- Service endpoint step registration requires both: (1) endpoint + (2) step for message/table binding
- Webhook supports sync and async steps; Azure Service Bus supports asynchronous steps only

---

## Common Traps

1. **One-way vs Queue confusion:** One-way sounds "simpler" but requires an active listener and will retry/fail when listener is offline. Queue is the durable choice.

2. **Wrong EntityReference name in Azure-aware plug-in:** Using the business table name (e.g., `"account"`) instead of `"serviceendpoint"` will fail silently or throw an error.

3. **Setting alternate key as a regular attribute:** `entity["accountnumber"] = "X"` sets the field value but does NOT identify the row by alternate key for update/upsert — must use `Entity(String, KeyAttributeCollection)` constructor.

4. **Expecting webhook response body to drive behavior:** Dataverse ignores the response body entirely. A 200 status = success; any returned JSON has no effect on the Dataverse transaction.

5. **Adding business logic to Azure-aware plug-ins:** Because async plug-in retries replay the entire execute method, any extra side effects will run multiple times during Service Bus outages.

6. **Notification service on synchronous steps:** `IServiceEndpointNotificationService` is null for synchronous plug-ins — always register as async + sandbox.

7. **Alternate key characters in API calls:** A key column might uniquely identify rows in Dataverse but still break integration if the values contain `/`, `+`, or other unsupported characters.

8. **Reinitializing vs retrying an expired delta token:** You cannot extend or retry an expired change tracking token — you must restart the baseline sync.

9. **Event Hub auth:** Only SAS is supported for Event Hub service endpoint registrations — OAuth or other modes are not valid here.

10. **Topic vs Queue for fan-out:** A queue delivers each message to one consumer. Only a topic supports multiple independent subscribers receiving the same event.

---

## Deeper Exam Detail

This section adds depth, SDK specifics, current product behavior, limits, and edge-case decision rules. All claims are sourced from Microsoft Learn unless marked "(unverified)".

---

### A. Azure Service Bus: fuller contract details and runtime behavior

#### Two-way and REST contracts: return value handling
The **Two-way** contract allows a **string value** to be returned from the listener to the Dataverse plug-in or custom workflow activity that initiated the post. The `IServiceEndpointNotificationService.Execute()` call returns this string. The **REST contract** behaves identically to two-way but targets a REST endpoint instead of a WCF relay. Neither two-way nor REST can replace Queue for durability — both still require an active listener. [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/azure-integration]

> **Plain English — Why IServiceEndpointNotificationService appears here:** This interface is not exclusive to Service Bus. It is the single interface Dataverse uses to send events to ANY registered service endpoint — Service Bus, webhooks, relay contracts. It is a generic "send this event to an external endpoint" interface. The contract type (Queue, Two-way, REST, Webhook) determines where the message goes and whether a response comes back.
>
> **What Two-way/REST can actually do:** The string response is returned to YOUR plug-in code. The external listener cannot directly control Dataverse — it just returns a string. Your plug-in then interprets that string and decides what to do: call `orgService.Update()` to write a field, call `orgService.Create()` to create a record, or throw `InvalidPluginExecutionException` to cancel the save and show an error to the user. The plug-in has full access to Dataverse via `IOrganizationService` and can perform any CRUD operation based on the response. If the step is synchronous, all of this runs inside the same transaction.

#### What if... decision rules for contract selection

| Scenario | Correct contract | Why |
|---|---|---|
| Listener is sometimes offline | Queue | Brokered; no active listener needed |
| Need a response string back to the plug-in | Two-way or REST | Only contracts that return a value |
| Multiple independent downstream processors | Topic | Fan-out; queue delivers to one consumer only |
| Sub-second analytics ingestion at scale | Event Hub | Designed for streaming; SAS auth only |
| Simple relay, listener always online | One-way | Relay contract; lowest overhead |

#### Authorization: SAS is the only supported model
All Dataverse-to-Azure-Service-Bus integrations use **Shared Access Signatures (SAS)** for authorization. The claim posted by Dataverse is signed by the `AppFabricIssuer` certificate in the Dataverse configuration database. OAuth or Managed Identity are not supported directly through the Plug-in Registration Tool service endpoint model (as of 2026). [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/azure-integration]

#### Data context type difference: IPluginExecutionContext vs RemoteExecutionContext
Inside the Dataverse event pipeline the context is `IPluginExecutionContext`. When posted to the Azure Service Bus it is serialized as `RemoteExecutionContext`. The `RemoteExecutionContext` can be formatted as **.NET binary** (default), **XML**, or **JSON**, enabling non-.NET consumers to deserialize it. [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/azure-integration]

#### Synchronous step caveat for service endpoints
It is technically possible to register a service endpoint step as **synchronous**. When a synchronous step posts to Azure Service Bus and an error occurs after the request is sent, the **Dataverse data operation rolls back** but the message already sent to Azure **cannot be recalled**. This creates a potential data inconsistency. Microsoft therefore recommends registering service endpoint steps as **asynchronous** for best system performance. [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/work-data-azure-solution]

---

### B. Webhooks: deeper behavior, limits, and edge cases

#### Authentication option mechanics

| Type | How Dataverse sends it | Example |
|---|---|---|
| `HttpHeader` | As one or more key-value pairs in the HTTP request header | `Key1: Value1` |
| `WebhookKey` | As `?code=<value>` query string appended to the URL | `?code=00000000-0000-0000-0000-000000000001` |
| `HttpQueryString` | As arbitrary key-value query string pairs | `?Key1=Value1&Key2=Value2` |

Only enter **the value** (not `code=`) when registering `WebhookKey` in the Plug-in Registration Tool — the tool adds the `code=` prefix automatically. [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/register-web-hook]

> **HttpHeader vs HttpQueryString — security difference:** Both send a secret key, but in different locations. `HttpHeader` puts the secret in the request header (not visible in the URL, not logged by default — more secure). `HttpQueryString` puts it in the URL itself (`?mykey=secret`) — URLs are commonly logged by web servers, proxies, and browsers, so the secret ends up in plain-text logs. `WebhookKey` is just a fixed-format version of `HttpQueryString` where the key name is always `code`.

#### What if... webhook vs Service Bus decision

| Condition | Use webhook | Use Service Bus |
|---|---|---|
| External app is a simple HTTP endpoint | Yes | No |
| Need durability when endpoint is down | No | Yes (Queue) |
| Volumes may exceed endpoint throughput | No | Yes (Service Bus acts as a buffer — messages queue up and your consumer reads at its own pace; webhook fires directly at your endpoint with no buffer, so a burst of events can overwhelm it) |
| Need fan-out to multiple consumers | No | Yes (Topic) |
| Need sync step that can return data | No (body ignored) | Yes (Two-way/REST) |
| Endpoint is an Azure Function with `?code=` key | Yes (WebhookKey) | No |

---

### C. UpsertRequest and alternate keys: SDK internals and edge cases

#### Server-side Upsert processing logic (standard tables)
The server resolves the upsert in this exact order:
1. If `Entity.Id` is set, look up by primary key first; otherwise use `Entity.KeyAttributes`.
2. **Record found:** Strip the alternate key data from `Entity.Attributes` (you cannot change the key values through the same keys used to identify the row), call `Update`, set `UpsertResponse.RecordCreated = false`.
3. **Record not found:** Copy key data into `Entity.Attributes` if absent, call `Create`, set `UpsertResponse.RecordCreated = true`.

Key implication: **You cannot update alternate key column values** by including them both as the lookup key and in the body. To change an alternate key value, identify the record by primary key (or a different alternate key) and then update the column directly. [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-upsert-insert-update-record]

> **Plain English:** You cannot use the same alternate key to both FIND the record and CHANGE that key's value at the same time. If you use `erp_customerid = CUST-1001` to identify the record and also include `erp_customerid = CUST-9999` in the body, Dataverse strips the key from the body before updating — your change to `CUST-9999` is silently ignored. To actually change an alternate key value, identify the record by its GUID (primary key) instead, then update the column directly.

#### Elastic table upsert differs from standard tables
For **elastic tables**, `Upsert` does not fire separate `Create` or `Update` events — it directly overwrites the record. Business logic registered on `Create` or `Update` messages will **not fire** when `Upsert` is used on elastic tables. You must also register your logic on the `Upsert` message if you need consistent behavior. [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-upsert-insert-update-record]

> **Plain English — why elastic tables skip Create/Update:** Standard tables store data in SQL Server, where Upsert internally resolves to a Create or Update call — so those events fire normally. Elastic tables store data in Azure Cosmos DB, which has a native "just write this document" operation that bypasses the Create/Update event chain entirely. Whether the record exists or not, Cosmos DB just writes directly — no Create event, no Update event, regardless. This is by design for performance. The fix is to also register your plugin on the `Upsert` message so it runs regardless of which write path was used.

#### Performance note
Microsoft explicitly states there is a **performance penalty** when using `Upsert` vs `Create` because `Upsert` requires an existence check. If you know the record does not exist, prefer `Create` for performance-sensitive batch loads. [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-upsert-insert-update-record]

#### Web API: distinguishing create vs update in the response
A plain Web API `PATCH` (upsert) always returns **`204 No Content`** regardless of whether the record was created or updated. To distinguish the two, add the `Prefer: return=representation` header: the response will then be **`201 Created`** for a new record or **`200 OK`** for an update. Note that this adds an extra server-side `Retrieve` operation and has a performance cost. [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-upsert-insert-update-record]

#### Blocking update (no create): `If-Match: *`
Adding `If-Match: *` to a Web API `PATCH` converts it from upsert to a pure **update** — it returns `404 Not Found` if no matching record exists. Conversely, `If-None-Match: *` blocks the update path: the request succeeds only if the record does **not** yet exist (create-only). [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-upsert-insert-update-record]

#### What if... body key values conflict with URL key values on create
On a Web API upsert where the record does not exist, if the request body contains alternate key fields with **different values** than those in the URL, the server uses the **body values** to create the record — not the URL values. To avoid this ambiguity, Microsoft's guidance is to **omit alternate key columns from the request body** entirely; let the server copy them from the URL. [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-upsert-insert-update-record]

> **Simple rule:** Put the alternate key in the URL only. Never repeat it in the body. If you do repeat it with a different value on a create, the body value wins — which is confusing and unpredictable. Omit it from the body entirely and let Dataverse copy it from the URL automatically.

---

### D. Change tracking: SDK path, constraints, and ordering guarantees

#### .NET SDK: RetrieveEntityChangesRequest
The SDK equivalent of the Web API delta query is `RetrieveEntityChangesRequest`. Key fields:
- `EntityName` — logical name of the table
- `Columns` — `ColumnSet` of columns to return
- `PageInfo` — paging with `Count` (max page size), `PageNumber`, `PagingCookie`
- `DataVersion` — the version token from the previous response (omit on first run)

On the first call (no token), **all records are returned as new** and **deleted records are not included**. Store the `response.EntityChanges.DataToken` to use on subsequent calls. [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-change-tracking-synchronize-data-external-systems]

#### Unsupported query options with change tracking
When the `Prefer: odata.track-changes` header is present in a Web API request, the following query options are **not supported** and return an error if included: `$filter`, `$orderby`, `$expand`, `$top`. Use `$select` to limit columns and paging parameters to page through results. [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-change-tracking-synchronize-data-external-systems]

> **Why $select is allowed but $filter is not:** `$select` controls which COLUMNS come back — it only trims the data shape, it does not affect which rows are returned. Change tracking integrity is not affected. `$filter` controls which ROWS come back — it would silently skip changed records that don't match the filter, meaning your delta link would advance past those records and they would be lost forever. Change tracking must return every changed row to guarantee completeness. `$select` is safe; `$filter` breaks the guarantee.

#### Record ordering in delta responses
The server returns records in a defined order: **new or updated records first** (sorted by version number), then **deleted records**. For a page size of 5,000, if there are 3,000 created/updated and 2,000 deleted, you receive all 5,000 in one response — updated records in positions 1–3,000 and deleted records in positions 3,001–5,000. If the new/updated count exceeds 5,000 you must page through that subset before deleted records appear. [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-change-tracking-synchronize-data-external-systems]

#### Access requirement
The calling user must have **organization-level read access** to the table. Partial read access (e.g., business unit scope) causes a privilege check error on `RetrieveEntityChanges`. [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-change-tracking-synchronize-data-external-systems]

> **Plain English:** Dataverse has four read access levels: User (own records only), Business Unit (own BU), Parent-Child Business Unit (own BU + child BUs), and Organization (all records). Change tracking requires Organization level because it tracks changes across the entire table — it has no concept of BU boundaries. Even Business Unit access is not enough. Your integration service account must have org-level read on the synced table, or the call fails with a privilege error.

#### Phantom deletes
If a record is created and then deleted **between two delta queries**, the client will see a **deleted-entity entry** in the next delta response even though it never saw the created record. Integration code must handle deletes for records it has no local copy of without throwing an error. [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-change-tracking-synchronize-data-external-systems]

> **Plain English:** A record can be created and deleted in Dataverse between your two syncs. Your next delta response includes a deletion notification for a GUID you have never seen. If your code does `localRecord.Delete()` without checking first, it crashes with a null reference. Always check: `if (localRecord == null) return;` — skip gracefully if not found locally.

#### Cannot disable change tracking once enabled
Once `EntityMetadata.ChangeTrackingEnabled` is set to `true` on a table, **it cannot be disabled**. Plan table configuration accordingly. To check programmatically whether a table supports enabling change tracking, read `EntityMetadata.CanChangeTrackingBeEnabled`. [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-change-tracking-synchronize-data-external-systems]

#### Checking whether change tracking is enabled via Web API metadata
```http
GET [Organization URI]/api/data/v9.2/EntityDefinitions?$select=SchemaName&$filter=ChangeTrackingEnabled eq true
```
The `$metadata` document also exposes the `Org.OData.Capabilities.V1.ChangeTracking` annotation for entity sets that have it enabled. [https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-change-tracking-synchronize-data-external-systems]

---

### E. Power Automate Dataverse connector: trigger depth and integration patterns

#### "When a row is added, modified, or deleted" trigger — full option set

**Change type (trigger condition):** `Added`, `Modified`, `Deleted`, or `Added or Modified or Deleted`. The SDK message name is available at runtime via `triggerOutputs()['body/SdkMessage']` returning `Create`, `Update`, or `Delete`. [https://learn.microsoft.com/en-us/power-automate/dataverse/create-update-delete-trigger]

**Scope options:**

| Scope | What it monitors |
|---|---|
| User | Rows owned by the flow-running user only |
| Business Unit | Rows owned by anyone in the user's business unit |
| Parent: Child business unit | Rows owned by the user's BU or any child BU |
| Organization | All rows in the environment regardless of owner |

[https://learn.microsoft.com/en-us/power-automate/dataverse/create-update-delete-trigger]

**Select columns (filtering attributes) — critical limits:**
- Applies **only to the Update (Modified) change type**; Create and Delete always fire for all columns.
- Accepts a **comma-separated list of logical column names**.
- **Lookup columns are not supported** — if you include a lookup column, changes to that column will not trigger the flow.
- Supported scalar types: text, number, date/time, choice.
- Not supported on virtual tables.
- The flow still runs if the column value submitted in the update is **unchanged** from the existing value (the filter is based on which columns are included in the request, not whether the value actually changed).

> **Plain English:** This lets you say "only trigger my flow when these specific columns are updated." Without it, every update to a record fires the flow regardless of what changed. Key trap: it only works for Updates — Create and Delete always fire. Lookup columns are silently ignored (no error). Most importantly, the filter checks whether the column was *included in the update request*, not whether the value actually changed — so if someone sends an update with `revenue = 500000` and revenue was already 500000, the flow still fires.

[https://learn.microsoft.com/en-us/power-automate/dataverse/create-update-delete-trigger]

**Filter rows (OData expression):**
- Written in OData style but **must not include the `$filter=` prefix** (that prefix is for direct API calls only).
- The expression is evaluated **after** the row change is saved; the flow runs only when the expression evaluates to `true`.
- Can be combined with Select columns: both conditions must be true for the flow to fire.
- Example: `firstname eq 'John'` or `contains(firstname,'John')`.

[https://learn.microsoft.com/en-us/power-automate/dataverse/create-update-delete-trigger]

**"Delay until" advanced option:**
An OData-style UTC timestamp that delays the flow trigger. Unlike the standard Power Automate `Delay until` action, the Dataverse trigger-level `Delay until` **never expires**, making it suitable for very long delays without the flow timing out. [https://learn.microsoft.com/en-us/power-automate/dataverse/create-update-delete-trigger]

> **Plain English:** The flow triggers when the record changes, but waits until the specified timestamp before actually running. Like setting an alarm — the alarm is set now but only rings later. Real-world use: a hotel booking is created today, but you want to send a reminder email 24 hours before check-in (weeks away). Set Delay Until to the day before check-in. The trigger-level version never expires, so it's safe for delays of weeks or months unlike the in-flow Delay Until action.

**Run As (user impersonation):**
Three options: `Flow owner`, `Row owner` (owner of the changed row; defaults to flow owner if a team owns the row), or `Modifying user` (the user who triggered the change). Requires the `prvActOnBehalfOfAnotherUser` privilege. The **Delegate** security role includes this privilege by default. [https://learn.microsoft.com/en-us/power-automate/dataverse/create-update-delete-trigger]

**Relationship type limitation:**
The trigger does **not** fire for changes on relationship records of type **1:N or N:N**. [https://learn.microsoft.com/en-us/power-automate/dataverse/create-update-delete-trigger]

#### "When an action is performed" trigger
This trigger fires when a Dataverse **custom process action** (or custom API) executes successfully. The action must belong to a **Catalog and Category** (the connector's organization mechanism) and the flow owner must have read access to the relevant `sdkmessage`, `customapi`, or `workflows` tables.

Input/output parameters from the action are exposed as **dynamic content** in the flow with the naming scheme `ActionInputs_<ParameterName>` and `ActionOutputs_<ParameterName>`. For complex types (entity objects) the last segment is the column logical name, e.g., `ActionInputs_account_donotfax`. [https://learn.microsoft.com/en-us/power-automate/dataverse/action-trigger]

#### Prerequisites for the row-change trigger
The flow creator must have **user-level Create, Read, Write, and Delete** permissions on the **Callback Registration** table in Dataverse. This is the underlying mechanism the connector uses to register the trigger. [https://learn.microsoft.com/en-us/power-automate/dataverse/create-update-delete-trigger]

#### What if... multiple rapid updates to the same row
Power Automate **evaluates the trigger independently for each update event**, even when the updated values are the same as before. A burst of five rapid updates to one row can result in **five separate flow runs**. Use Filter rows and/or Select columns to minimize unnecessary executions, and consider idempotent flow logic. [https://learn.microsoft.com/en-us/power-automate/dataverse/create-update-delete-trigger]

> **Plain English — idempotent flow logic:** Make your flow safe to run multiple times with the same result as running once. Instead of "create a task," do "create a task only if one doesn't already exist." Instead of "send a welcome email," do "send a welcome email only if WelcomeEmailSent is false, then set it to true." The pattern is always: (1) check if work is already done, (2) if yes skip, (3) if no do the work and mark it done. This way 5 flow runs produce the same outcome as 1 run.

#### Scaling comparison: webhook vs Power Automate vs Service Bus

| Factor | Webhook | Power Automate cloud flow | Azure Service Bus |
|---|---|---|---|
| Scale ceiling | Endpoint throughput | Power Automate throttling limits | Very high (enterprise bus) |
| Sync capable | Yes (can run inside Dataverse transaction, block the save, rollback on failure) | No (always async, never inside the transaction) | No (always async, never inside the transaction) |
| Durability | None (no retry queue) | Limited (run history, re-submit) | High (Queue/Topic) |
| Code required | Endpoint code only | Low-code / no-code | Listener code required |
| Response body returned | No (status code only) | No (outbound notification only) | Two-way/REST only |

[https://learn.microsoft.com/en-us/power-apps/developer/data-platform/use-webhooks] [https://learn.microsoft.com/en-us/power-automate/dataverse/create-update-delete-trigger]
