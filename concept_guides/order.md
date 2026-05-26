# Order & Sequences

The PL-400 exam loves "put these steps in the correct order" and "what runs first"
questions. This page gathers **every ordered sequence** scattered across the six
domain guides into one place. For each one: the steps, **why the order is what it
is** (the concept, not just memorization), and the trap that makes the wrong order
look tempting.

> How to use this page: don't memorize the lists cold. Read the **"Why this order"**
> line under each — almost every exam ordering question is solvable from the
> underlying rule (e.g. "reject before the transaction opens", "you can't reference
> a thing before it exists").

---

## 1. Plug-in Execution Pipeline (stages, in order)

**PreValidation → PreOperation → Main Operation → PostOperation**

| Stage | When it runs | Use it to |
|---|---|---|
| PreValidation | Outside the DB transaction | Reject bad data cheaply (no rollback cost) |
| PreOperation | Inside the transaction, before write | Mutate the incoming values |
| Main Operation | The core Dataverse write | (platform / data providers) |
| PostOperation | Inside transaction (sync) or after (async) | React once the record exists |

**Why this order:** it mirrors the life of a save request — *validate the request →
adjust the data → write it → react to the written record*. The transaction "opens"
between PreValidation and PreOperation, which is the whole point of the ordering.

**Trap:** PreOperation *sounds* earlier/safer than PostOperation, so people validate
there. Wrong — **PreValidation** runs *outside* the transaction, so rejecting there
avoids the rollback cost entirely. "Reject early, reject outside the transaction."

---

## 2. Plug-in Registration Sequence

1. **Register the assembly** (the compiled DLL)
2. **Register the step** (message + table + stage + mode)
3. **Configure step details** (filtering attributes, entity images)
4. **Add the assembly to the unmanaged solution**
5. **Add the step to the unmanaged solution**

**Why this order:** each item **can't exist until its parent exists** — a step
belongs to an assembly, step details belong to a step. Then solution packaging
(4–5) comes last because you can only add things to a solution once they exist.

**Trap:** forgetting steps 4–5 — the plug-in *works* in the dev environment but
isn't in the solution, so it never travels to Test/Prod.

---

## 3. Expose a Custom API as a Business Event (Catalog hierarchy)

1. **Create the root Catalog**
2. **Create a Category** under the catalog
3. **Create the CatalogAssignment** linking the Custom API (or table) to the category

**Why this order:** classic parent-before-child — a category needs a catalog to live
in, and the assignment needs both a category to point *to* and the API to point *at*.

**Trap:** stopping after step 2. The **CatalogAssignment** is the link that actually
publishes the action as a business event; without it the hierarchy looks complete but
does nothing.

---

## 4. Register Dataverse → Azure Messaging (Service Bus / Event Hub)

1. **Register a service endpoint** — defines the Azure target, contract type, and auth
2. **Register a step** — binds the Dataverse event (message + table) to that endpoint

**Why this order:** the step has to point at an endpoint, so the endpoint must exist
first. (Same parent-before-child logic as plug-in registration — the endpoint plays
the role the assembly plays for plug-ins.)

**Trap:** in the Azure-aware plug-in, referencing the business table name (e.g.
`"account"`) instead of `"serviceendpoint"` as the EntityReference.

---

## 5. Change Tracking — Initial Setup Sequence

1. **Enable "Track changes"** on the table
2. **Send the initial request** with the `Prefer: odata.track-changes` header
3. **Process the returned rows**, including deleted-entity entries
4. **Persist the `@odata.deltaLink`** for the next incremental cycle

**Why this order:** you can't ask for changes (2) until tracking is on (1); you can't
get a delta link to save (4) until you've made the baseline call (2–3). Each step
produces the input the next one needs.

**Trap:** an **expired** delta token cannot be retried or extended — you must restart
the baseline sync from step 2.

---

## 6. Recommended Inbound/Outbound Integration Pattern (full lifecycle)

1. Define an **alternate key** on the business-identifier column
2. Use **UpsertRequest** (SDK) or **PATCH by alternate-key URL** (Web API) for inbound writes
3. Enable **change tracking** for outbound deltas
4. **Persist the `@odata.deltaLink`** after each cycle
5. Handle **deleted-entity entries** in delta responses
6. Handle **429 (throttling)** with `Retry-After` backoff

**Why this order:** it's two pipelines stitched together — inbound (1–2: identify by
business key, then upsert) then outbound (3–5: track and pull deltas) — with
resilience (6) wrapping both. The alternate key comes first because upsert *depends*
on it.

---

## 7. ALM CI/CD — Source-Control Sequence (Dev → Test)

1. **Export** the unmanaged solution from Development
2. **Unpack** the zip into component files (readable diffs in source control)
3. **Commit** the unpacked files
4. **Pack** a managed build artifact from the source-controlled files
5. **Import** the managed artifact into Test (with a deployment settings file)
6. Run **end-to-end validation** in Test

**Why this order:** unmanaged is the *editable source* (export/unpack/commit), managed
is the *shippable output* (pack/import). You author unmanaged and ship managed — never
the reverse. The **Unpack** must sit between export and `git add`, or your diffs are an
opaque binary zip.

**Trap:** importing **unmanaged** into Test/Prod. Downstream environments get
**managed** solutions only.

---

## 8. Pipelines — Delegated-Deployment / Approval Flow

1. Create the cloud flow **in the pipelines host environment** (solution context)
2. Select the **OnApprovalStarted** trigger
3. Add approval logic + an approve/reject branch
4. Call **UpdateApprovalStatus** using the **service principal connection**

**Why this order:** the trigger (2) defines *when* the flow wakes up, the logic (3)
makes the decision, and the action (4) writes that decision back to the pipeline. The
trigger always precedes the action it feeds.

**Trap:** a stage-name trigger condition is a **gatekeeper, not an actor** — it only
decides whether the flow runs. The actual approve/reject lives in the steps *after*
the trigger (e.g. `UpdatePreDeploymentStepStatus`).

---

## 9. Restore a Backup to Production

1. Change the production environment's type to **Sandbox**
2. **Restore** the backup
3. Change the environment type **back to Production**

**Why this order:** restore is only permitted into a sandbox-type environment, so you
temporarily demote, restore, then promote. (Source and target must also be in the
**same region**.)

---

## 10. PCF Control Lifecycle (field control)

**init → updateView → getOutputs → destroy**

| Method | Role |
|---|---|
| `init` | One-time setup; receives context + container |
| `updateView` | Runs on every data/layout change — the workhorse |
| `getOutputs` | Hands changed values back to the host |
| `destroy` | Cleanup when the control is removed |

**Why this order:** set up once → react to changes repeatedly → report values out →
tear down. `updateView` is the only one that fires many times.

**Trap:** putting one-time setup in `updateView` (runs repeatedly) or expecting
`getOutputs` to *render* (it only reports values).

---

## 11. PCF Deployment & Packaging Flow

1. **Implement the control logic** (declare Device / Utility / Web API features used)
2. **Build the PCF project** (`msbuild`, or `pac pcf push` for fast dev iteration)
3. **Create a solution project** (`pac solution init`) and **add a reference** to the
   PCF project (`pac solution add-reference`)
4. **Build the solution project** and **import the resulting ZIP** into Dataverse

**Why this order:** you can't reference a component that isn't built (3 needs 2), and
you can't import a solution that hasn't been assembled (4 needs 3). `pac pcf push` is a
dev-iteration shortcut; the solution route (3–4) is how it actually ships through ALM.

**Trap:** treating `pac pcf push` as the deployment method. It's for dev iteration —
real deployment goes through a **solution**.

---

## 12. Call a Cloud Flow from a Canvas-App Button

1. **Add the flow** from the Power Automate pane (flow must have a Power Apps trigger)
2. Select the button's **`OnSelect`** property
3. Enter **`FlowName.Run(params)`** in the formula bar
4. **Test** in Play mode

**Why this order:** the flow must be associated with the app (1) before its `.Run()`
is callable (3). Selecting the property (2) is just where you type the call.

---

## 13. Delegation Warning — Fix Path

1. **Identify** delegation warnings (yellow triangle in the formula bar, or Monitor)
2. **Remove/replace** non-delegable functions with delegable equivalents
3. Use **server-side views** to pre-filter instead of complex client-side expressions
4. **Validate** in Monitor that the query runs server-side and returns correct rows

**Why this order:** diagnose → fix → reduce load → confirm. Validation comes last
because you can only confirm a fix after making it.

**Trap:** "raise the row limit to 2000" does **not** fix delegation — it just changes
how many non-delegated rows are pulled locally.

---

## 14. Monitor — Diagnostic Workflow

1. **Start a fresh Monitor session** (clean capture, no stale noise)
2. **Reproduce** the failing action
3. **Correlate** Monitor events with the browser console and Network tab
4. **Retest** after isolating and addressing the cause

**Why this order:** capture cleanly → trigger the bug → analyze → verify the fix. A
fresh session first is what keeps the capture readable.

---

## Deeper Exam Detail

> Exact stage codes, ordering-within-a-stage rules, and the cross-cutting "where does
> X sit in the order" gotchas the exam uses to separate guesses from understanding.

### A. Plug-in pipeline — exact stage codes and transaction boundary

| Stage | Stage code | Transaction |
|---|---|---|
| PreValidation | **10** | Outside (before tx) |
| PreOperation | **20** | Inside |
| Main Operation | — (stage **30** for custom data providers) | Inside |
| PostOperation (sync) | **40** | Inside |
| PostOperation (async) | **40** | Outside (via async service) |

- The transaction boundary falls **between stage 10 and stage 20**. That single fact
  answers most "which stage" questions: rejection that must avoid rollback → 10;
  in-transaction work → 20/40.
- A **custom data provider** (virtual tables) plug-in runs at **stage 30**, the main
  core stage — *not* the ordinary 10/20/40 used for normal steps.

### B. Ordering *within* a single stage — Execution Order

- When multiple steps register on the **same message + table + stage**, the **Execution
  Order** value decides the sequence among them.
- **Equal Execution Order = non-deterministic** order that can differ between
  environments. Always assign distinct values. This is a subtle "what runs first"
  question that isn't about the pipeline stages at all — it's about steps *within* one
  stage.

### C. Entity image availability follows the pipeline order

- **PreImage** (state *before* the operation) is available in **PreOperation and
  PostOperation**.
- **PostImage** (state *after* the operation) is only meaningful **PostOperation** —
  the record hasn't been written yet earlier in the order.
- On **Create**, there is no PreImage (nothing existed before); on **Delete**, there is
  no PostImage (nothing exists after). The available image is dictated by where you are
  in the order.

### D. Elastic-table ordering caveat (rejection must be early)

- On **elastic tables**, throwing `InvalidPluginExecutionException` in **PreOperation
  or PostOperation** returns an error but does **not** roll back the already-written
  row. **PreValidation (stage 10) is the only safe rejection point** — another reason
  the "reject first, outside the transaction" ordering matters.

### E. "Why doesn't my action appear in the Power Automate trigger?" (ordered checks)

1. **Is Function = Yes** → it must be an **Action** (Is Function = No) for connector discoverability.
2. Missing **CatalogAssignment** (see sequence 3).
3. The user **lacks read access** to the Custom API, Process, and SDK Message tables.

Work the checks in that order — it goes from the most common cause (wrong type) to the
least obvious (table privileges).

### F. ALM artifact direction (the rule behind sequence 7)

- **Unmanaged = source you edit; managed = output you ship.** Every ALM ordering
  question reduces to this: author in unmanaged (export → unpack → commit), produce and
  promote managed (pack → import). The **Unpack** step must fall *between* export and
  source-control commit, or diffs are unreadable binary.
