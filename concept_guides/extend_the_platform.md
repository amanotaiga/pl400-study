# PL-400 Extend the Platform — Concept Study Guide

> Synthesized from 189 exam questions. Domain weight: 30–35%.

---

## 1. Plug-in Execution Pipeline

### Pipeline Stages

| Stage | Stage Code | Transaction? | Key Use |
|---|---|---|---|
| PreValidation | 10 | Outside (before tx) | Early rejection; reject here to avoid rollback cost |
| PreOperation | 20 | Inside | Mutate incoming entity values before write |
| Main Operation | — | Inside | Core Dataverse operation |
| PostOperation (sync) | 40 | Inside | Post-save logic that must stay in transaction |
| PostOperation (async) | 40 | Outside | Non-blocking, non-critical work |

**Decision rule — which stage to register:**
- **Must reject the operation** → PreValidation. Microsoft says throw `InvalidPluginExecutionException` preferably in PreValidation; cancellation here avoids database rollback.
- **Must change incoming column values** → PreOperation. Microsoft explicitly recommends mutating `InputParameters["Target"]` in PreOperation; changes participate in the same save request without triggering a second Update event.
- **Must not trigger a second Update** → Do NOT update the entity in PostOperation; that fires a new Update pipeline.
- **Work does not need to block the user** → Async PostOperation. External service calls, fraud scoring, scoring APIs — move them async when the score is not needed before the save completes.

**Common distractor:** PreOperation looks "earlier" than PostOperation so developers put validation there. Wrong — PreValidation exits the transaction entirely, reducing rollback cost.

### Plug-in Class Design (IPlugin)

- **Stateless class is mandatory.** Never store per-invocation state in member fields or properties (e.g., `private IOrganizationService service`). The platform caches and reuses plug-in instances. Member fields cause thread-safety and data-consistency bugs under load.
- All invocation-specific data must live in local variables inside `Execute`.
- Avoid `ExecuteMultipleRequest` / `ExecuteTransactionRequest` inside a plug-in. Microsoft says these batch types are for client-side latency reduction; they add complexity and blocking inside the synchronous pipeline.

### Execution Context — Key Members

| Member | Purpose |
|---|---|
| `InputParameters` | Request payload that triggered the event (e.g., `Target` entity) |
| `OutputParameters` | Response values to return to the caller |
| `SharedVariables` | Pass values from one pipeline step to a later step (PreOp → PostOp) |
| `PreEntityImages` | Snapshot of row before main operation (registered by alias) |
| `PostEntityImages` | Snapshot of row after main operation (registered by alias) |
| `CorrelationId` | Trace correlation (read-only; do not persist across executions) |
| `ParentContext` | Execution context of the parent operation (not for passing data) |

**SharedVariables vs. OutputParameters:** SharedVariables passes data *within* the pipeline to later steps. OutputParameters returns values *to the caller* of the message.

### Service Factory — Identity Choice Inside Plug-ins

| Value | Resulting identity |
|---|---|
| `Guid.Empty` | Same user as `context.UserId` (follows step impersonation setting) |
| `null` | SYSTEM account |
| `context.InitiatingUserId` | User who originally triggered the action |

Use `Guid.Empty` as the default when the plug-in should run as the current execution user.

### Step Impersonation (Run in User's Context)

When calling users lack privileges needed by plug-in operations (e.g., creating a follow-up task), change the step's **Run in User's Context** setting to a user with sufficient rights rather than broadening everyone's security role.

---

## 2. Entity Images

### Availability by Stage and Message

| Message | Stage | Pre Image | Post Image |
|---|---|---|---|
| Create | PostOperation | No | Yes |
| Update | PreOperation | Yes | No |
| Update | PostOperation | Yes | Yes |
| Delete | PreOperation | Yes | No |
| Delete | PostOperation | Yes | No |

**Key rules:**
- A Pre Image on a Create step does not exist (no prior row). This is a common wrong answer.
- A Post Image on Delete does not exist (row is gone).
- To compare old vs. new values after an Update → PostOperation with both Pre and Post Images.
- To mutate values before save without an extra retrieve → PreOperation + Pre Image for old values.

**Performance rule:** Register only the specific columns needed in each image. Microsoft warns that accepting the default "all columns" setting negatively affects performance.

**Access pattern:** Use the alias string defined at registration time as the key:
```csharp
var before = context.PreEntityImages["myAlias"];
```

---

## 3. Filtering Attributes & Execution Order

- **Filtering attributes** on an Update step limit execution to requests that include those specific columns. Without filtering, the plug-in fires on every update — even when users change unrelated fields.
- **Do not include the primary key** (`accountid`, etc.) in filtering attributes. The primary key is always present in Update requests, so including it defeats filtering.
- **Execution Order** determines sequence within a stage for multiple steps on the same message/table. If two steps share the same execution order value, the order is non-deterministic and can vary between environments. Always assign distinct values.

### Plug-in Registration Sequence

Correct order in Plug-in Registration Tool:
1. Register the assembly
2. Register the step (message, entity, stage, mode)
3. Configure step details (filtering attributes, images)
4. Add assembly to unmanaged solution
5. Add step to unmanaged solution

---

## 4. Custom APIs

### Design Properties

| Property | Options | Notes |
|---|---|---|
| Binding Type | Global, Entity, EntityCollection | Cannot be changed after save |
| Is Function | Yes / No | Functions = HTTP GET, read-only, no side effects; Actions = side effects |
| AllowedCustomProcessingStepType | None, Async Only, Sync and Async | Controls whether others can register additional steps |
| Execute Privilege Name | Optional privilege | Restricts who can invoke the API |
| Is Private | Yes / No | Hides from Web API `$metadata` and code-generation discovery |
| WorkflowSdkStepEnabled | Yes / No | Enables use as a workflow action |

**Immutable after save:** Binding Type, BoundEntityLogicalName, IsFunction. If wrong, delete and recreate.

### AllowedCustomProcessingStepType Decision Table

| Goal | Setting |
|---|---|
| Only the main plug-in runs — no extensions by others | **None** |
| Expose as business event; allow async subscriber steps | **Async Only** |
| Fully open, like standard Dataverse messages | **Sync and Async** |

### Custom API as Workflow Action — Constraints

For `WorkflowSdkStepEnabled = true`:
- **Is Function must be false** (actions only).
- Supported request/response property types are limited to a specific list (EntityReference, String, Integer, etc.).
- EntityCollection and StringArray are NOT supported.
- EntityReference is valid only when the API is entity-bound.

### Custom API — Plug-in Wiring

- Set the **Plug-in Type** field on the custom API to associate the registered class as the main operation.
- If Plug-in Type is empty, invocation succeeds but no logic runs.
- **Workaround for profiler debugging and secure configuration:** Register the plug-in type on the **PostOperation stage** of the custom API message instead of directly on the main-operation field. This enables Plug-in Profiler and secure/unsecure configuration.

### InputParameters / OutputParameters for Custom APIs

- Request parameter values → read from `context.InputParameters["paramName"]`
- Response property values → write to `context.OutputParameters["propName"]`

Common mistake: writing the response value back to `InputParameters`.

---

## 5. Business Events & Catalog

### Hierarchy

`Catalog (root)` → `Catalog Category` → `CatalogAssignment (links API/table to category)`

Steps to expose an action as a business event:
1. Create root Catalog
2. Create Category under the catalog
3. Create **CatalogAssignment** linking the custom API or table to the category

**CatalogAssignment** is the missing piece developers often forget after building the hierarchy.

### User-Owned Tables

When a user-owned table is cataloged, Dataverse automatically exposes its security operations (GrantAccess, ModifyAccess, RevokeAccess) as business events — no synchronous plug-in detection layer needed.

### Trigger in Power Automate

Business events appear in the Dataverse **"When an action is performed"** trigger — not in "When a row is added, modified or deleted."

### Why an Action Doesn't Appear in the Trigger

1. **Is Function = Yes** → must be an Action (Is Function = No) for Power Automate connector discoverability.
2. Missing CatalogAssignment.
3. User lacks read access to Custom API, Process, and SDK Message tables.

---

## 6. Web API / OData

### Core Patterns

| Goal | Approach |
|---|---|
| Read-only query, optimize columns | `GET` with `$select` |
| Create new row | `POST` to entity set |
| Update specific columns | `PATCH` (sparse) |
| Upsert — create or update | `PATCH` without conditional headers |
| Update-only (fail if missing) | `PATCH` with `If-Match: *` → 404 if missing |
| Create-only (fail if exists) | `POST` with `If-None-Match: *` → 412 if exists |
| Optimistic concurrency check | `PATCH` with `If-Match: W/"etag"` → 412 if changed |

**Always use `$select`**. Omitting `$select` returns all columns — Microsoft explicitly flags `ColumnSet(true)` / no `$select` as a performance anti-pattern.

### Batch Requests

- **`$batch` change set** = multiple operations, single HTTP call, **atomic transaction** for standard tables.
- Elastic tables do **not** support transactions via change sets or `ExecuteTransactionRequest`. Do not assume atomicity on elastic tables.

### SDK Equivalent

- **`ExecuteTransactionRequest`** = SDK equivalent of a `$batch` change set (ordered, atomic).
- **`CreateMultipleRequest` / `UpdateMultipleRequest`** = bulk inserts/updates of the same table type (preferred for large volumes over same table).
- **`UpsertRequest`** = create-or-update without a prior existence check; costs more than `Create` when you know the row is new.
- **`RetrieveMultiple` + paging cookie** = large result set pagination.

### Service Protection Limits & Retry

| Client Type | Retry Mechanism |
|---|---|
| Web API (custom code) | Read `Retry-After` header from 429 response; wait, then retry |
| .NET SDK | `ServiceClient` / `CrmServiceClient` automatically pause and resend after Retry-After |
| Interactive apps | Show "server busy" state; do not allow repeated user submissions while retrying |
| Bulk non-interactive | Start with lower parallelism; gradually increase; honor recommended DOP |

**Never** immediately resubmit on 429. **Never** assume batching bypasses service protection limits.

### Authentication

| Scenario | Approach |
|---|---|
| OAuth Web API from .NET | Bearer token in `Authorization` header |
| App-only / scheduled / non-interactive | Client credentials flow (`/.default` scope, not `user_impersonation`) |
| Delegated user access | Authorization code flow; grant `Access Dynamics 365` delegated permission; app registered in Entra ID |
| JavaScript SPA | MSAL.js + Dataverse CORS |
| Azure Function (managed identity) | `ManagedIdentityCredential` with `/.default` scope; create Dataverse application user with roles |

**Common mistake:** Using `user_impersonation` scope for app-only (managed identity) calls. Correct scope is `<env-url>/.default`.

### Managed Identity for Azure Functions → Dataverse

Two required actions:
1. **Enable managed identity** on the Function App (user-assigned preferred when shared across multiple functions or when Function App may be recreated).
2. **Create Dataverse application user** for that identity and assign security roles.

**User-assigned vs. system-assigned identity:**
- System-assigned: tied to the app instance; deleted when app is deleted.
- User-assigned: standalone resource; survives app deletion; can be shared across multiple Function Apps.

When multiple user-assigned identities are attached, use `ManagedIdentityCredential` with an explicit `clientId` (not `DefaultAzureCredential`) for deterministic production auth.

---

## 7. Custom Connectors

### Creation Starting Points

| Source | When to use |
|---|---|
| OpenAPI 2.0 file import | Existing API contract in a file |
| GitHub OpenAPI import | Contract stored in GitHub repository |
| Azure service import | API already in Azure (APIM, Functions) |
| Blank wizard | No existing definition |

**Important:** Custom connectors require **OpenAPI 2.0 (Swagger)** format. OpenAPI 3.0 is NOT supported for import. Convert first.

### OpenAPI Extensions for Connector Usability

| Extension | Scope | Purpose |
|---|---|---|
| `summary` | Operation | User-facing title for an operation |
| `x-ms-summary` | Parameter, response schema field | User-facing title for a field/parameter |
| `description` | Operation, parameter | Detailed explanatory text (not the display title) |
| `x-ms-visibility` | Operation, parameter | `important`, `advanced`, `internal` (hide from UI) |
| `x-ms-dynamic-values` | Parameter | Populate a dropdown from another operation |
| `x-ms-dynamic-list` | Parameter | Required alongside `x-ms-dynamic-values` for ambiguous references or property references within parameters |
| `x-ms-dynamic-schema` | Parameter/response | Discover schema dynamically |
| `x-ms-dynamic-properties` | Parameter/response | Required alongside `x-ms-dynamic-schema` for ambiguous references |
| `x-ms-url-encoding` | Path parameter | Control single vs. double URL encoding |
| `x-ms-trigger` | Operation | Marks operation as a connector trigger |
| `x-ms-notification-url` | Parameter | Webhook callback URL |
| `x-ms-notification-content` | Response | Webhook response schema |

**Rule for `x-ms-visibility: internal` + `required: true`:** Must also provide a `default` value, otherwise the parameter has no usable value source.

**Rule for dynamic extensions on body parameters:** Dynamic extensions (`x-ms-dynamic-values`, etc.) must be placed in the **body schema**, not on the body parameter wrapper itself.

### Authentication Types

| Type | Use case |
|---|---|
| No authentication | Public APIs |
| API key | Static shared key; configure parameter **location** (Header vs. Query) to match backend expectation |
| Basic authentication | Username + password |
| OAuth 2.0 | Per-user delegated access; requires Authorization URL + Token URL at minimum |

**OAuth 2.0 Limitations:**
- **Client credentials grant type is NOT supported** in custom connectors. Unattended/app-only OAuth patterns cannot use standard custom connectors.
- For generic OAuth 2.0: both **Authorization URL** and **Token URL** are required. Refresh URL is for token renewal, not the initial flow.
- Common OAuth failure after ~60 min → check **Refresh URL** configuration.
- Redirect URI mismatch after sign-in redirect → register the connector's redirect URI in the Entra app registration.

**Multi-auth (Basic + API Key in same connector):** The wizard does not support multiple auth types. Use the **Connectors CLI** and define `connectionParameterSets` in `apiProperties.json`.

### Policy Templates

| Template | Use |
|---|---|
| Set HTTP Header | Inject or override a request or response header |
| Set Query String Parameter | Add/update a query parameter at runtime |
| Set Host URL | Replace the backend host (for region-based routing) |
| Route Request | Redirect to a different relative path on the same service |

**Section matters:** Run policy on **Request** to affect the outbound call. Running on **Response** or **Failure** is too late to change the request.

**Route Request vs. Set Host URL:** Route Request is for same-service path changes. Changing from `api.contoso.com` to `eu.api.contoso.com` is a **host** change → use Set Host URL.

### Custom Code in Connectors

- Only **one script file** per connector is allowed.
- Custom code takes precedence over the codeless definition.
- Use **`this.Context.SendAsync()`** instead of creating your own `HttpClient`.
- Branch on **`Context.OperationId`** to apply different logic per action in a single script.
- **Custom code cannot be used with the on-premises data gateway.**
- Custom code can scope to specific operations; unselected operations remain codeless.

### Custom Code for Data Transformation

The exam skill "Develop code for a custom connector to transform data" tests whether you can write a C# script that modifies the request sent to the backend or the response returned to the caller.

**Script structure:**

```csharp
public class Script : ScriptBase
{
    public override async Task<HttpResponseMessage> ExecuteAsync()
    {
        // Branch on operation to apply different logic
        if (Context.OperationId == "GetItems")
        {
            // Transform the REQUEST before sending to the backend
            var requestContent = await Context.Request.Content.ReadAsStringAsync();
            var requestBody = JObject.Parse(requestContent);
            requestBody["extraField"] = "injected";
            Context.Request.Content = CreateJsonContent(requestBody.ToString());
        }

        // Send the (possibly modified) request
        var response = await Context.SendAsync(Context.Request, CancellationToken);

        if (Context.OperationId == "GetItems" && response.IsSuccessStatusCode)
        {
            // Transform the RESPONSE before returning to Power Automate / Power Apps
            var responseContent = await response.Content.ReadAsStringAsync();
            var responseBody = JObject.Parse(responseContent);
            responseBody["transformedField"] = responseBody["originalField"];
            responseBody.Remove("originalField");
            response.Content = CreateJsonContent(responseBody.ToString());
        }

        return response;
    }
}
```

**Key rules:**
- Use `Context.SendAsync(Context.Request, CancellationToken)` — **never** create your own `HttpClient`.
- Branch on `Context.OperationId` to apply per-action logic in a single script file.
- `CreateJsonContent(string)` is the helper for setting JSON response/request bodies.
- Modify `Context.Request.Content` to transform the outbound request; modify the returned `response.Content` to transform the response.
- **Only one script file per connector**; it handles all operations.
- **Cannot be combined with on-premises data gateway** — custom code requires cloud endpoints.

**Common transformation scenarios the exam may test:**

| Scenario | Approach |
|---|---|
| Backend returns a flat array but Power Automate needs a wrapper object | Parse response JSON, wrap array in `{"items": [...]}`, replace response content |
| Request must include a computed field the caller doesn't provide | Intercept request, compute value from other params, inject before `SendAsync` |
| Backend returns camelCase but connector schema uses PascalCase | Parse response, remap property names, return modified JSON |
| Different operations need different auth headers | Branch on `OperationId`, set `Context.Request.Headers` per branch |

### CORS for APIM-backed Connectors

Browser-based Power Platform clients require:
1. Enable **APIM CORS policy** to allow the Power Platform origin.
2. Set an **Origin header policy** in the connector so the request carries a matching origin.

---

## 8. Power Automate Cloud Flows

### Trigger Optimization

| Trigger setting | Purpose |
|---|---|
| **Trigger conditions** | Prevent flow from starting unless expression is true; reduces runs and request consumption; no run history logged when not triggered |
| **Select columns** (Dataverse) | Limits trigger to fire only when specified columns are in the update request |
| **Filter rows** (Dataverse) | OData filter evaluated after save; row must match expression for flow to run |
| **Change type** | Create / Modified / Delete |
| **Scope** | User-level, Business Unit, Organization |

**Select columns vs. Filter rows:** Select columns = which changed columns should cause evaluation. Filter rows = post-save row-state test. Use both together for precision.

**Gotcha:** Without Select columns on an Update trigger, any update to a row satisfying the filter expression will start the flow, even if unrelated columns changed.

### Row Selection Trigger

- Use **"When a row is selected"** for user-initiated flows launched from model-driven app views for selected records. This is distinct from row-change triggers.

### Retry Policies

| Policy | Behavior | When to use |
|---|---|---|
| None | No retry | Not recommended for external calls |
| Fixed | Constant interval retry | Basic transient failure |
| **Exponential** | Increasing intervals | **Preferred** for external services (429, 5xx); reduces hammering |

### Error Handling — Scopes

Use **Scopes with Configure run after** for try/catch/finally patterns:
- Main logic scope (Try) → error-handling scope runs after Failed/TimedOut.
- `Terminate` action with **Failed** status is needed if the Catch path should mark the run as failed (otherwise, successful error-logging makes the run appear green).

**`result('Try')` function** → returns an array of top-level action results within a scope (status, error detail). Use in Catch scope to identify which actions failed.

**`workflow()` function** → returns current run metadata (use to build a run URL for support emails).

### runAfter Configuration

```json
"runAfter": {
  "Call_API": ["Failed", "TimedOut"]
}
```
To catch only real failures, use `["Failed", "TimedOut"]`. Including `"Succeeded"` or `"Skipped"` makes the error branch fire for non-errors.

### Child Flows

| Requirement | Rule |
|---|---|
| Child trigger | Must use **"Manually trigger a flow"** |
| Solution placement | Parent and child must be in the **same solution** |
| Connection handling | Child must use **embedded connections** (edit Run only users); connections cannot be passed from parent to child |
| Discovery | Child appears in "Run a Child Flow" picker only when trigger and solution requirements are met |

Import a child flow into a solution rather than creating it there can cause unexpected behavior. Create flows directly in the solution.

### Expressions — Key Functions

| Function | Use |
|---|---|
| `int()` | Convert string to integer for numeric comparison |
| `greater()` | Greater-than comparison |
| `toLower()` / `toUpper()` | Case-normalize strings before equality check |
| `equals()` | Equality check |
| `trim()` | Remove surrounding whitespace |
| `empty()` | True for empty string, null, empty array/object |
| `split()` | Tokenize delimited string into array |
| `first()` | First element of an array |
| `if()` | Conditional value — returns one of two values |
| `coalesce()` | First non-**null** value — does NOT handle empty strings |
| `concat()` | String concatenation |
| `formatDateTime()` | Format date with pattern (e.g., `yyyyMMdd`) |
| `result('ScopeName')` | Array of top-level action results inside a scope |
| `workflow()` | Current run metadata |

**`coalesce` trap:** Returns first non-null value but treats `""` (empty string) as a valid non-null result. Use `if(empty(trim(value)), 'fallback', value)` instead when blank strings should fall back.

### Dataverse Connector in Flows

- **"Perform an unbound action"** → invoke a global custom API (not bound to a row).
- **"Perform a bound action"** → invoke an entity-bound custom API for a specific row.
- Set Environment parameter to **(Current)** for best performance; Microsoft says this uses native direct integration.
- **Service principal ownership of flows:** Create Dataverse application user for the Entra service principal, then create the connection using "Connect with service principal."
- For **non-solution flows** owned by a service principal: the OAuth connection must be **shared with the app user** before changing ownership.

### Secure Handling in Flows

| Setting | Purpose |
|---|---|
| **Sensitive text input** | Masks manual password/secret input from run history |
| **Secure inputs** | Masks action input values from run history |
| **Secure outputs** | Masks action output values from run history |
| **Secure environment variable (Secret type)** | Backed by Azure Key Vault; reference rather than stores the secret |

**`RetrieveEnvironmentVariableSecretValue`** is the only way to use a Key Vault-backed secret environment variable in a flow — it does NOT appear in the dynamic content selector. Call it via "Perform an unbound action" on the Dataverse connector, then enable Secure Outputs on that step and Secure Inputs/Outputs on the consuming HTTP step.

---

## 9. Environment Variables & Azure Key Vault

### Key Vault–Backed Secret Variables

| Role | Required Azure role |
|---|---|
| Makers creating/using the variable | **Key Vault Secrets User** |
| Microsoft Dataverse service principal | **Key Vault Secrets User** |

**Previous guidance said Key Vault Reader — this is NO LONGER sufficient.** Both the maker and Dataverse need Secrets User.

**Automating secret rotation:** Use Azure Event Grid + a cloud flow triggered by `SecretNewVersionCreated` event → call `NotifyEnvironmentVariableSecretChange` (Dataverse unbound action). This is the only supported automated rotation notification path.

**ALM principle:** The solution stores the secret *reference* (environment variable); the actual secret stays in Key Vault. Use Secret-type environment variables instead of Text-type for API credentials.

---

## 10. Azure Functions Integration

### Trigger Selection

| Scenario | Trigger |
|---|---|
| Custom connector action / webhook receiver | HTTP trigger |
| Scheduled background job | Timer trigger |
| Dataverse → Azure Service Bus → Function | Service Bus trigger |
| Process Azure Event Hubs stream | Event Hubs trigger |

### Timer Trigger Best Practices

- `runOnStartup: true` → function runs on every app restart and scale event. **Disable in production.**
- `useMonitor: true` → enables durable schedule monitoring so missed schedules are tracked across restarts. **Enable for production schedules.**

### HTTP Trigger Timeout Limit

Azure HTTP-triggered functions have a hard **230-second timeout** due to Azure Load Balancer. For operations exceeding this:
- Use the **Durable Functions async HTTP pattern**: start orchestration, return tracking response immediately, caller polls status.

### Azure Functions OpenAPI Extension

Build order for Azure Function → Custom Connector:
1. Install OpenAPI extension in project
2. Add HTTP trigger endpoint with OpenAPI annotations
3. Publish to Azure
4. Import OpenAPI definition into custom connector

### Durable Functions

Use Durable Functions when:
- Workload runs for **minutes or hours** (long-running).
- Must survive **retries and restarts** (stateful checkpointing).
- Must wait for **external events** (callbacks, approvals) and resume.
- Need status polling without holding the original request open.

Not appropriate for: synchronous Dataverse validation, UI form rules, client-side logic.

### Azure Service Bus Integration

- Dataverse can post remote execution context to a Service Bus queue/topic via a registered Service Endpoint.
- Azure Function uses a **Service Bus trigger** to process those messages asynchronously.
- With a queue endpoint contract, the listener does not need to be permanently active — messages queue until the function picks them up.

---

## 11. PCF / Code Components

(Minimal coverage in this question set — referenced obliquely as a wrong answer distractor. Know that PCF components are for UI rendering, not for server-side Dataverse operations or connector patterns.)

---

## 12. Quick-Fire Facts

1. **Pipeline stage codes:** PreValidation = 10, PreOperation = 20, PostOperation = 40. Stage 50 does not exist.
2. **Throw `InvalidPluginExecutionException` in PreValidation** to cancel with the least rollback cost.
3. **Pre Image on Create does not exist.** Post Image on Delete does not exist.
4. **`accountid` in filtering attributes defeats filtering** — the primary key is always in update requests.
5. **Custom API BindingType is immutable** after save. Delete and recreate if wrong.
6. **Is Function = Yes** blocks workflow use and blocks Power Automate connector discoverability.
7. **AllowedCustomProcessingStepType = Async Only** is the recommended setting for business-event-style custom APIs.
8. **OpenAPI 3.0 is not supported** for custom connector import. Convert to 2.0 first.
9. **Client credentials grant is not supported** by custom connectors.
10. **`coalesce()` does not catch empty strings** — use `if(empty(trim()))` instead.
11. **`Retry-After` header** in a 429 response tells the client exactly how long to wait — always honor it.
12. **`ColumnSet(true)` / new `ColumnSet(true)`** = SELECT * = performance anti-pattern. Always specify columns.
13. **`ExecuteMultipleRequest` / `ExecuteTransactionRequest` are forbidden inside plug-ins.**
14. **Elastic tables do not support transactions** via change sets or ExecuteTransactionRequest.
15. **`PATCH` + `If-Match: *`** = update-only; fails with 404 if row missing.
16. **`PATCH` + `If-Match: W/"etag"`** = optimistic concurrency; fails with 412 if ETag changed.
17. **User-assigned managed identity** survives Function App deletion; system-assigned does not.
18. **App-only scope = `<env-url>/.default`**, not `user_impersonation`.
19. **Child flows must use "Manually trigger a flow"** and be in the same solution as the parent.
20. **Non-solution flows owned by a service principal** require the OAuth connection to be shared with the app user.
21. **`runOnStartup: false` + `useMonitor: true`** = correct production timer trigger config.
22. **`result('ScopeName')`** = inspect top-level action results inside a scope (for catch blocks).
23. **`workflow()`** = current run metadata (for building run URLs in error emails).
24. **Key Vault Secrets User** role (not Reader) is required for both makers and Dataverse.
25. **`RetrieveEnvironmentVariableSecretValue`** = only supported way to consume a Key Vault secret env var in a flow; not in dynamic content picker.
26. **Trigger conditions** prevent the flow from even starting (no run history logged); a Condition action inside the flow still runs and logs.
27. **Select columns** (Dataverse trigger) = which changed columns should cause evaluation; **Filter rows** = post-save OData filter on the row state.
28. **`Prefer: return=representation` + `$select`** = upsert response that identifies create (201) vs. update (200) with minimal payload.
29. **GitHub raw URL** (not the HTML page URL) is required when importing an OpenAPI definition from GitHub.
30. **Custom code + on-premises data gateway** is an unsupported combination.

---

## 13. Common Traps

| Trap | Correct understanding |
|---|---|
| "PreOperation is the best stage to validate and reject" | PreValidation is better for rejection — it occurs before the transaction, avoiding rollback cost |
| "Setting a field in PostOperation won't trigger another Update" | It WILL trigger a second Update event. Mutate Target in PreOperation instead |
| "I can pass state between plug-ins using member fields" | Member fields are reused across instances — use local variables and SharedVariables |
| "ExecuteMultipleRequest inside a plug-in batches work efficiently" | Forbidden in plug-ins; adds blocking and complexity inside the synchronous pipeline |
| "All columns in ColumnSet is fine as a default" | Microsoft explicitly calls this out as a performance anti-pattern |
| "coalesce() handles blank strings" | coalesce() only handles nulls; empty strings pass through. Use if+empty+trim |
| "A custom connector supports client_credentials grant" | Not supported; unattended app-only OAuth cannot use standard custom connectors |
| "OpenAPI 3.0 works for custom connector import" | Only OpenAPI 2.0 is supported; convert first |
| "Dynamic extensions go on the body parameter" | They must go inside the body schema, not the parameter wrapper |
| "Key Vault Reader role is sufficient for secret env vars" | Key Vault Secrets User is now required for both makers and Dataverse |
| "Retry-After is optional; I can use fixed delays" | Microsoft says to honor the platform-provided value; fixed guesses are less accurate |
| "Setting If-Match: * on PATCH creates rows if missing" | If-Match: * forces update-only; 404 if missing. Omit headers for upsert behavior |
| "PostOperation async can cancel an operation" | Async PostOperation runs after commit; it cannot cancel the operation |
| "A Pre Image on Create step is available" | Pre Images on Create do not exist — there is no prior row |
| "Including accountid in filtering attributes is harmless" | It defeats filtering; the primary key is always in Update payloads |
| "System-assigned identity is ideal for shared Function Apps" | User-assigned identity is the right choice when identity must survive app deletion or be shared |
| "user_impersonation scope works for managed identity Dataverse calls" | App-only calls need /.default scope; user_impersonation is for delegated user flows |
| "Is Function = Yes is fine for workflow-enabled custom APIs" | Is Function must be false (action) when WorkflowSdkStepEnabled = true |
| "runOnStartup: true is a safe production timer setting" | It causes extra runs on every restart and scale event; disable in production |
| "A global custom API needs EntityReference binding for a record operation" | Entity-bound custom API (BindingType = Entity) creates a Target parameter automatically; global is for non-row operations |

---

## Deeper Exam Detail

> This section adds depth, exact numbers, edge cases, and SDK/API specifics. All claims are sourced from Microsoft Learn unless marked "(unverified)".

---

### A. Plug-in Execution Pipeline — Deeper Detail

#### Stage descriptions from the official docs (verbatim intent)

| Stage | Transaction scope | Official description nuance |
|---|---|---|
| PreValidation | **Outside** the database transaction for the initial operation | Subsequent operations triggered by extensions in other stages pass through PreValidation **inside the calling extension's transaction** |
| PreOperation | Inside transaction | If you want to change entity values, do it here. Canceling here **triggers a rollback** and has significant performance impact |
| MainOperation | Inside transaction | For internal use, custom APIs, and virtual table data providers only |
| PostOperation (sync) | Inside transaction | Modify message properties before return. Avoid applying changes to an entity in the message — it triggers a new Update event |
| PostOperation (async) | Outside transaction | Runs after record operation completes via the async service |

Source: [Event Framework — Microsoft Dataverse](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/event-framework)

**Special async-only rule:** You must use asynchronous mode when registering a plug-in on the Create message of the **SystemUser** (User) entity if the plug-in performs an update operation. This is because the related `UserSettings` record is not created until after the `SystemUser` row is committed, which only exists outside the transaction.

#### IPluginExecutionContext — Full Context Members

Beyond `InputParameters`, `OutputParameters`, `SharedVariables`, `PreEntityImages`, `PostEntityImages`, and `CorrelationId` covered in the exam guide, the execution context also exposes:

| Member | Purpose |
|---|---|
| `Stage` | Integer code of the current pipeline stage (10 / 20 / 30 / 40) |
| `MessageName` | The name of the message (e.g., "Create", "Update", your custom API name) |
| `PrimaryEntityName` | Logical name of the primary table |
| `PrimaryEntityId` | GUID of the primary entity record |
| `UserId` | The user the plug-in is running as (affected by impersonation setting) |
| `InitiatingUserId` | The user who originally triggered the operation |
| `BusinessUnitId` | Business unit of the user |
| `OrganizationId` | GUID of the organization |
| `OrganizationName` | Unique name of the organization |
| `Depth` | Current call-stack depth (for loop prevention — see above) |
| `IsExecutingOffline` | Whether the plug-in is running in offline mode (legacy) |
| `IsInTransaction` | Whether the plug-in is inside a database transaction |
| `IsOfflinePlayback` | Whether executing during offline sync playback |
| `OperationId` | Unique identifier for the current operation |
| `RequestId` | Unique identifier of the request |

Source: [Understand execution context — Microsoft Dataverse](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/understand-the-data-context)

#### OutputParameters: Only Available in PostOperation

`OutputParameters` are not populated until after the database transaction completes. They are therefore only accessible in plug-ins registered for the **PostOperation** stage. Attempting to read them in PreValidation or PreOperation yields an empty collection. Source: [Understand execution context](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/understand-the-data-context)

---

### B. Custom API — Additional Properties and Constraints

#### Full Workflow-Supported Parameter Types

When `WorkflowSdkStepEnabled = true`, request parameters and response properties are limited to:

| Supported | Not Supported |
|---|---|
| Boolean, DateTime, Decimal, Float, Integer, Money, Picklist, String, Guid | Entity, EntityCollection, StringArray |
| EntityReference (only when API is entity-bound) | — |

Source: [Create and use custom APIs](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/custom-api)

#### Functions Must Return Data

A Custom API with `IsFunction = true` must include at least one response property to be valid. A function with no response property will not appear in the Web API `$metadata` service document, and callers receive `404 Not Found` with `"Resource not found for the segment 'your_function_name'."`. Source: [Create and use custom APIs](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/custom-api)

#### Is Private — What It Actually Prevents (and Doesn't)

Setting `IsPrivate = true`:
- Removes the API from the Web API `$metadata` (CSDL) service document.
- Prevents Dataverse code-generation tools from generating classes for the message.
- Does **not** prevent the API from being invoked if a caller knows the message name and can compose a valid request.
- Use `IsPrivate = false` during development so you can see $metadata output; switch to `true` before shipping the managed solution.
- Known issue: **Private messages cannot be used inside plug-ins.** Source: [Create and use custom APIs](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/custom-api)

---

### C. Web API / OData — Deeper Detail

#### $batch Limits and Structure

- A `$batch` request can contain up to **1,000 individual requests**.
- `$batch` requests cannot contain other `$batch` requests.
- `GET` requests are **not allowed inside change sets** (a change set is for data-modification operations only).
- Each batch item must include its own HTTP headers; headers on the outer `$batch` request do **not** cascade to individual items.
- Line endings in `$batch` payloads must be **CRLF**; other line endings can cause deserialization errors.
- URL length inside a `$batch` body can be up to **64 KB (65,536 characters)** — use this to work around the normal URL length limit for complex FetchXML queries.
- The `Prefer: odata.continue-on-error` header makes the server continue processing remaining requests after a failure, returning status `200 OK` with individual error details embedded in the response body. Without it, the entire batch stops at the first error.

Source: [Execute Batch Operations Using the Web API](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/execute-batch-operations-using-web-api)

#### Service Protection API Limit — Three Facets with Exact Numbers

Per **web server** (most environments have multiple web servers):

| Facet | Limit | Sliding window |
|---|---|---|
| Number of requests | **6,000** requests | 5 minutes (300 seconds) |
| Combined execution time | **20 minutes (1,200,000 ms)** | 5 minutes |
| Concurrent requests | **52 or higher** | Instantaneous |

- Limits are enforced **per user**, not per environment. Each authenticated user has an independent limit.
- Plug-in and custom workflow activity internal calls **do not count** toward the request number or execution time limits, but their execution time is added to the originating request's execution-time accrual.
- **Error codes for SDK for .NET:** number of requests = `-2147015902` (`0x80072322`); execution time = `-2147015903` (`0x80072321`); concurrent requests = `-2147015898` (`0x80072326`).
- The `Retry-After` duration is calculated based on the nature of the preceding 5-minute period's requests. Continued demanding requests after a 429 extend the Retry-After duration further.
- Service protection limits do **not** apply to Dataverse Search (which uses `api/search` instead of `api/data`). Dataverse Search has a separate limit of **one request per second per user**.

Source: [Service protection API limits](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/api-limits)

#### SDK Auto-Retry: Which Classes Auto-Retry vs Which Do Not

| Class | Auto-retries on 429? |
|---|---|
| `ServiceClient` (PowerPlatform.Dataverse.Client) | Yes — automatically pauses and resends after Retry-After |
| `CrmServiceClient` (Xrm.Tooling.Connector) v9.0.2.16+ | Yes |
| `OrganizationServiceProxy` | No — **deprecated**; replace with ServiceClient |
| `OrganizationWebProxyClient` | No — **deprecated**; replace with ServiceClient |

Source: [Service protection API limits](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/api-limits)

#### Maximize Throughput — Official Guidance Summary

1. Start with low parallelism; gradually increase until you hit 429s; let Retry-After guide the upper bound.
2. Prefer individual requests with high parallelism over large batches — for Web API, JSON payload per request is small, so network latency is not a bottleneck.
3. If using `ExecuteMultiple`, start with batch size 10 and increase; larger batches increase execution-time limit exposure more than they reduce request-count exposure.

Source: [Service protection API limits](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/api-limits)

---

### D. Bulk Operations (CreateMultiple / UpdateMultiple / UpsertMultiple / DeleteMultiple)

#### Which Tables Support Bulk Messages

- All **elastic tables** support CreateMultiple, UpdateMultiple, UpsertMultiple, and DeleteMultiple.
- **Standard tables**: custom standard tables and many common tables support CreateMultiple and UpdateMultiple, but **not all**. Test availability by querying `sdkmessagefilters` for the specific table/message combination.
- `DeleteMultiple` is **elastic tables only**; calling it on a standard table returns `"DeleteMultiple has not yet been implemented."`.

Source: [Use bulk operation messages](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/bulk-operations)

#### On-Error Behavior Difference: Standard vs Elastic

- **Standard tables**: any error causes the **entire operation to roll back**. Only use when you have high confidence all records will succeed.
- **Elastic tables**: **partial success** is possible. Retrieve per-record status from `OrganizationServiceFault.ErrorDetails["Plugin.BulkApiErrorDetails"]` (SDK) or include `Prefer: odata.include-annotations=Microsoft.PowerApps.CDS.ErrorDetails.*` (Web API).

Source: [Use bulk operation messages](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/bulk-operations)

#### Bulk Messages in Plug-ins — Still Forbidden

Like `ExecuteMultiple` and `ExecuteTransaction`, the bulk operation messages (`CreateMultiple`, `UpdateMultiple`, etc.) **cannot be used inside plug-in code**. However, you **should** write plug-ins *for* the CreateMultiple and UpdateMultiple messages (i.e., plug-ins that handle those messages when clients use them). Source: [Use bulk operation messages](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/bulk-operations)

#### API Limit Accrual for Bulk Messages

- **Service protection — number of requests:** One bulk request counts as **one request** toward the 6,000/5-min limit (regardless of how many records are in `Targets`). Bulk operations therefore reduce exposure to the request-count facet.
- **Service protection — execution time:** Each bulk request typically takes longer. Sending in parallel increases exposure to the **execution-time** facet (1,200 seconds/5-min).
- **Power Platform API entitlement limits (daily):** Each record in `Targets` counts individually toward the daily entitlement. Bulk operations provide no bypass.

Source: [Use bulk operation messages — FAQ](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/bulk-operations)

---

### E. Environment Variables with Azure Key Vault — Additional Rules

#### Required Roles (Both Needed)

| Principal | Required Azure RBAC role |
|---|---|
| Maker (user who creates/uses the env var) | **Key Vault Secrets User** |
| Microsoft Dataverse service principal (App ID `00000007-0000-0000-c000-000000000000`) | **Key Vault Secrets User** |

Previous instructions specified Key Vault Reader — this is no longer sufficient. If you configured Key Vault with Reader, add Secrets User to avoid retrieval failures. Source: [Use environment variables for Azure Key Vault secrets](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/environmentvariables-azure-key-vault-secrets)

#### Key Vault Must Be in Same Tenant

Azure Key Vault must be in the **same tenant** as the Power Platform environment. Cross-tenant key vault integration is not supported. Source: [Use environment variables for Azure Key Vault secrets](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/environmentvariables-azure-key-vault-secrets)

#### Scope of Use

Environment variables referencing Azure Key Vault secrets are currently limited to:
- Power Automate cloud flows
- Copilot Studio agents
- Custom connectors

They are **not** accessible via the general API or in other customizations such as client-side scripts, plug-ins, or canvas apps directly. Source: [Use environment variables for Azure Key Vault secrets](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/environmentvariables-azure-key-vault-secrets)

---

### F. Durable Functions — Async HTTP Pattern Details

#### Polling Consumer Pattern (Built-In)

When an HTTP-triggered function starts an orchestration and returns `CreateCheckStatusResponse`, the caller receives:

- **HTTP 202 Accepted** with a `Location` header pointing to `statusQueryGetUri`.
- A `Retry-After` header (default 10 seconds) as a hint to the polling interval.
- Response body JSON with five management URIs: `statusQueryGetUri`, `sendEventPostUri`, `terminatePostUri`, `purgeHistoryDeleteUri`, and `id`.

The caller polls `statusQueryGetUri`. While the orchestration runs, polling returns `202` with a new `Location` header. When the orchestration completes or fails, it returns `200 OK` with the result. This pattern is built into the Durable Functions extension — no custom polling code is required. Source: [HTTP Features in Durable Functions](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-http-features)

#### Managed Identity in Durable Orchestrations

Durable Functions supports `ManagedIdentityTokenSource` for acquiring Entra ID tokens inside `context.CallHttpAsync(...)`. The token source:
- Automatically fetches and refreshes tokens.
- Never stores tokens in durable orchestration state.
- Attaches the token as a `Bearer` token in the `Authorization` header.

To call Dataverse from a Durable orchestrator, pass `ManagedIdentityTokenSource("<dataverse-env-url>/.default")` as the `tokenSource` parameter. This eliminates manual token management. Source: [HTTP Features in Durable Functions](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-http-features)

---

### G. Additional Edge-Case Decision Rules

| Scenario | Decision |
|---|---|
| Bulk operation on standard table partially fails | Entire operation rolls back; consider ExecuteMultiple with ContinueOnError fallback if partial success is acceptable |
| Bulk operation on elastic table partially fails | Partial success possible; inspect per-record status from error details |
| Need to determine whether a standard table supports CreateMultiple | Query `sdkmessagefilters` for the table name and message name combination |
| Running CreateMultiple plug-in along with existing Create plug-in | Both fire; if logic is equivalent, remove from single-op plug-in or it runs twice |
| Need to use Key Vault secret env var in a canvas app formula | Not supported; limited to flows, Copilot Studio, and custom connectors |
| Durable orchestrator needs to call Dataverse API with managed identity | Use `ManagedIdentityTokenSource("<env-url>/.default")` in `CallHttpAsync`; token refresh is automatic |
| $batch operation stops on first error and discards remaining requests | Add `Prefer: odata.continue-on-error` header to process all items and return aggregate results |
