# PL-400 Concept Guide: Create a Technical Design (10–15%)

---

## 1. Dataverse Table Types

### Key Facts

- **Standard table**: Native Dataverse storage with full relational modeling, plug-in pipeline, security roles, auditing, ownership, and complex joins. Best for core business records.
- **Elastic table**: Horizontally scalable, high-throughput Dataverse-backed storage. Designed for very large datasets, bursty writes, append-heavy patterns (telemetry, IoT events), and retention-based cleanup. Does NOT require complex relational joins or transactional logic across tables.
- **Virtual table**: Surfaces data from an external system (e.g., Azure SQL) as Dataverse table data without copying it into Dataverse. The external system remains the system of record. Supports model-driven app forms and views. Lacks full native Dataverse behaviors (ownership, auditing, plug-ins, offline support, etc.).

### Decision Rules

| Requirement signal | Choose |
|---|---|
| Core business data, security, auditing, relationships | Standard table |
| Millions of rows, bursty writes, telemetry/IoT, retention | Elastic table |
| External system stays master, no replication desired | Virtual table |
| Was virtual, but external master requirement dropped + need native behaviors | Migrate to Standard table |

### When Virtual Table Goes Wrong

If the team discovers that record-centric Dataverse behaviors are missing (ownership, audit, offline, plug-ins) and the external system no longer needs to be the master, the correct fix is to **switch to a standard table**, not to add caching layers over the virtual table.

### Common Distractors

- **Elastic table for external data** — wrong; elastic is for high-volume native storage, not for projecting external sources.
- **Virtual table when you need transactional plug-in logic** — virtual tables do not participate in the standard Dataverse event pipeline the same way.
- **Standard table for 50M telemetry rows** — correct architecture but wrong scale fit; elastic is designed for this.

---

## 2. Security Model: Roles, Teams, Business Units, Row Sharing

### Key Facts

- **Security role**: Defines privileges at the table/column/row level. Assigned to users or teams.
- **Owner team**: A team that can own records. Members inherit the team's security role. Membership ≠ automatic privileges — the team must have a role assigned.
- **Business unit**: Organizational boundary for data partitioning. Affects default record ownership and access scope.
- **Row sharing**: Grants access to a single specific record to a user or team without changing their broader security role. Narrowest possible access grant.
- **Environment security group**: Controls which licensed Entra users can be members of (admitted to) an environment.
- **Application user**: Nonhuman Dataverse identity created from an Entra app registration. Must be assigned a security role. Used for unattended integrations and service-to-service calls.
- **DLP policy**: Governs which connectors can be used together in apps and flows. Operates at the connector/data-movement layer, NOT at the Dataverse record layer.

### Decision Rules

| Requirement | Mechanism |
|---|---|
| Grant access to ONE record without changing user's broader role | Row sharing |
| Rotating user groups with shared access patterns | Team-based access model |
| Restrict who can enter an environment at all | Environment security group |
| Unattended Azure/integration identity with least privilege | Application user + custom security role |
| Block connector combinations in apps and flows | DLP policy |
| Organizational data partitioning by region/department | Business units |

### Common Distractors

- **DLP to fix record access** — DLP controls connector groupings, not Dataverse row visibility. A security role cannot fix a DLP block, and a DLP policy cannot grant row access.
- **Business unit reassignment to share one record** — too broad; row sharing is the narrow, correct tool.
- **Adding a user to an owner team without assigning a role** — membership alone does not grant record access.
- **System Administrator for an integration user** — violates least-privilege; use a custom scoped role.

---

## 3. Server-Side Logic: Plug-ins, Custom API, Power Fx Functions

### When to Use Each

| Component | Trigger model | Caller model | Complexity/control | Maker-friendly |
|---|---|---|---|---|
| **PreValidation plug-in** | Dataverse event pipeline (before DB transaction) | All channels (apps, APIs, imports, flows) | High (.NET) | No |
| **PreOperation plug-in** | Dataverse event pipeline (before commit, in transaction) | All channels | High (.NET) | No |
| **PostOperation plug-in** | After commit | All channels | High (.NET) | No |
| **Custom API (unbound)** | Explicit message call (on-demand) | Code, flows, canvas apps, model-driven | High (.NET, structured params, telemetry) | No |
| **Dataverse Power Fx function** | Explicit on-demand call | Apps, flows | Low-code, simple logic | Yes |
| **Business rule (table-scoped)** | Form/save events on table | Model-driven app forms (entity scope = all forms) | No-code | Yes |
| **Client script (JavaScript)** | Form events in model-driven app | Single app session only | Medium | Partial |

### Key Decision Rules

- Need to **block an invalid write from ALL channels** (imports, integrations, APIs)? → **PreValidation or PreOperation plug-in**
- Need a **reusable callable operation** with a formal Dataverse message, structured input/output, and .NET control? → **Custom API (unbound)**
- Need **reusable server-side logic** callable from apps and flows, low complexity, maker-maintainable? → **Dataverse Power Fx function**
- Need **conditional field visibility / requirement level / recommendations** on forms, no code, all forms for a table? → **Entity-scoped business rule**
- Need **immediate UI feedback** during form editing (show/hide tabs, set fields reactively)? → **Client script**
- Logic must run **in-transaction before commit** to block bad data? → **PreOperation plug-in** (PreValidation runs before even entering the transaction)

### Plug-in Stage Distinction

- **PreValidation**: Before DB transaction begins. Can throw to reject the operation. Best for input validation.
- **PreOperation**: Inside the transaction, before the main operation. Can modify input before it's saved.
- **PostOperation**: After main operation, still inside transaction. Best for cascading creates/updates.

### The "Cloud Flow as Validation" Anti-Pattern

A Dataverse-triggered cloud flow runs **after** the data event. It cannot prevent invalid data from being committed or from being read by downstream consumers before the flow corrects it. If universal enforcement before commit is required, the correct fix is a **PreValidation or PreOperation plug-in**.

### Custom API vs. Power Fx Function

| Dimension | Custom API | Power Fx Function |
|---|---|---|
| Implementation | .NET plug-in class (IPlugin) | Low-code Power Fx |
| Caller surface | Formal Dataverse message, callable from code and flows | Callable from apps and flows |
| Best for | Complex logic, telemetry, structured error, external .NET callers | Simple reusable logic, maker-maintainable |
| Table-event bound? | No (unbound) | No |
| Requires deployment | Yes (solution + plug-in assembly) | No |

**Code signal**: A plug-in that checks `context.MessageName != "contoso_SubmitOrder"` is backing a **Custom API**, not a table event.

---

## 4. Client-Side Logic: JavaScript, Business Rules, PCF

### Decision Rules

| Requirement | Best fit |
|---|---|
| Immediate UI feedback on form edits (show/hide, set field) | Client script |
| Form validation + guidance + field requirements, no code, all forms | Entity-scoped business rule |
| Reusable custom UI control for model-driven AND canvas apps | PCF code component |
| Reusable header/filter block for multiple canvas apps, low-code updates | Canvas component library |
| Command visibility based on column value in model-driven app | Modern command designer + Power Fx |

### PCF vs. Canvas Component vs. JavaScript Library

| Dimension | PCF code component | Canvas component library | JavaScript library |
|---|---|---|---|
| Works in model-driven app | Yes | No | Yes (form scripting) |
| Works in canvas app | Yes | Yes | No |
| Custom rendering | Yes | Yes | Limited |
| Typed manifest properties | Yes | Yes | No |
| Solution-packaged | Yes | Yes | Yes |
| Low-code updates | No (compiled) | Yes | Partial |

**Rule**: If the control must work in both model-driven and canvas apps → **PCF**. If canvas-only and low-code maintainability is key → **Canvas component library**.

### DOM Manipulation Anti-Pattern

Directly accessing `document.getElementById()` inside a model-driven form script is brittle. If the team wants a reusable, resilient UI pattern across forms, the correct redesign is a **PCF code component**, not a shared JavaScript library (which preserves the same DOM-coupling problem).

### Command Bar Design

- Use **modern command designer** with **Power Fx** for visibility rules (`Status = Active` → show command).
- Commands defined in one app cannot be directly added to a different app's command component library — commands are app-scoped in the platform.
- **Plug-ins are wrong** for command visibility logic; that belongs in the UI/command layer.

---

## 5. Integration Patterns: Outbound Events from Dataverse

### Comparison Table

| Pattern | Synchronous? | Durable queue? | Best for |
|---|---|---|---|
| **Webhook** | Can be sync or async | No | Direct HTTP POST to external app; sync external validation in request path |
| **Azure Service Bus endpoint** | Async | Yes | Fan-out to multiple Azure consumers; burst absorption; offline consumer resilience |
| **Azure Function (direct)** | Async | No | Custom compute, retry control, long-running external calls |
| **Custom API** | Sync (in Dataverse) | No | Reusable Dataverse operation surface |

### Decision Rules

- Bursts expected + consumers can process later + listener downtime must not lose messages → **Azure Service Bus**
- External validation must participate **in the same Dataverse transaction before commit** → **Webhook** (registered on synchronous step), NOT Service Bus (async)
- Multiple Azure consumers need the same event fan-out → **Service Bus**
- Long-running external API call (e.g., 40 seconds), result not needed before save → **Azure Function** (triggered async)

### Inbound: ERP → Dataverse Without GUID Lookups

When an external system owns its own business identifier and the Dataverse GUID is unknown, use **Upsert with alternate keys**. Alternate keys let Dataverse identify rows by business columns; a single Upsert call creates or updates idempotently.

---

## 6. Authentication and Identity

### Patterns

| Scenario | Correct pattern |
|---|---|
| Unattended Azure Function or sync worker calling Dataverse | OAuth client credentials flow (service-to-service) via Entra ID |
| Nonhuman identity in Dataverse with least privilege | Application user + custom security role |
| Per-user sign-in for custom connector (each maker authenticates as themselves) | Custom connector with OAuth 2.0 / Entra ID |
| API key in connector definition | Wrong if requirement is to eliminate shared secrets |
| Mission-critical flow that must survive staff changes | Service principal (application user) as flow owner |
| HTTP 403 after successful Entra token acquisition | Missing Dataverse app-user role assignment (auth vs. authz distinction) |

### Key Principle: Authentication ≠ Authorization

A valid Entra token proves authentication succeeded. A 403 from Dataverse means authorization failed — the application user exists but has no (or wrong) security role assigned in that environment.

### Moving API Key to Environment Variable Is Not Enough

Storing an API key in an environment variable changes the **storage location** of the secret but does not change the **authentication pattern**. If the requirement is to eliminate long-lived shared secrets, the connector must be redesigned to use **OAuth 2.0 / Entra ID**.

---

## 7. ALM: Solution Design, Environment Variables, Connection References

### Key Facts

- **Environment variables**: Store environment-specific configuration values (endpoints, queue names, non-secret settings, connector host/base URL/client ID) in the solution. Values differ by environment; the solution logic stays unchanged.
- **Connection references**: Solution-aware pointer to a connection for a specific connector. Solution-aware flows bind to the reference, not to the raw connection. During import, the admin supplies the connection for each reference in the target environment.
- **Managed solutions**: The correct deployment vehicle. Unmanaged customizations in test/prod are an ALM anti-pattern.
- **Hard-coded connector IDs / URLs**: Fragile; break after import to a new environment.

### Decision Rule

For any solution that deploys across DEV → TEST → PROD:
- Environment-specific values → **environment variables**
- Connector bindings for flows → **connection references**
- Both together = portable, maintainable, managed-solution-ready design

### Custom Connector + Environment Variables

Microsoft documents that environment variables can update key connector properties in a solution: Host, Base URL, Client ID, Client Secret, Login URL, Refresh URL. This is the correct mechanism for environment-specific connector settings, alongside a connection reference for runtime binding.

---

## 8. Custom Connector Design

### OpenAPI and Authentication

- Custom connectors support import from **OpenAPI 2.0** (Swagger). OpenAPI 3.0 is NOT supported for import.
- Use OpenAPI import to stay aligned with a maintained API contract and to support connector-specific metadata extensions.
- **x-ms-visibility: internal** hides a parameter from makers. If the parameter is also `required: true`, a **default value must be provided** — otherwise the platform has no way to supply the required value.
- **x-ms-visibility: advanced** shows but collapses the parameter.
- **x-ms-summary**: Provides a user-friendly label for the parameter.

### Custom Code Limitation

Custom code in a custom connector (request/response transformation scripts) is **not supported when the connector uses the on-premises data gateway**. This is a design-time decision, not a configuration fix.

### Authentication Types

| Type | Use when |
|---|---|
| API key | Simple shared key; not suitable when per-user identity is required |
| Basic auth | Username/password; not suitable for eliminating shared secrets |
| OAuth 2.0 / Entra ID | Per-user delegated identity, MFA, conditional access, no shared secret |
| Anonymous | Public APIs only |

---

## 9. Cloud Flow Design

### Trigger Types

| Type | Starts when |
|---|---|
| Automated | System event (e.g., Dataverse row created/updated) |
| Instant | User initiates manually |
| Scheduled | Timer fires |
| Desktop flow | UI automation via gateway |

Event-driven reaction to Dataverse changes → **Automated cloud flow** (not instant, not scheduled).

### Reuse and ALM

- **Child flow**: Centralizes reusable automation logic callable by multiple parent flows. Update once, all callers benefit. Must be solution-aware.
- **Connection references + environment variables**: Required for portable cloud flows in managed solutions.

### Self-Trigger Recursion Prevention

When a Dataverse-triggered flow updates the same row it triggered on, use a **trigger condition** (e.g., `@not(equals(triggerOutputs()?['body/cr6f8_processed'], true))`) to prevent infinite loops. This filters at the trigger level, which is cleaner than branching inside the flow.

### Concurrency and Duplicate Prevention

If parallel flow runs are causing duplicate downstream effects against a non-idempotent external API, the first fix is to **limit trigger concurrency** (serialize runs). Increasing retries would worsen the duplication problem.

### Change Tracking for Efficient Sync

For scheduled Azure Function sync jobs reading Dataverse:
- Use **OAuth client credentials** for unattended auth.
- Enable **Dataverse change tracking** to retrieve only rows changed since the last sync, minimizing reads and supporting efficient resume.

---

## 10. Native Platform vs. Custom Development

### Out-of-the-Box Capabilities (no custom code needed)

| Requirement | OOB feature |
|---|---|
| Guide users through staged steps on a record | Business process flow |
| Human sign-off / approval routing | Power Automate approval action |
| Sum related record values at parent level | Rollup column |
| Conditional field visibility/requirement/recommendation | Business rule (entity-scoped) |
| Detect duplicates before save | Duplicate detection rules |
| Aggregate calculated value shown on form | Formula column (but: NOT supported in mobile offline) |

### Formula Column Limitation

Formula columns do **not** display values when the app is in **mobile offline mode**. If offline support is required, formula columns fail the full requirement.

### "Prefer OOB First" Principle

Before recommending a plug-in, PCF control, or custom code, verify the requirement cannot be met by: business rules, rollup/formula columns, duplicate detection, business process flows, or approval flows. Only escalate to custom code when OOB clearly falls short.

---

## 11. Connector vs. Virtual Table Decision

### When to Use a Connector Directly

- The external system performs **live SaaS actions** (e.g., create a Planner task, send a message).
- The **external system remains the master** and you are calling its API, not modeling its data.
- The interaction is operational/transactional against the external API.

### When to Use a Virtual Table

- The external data must **appear in model-driven app forms and views** as Dataverse table data.
- The external system remains the record master, but **data duplication is explicitly unwanted**.
- No synchronization pipeline should be built.

### When to Use a Standard Table (with possible connector or sync)

- The data needs **full Dataverse behaviors**: ownership, security roles, auditing, plug-ins, offline, relationships, complex reporting.
- The external system is no longer the master.

---

## Quick-Fire Facts

1. **Row sharing** = narrowest security grant; one record, one user/team, no role change.
2. **Owner team membership alone ≠ record access**; the team must have a security role assigned.
3. **DLP ≠ Dataverse row security**; they solve completely different problems.
4. **PreValidation** runs before the DB transaction; use it to reject invalid data universally.
5. **Cloud flows triggered by Dataverse run after the event** — they cannot prevent invalid data from being committed.
6. **HTTP 403 after successful Entra token** = missing app-user role in Dataverse (authz, not authn).
7. **Service Bus** = durable queue, offline consumer resilience, burst absorption; **Webhook** = synchronous external participation in the request path.
8. **Upsert + alternate keys** = create-or-update without needing the Dataverse GUID.
9. **x-ms-visibility: internal + required = must have a default value** in the OpenAPI definition.
10. **Custom code + on-premises data gateway = unsupported combination** in custom connectors.
11. **OpenAPI 2.0 (Swagger) only** — OpenAPI 3.0 is not supported for custom connector import.
12. **Environment variables** store config; **connection references** store connector bindings — both needed for managed solution ALM.
13. **PCF** = cross-surface (model-driven + canvas); **canvas component library** = canvas-only, low-code updates.
14. **Service principal / application user** = correct identity for mission-critical flows and unattended integrations.
15. **Elastic tables** = bursty high-volume native Dataverse storage; **virtual tables** = external data, no replication.
16. **Formula columns do not work in mobile offline mode**.
17. **Change tracking** in Dataverse = efficient incremental sync (fetch only what changed since last run).
18. **Trigger concurrency limiting** = first fix for duplicate downstream effects from parallel flow runs.
19. **Custom API unbound message** = formal callable Dataverse operation; backing plug-in checks `context.MessageName`.
20. **Moving an API key to an environment variable does not eliminate the shared-secret pattern** — OAuth 2.0 is required.

---

## Common Traps

| Trap | Why it's wrong |
|---|---|
| Using a DLP policy to fix record-level access | DLP governs connector groupings, not Dataverse row visibility |
| Assigning System Administrator to an integration user | Violates least-privilege; use a custom scoped security role |
| Using a cloud flow for universal pre-commit validation | Flows run after the event; invalid data can already be read by downstream consumers |
| Using Service Bus when external validation must be in-transaction | Service Bus is async; use a Webhook on a synchronous step instead |
| Using a virtual table when the team expects plug-ins, auditing, offline | Virtual tables lack full native Dataverse behaviors |
| Using a canvas component when the control must also work in model-driven apps | Canvas components are canvas-only; use PCF |
| Thinking "store the API key in an environment variable" removes the shared-secret risk | The secret still exists; only OAuth/Entra eliminates the shared-secret pattern |
| Registering a plug-in for command visibility | Command visibility belongs in the command designer/Power Fx layer, not server-side pipeline |
| Adding a user to an owner team without assigning a security role to the team | Membership ≠ privileges |
| Assuming formula columns work in all scenarios | They do not render in mobile offline mode |
| Using a synchronous plug-in for a 40-second external API call | Blocks the Dataverse request path; use Azure Function triggered asynchronously |
| Reusing a command definition across apps via component library | Commands defined in one app cannot simply be added to another app's command library |

---

## Deeper Exam Detail

This section contains deeper product behavior, edge-case decision rules, and current platform limits. All claims are sourced against Microsoft Learn documentation unless marked "(unverified)".

---

### A. Dataverse Table Types — Deeper Detail

#### Full taxonomy (four types)

The four table types visible in Power Apps are **Standard**, **Activity**, **Virtual**, and **Elastic**. The exam guide covers three; activity tables are a distinct type. [learn.microsoft.com/en-us/power-apps/maker/data-platform/types-of-entities](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/types-of-entities)

#### Activity tables

An activity table is a special sub-type of standard table that models calendar-relevant interactions. Key constraints:

- Activity tables can only be **user- or team-owned**, never organization-owned. You cannot change this after table creation.
- All activity tables share a common base set of columns (Subject, Regarding lookup, Start/End times, Duration, Status) because they all inherit from the `ActivityPointer` base table. Queries across all activity types are possible through `ActivityPointer`.
- Out-of-box activity types: Appointment, Email, Fax, Letter, Phone Call, Recurring Appointment, Task. Custom activity tables (e.g., SMS, chat) can be created via Advanced Options → Type = Activity.
- Once you save an activity table, you **cannot change** the Activity type setting or the "Display in Activity menus" flag.
- Enabling activities on a non-activity table (so that it can appear in the Regarding lookup) is a one-way operation and **cannot be disabled** once enabled.

[learn.microsoft.com/en-us/power-apps/developer/data-platform/activity-entities](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/activity-entities)

#### Table ownership — the third variant

Standard and custom tables have two ownership choices: **User or team** and **Organization**. A few Dataverse system tables use a third type, **Business Unit** ownership (e.g., Business Unit, Calendar, Team, Security Role tables). This variant is not available when creating custom tables. [learn.microsoft.com/en-us/power-apps/maker/data-platform/types-of-entities](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/types-of-entities)

**Critical design-time lock**: Ownership type **cannot be changed** after a table is created. Getting this wrong means deleting and recreating the table.

#### Elastic tables — deeper specifics

Elastic tables are backed by **Azure Cosmos DB** and horizontally partition data using a `partitionid` string column. [learn.microsoft.com/en-us/power-apps/developer/data-platform/elastic-tables](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/elastic-tables)

Key facts not in the core guide:

- **Elastic tables do NOT support multi-record transactions.** `ExecuteTransactionRequest` and Web API `$batch` changesets succeed silently but are **not atomic**. Do not rely on rollback behavior.
- **Deep insert is not supported** on elastic tables. You cannot create related records in one operation; each record must be created individually.
- **PreValidation plug-in stage is safe for throwing errors** on elastic tables. However, throwing `InvalidPluginExecutionException` in `PreOperation` or `PostOperation` returns an error to the caller but does NOT roll back the already-written record — unlike standard tables. Always validate in `PreValidation` for elastic tables.

**What if you need both high-volume storage AND transactional integrity?** A combination of elastic tables (high-volume event log) and standard tables (master record) is the correct design pattern. Do not put transactional cross-record logic on the elastic table side.

#### Virtual tables — data provider options

Virtual tables require a **data provider** registered in Dataverse that handles CRUD operations against the external source. Three approaches exist: [learn.microsoft.com/en-us/power-apps/developer/data-platform/virtual-entities/custom-ve-data-providers](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/virtual-entities/custom-ve-data-providers)

| Data provider approach | When to use |
|---|---|
| OData v4 Data Provider (built-in) | External source exposes an OData v4 interface. No custom code needed for the provider itself. |
| Virtual connector (built-in) | External source is accessible via a Power Platform connector (e.g., SharePoint, SQL). Low-code setup. |
| Custom data provider (code) | External source type is not covered by existing providers. Requires .NET plug-ins registered on Retrieve, RetrieveMultiple, Create, Update, Delete events via the `EntityDataProvider` table. |

A custom data provider plug-in runs at **stage 30** (the main core transaction stage), not at the standard PreValidation/PreOperation/PostOperation stages used for ordinary plug-in steps. The `Microsoft.Xrm.Sdk.Data` NuGet package provides the `QueryExpressionVisitor` framework to translate incoming FetchXML/QueryExpression objects into external source queries.

**What if the virtual table provider times out against the external source?** The custom provider must throw `TimeoutException` from `Microsoft.Xrm.Sdk.Data.Exceptions` to surface a proper error. Generic exceptions will produce cryptic failures.

---

### B. Security and Identity — Full Depth

#### Privilege depth (access levels) — the five-tier model

Each privilege on each table in a security role has one of five access levels. [learn.microsoft.com/en-us/power-platform/admin/security-roles-privileges](https://learn.microsoft.com/en-us/power-platform/admin/security-roles-privileges)

| Level name (UI) | Scope | Notes |
|---|---|---|
| **None** | No access | The privilege is explicitly denied. |
| **User** (Basic) | Records the user owns, or records shared with the user or user's teams | Typical for sales/service reps. Default for new security roles. |
| **Business Unit** (Local) | All records in the user's own business unit | Gives access to peers' records. Requires care — grants access to all BU-owned records. |
| **Parent: Child Business Unit** (Deep) | User's BU plus all subordinate BUs | For managers who oversee multiple sub-units. |
| **Organization** (Global) | All records in the entire environment | Use sparingly; this level trumps all row-level restrictions. |

For **organization-owned** tables (e.g., system configuration tables), the only access levels available are **Organization** or **None** — the user/BU tiers do not apply because there is no individual ownership concept.

**Privilege accumulation rule**: When a user has multiple roles or belongs to multiple teams with roles, the *most permissive* access level for any given privilege wins. You cannot restrict a permission granted by one role using a second role.

**What if you want to hide a single record from a user who has Org-level Read access?** You cannot. All-access grants are additive; there is no "deny" at the record level in standard Dataverse security. This is the documented design: "all privilege grants are cumulative with the greatest amount of access prevailing." Row sharing can only *add* access, not remove it. [learn.microsoft.com/en-us/power-platform/admin/wp-security-cds](https://learn.microsoft.com/en-us/power-platform/admin/wp-security-cds)

#### Eight table privileges

Beyond Create/Read/Write/Delete, two less-obvious privileges matter in design:

- **Append**: Required to attach *another* record to the current record (e.g., adding a Note to an Opportunity). The user acting needs Append on the Note.
- **Append To**: Required on the *parent* record to receive an attachment (e.g., the user adding a Note to an Opportunity also needs AppendTo on the Opportunity).
- **Share**: Required to share a record you own with another user. This is the privilege that enables row sharing.
- **Assign**: Required to change record ownership to another user or team.

#### Owner teams vs. Access teams vs. Microsoft Entra group teams

[learn.microsoft.com/en-us/power-platform/admin/wp-security-cds](https://learn.microsoft.com/en-us/power-platform/admin/wp-security-cds)

| Team type | Can own records | Can have security roles assigned | Membership management | Best for |
|---|---|---|---|---|
| **Owner team** | Yes | Yes | Manual (admin managed) | Shared record ownership and role grants for a stable group |
| **Access team** | No | No | Auto-created per record via Access Team Template; or manual | Per-record sharing with a dynamic group; more performant than row sharing at scale |
| **Microsoft Entra group team** | Yes (when mapped to a BU) | Yes (via group team assignment) | Driven by Entra group membership | SSO-driven automatic access grant when users join/leave Entra groups |

Access teams are more performant than row-level sharing because they do not allow record ownership and do not have security roles; access is purely from the shared record + team membership. Access teams are auto-created per record from a template (Access Team Template) that defines which privilege level (e.g., Read + Write) is granted.

**What if you need a user automatically added to a BU's access when they join an Azure AD group?** Use a **Microsoft Entra group team** mapped to that BU with the appropriate security role. The user appears in Dataverse automatically upon environment access; no manual role assignment needed. [learn.microsoft.com/en-us/power-platform/admin/wp-security-cds](https://learn.microsoft.com/en-us/power-platform/admin/wp-security-cds)

#### Row sharing (Principal Object Access — POA)

Row sharing is stored in the `PrincipalObjectAccess` (POA) system table. Each share creates a row in POA granting a specific user or team a set of privileges on a specific record. Key design considerations:

- Sharing is **performance-intensive at scale**. Microsoft explicitly warns it is "a less performant way of controlling access" and "tougher to troubleshoot." Use it as an exception, not a pattern.
- Sharing can be done with a user or a team. Sharing with a team is more efficient than sharing with many individual users.
- Sharing can **only add** privileges; it cannot reduce them. A user with Org-level Read cannot be "un-shared" to remove that access.
- **Access teams + templates** are the recommended alternative to per-record row sharing for recurring patterns.

#### Column (field) security profiles

Column-level security lets you restrict access to individual columns beyond the record-level security role. [learn.microsoft.com/en-us/power-platform/admin/wp-security-cds](https://learn.microsoft.com/en-us/power-platform/admin/wp-security-cds)

- Can be enabled on custom columns and most system columns that contain PII. Whether a system column supports column security is defined in its metadata.
- A **Column Security Profile** is a named container that specifies Create, Update, and Read access for each secured column.
- Profiles are assigned to users or teams.
- **Column-level security is layered on top of record-level security**: a user must first have access to the record before the column profile applies. A column profile cannot grant access to a record the user cannot already see.
- Overuse of column security adds query overhead. Use it selectively for high-sensitivity fields (e.g., salary, SSN).
- Security roles and column security profiles can be packaged in solutions and moved across environments; Business Units and Teams must be recreated per environment.

---

### C. Logic Placement — Fuller Option List and Current Behavior

The core guide covers plug-ins, Custom API, Power Fx functions, business rules, and client scripts. The following adds Custom Process Actions (workflow actions), background operations, and real-time vs. asynchronous workflow distinctions.

#### Custom API vs. Custom Process Action (workflow action) — full comparison

[learn.microsoft.com/en-us/power-apps/developer/data-platform/custom-api](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/custom-api)

| Dimension | Custom API | Custom Process Action |
|---|---|---|
| Design approach | Code-first (.NET plug-in; no dependency on workflow engine) | Declarative (workflow designer; can be no-code or include plug-in steps) |
| Callable from Power Automate (Dataverse connector) | Yes (as Action) | Yes |
| Callable as Workflow step (classic workflow designer) | Only if `WorkflowSdkStepEnabled = true` (with type restrictions) | Yes natively |
| Is Function (GET/read-only) | Yes (set `Is Function = true`) | No |
| Binding type | Global, Entity, EntityCollection | Global only |
| Can restrict extensibility | Yes (`AllowedCustomProcessingStepType = None`) | No |
| Can be a business event trigger (Power Automate trigger) | Yes (`AllowedCustomProcessingStepType = AsyncOnly`) | No |
| Supported parameter types | Full SDK types (Entity, EntityCollection, StringArray, etc.) | Subset (Boolean, DateTime, Decimal, EntityReference, Float, Integer, Money, Picklist, String, Guid) — Entity/EntityCollection/StringArray are NOT supported for workflow-enabled custom APIs |
| Background operation support | Yes (custom API is required for background operations) | No |
| Microsoft recommendation | Preferred for new developer-defined messages | Acceptable for no-code declarative needs; migrate to Custom API for developer scenarios |

**What if you need to call a custom operation from a classic background workflow?** Set `WorkflowSdkStepEnabled = true` on the Custom API. Note: this forces `Is Function = false` and restricts parameter types to the workflow-compatible subset.

**What if you want a Custom API that no other plug-in can intercept or cancel?** Set `AllowedCustomProcessingStepType = None`. This prevents any third-party step registrations on the message.

#### Synchronous plug-in vs. asynchronous plug-in vs. real-time workflow vs. background workflow

| Execution model | Runs in transaction? | Blocks user/API call? | Can cancel operation? | Use when |
|---|---|---|---|---|
| Sync plug-in (any stage) | Yes (standard tables) | Yes | Yes (PreValidation/PreOperation) | Validation, data modification before/after commit, must be in-transaction |
| Async plug-in (PostOperation async) | No | No | No | Post-commit side effects; long-running tasks acceptable; failures do not roll back the main operation |
| Real-time workflow (synchronous) | Yes | Yes | Yes (if configured) | No-code alternative to sync plug-in for simple step-based logic |
| Background workflow (asynchronous) | No | No | No | No-code long-running automation, approval chains, sequential steps over time |

**Elastic table caveat**: Sync plug-ins registered on PostOperation for elastic tables do NOT roll back the main operation if they throw an error — the record is already written. PreValidation is the only safe stage for rejection logic on elastic tables. [learn.microsoft.com/en-us/power-apps/developer/data-platform/elastic-tables](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/elastic-tables)

#### Background operations (Custom API + async execution)

Background operations use the Custom API mechanism to queue an operation for asynchronous server-side execution. The calling client does not wait for completion. This is distinct from:
- An async plug-in step (which fires as a side effect of a Dataverse message)
- A Power Automate cloud flow (which runs in the Power Automate runtime)

Background operations are appropriate when: the logic is complex, coded in .NET, must run on the Dataverse server, and the caller should not block. [learn.microsoft.com/en-us/power-apps/developer/data-platform/custom-api](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/custom-api)

#### Business rule scope — "Entity" vs. specific form

Business rules have two scope settings:
- **Entity (table)**: The rule fires for all forms associated with the table AND is enforced server-side on save (for certain action types like Set Column Value, Set Business Required, Set Default Value). This is the correct scope for universal enforcement across all app surfaces.
- **Specific form**: The rule fires only for that one form in the model-driven app. Not enforced server-side. Effectively a client-only rule.

**What if a business rule is set to a specific form scope but needs to enforce a required field for all channels?** Change scope to Entity. Only Entity-scope rules participate in server-side validation for applicable action types. [learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-create-business-rule](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/data-platform-create-business-rule)

#### Complete logic placement decision map

| Requirement | Best fit | Why not alternatives |
|---|---|---|
| Block invalid write from ALL channels before commit | PreValidation plug-in | Cloud flow: runs post-commit; business rule set field: not universal enforcement for all action types |
| Modify input data in-transaction before the record is written | PreOperation plug-in | PostOperation: too late to modify the write; PreValidation: runs before transaction begins |
| Post-commit side effect (e.g., send notification) that can tolerate failure | Async PostOperation plug-in | Sync PostOperation: unnecessarily blocks the caller; cloud flow is also valid but adds Power Automate dependency |
| Reusable callable server operation with .NET, structured params, Power Automate callable | Custom API | Custom Process Action: no Function support, parameter type limits |
| Reusable callable operation, no-code, limited types, callable from classic workflow | Custom Process Action | Custom API: requires .NET assembly |
| Conditional field show/hide on ALL forms, no code | Entity-scoped business rule | Form-scoped rule: not enforced on other forms; client script: requires code |
| Conditional field show/hide immediately during user editing (reactive) | Client script | Business rule: does not react to every keystroke; only fires on form load and save events |
| Expose a new Power Automate trigger from Dataverse | Custom API with `AllowedCustomProcessingStepType = AsyncOnly` (business events pattern) | Custom Process Action: cannot create Power Automate triggers |
| Long-running .NET server logic, caller should not wait | Background operation (Custom API) | Sync plug-in: blocks caller; cloud flow: runs in Power Automate runtime, not Dataverse server |
