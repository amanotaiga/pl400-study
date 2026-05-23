# PL-400 Study Guide: Implement Power Apps Improvements (10–15%)

---

## 1. Component Libraries for Reusable Canvas App UI

### Key Facts
- A **component library** is the purpose-built artifact for storing reusable canvas app components that can be shared across multiple apps.
- Components can expose **custom input and output properties**, allowing each consuming app to inject app-specific values (e.g., `StatusText`) while rendering logic stays centralized.
- Component libraries are deployed inside solutions and behave consistently across environments after solution import.
- No custom code is required — component libraries stay within the low-code canvas model (contrast with PCF code components, which require TypeScript/React).

### Decision Rules
| Scenario | Correct Artifact |
|---|---|
| Reusable UI controls (header, badge, footer) shared across multiple canvas apps, centrally updatable | Component library |
| Reuse inside one canvas app only | App-level local component |
| Extend with code (custom rendering, complex interaction) | PCF code component |
| Integrate external services | Custom connector |
| Store configuration per environment | Environment variable |
| ALM packaging and deployment | Solution / solution patch |

### Lifecycle Trap: Update Adoption
- Publishing an updated component library makes the new version **available**, but each consuming app must **adopt the update and be republished** before production reflects the change.
- Symptom: updated library published, but consuming apps still show old style in production.
- Fix: open each consuming app, accept the updated component dependency, republish.

### Common Distractors
- **Solution patch** — ALM mechanism, not a UI reuse mechanism.
- **Environment variable** — stores runtime config, not UI components.
- **Custom connector** — integrates external APIs, not shared UI.
- **PCF package** — valid for code-first components, but fails the "no custom code" requirement.
- **Copying controls between apps** — creates duplication and makes centralized updates impossible.

---

## 2. Canvas App Performance Optimization

### Key Facts
- **App.OnStart** that runs `ClearCollect(colOrders, Orders)` against a large table is a primary cause of slow startup — it pulls the full table client-side before the first screen renders.
- For large Dataverse tables (hundreds of thousands or millions of rows), **direct gallery binding with delegable queries** is always preferred over preloading into collections.
- **`TextInput.DelayOutput = true`** prevents a search query from firing on every keystroke, reducing connector call churn and HTTP 429 throttling.
- **`Concurrent()`** parallelizes independent data loads to reduce total startup wait time, but is only appropriate for small reference lists that are genuinely needed on first screen.
- **Server-side views** pre-filter data before it reaches the app, reducing payload and client-side compute.

### Design Rules
| Situation | Recommended Pattern |
|---|---|
| Large table (>500 rows), search/filter | Direct gallery binding with delegable Filter/StartsWith |
| Small independent reference lists needed at startup | `Concurrent()` with `ClearCollect` |
| Search box issuing too many requests as user types | Set `DelayOutput = true` |
| Pre-filter a large table before querying | Create a server-side Dataverse view |
| Full table preloaded at startup causing slowness | Remove startup `ClearCollect`, use on-demand query |

### What "Raising the Row Limit to 2000" Does NOT Fix
Raising the row limit to 2000 only means the app downloads up to 2000 rows locally for non-delegable processing. It does not fix correctness for tables larger than 2000 rows, does not improve performance, and does not replace delegation. It is never the best answer.

---

## 3. Delegation and Delegable Functions

### Key Facts
- **Delegation** means the data source (e.g., Dataverse) executes the query server-side and returns only matching rows. The app never downloads the full table.
- When a formula is **non-delegable**, Power Apps fetches only the first 500 rows (default) or up to 2000 (if row limit raised) and evaluates locally — producing **silently incomplete results** on large tables.
- Monitor surfaces delegation issues at runtime as a warning that "only the first portion of records was queried."

### Delegable vs. Non-Delegable Patterns (Dataverse)

| Pattern | Delegable? | Notes |
|---|---|---|
| `Filter(Table, StartsWith(col, txt))` | Yes | Preferred search pattern |
| `Filter(Table, col = value)` | Yes | Simple equality |
| `Filter(Table, Left(col, 3) = txt)` | No | String manipulation not pushed to server |
| `Filter(Table, Amount > Value(txt))` | Yes (numeric comparison) | But combining with non-delegable kills delegation |
| `Search(Table, txt, col)` | Yes (Dataverse) | |
| `AddColumns` before server filter | No | Forces client-side evaluation |
| `In` operator against remote source | Depends on source | Often non-delegable |

### Fix Path
1. Identify delegation warnings in the formula bar (yellow triangle) or in Monitor runtime warnings.
2. Remove or replace non-delegable functions with delegable equivalents.
3. Use server-side views to pre-filter instead of complex client-side expressions.
4. Validate with Monitor that the query runs server-side and returns correct records.

---

## 4. Power Fx Formula Optimization

### `Concurrent()` — Parallel Execution
- Runs multiple independent formulas **simultaneously**, reducing total wait when loading several data sources.
- **Critical constraint**: formulas inside the same `Concurrent()` block must not depend on each other. There is no guaranteed execution order within the block.
- Formulas placed **after** `Concurrent()` (chained with `;`) safely execute after all parallel branches finish.

```powerfx
// WRONG — Set depends on colAccounts which may not be loaded yet
Concurrent(
    ClearCollect(colAccounts, Accounts),
    ClearCollect(colContacts, Contacts),
    Set(varTotal, CountRows(colAccounts))   // <-- BAD: dependency inside Concurrent
)

// CORRECT — dependent logic placed after Concurrent
Concurrent(
    ClearCollect(colAccounts, Accounts),
    ClearCollect(colContacts, Contacts)
);
Set(varTotal, CountRows(colAccounts) + CountRows(colContacts))
```

### `With()` — Local Scoped Calculations
- Defines named values local to a single formula; no context or global variables needed.
- Preferred for complex declarative label/property formulas where intermediate values would otherwise be repeated.
- Does not create app state; purely formula-scoped.

### `As` Operator — Disambiguating Record Scopes
- Renames the current record in record-scope functions (`Filter`, `AddColumns`, `ForAll`, etc.).
- Resolves ambiguity when nesting multiple record-scoped functions where column names collide.
- Preferred over relying on `ThisItem` / `ThisRecord` in deeply nested formulas.

### `ForAll()` — Iteration Constraints
- Records in `ForAll` can be processed **in any order and in parallel** — do not assume sequential execution.
- `UpdateContext`, `Clear`, and `ClearCollect` cannot be used inside `ForAll`.
- Running totals or order-dependent accumulation inside `ForAll` will produce inconsistent results.
- Fix: move aggregate calculations (e.g., `Sum`) outside `ForAll`; keep per-record actions inside.

### `Sequence()` — Generating Numeric Tables
- Generates a single-column table of sequential numbers (e.g., 1–12 for a month selector) directly in Power Fx without manually building a collection.

---

## 5. Canvas App and Cloud Flow Integration

### Invoking a Cloud Flow from a Button

Correct sequence to wire an existing flow to a canvas app button:
1. **Add the flow** from the Power Automate pane (flow must have a Power Apps trigger).
2. **Select the button's `OnSelect` property**.
3. **Enter `FlowName.Run(params)`** in the formula bar.
4. **Test** in Play mode.

The flow cannot be referenced in a formula until it has been added to the app context. Step order matters.

### Returning Data from a Flow to a Canvas App
- Problem: flow runs successfully but app cannot capture output.
- Cause: flow is missing the **"Respond to a PowerApp or flow"** action. A `Compose` action creates a value inside the flow but does not expose it back to the caller.
- Fix: add the **"Respond to a PowerApp or flow"** response action with explicit output parameters.

### Async Flow vs. Transactional Plug-in — When to Use Which

| Requirement | Correct Component |
|---|---|
| Multi-connector orchestration (Dataverse + SharePoint + Teams), user continues immediately | Cloud flow (async) |
| Immediate validation, rollback on failure, enforced for ALL write paths (all apps + APIs) | Dataverse plug-in |
| Simple field validation on a single form, no code | Business rule |
| Canvas-app only, simple formula logic | Power Fx in the app |

### Orphaned Flow Reference
- Flows added via an **older version of the Power Apps panel** can become orphaned after app edits.
- Symptom: flow disappears from app, reference no longer available.
- Fix: **re-add the flow manually** from the Power Automate pane. This is a documented operational issue, not an architectural redesign problem.

---

## 6. Monitor Tool and Runtime Debugging

### What Monitor Shows
- Connector call timings, HTTP response codes (including 429 throttling), request/response payloads.
- Control events, formula evaluation traces.
- Delegation warnings ("only the first portion of records was queried").
- Works for both **studio sessions** (authoring) and **published app sessions** (production debugging).

### Monitor Diagnostic Workflow
Correct troubleshooting order:
1. **Start a fresh Monitor session** (clean capture, no stale noise).
2. **Reproduce the failing action**.
3. **Correlate Monitor events** with browser console and Network tab.
4. **Retest** after isolating and addressing the cause.

### Monitor vs. Browser DevTools

| Scenario | Best First Tool |
|---|---|
| Canvas app connector calls, timing, delegation issues | Monitor |
| Model-driven app JavaScript error, click handler not firing | Browser DevTools |
| Need to confirm browser-side script execution + network request | Browser DevTools |
| Cross-tool correlation of app events + network | Monitor + DevTools together |

### Common HTTP 429 Pattern
- Multiple connector calls in a short window + HTTP 429 responses in Monitor = **connector throttling**.
- Root cause: app issues too many requests (e.g., per-keystroke search queries).
- Fix: `DelayOutput = true` on the search input, or restructure to reduce redundant calls.

---

## 7. Model-Driven App Performance

### Form Load Optimization
- **Collapsed tabs**: move heavy subgrids/components off the initially expanded area so they are not rendered on first load. Users can still expand them when needed.
- **Role-specific forms**: deliver a lighter form to users who need fewer fields/components (e.g., sales reps vs. managers). Reduces scripts, subgrids, and related data loaded per persona.
- **Defer JavaScript Web API calls**: if data is only needed when a secondary tab is opened, do not fetch it in the `onLoad` handler. Fetch on demand.

### View Optimization
- **Trim default view columns**: fewer columns = less data fetched and rendered on the landing list.
- **Use narrow owner-filtered views as default** (e.g., "My Open Accounts") on large tables: reduces row count dramatically vs. "All Open Accounts."

### Model-Driven Form Optimization Decision Table

| Problem | Fix |
|---|---|
| Subgrid loaded but rarely used immediately | Collapse tab containing subgrid |
| One form overloaded for multiple personas | Create role-specific forms |
| JavaScript fetching data not needed at first render | Defer Web API call to user action |
| Landing view slow on million-row table | Use owner-filtered view, trim columns |
| Too many unnecessary columns in default view | Remove non-essential columns from view |

---

## 8. Quick-Fire Facts

- `Concurrent()` requires that formulas inside it are **independent** — no branch may reference another branch's output.
- `With()` is the preferred Power Fx pattern for local intermediate values in a single declarative formula — no variables needed.
- `As` renames the current record in nested record-scope formulas to resolve column name ambiguity.
- `Sequence()` generates a table of sequential numbers inline without a collection.
- `ForAll()` does not guarantee order; do not accumulate running totals inside it.
- `Left()`, `Mid()`, `Right()` on a column inside `Filter` = **non-delegable** against Dataverse.
- `StartsWith()` on a column inside `Filter` = **delegable** against Dataverse — preferred search pattern.
- `AddColumns` before a server-side filter forces client-side evaluation — non-delegable.
- Raising row limit to 2000 does **not** fix delegation problems on tables > 2000 rows.
- Component library components must be **adopted and the app republished** before updates appear in production.
- A canvas app component exposes **input properties** so consuming apps can inject values while keeping rendering logic central.
- Cloud flow must have a **Power Apps trigger** to be addable to a canvas app.
- "Respond to a PowerApp or flow" action is required to return output from a flow to a canvas app.
- `DelayOutput = true` on `TextInput` reduces per-keystroke connector calls.
- Monitor's **published app debugging** mode enables production-level runtime trace without modifying the app.

---

## 9. Common Traps

1. **Raising the row limit instead of fixing delegation** — the exam always prefers delegation over a higher cap.
2. **Keeping `Set()` or aggregate logic inside `Concurrent()`** — dependent formulas must go after `Concurrent()`, not inside it.
3. **Using a cloud flow when a plug-in is needed** — if the requirement says "enforced for all write paths" or "rollback on failure," the answer is a plug-in, not a flow.
4. **Forgetting the "Respond to a PowerApp or flow" action** — a flow that doesn't include this action cannot return values to the calling app, even if it runs successfully.
5. **Not republishing consuming apps after a component library update** — publishing the library is not enough; each app must adopt the new version and be republished.
6. **Using `ClearCollect` on large tables at startup** — always the wrong pattern for large transactional tables; use direct delegable gallery binding instead.
7. **Running Web API calls in `onLoad` for data used only on secondary tabs** — defer the call to when the user actually needs the data.
8. **Choosing Monitor for JavaScript click-handler debugging** — Browser DevTools is the correct first tool for client-side script and network inspection in model-driven apps.
9. **Placing running-total logic inside `ForAll`** — ForAll can run in any order; aggregates like `Sum` must go outside the loop.
10. **Assuming a component library update is instant** — the library lifecycle and the consuming-app lifecycle are independent; updates require explicit adoption.

---

## Deeper Exam Detail

This section contains fuller function lists, current platform limits, tooling specifics, and edge-case decision rules sourced directly from Microsoft Learn.

---

### A. Delegation deep-dive: full per-data-source function tables

#### Default and maximum row limits

- The non-delegable result cap defaults to **500 rows**. It can be raised to a maximum of **2,000 rows** via **Settings > General > Data row limit** (range 1–2,000). [Source: Understand delegation in a canvas app](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/delegation-overview)
- Diagnostic tip: set the row limit to **1** during development. Any non-delegable query returns exactly one record, making incomplete-result bugs immediately obvious in testing before the app ships to production. [Source: Understand delegation in a canvas app](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/delegation-overview)
- Delegation warnings appear as a **blue wavy underline** (not yellow triangle) in the formula bar when a formula uses a delegable data source but contains a non-delegable expression.

#### Delegable vs. non-delegable: Dataverse

Full reference table per data type (Number, Text, Choice, DateTime, Guid). [Source: Connect to Microsoft Dataverse](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-common-data-service)

| Function / Operator | Number | Text | Choice | DateTime | Guid |
|---|---|---|---|---|---|
| `<`, `<=`, `>`, `>=` | Yes | Yes | No | Yes | — |
| `=`, `<>` | Yes | Yes | Yes | Yes | Yes |
| `And` / `Or` / `Not` | Yes | Yes | Yes | Yes | Yes |
| `Filter` | Yes | Yes | Yes | Yes | Yes |
| `Search` | No | Yes | No | No | — |
| `StartsWith` | — | Yes | — | — | — |
| `In` (membership) | Yes | Yes | Yes | Yes | Yes |
| `In` (substring) | — | Yes | — | — | — |
| `IsBlank` | Yes | Yes | No | Yes | Yes |
| `Lookup` | Yes | Yes | Yes | Yes | Yes |
| `First` | Yes | Yes | Yes | Yes | Yes |
| `Sort` / `SortByColumns` | Yes | Yes | Yes | Yes | — |
| `Sum`, `Min`, `Max`, `Avg` | Yes (up to 50,000 rows) | — | — | No | — |
| `CountRows` / `CountIf` | Yes | Yes | Yes | Yes | Yes |
| `UpdateIf` / `RemoveIf` | Simulated (500/2,000 cap) | — | — | No | — |

**Key Dataverse-specific caveats:**

**Delegation**

- `Search` is delegable for **Text columns only** — not delegable for Number, Choice, or DateTime
- **Arithmetic inside `Filter`** (e.g., `field + 10 > 100`) breaks delegation even for numeric columns
- These text functions inside `Filter` are **not delegable**: `Left`, `Mid`, `Right`, `Upper`, `Lower`, `Len`, `Trim`, `Substitute`, `Replace`
- `StartsWith` and `EndsWith` **are** delegable
- `Text(column)` type casting inside `Filter` is **not delegable**

**Row Count**

- `CountRows` uses a **cached** row count
- For a precise live count under 50,000 rows, use `CountIf(table, true)` instead

**Aggregate Functions**

- `Sum`, `Min`, `Max`, `Avg` are limited to **50,000 rows**
- Not supported on **views**

**Query Limits**

- The `In` membership operator is subject to Dataverse's **15-table query limit**
- Lookup expansion is limited to **2 levels**; a single query can join up to **20 entities** [Source: Connect to Microsoft Dataverse](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-common-data-service)

**Direct Dataverse Actions (Power Fx)**

- Available by default in **new apps** via the `Environment` language object
- For **older apps**: enable via `Settings > Upcoming features > Retired > Dataverse actions`
- Replaces many Power Automate flows that only call Dataverse [Source: Connect to Microsoft Dataverse](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-common-data-service)

#### Delegable vs. non-delegable: SharePoint

[Source: Connect to SharePoint from a canvas app](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/connection-sharepoint-online)

| Function / Operator | Number | Text | Boolean | DateTime | Complex (Choice, Person, Lookup) |
|---|---|---|---|---|---|
| `=` | Yes | Yes | Yes | Yes | Yes |
| `<`, `<=`, `>`, `>=`, `<>` | Yes | No | No | Yes | Yes |
| `Filter` | Yes | Yes | Yes | Yes | Yes |
| `Lookup` | Yes | Yes | Yes | Yes | Yes |
| `Sort` / `SortByColumns` | Yes | Yes | Yes | Yes | No |
| `StartsWith` | — | Yes | — | — | Yes (not on Choice/Lookup subfields) |
| `IsBlank` | — | No | — | — | No |
| `UpdateIf` / `RemoveIf` | Simulated (500/2,000 cap) | No | — | — | No |

**Key SharePoint-specific caveats:**
- `And` / `Or` are delegable; `Not` is **not** delegable to SharePoint.
- SharePoint system fields (e.g., `IsFolder`, `ContentType`, `VersionNumber`, `Path`) do **not** delegate.
- SharePoint ID fields appear as Number in Power Apps but the underlying type is Text — only `=` delegates on ID; relational operators (`<`, `>`, etc.) do not.
- For Complex types (Choice, Person, Lookup), only `Email` and `DisplayName` subfields of Person are delegable.
- `IsBlank` on Text columns does not delegate to SharePoint. Workaround: use `Filter(..., col = Blank())` for `=` comparisons, which does delegate (though it does not treat empty string as blank — be aware of semantic difference).

#### Delegable vs. non-delegable: SQL Server

[Source: Connect to SQL Server from Power Apps overview](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections/sql-connection-overview)

| Function / Operator | Number | Text | Boolean | DateTime | Guid |
|---|---|---|---|---|---|
| `=`, `<>` | Yes | Yes | Yes | Yes | Yes |
| `<`, `<=`, `>`, `>=` | Yes | No | No | Yes | — |
| `+`, `-`, `*`, `/` | Yes | — | — | No | — |
| `Filter` | Yes | Yes | Yes | Yes | Yes |
| `Search` | No | Yes | No | No | — |
| `StartsWith` | — | Yes | — | — | — |
| `EndsWith` | — | Yes | — | — | — |
| `In` (substring) | — | Yes | — | — | — |
| `Lookup` | Yes | Yes | Yes | Yes | Yes |
| `Sort` / `SortByColumns` | Yes | Yes | Yes | Yes | — |
| `Sum` | Yes | — | — | — | — |
| `Average` | Yes | — | — | — | — |
| `Min` / `Max` | Yes | — | — | No | — |
| `Len` | — | Yes (varchar only) | — | — | — |
| `IsBlank` | No | No | No | No | No |
| `UpdateIf` / `RemoveIf` | Simulated (500/2,000 cap) | Yes | Yes | Yes | Yes |

**Key SQL Server-specific caveats:**
- `IsBlank` is **not** delegable for SQL Server on any data type. Workaround: `Filter(..., col <> Blank())`.
- `Len` delegates but behaves unexpectedly on `char(N)` columns, which always report length N. Use `varchar`/`nvarchar` to avoid this.
- `EndsWith` is delegable but only when the column is on the left side: `EndsWith(column, "value")`. Reversing the arguments breaks delegation.
- Direct date filters via an on-premises Data Gateway for SQL Server do not delegate. Workaround: add a computed column in SQL (e.g., `DateAsInt AS YEAR(date)*10000 + MONTH(date)*100 + DAY(date)`) and filter on the integer column.
- Arithmetic operators (`+`, `-`, `*`, `/`) delegate for Number but not DateTime.

#### What if... delegation edge cases

| Scenario | Behavior |
|---|---|
| Formula mixes one delegable and one non-delegable expression with `And` | The **entire** `Filter` becomes non-delegable. Both sides must be delegable to push the query server-side. |
| `AddColumns` wraps a table before `Filter` | Forces client-side evaluation — the entire expression is non-delegable regardless of what `Filter` contains. |
| Entity property is on the right-hand side of `=` in Dataverse `Filter` | Non-delegable. The entity property **must** be on the left-hand side: `Filter(Table, col = value)` not `Filter(Table, value = col)`. |
| `In` with a related table column (e.g., `PrimaryContact.Fullname`) | Non-delegable. `In` only delegates for columns on the base (root) table. |
| `Sort` with a formula (e.g., `Sort(table, Left(col,3))`) | Non-delegable. `Sort` only accepts a single column name — no transformations. |

---

### B. App.Formulas (named formulas) and OnStart — full behavioral differences

[Source: App object in Power Apps](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/object-app)

| Characteristic | `App.OnStart` | `App.Formulas` (named formulas) |
|---|---|---|
| Evaluation model | Imperative, sequential | Declarative, lazy (deferred until value is needed) |
| Timing dependency | Must complete before first screen renders (blocks startup) | No timing dependency; can reference each other in any order |
| Can be mutated elsewhere in app | Variables set here can be overwritten by any `Set()` | Immutable — definition is the single source of truth |
| Can use behavior functions (`Set`, `Collect`, `Navigate`) | Yes | No (except via behavior user-defined functions wrapped in `{}`) |
| Studio load time improvement | Baseline | Up to **80% faster** Studio load when `OnStart` variables are migrated to named formulas |
| Auto-update when dependencies change | No — runs only at startup | Yes — recalculates automatically when referenced data changes |
| Circular references | Not enforced | Not allowed; causes a studio error |
| Available in `StartScreen` | No | Yes |

**Named formula constraints:**
- Cannot call behavior functions (`Set`, `Collect`, `Navigate`, `Patch`, etc.) unless wrapped in a behavior user-defined function using `{}` syntax.
- Cannot create circular references (`a = b; b = a;` is a compile error).
- Type is inferred — no explicit type annotation required for data named formulas.
- Can call each other in any order (the system resolves dependencies automatically).

**`App.OnStart` current status:**
- Microsoft documentation explicitly warns: "Using the OnStart property can cause performance problems when loading an app." It may be disabled by default in future. The `StartScreen` property and named formulas are the recommended replacements.
- Non-blocking `OnStart` (a preview feature) allows screens to render before `OnStart` finishes — meaning variables initialized in `OnStart` may not be ready when a screen's `OnVisible` or control formulas evaluate them. Named formulas avoid this race condition entirely.

**User-defined functions (UDF) in App.Formulas:**
- Power Fx now supports parameterized named formulas (user-defined functions): `FunctionName(Param: Type): ReturnType = formula;`
- Behavior UDFs (with side effects) use curly-brace syntax: `FunctionName(Param: Type): Void = { Set(x, y); Patch(...); };`
- Recursion is not yet supported in UDFs.
- UDFs cannot be used directly in Power Fx commanding (ribbon/command bar).

---

### C. Canvas performance — additional limits, patterns, and tooling

#### Control count and app size

- Solution Checker rule `app-reduce-screen-controls` fires at the **Medium** severity level when a screen has too many controls, signaling a performance risk. There is no single hard numeric control-count limit documented, but guidance recommends keeping screen control counts low. [Source: Solution Checker rules](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/use-powerapps-checker)
- Solution Checker also flags `app-use-delayoutput-text-input` (Medium / Performance) when a `TextInput` control does not have `DelayOutput = true`, indicating an authoring-time best-practice check, not just a runtime recommendation. [Source: Solution Checker rules](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/use-powerapps-checker)

#### Caching pattern with collections

- The correct pattern is to cache **small, relatively static** reference data (e.g., a lookup table of 50 countries). Do not cache large transactional tables.
- After caching with `ClearCollect`, subsequent reads are instant (memory) and require no network calls, so `Concurrent()` is valuable here: it eliminates the sequential wait when loading multiple small reference collections.
- Collections and context variables do not participate in delegation and are not subject to the non-delegable row limit — all rows cached into a collection are available locally.

#### Additional anti-patterns flagged by Microsoft documentation

- **Overloading `OnStart`**: every formula in `OnStart` must complete before the first screen renders. Each additional `ClearCollect` or `Set` in `OnStart` adds to this blocking wait. Migrate to named formulas to defer evaluation.
- **`Timer` controls with short `Duration`**: frequent timer firings generate many connector calls in a short window, causing 429 throttling (visible in Monitor as "Rate limit exceeded").
- **`CountRows` on large Dataverse tables**: `CountRows` on Dataverse uses a cached value, not a live count. If an app shows a live progress counter that calls `CountRows` (or `CountIf`) per record in a `ForAll` loop, each iteration generates a `getRows` request — Monitor will show a cascade of requests leading to 429 errors. [Source: Debugging canvas apps with Live monitor](https://learn.microsoft.com/en-us/power-apps/maker/monitor-canvasapps)

---

### D. Component libraries — additional properties, customization, and ALM behavior

[Source: Component library](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/component-library) | [Source: Canvas component properties](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/component-properties)

#### Four types of canvas component custom properties

| Property Type | Direction | Can use behavior functions? | Participates in data flow? | Typical use |
|---|---|---|---|---|
| **Data – Input** | App → Component | No | Yes | App injects a color, text, or record into the component |
| **Data – Output** | Component → App | No | Yes | Component exposes a calculated/selected value back to the app |
| **Function – Output** | Component → App (callable by app) | No | No | Reusable calculation exposed as a function the app calls |
| **Function – Input** | App → Component (callback) | No | No | App provides custom logic the component calls (callback pattern) |
| **Action** | Component → App (side-effects) | Yes | No | Component exposes a `Reset()` or `Save()` with side effects |
| **Event** | App → Component (called by component) | Yes | No | Component fires `OnButtonClicked`; app defines what happens |

- Function properties cannot access component-internal variables or trigger data flow — all required values must be passed as arguments.
- Action and Event properties support chained expressions and can mutate collections and variables (behavior formulas).
- **Code components (PCF) are explicitly not supported inside component libraries.** A component library can only contain canvas components. [Source: Component library](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/component-library)

#### Customization and library link breaking

- By default, every component has **Allow customization** set to **On**. When a consuming app selects "Edit component" on such a component, Power Apps copies the component locally and **severs the link to the library**. The local copy receives no future library updates.
- Setting **Allow customization = Off** prevents consuming apps from breaking the library link. The only edit path is through the source library.
- When a local copy exists alongside library-linked instances, only the local copy instances are affected by local edits; library-linked instances remain synced.

#### Library deletion protection

- A component library cannot be deleted if any canvas app still references it. The deletion attempt will show affected app dependencies. Remove the component from all consuming apps before deleting the library.

#### Sharing component libraries to security groups (ALM edge case)

- Component libraries in solutions cannot use the standard sharing UI for security groups. Use the PowerShell cmdlet `Set-AdminPowerAppRoleAssignment` with `CanEdit` permission level instead. [Source: Component library](https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/component-library)

---

### E. Monitor tool — full capabilities and session sharing

[Source: Live monitor overview](https://learn.microsoft.com/en-us/power-apps/maker/monitor-overview) | [Source: Debugging canvas apps with Live monitor](https://learn.microsoft.com/en-us/power-apps/maker/monitor-canvasapps)

#### Event columns captured by Monitor

| Column | What it shows |
|---|---|
| Id | Sequence number |
| Time | Timestamp of event |
| Category | Event type: `Network`, `UserAction`, `Trace`, etc. |
| Operation | Internal operation name (e.g., `createRow`, `getRows`, `navigateTo`) |
| Result | Human-readable status (e.g., `Error`, `Success`) |
| Result Info | Translated detail (e.g., `"Too many requests"` for HTTP 429) |
| Status | HTTP status code (200, 429, 400, etc.) |
| Duration | Milliseconds for the request round-trip |
| Data Source | Name of the Dataverse table or connector accessed |
| Control | Control that triggered the event |
| Property | The control property that evaluated (e.g., `Items`, `OnSelect`) |
| Response size | Bytes received from the data source |

Selecting any event opens a panel with four tabs: **Details**, **Formula** (the Power Fx expression that triggered the event), **Request** (outbound HTTP), **Response** (JSON payload).

#### Published app debugging — "Debug published app" setting

- To see source expressions (formula text) in Monitor for a published app, enable **File > Settings > Debug published app** before publishing. This setting publishes expression metadata alongside the app.
- **Warning**: enabling this setting has a performance impact on all users. Disable it as soon as debugging is complete. [Source: Debugging canvas apps with Live monitor](https://learn.microsoft.com/en-us/power-apps/maker/monitor-canvasapps)

#### Sharing a Monitor session (mobile debugging)

- For apps running on **Power Apps Mobile**, copy the monitor link via **Copy monitor link** (available at `make.preview.powerapps.com`) and open it on the device using the Power Apps mobile app (not a browser). This creates a connected Monitor session for the device. [Source: Debugging canvas apps with Live monitor](https://learn.microsoft.com/en-us/power-apps/maker/monitor-canvasapps)

#### Security roles required for Monitor

| App type | Required role |
|---|---|
| Canvas app | Environment Admin or Environment Maker |
| Model-driven app | System Administrator or System Customizer |

#### `Trace()` function integration

- Calling `Trace("message", TraceSeverity.Information)` in a Power Fx formula emits a custom event visible in Monitor under the `Trace` category. Use it in `App.OnError` to log error details without surfacing an error banner to users:
  ```powerfx
  App.OnError = Trace($"Error {FirstError.Message} in {FirstError.Source}")
  ```
  To also show the default error banner, rethrow after the trace: `Trace(...); Error(FirstError)`. [Source: App object in Power Apps](https://learn.microsoft.com/en-us/power-platform/power-fx/reference/object-app)

---

### F. Solution Checker — rule categories and canvas-app-specific rules

[Source: Improve component performance, stability, and reliability with solution checker](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/use-powerapps-checker)

#### What Solution Checker analyzes

- Dataverse custom workflow activities (plug-ins)
- Web resources (HTML and JavaScript) — ES6 through ES9 syntax supported; later syntax flagged as `web-unsupported-syntax`
- Dataverse configurations (SDK message steps)
- Power Automate flows (via embedded Flow Checker)
- Power Fx expressions in canvas apps (via App Checker integration)
- Desktop flows

#### Report severity levels: Critical, High, Medium, Low, Informational

- **Critical** violations are **blocked or warned** when Solution Checker enforcement is configured in Managed Environments.

#### Canvas app-specific Solution Checker rules

| Rule ID | Description | Severity | Category |
|---|---|---|---|
| `app-formula-issues-high` | Formula errors in canvas app | Critical | Design |
| `app-formula-issues-medium` | Formula warnings | Medium | Design |
| `app-formula-issues-low` | Formula informational issues | Low | Design |
| `app-use-delayoutput-text-input` | TextInput without `DelayOutput = true` | Medium | Performance |
| `app-reduce-screen-controls` | Too many controls on a screen | Medium | Performance |
| `app-include-accessible-label` | Controls missing explicit accessibility labels | Medium | Accessibility |
| `app-include-alternative-input` | Interactive elements not keyboard-accessible | Medium | Accessibility |
| `app-avoid-autostart` | Media player with autostart enabled | Medium | Accessibility |

#### Key web-resource rules relevant to model-driven app developers

| Rule ID | Severity | Category | Meaning |
|---|---|---|---|
| `use-async` | Critical | Performance | All HTTP/HTTPS calls must be async |
| `avoid-eval` | Critical | Security | `eval()` and equivalents are banned |
| `avoid-ui-refreshribbon` | Critical | Performance | Do not call `refreshRibbon` in form `onLoad` or `EnableRule` |
| `use-getsecurityroleprivilegesinfo` | High | Performance | Use `getSecurityRolePrivilegesInfo` instead of `securityRolePrivileges` |
| `avoid-modals` | High | Supportability | Modal dialogs are not supported |
| `avoid-browser-specific-api` | Critical | Upgrade readiness | IE-specific APIs are banned |

#### Solution Checker vs. App Checker

| Tool | When it runs | What it covers | Output location |
|---|---|---|---|
| **App Checker** | Inside Power Apps Studio, on-demand (toolbar icon) | Formula errors and accessibility issues in the current canvas app | In-studio panel |
| **Solution Checker** | On an exported unmanaged solution (portal or PowerShell) | Canvas apps + plug-ins + web resources + flows + desktop flows in the full solution | Portal report + email + downloadable Excel |

- Solution Checker does **not** guarantee a successful solution import — it performs static analysis only and does not know the destination environment's state.
- Run Solution Checker rules locally during development for JavaScript/TypeScript web resources using the npm package `@microsoft/eslint-plugin-power-apps`.

---

### G. Cloud flow integration — edge cases and error handling

#### Power Apps trigger parameter passing

- When a canvas app calls a flow with `FlowName.Run(param1, param2)`, the parameters must be declared in the Power Apps trigger and appear in that exact order. Renaming a parameter in the flow after wiring the app button breaks the call (the app holds positional references).
- A flow can only be added to a canvas app if it has a **Power Apps (V2) trigger** (or legacy "Power Apps" trigger). Flows with other triggers (e.g., manual, scheduled) are not available in the Power Automate pane.

#### Returning multiple output values

- The "Respond to a PowerApp or flow" action supports multiple named output parameters. Each parameter becomes a property on the object returned by `FlowName.Run(...)`. Access them as `FlowName.Run(...).outputParamName` in Power Fx.
- If the flow errors before reaching the "Respond" action, the `.Run()` call in the app returns an error. Wrap with `IfError(FlowName.Run(...), <fallback>)` to handle gracefully.

#### Async vs. synchronous behavior

- By default, a canvas app button that calls a flow **waits synchronously** for the flow to complete and return before the `OnSelect` formula continues. Long-running flows block the UI during this wait.
- For flows that take more than a few seconds, consider using a separate "trigger and forget" pattern: the flow writes status to a Dataverse table, and the app polls or uses a timer to check status. This keeps the UI responsive.

#### Orphaned flow references (additional detail)

- Flows added via the older Power Apps panel (pre-2021 connector model) can lose their reference when the app is re-opened after the flow is modified in Power Automate. The app's formula bar may still show `FlowName.Run(...)` but the flow no longer appears in the data panel.
- Fix: remove the broken reference, re-add the flow from the Power Automate pane, and update the formula. Do not rename the flow between app edits, as the name is part of the reference.

---

### H. Model-driven app Monitor specifics

[Source: Live monitor overview](https://learn.microsoft.com/en-us/power-apps/maker/monitor-overview)

- For model-driven apps, Monitor captures: **page navigation**, **command executions**, **form load events**, **Web API requests** (createRecord, retrieveRecord, updateRecord), and **JavaScript errors**.
- Monitor for model-driven apps requires **System Administrator or System Customizer** role — a higher privilege than canvas apps (which only need Environment Maker).
- Monitor does **not** replace Browser DevTools for debugging custom JavaScript in model-driven apps. Monitor shows the event stream at the app level; DevTools shows the actual JavaScript call stack, breakpoints, and network requests at the browser level. Use Monitor first to identify which operation is failing, then use DevTools to inspect the specific JavaScript execution.

---

### I. Quick-reference: "What if..." decision rules not in the exam section

| Scenario | Decision |
|---|---|
| Need a delegable search that matches anywhere in a string (not just start) | Use `Search(table, txt, "colName")` for Dataverse/SQL (delegable); `StartsWith` only matches the beginning. `In` (substring) is delegable for SQL text columns but not Dataverse text. |
| Need to filter on a related table column (e.g., Account.Owner.Name) | Likely non-delegable in most data sources. Create a server-side Dataverse view with the filter pre-applied instead. |
| `CountRows` appears correct in the app but mismatches actual table count | Dataverse `CountRows` uses a cached value. Use `CountIf(table, true)` for a live, accurate count (works for tables under 50,000 rows). |
| Component update was published but a specific consuming app did not receive it | The maker must open the consuming app, use the "Check for updates" option in the Insert pane, review changes, and republish — this cannot be forced from the library side. |
| Named formula references another named formula that hasn't been "defined yet" in the Formulas property | No problem — named formulas can reference each other in any order. The system resolves dependency order automatically (no circular reference allowed). |
| App needs to pass a table/record type to a user-defined function | Declare the type using `Type()` and reference it in the function signature. Use `RecordOf(TableType)` to extract the record type from a table type for single-record parameters. |
| Solution Checker flags `use-async` as Critical on a web resource | The JavaScript is making a synchronous XMLHttpRequest. Rewrite using `XMLHttpRequest` with `async=true` or use the Fetch API / Xrm.WebApi async methods. |
| Want to debug a canvas app issue reported by a remote user without giving them studio access | Use **Monitor** published-app mode: from the Apps list, select the app > Live monitor > Play published app. A separate browser tab opens the published app connected to your Monitor session. Alternatively, send the user a **Copy monitor link** for Mobile. |
