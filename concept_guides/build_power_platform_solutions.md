# PL-400 Study Guide: Build Power Platform Solutions (10–15%)

---

## 1. Environment Variables

### Key Facts

- Environment variables store **configuration values** (URLs, queue names, API keys, feature flags) separately from the components that consume them.
- They travel **inside the solution** as a definition; the *value* can differ per environment.
- A secret environment variable references a value in **Azure Key Vault** — it does not store the secret in the solution or in plain text. Use this for OAuth client secrets consumed by custom connectors and flows.
  - **Azure Key Vault** is an Azure cloud service for securely storing secrets (passwords, API keys, certificates). The env var stores only a *reference* to the Key Vault entry — the actual value never leaves Key Vault.
  - Key Vault must be in the **same tenant** as the Power Platform environment — cross-tenant is not supported.
  - The **Key Vault Secrets User** role is required (not Reader). Reader lets you see a secret exists but cannot retrieve its value; Secrets User grants the `secrets/get` permission needed to read the actual value.
  - To use a Key Vault-backed secret inside a flow, call **`RetrieveEnvironmentVariableSecretValue`** explicitly — it does not appear in the dynamic content selector.
  - `Microsoft.PowerPlatform` resource provider must be registered on the Azure subscription.
- When a variable has **no default value, no packaged solution value, and no existing target value**, the import wizard prompts for a new value.
- After changing a variable value directly in an environment (not via import), **cloud flows must be cycled** (turned off and on) to pick up the new value — the running flow holds a cached reference.
- To force a target environment to supply a fresh value on import, **remove the solution value before export**; the development environment keeps its own value while the target is prompted.

### Decision Rules

| Situation | Correct control |
|---|---|
| URL / queue name / feature flag differs by environment | Environment variable (text type) |
| OAuth client secret differs by environment | Secret environment variable (Key Vault-backed) |
| Connection binding differs by environment | Connection reference (not env var) |
| Value already in target env + default exists | No prompt during import |
| No default, no solution value, no target value | Prompted during import |

### Common Distractors

- **Text environment variable for secrets** — wrong because it stores the value in plain text inside the solution.
- **Connection reference for all per-environment config** — connection references handle connection *plumbing*, not arbitrary config values like URLs or feature flags.
- **Reimporting the managed solution to refresh a flow** — excessive; cycling the flow is sufficient.
- **Converting the variable to JSON** — irrelevant to the problem.

---

## 2. Connection References

### Key Facts

- Connection references are solution components that abstract the **connection binding** used by flows and canvas apps.
- They allow the same solution to bind to different connections in Dev, Test, and Prod without editing flow internals.
- During solution import, connection references can be supplied so flows **turn on automatically** after import.
- They are used alongside environment variables — env vars for config values, connection references for connector identity.
- For **application users** (service principals), the connection reference identity must have the necessary Dataverse security roles assigned in *each target environment* or flows will fail with privilege errors post-import.

### Common Distractors

- **Connection references replace environment variables** — they do not. Connection references handle the connector; env vars handle configuration values.
- **Direct connector bindings per app** — not portable across environments.

---

## 3. Solutions — Managed vs. Unmanaged, Layers, and ALM

### Managed vs. Unmanaged

| Attribute | Unmanaged | Managed |
|---|---|---|
| Editing in target environment | Full editing allowed | Components locked; direct edits create unmanaged customizations on top |
| Purpose | Development source | Deployment artifact to downstream environments |
| Removal | Manual component-by-component | Delete the solution to remove all its components |
| Carries values forward | Yes | Yes, but env var values can be overridden per environment |
| Layer it creates | Active/Unmanaged layer | Managed layer |

### Solution Layers and Runtime Precedence

- Dataverse evaluates components at runtime using a **layer stack**. The **topmost layer wins**.
- Layer order (top to bottom): **Unmanaged (Active) > Managed (highest publisher order) > Managed (lower) > Base**.
- A direct edit to a managed component in a downstream environment creates an **unmanaged Active layer** that sits above all managed layers — this is the most common cause of "managed updates seem to do nothing."
- To restore managed control: **remove the unmanaged active customization** from the solution layers experience.
- If **another managed solution is on top** (e.g., SalesExtension above AppCore 2.1), that top managed layer wins — neither cycling the flow nor using "Overwrite Customizations" removes it. The fix must come from the owning publisher or by changing the layering arrangement.
- **Overwrite Customizations** during import copies the incoming value to the Active layer; it does not displace a managed solution that is already the top layer.
  - It sounds like it forces the imported value to win — but it only *writes* to the Active layer; it does NOT *remove* the Active layer if one already exists. The Active layer stays on top and continues to win at runtime.
  - It also cannot displace a higher managed solution (e.g. SalesExtension above AppCore). Writing to the Active layer still lands below the top managed solution.

### Segmented Solutions and Source Authoring

- **Use segmented solutions**: include only the specific component assets needed (e.g., specific columns, not the entire table). This reduces unnecessary managed layers and conflict surface.
- **Author all changes in the source/development environment** — never edit managed components directly in downstream environments. Changes must be made unmanaged in the source and then re-deployed.
- For **modular multi-team architectures**: build a shared managed *base layer*, import it into each app team's dev environment, and let each team author an *app-layer unmanaged solution* on top. This creates clear import order and independent release cadences.
- Use the **same publisher** across layered solutions to keep the layer model manageable.
  - The publisher prefix (e.g. `contoso_`) becomes part of every *new* component's schema name at creation (e.g. `contoso_name`). Once a component exists, any solution from any publisher can modify it — different publishers do not break layering on existing components.
  - The recommendation is **governance/clarity**, not a hard technical rule: one prefix across all your solutions makes ownership immediately obvious; mixed prefixes make it harder to distinguish your components from third-party ones.

### Dependencies Between Solutions

- Dependencies between solutions **enforce import order** — if Solution B depends on components in Solution A, Solution A must be imported first.
- When two solutions are tightly coupled (one cannot stand alone), the cleaner ALM design is usually to **consolidate them** rather than document a fragile import sequence.
- Use **Add Required Components** to pull dependent artifacts (web resources, component libraries, tables, columns) into the same solution before export.
- Missing dependency errors are resolved by correcting the source solution and re-exporting — never by manually recreating components in target environments (this creates drift).

---

## 4. ALM Pipeline — Azure DevOps & Power Platform Build Tools

### Standard CI/CD Sequence

```
Dev (unmanaged) → Export → Unpack → Source Control → Pack (managed) → Import into Test/Prod
```

Correct step order:
1. **Export** the unmanaged solution from Development.
2. **Unpack** (decompose the zip into component files) — enables readable diffs and merge review in source control.
3. **Commit** unpacked files to source control.
4. **Pack** a managed build artifact from source-controlled files.
5. **Import** the managed artifact into Test (with deployment settings).
6. Run **end-to-end validation** in Test.

### Key Build Tools Tasks

| Task | Purpose |
|---|---|
| PowerPlatformExportSolution | Exports unmanaged solution as zip |
| **Unpack Solution** | Decomposes zip into source-controllable component files (insert before `git add`) |
| **Checker task** | Runs static analysis against solution; fails pipeline on rule violations (put in validation/build stage, before import) |
| PowerPlatformImportSolution | Imports managed artifact; accepts deployment settings file |
| WhoAmI | Connectivity validation only — not a quality gate |

### Deployment Settings File

- A JSON file that pre-populates **connection reference values** and **environment variable values** during automated import.
- Eliminates the need for makers to manually reconfigure after each deployment.
- Store it in source control alongside the unpacked solution.
- It is the fix when flows remain disconnected and env variable values are blank after automated import.

### Service Principal / Workload Identity Federation

- Use **service principal authentication** (Workload Identity Federation recommended) to reduce secret handling overhead in pipelines.
- The application user representing the service principal must be assigned the necessary **Dataverse security roles** in each target environment.

---

## 5. Power Platform Pipelines (Pipelines Host)

### Personal vs. Custom Host Pipelines

| Attribute | Personal (Platform Host) | Custom Host |
|---|---|---|
| Max associated environments | 3 (Dev + 2 targets) | Unlimited |
| Shareability | Not sharable | Sharable with multiple makers/admins |
| Extensibility | Not extensible | Fully extensible via cloud flows |
| Use case | Individual makers | CoE governed shared deployments |

### Pipeline Extension Trigger/Action Mapping

| Extension point | Trigger | Completion action |
|---|---|---|
| Pre-export gate | OnDeploymentRequested | UpdatePreExportStepStatus |
| Delegated (approval) deployment | **OnApprovalStarted** | **UpdateApprovalStatus** (must use service principal connection) |
| Pre-deployment gate | **OnPreDeploymentStarted** | UpdatePreDeploymentStepStatus |

Common trap: Pre-deployment step uses **OnPreDeploymentStarted** — NOT OnDeploymentCompleted.

### Delegated Deployment Approval Flow — Correct Build Order

1. Create the cloud flow **in the pipelines host environment** (solution context required).
2. Select the **OnApprovalStarted** trigger.
3. Insert approval logic and branch condition (approve/reject).
4. Call **UpdateApprovalStatus** using the **service principal connection**.

### Stage-Name Filter Pattern

```
@equals(triggerOutputs()?['body/OutputParameters/DeploymentStageName'], 'Contoso UAT')
```
This trigger condition **filters** the flow so it runs only for the named stage — it does not approve, reject, or modify anything by itself.
- The condition is a **gatekeeper, not an actor**: if the stage name matches the flow runs; if not the flow is skipped entirely. No approval, no rejection, no data change.
- The actual approve/reject logic lives in the flow steps *after* the trigger — e.g. a Send Approval action followed by `UpdatePreDeploymentStepStatus` that writes the decision back to the pipeline.

---

## 6. Environment Types and Backup/Restore

### Developer Environment

- Free, isolated workspace for one developer — use instead of the shared tenant default environment.
- Suitable for building and testing apps, flows, Dataverse tables, and **premium/custom connectors**.
- Not for shared business workloads; intended only for the owner.

### Backup and Restore Rules

- Microsoft allows restores only **into sandbox or developer environments** — not directly into production.
- Source and target must be in the **same region**.
- To restore a production environment: **change its type to sandbox**, perform the restore, then change it back to production.
- Restoring onto the source environment itself is not allowed when the requirement specifies a "different environment."

---

## 7. Dataverse Security Model

### Privilege Taxonomy

| Privilege | When required |
|---|---|
| Read | Open a record |
| Write | Update a record |
| Create | Insert a new record |
| Delete | Remove a record |
| **Assign** | Transfer record ownership to another user/team |
| **Append** | Associate *this* record to another (e.g., set a lookup on the current record) |
| **Append To** | Allow another record to be associated *to this* table (e.g., receive the lookup pointer) |
| Share | Share a record with another user/team |

**Append + Append To pair** is required whenever a lookup field is set or a note/related record is attached:
- The record being attached needs **Append**.
- The table receiving the relationship pointer needs **Append To**.

### Common Security Scenarios

| Symptom | Root cause | Fix |
|---|---|---|
| User can edit owned record but cannot reassign it | Missing **Assign** privilege | Add Assign to the role |
| User can create both tables but save fails on the relationship | Missing **Append** on child + **Append To** on parent | Add both |
| Managed solution update "does nothing" | Unmanaged Active layer or higher managed layer on top | Remove unmanaged layer or address top managed layer |
| Flow fails with privilege error in test but worked in dev | Application user not assigned security role in test | Assign role to app user in target environment |
| User sees secured column is read-only or save fails on that field | **Column security profile** not granting Update | Update column security profile |

### Column Security

- Column security profiles control **Read, Create, and Update** access to secured columns, independent of table-level role permissions.
- A user can have full table Write and still be blocked on a single secured column if their profile (or their team's profile) shows Update = Not Allowed.
- First diagnostic: check the column security profile when a save fails on one specific field while other fields on the same record save fine.

### Plug-in Execution Context

- A plug-in running in **Calling User context** applies the *interactive user's* privileges to all operations the plug-in performs.
- If the plug-in tries to write to a restricted table, it fails if the calling user lacks that privilege.
- Fix: switch the step to run as a different user (e.g., system or a service account with the required rights) or grant the calling user the needed privilege.

### Least-Privilege Design

- Grant only the operations required for the specific app behavior — no extras.
- For a field code component that reads and updates existing rows the user owns: **Read + Write** on that table is sufficient.
- For a lookup update: also add **Append** (on the record with the lookup) and **Append To** (on the target table).
- For a dataset code component reading a related table: add **Read** on the related table.
- Never grant System Customizer, Delete, or Assign to satisfy a simple read/update scenario.

### Team and Owner Access

- Only **owner teams** and **Microsoft Entra group teams** can own records.
- When automation starts reassigning records to a team, the team's security roles determine effective access for all team members — unexpected visibility can appear without changing any individual user's role.
  - **Visibility and access are separate privileges**: Read = visibility (can see the record); Write/Delete/Append/Share/Assign = access (can act on it). A team's role could grant Read only, or Read + Write, or any combination.
  - The concern is that *any* of those privileges can appear unexpectedly for all team members the moment records are reassigned — without touching a single individual user's role.

---

## 8. Power Fx — With() Function

- `With({ name: expr, ... }, result)` creates **named intermediate values** scoped to that formula only.
- No global variables, no persistent state, no connector calls — purely local formula organization.
- Use it to avoid repeating expensive sub-expressions and to keep complex single-property formulas readable.
- Distinct from `Set()` (app-scoped global variable) and `UpdateContext()` (screen-scoped variable).

---

## Quick-Fire Facts

1. **Secret environment variable** → Azure Key Vault-backed; do not use text variables for OAuth secrets.
2. **Cycle the flow** (off → on) after changing an env variable value directly in an environment — no reimport needed.
3. **Remove the solution value before export** to force the target to be prompted for a new value on import.
4. **Unmanaged Active layer beats every managed layer** — remove it when a managed update seems ineffective.
5. **Overwrite Customizations** copies to Active layer but does NOT displace a higher managed layer.
6. **Unpack Solution** task must run between export and `git add` to enable readable source-control diffs.
7. **Checker task** = static analysis / quality gate in the build/validation stage (before import).
8. **Deployment settings file** = JSON that pre-populates connection references and env var values during automated import.
9. **Custom host pipeline** is required for >2 target environments, sharing, or extensibility.
10. **OnApprovalStarted** + **UpdateApprovalStatus** (with service principal connection) = delegated deployment pattern.
11. **OnPreDeploymentStarted** (NOT OnDeploymentCompleted) triggers a pre-deployment gate extension.
12. **Restore to production**: change environment type to sandbox first, restore, then change back.
13. **Same region** is required for backup restore source and target.
14. **Developer environment** = free isolated sandbox for one developer; do not use the tenant default.
15. **Assign privilege** is separate from Write — users lose reassign ability if Assign is removed even while retaining Write.
16. **Append + Append To pair** is required for any record association or lookup update.
17. **Application user** in the target environment needs a security role assigned independently of the role in development.
18. **Consolidate tightly coupled solutions** rather than document brittle import order.
19. **Add Required Components** is the correct tool to pull dependent artifacts into a solution before export.
20. **With()** in Power Fx = named intermediate values, local scope only, not global state.

---

## Common Traps

- **Using a text environment variable for a client secret** — the exam expects *secret* env var (Key Vault-backed).
- **Expecting a managed import to override an existing unmanaged Active layer** — it won't; remove the Active layer first.
- **Confusing "Overwrite Customizations" with fixing a higher managed layer** — they are unrelated; Overwrite only affects the Active layer.
- **Forgetting to unpack before committing to source control** — the zip produces no meaningful diffs; always unpack first.
- **Using WhoAmI as a validation gate** — it tests connectivity only, not solution quality.
- **Assuming connection references replace environment variables** — they address different concerns.
- **Granting Write without Assign** after a role redesign — users lose the ability to reassign records they still own.
- **Missing Append/Append To when setting a lookup** — Create + Write alone are not enough to establish a relationship.
- **Restoring directly to production** — must change to sandbox first.
- **Using a personal pipeline when sharing or >2 targets are needed** — use a custom host pipeline.
- **Retrying the import before fixing the source solution** — always fix the source and re-export first.
- **Manually recreating missing components in target environments** — creates drift and bypasses the tracked solution model.
- **Expecting a plug-in in Calling User context to succeed on a restricted table** — it will fail if the calling user lacks privilege; change the execution context or grant the privilege.

---

## Deeper Exam Detail

This section contains deeper product behavior, exact limits, ALM tooling specifics, and "What if..." edge-case decision rules sourced directly from Microsoft Learn documentation.

---

### A. Solutions — Deeper Mechanics

#### Deleting a managed solution — data loss warning

- When you delete (uninstall) a managed solution, **all data stored in custom tables that were part of that solution is permanently deleted**, as well as data in custom columns that were part of the solution on other tables. This is irreversible. Plan the uninstall sequence carefully in production environments. [learn.microsoft.com/en-us/power-platform/alm/solution-concepts-alm](https://learn.microsoft.com/en-us/power-platform/alm/solution-concepts-alm)

#### You cannot import a managed solution into its own originating environment

- A managed solution exported from Environment A cannot be imported back into Environment A if that environment already contains the originating unmanaged solution. A separate environment is always required for managed solution testing. This is a platform constraint, not just a best-practice recommendation. [learn.microsoft.com/en-us/power-platform/alm/solution-concepts-alm](https://learn.microsoft.com/en-us/power-platform/alm/solution-concepts-alm)

#### Update vs. Upgrade vs. Stage-for-Upgrade — full option set

| Action | Components removed? | Patches merged? | When to use |
|---|---|---|---|
| **Update** | No — cannot delete components | No | Minor additions (new fields, new flows); hotfix delivery |
| **Upgrade** (immediate) | Yes — removes components no longer in solution; rolls up all patches | Yes | Major release; want clean removal of deprecated components |
| **Stage for Upgrade** (holding solution) | Deferred — creates a `_Upgrade` layer on top; apply later | Yes, when applied | Need to perform data migration or manual steps between import and apply |
| **Patch** | No — cannot delete components | N/A (patch IS a layer) | Small, targeted hotfixes layered on top of the base solution |

- Patches are **not recommended** by Microsoft; they add layering complexity without the full lifecycle benefits of a versioned upgrade. Prefer updates or upgrades over patches for new work. [learn.microsoft.com/en-us/power-platform/alm/solution-layers-alm](https://learn.microsoft.com/en-us/power-platform/alm/solution-layers-alm)
- After staging an upgrade, calling **Apply Upgrade** from the Solutions area flattens all patch and pending-upgrade layers into a single new base layer. [learn.microsoft.com/en-us/power-platform/alm/solution-layers-alm](https://learn.microsoft.com/en-us/power-platform/alm/solution-layers-alm)
- The `HoldingSolution: true` parameter on the `PowerPlatformImportSolution` Build Tools task imports a solution as a holding (staged) solution without applying it immediately, enabling pre-upgrade data operations. [learn.microsoft.com/en-us/power-platform/alm/devops-build-tool-tasks](https://learn.microsoft.com/en-us/power-platform/alm/devops-build-tool-tasks)

---

### B. Environment Variables — Deeper Mechanics

#### All five data types

| Data type | Stores | Notes |
|---|---|---|
| **Text** | Plain string up to 2,000 chars | URLs, names, feature flags |
| **Decimal number** | Numeric value | Thresholds, version numbers |
| **Two options** | Boolean (Yes/No) | Feature toggles |
| **JSON** | Structured JSON string | Complex config; still plain text in storage |
| **Data source** | Connector + parameter type (e.g., SharePoint site/list) | Connector-specific; connection not stored, only the parameter |
| **Secret** | Azure Key Vault reference | Client secrets, API keys; requires Key Vault integration setup |

[learn.microsoft.com/en-us/power-apps/maker/data-platform/environmentvariables](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/environmentvariables)

---

### C. SolutionPackager / pac solution — Tooling Details

#### SolutionPackager is superseded by pac CLI

- The standalone `SolutionPackager.exe` tool (distributed via the `Microsoft.CrmSdk.CoreTools` NuGet package) is **no longer the recommended approach**. Its capabilities are now incorporated into the **Power Platform CLI** (`pac solution unpack`, `pac solution pack`, `pac solution clone`, `pac solution sync`). Use the CLI in new pipelines. [learn.microsoft.com/en-us/power-platform/alm/solution-packager-tool](https://learn.microsoft.com/en-us/power-platform/alm/solution-packager-tool)

#### Two source control formats

| Format | Folder structure | Best for |
|---|---|---|
| **XML (legacy)** | `Other\Solution.xml`, `Other\Customizations.xml`, flat hierarchy | Existing pipelines; backward compatibility |
| **YAML** (new) | `solutions/<SolutionName>/solution.yml`, structured per-component folders | New projects; Dataverse Git integration; canvas apps and modern flows require this format |

- The YAML format is **auto-detected** by the presence of a `solutions/` subfolder containing `*solution.yml` files. If that subfolder is absent, the tool falls back to the XML format and reports a misleading error about a missing `Customizations.xml`. [learn.microsoft.com/en-us/power-platform/alm/solution-packager-tool](https://learn.microsoft.com/en-us/power-platform/alm/solution-packager-tool)
- Canvas app `.msapp` files and modern cloud flows are **only supported in the YAML format**. [learn.microsoft.com/en-us/power-platform/alm/solution-packager-tool](https://learn.microsoft.com/en-us/power-platform/alm/solution-packager-tool)

#### Key SolutionPackager parameters

| Parameter | Purpose |
|---|---|
| `/action:{Extract\|Pack}` | Required. Decompose a zip or assemble a zip. |
| `/packagetype:{Unmanaged\|Managed\|Both}` | Pack/extract as unmanaged, managed, or both. Default: Unmanaged. |
| `/allowWrite:{Yes\|No}` | Dry-run mode when No — verifies without writing files. |
| `/map:<file>` | XML mapping file to redirect plug-in assemblies or web resources from alternate build output folders. Critical for CI pipelines where assemblies are compiled separately. |
| `/localize` | Extract or merge all string resources into `.resx` files for localization. |

[learn.microsoft.com/en-us/power-platform/alm/solution-packager-tool](https://learn.microsoft.com/en-us/power-platform/alm/solution-packager-tool)

#### Build Tools task: HoldingSolution parameter

- The `PowerPlatformImportSolution` task includes `HoldingSolution: true|false` — when true, imports the solution as a **holding (staged) solution** (`_Upgrade` suffix) without applying it. The `PowerPlatformApplySolutionUpgrade` task is then run separately to complete the upgrade. This enables a data-migration window between import and apply. [learn.microsoft.com/en-us/power-platform/alm/devops-build-tool-tasks](https://learn.microsoft.com/en-us/power-platform/alm/devops-build-tool-tasks)

#### Build Tools task: async import and timeout

- For large solutions, set `AsyncOperation: true` on the Import task. Without it, the task **times out after 4 minutes**. With async enabled, the task polls until completion up to `MaxAsyncWaitTime` (default: 60 minutes). [learn.microsoft.com/en-us/power-platform/alm/devops-build-tool-tasks](https://learn.microsoft.com/en-us/power-platform/alm/devops-build-tool-tasks)

#### Power Platform Checker — two rule sets

- **Solution checker** rule set: same rules run from the Power Apps maker portal.
- **Marketplace** rule set: extended rules required to certify an app for publication to Microsoft Marketplace (AppSource). Use this rule set for ISV solutions before submission.
[learn.microsoft.com/en-us/power-platform/alm/devops-build-tool-tasks](https://learn.microsoft.com/en-us/power-platform/alm/devops-build-tool-tasks)

---

### D. Power Platform Pipelines — Deeper Mechanics

#### What pipelines deploy (and what they do not)

- Pipelines deploy **solutions + connection references + environment variables** configured for the target. They do **not** deploy Dataverse table data. Power BI Dashboards and Power BI Datasets are not currently supported. [learn.microsoft.com/en-us/power-platform/alm/pipelines](https://learn.microsoft.com/en-us/power-platform/alm/pipelines)

#### Artifact storage — automatic

- Pipelines **automatically export and store both managed and unmanaged solution artifacts** in the pipelines host environment for every deployment. This eliminates the need for a separate artifact storage step. [learn.microsoft.com/en-us/power-platform/alm/pipelines](https://learn.microsoft.com/en-us/power-platform/alm/pipelines)

#### Artifact immutability and bypass prevention

- The solution is exported at the moment the maker clicks **Deploy**. The **same artifact** is promoted through all subsequent pipeline stages — the system does not re-export for downstream stages. This design prevents customization from bypassing QA environments or approval gates. [learn.microsoft.com/en-us/power-platform/alm/pipelines](https://learn.microsoft.com/en-us/power-platform/alm/pipelines)

#### Default import behavior

- Pipelines always import as **Upgrade without Overwrite Customizations** — there is no current UI option to change this. If you need update-only semantics or overwrite, use Azure DevOps / GitHub Actions with the Build Tools import task directly. [learn.microsoft.com/en-us/power-platform/alm/pipelines](https://learn.microsoft.com/en-us/power-platform/alm/pipelines)

#### Managed Environments requirement (as of February 2026)

- All pipeline **target environments** (not development or host) must be **Managed Environments**. Starting February 2026, Microsoft automatically enables Managed Environments for any pipeline target that is not already enabled. Licenses granting premium use rights are required for all Managed Environments used as targets. Developer and host environments do not require Managed Environment status. [learn.microsoft.com/en-us/power-platform/alm/pipelines](https://learn.microsoft.com/en-us/power-platform/alm/pipelines)

#### Cross-region pipeline deployments

- By default, pipeline host and all associated environments must be in the **same geographic region**. Cross-geo deployments require the **Cross-Geo Solution Deployments** setting to be explicitly enabled on the host. [learn.microsoft.com/en-us/power-platform/alm/pipelines](https://learn.microsoft.com/en-us/power-platform/alm/pipelines)

#### Cross-tenant pipeline deployments

- Pipelines **cannot deploy across tenants**. For cross-tenant scenarios, use Azure DevOps or GitHub Actions. [learn.microsoft.com/en-us/power-platform/alm/pipelines](https://learn.microsoft.com/en-us/power-platform/alm/pipelines)

#### Rollback

- If the pipeline setting for rollback is enabled, you can redeploy a **previous solution version** from the run history view. If the setting is disabled, only higher (later) solution versions can be deployed. Workaround for disabled: download the artifact from the host, increment the version number in `solution.xml`, then manually import. [learn.microsoft.com/en-us/power-platform/alm/pipelines](https://learn.microsoft.com/en-us/power-platform/alm/pipelines)

#### One environment — one host

- An environment **cannot be associated with multiple pipeline hosts simultaneously**. To move an environment to a different host, add it to a pipeline in the new host, then delete the environment record from the original host. [learn.microsoft.com/en-us/power-platform/alm/pipelines](https://learn.microsoft.com/en-us/power-platform/alm/pipelines)

---

### E. "What if..." Edge-Case Decision Rules

These rules address scenarios not clearly covered by a single exam bullet point.

**What if I need to delete an environment variable value that was shipped as part of a managed solution?**
An update cannot delete solution components; you must ship an **upgrade** that excludes the value, then import it using the upgrade option (not update). [learn.microsoft.com/en-us/power-apps/maker/data-platform/environmentvariables](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/environmentvariables)

**What if the same component is included in two different managed solutions and both are installed?**
For most components (not forms/site maps/apps), the **last-installed managed solution wins** at runtime. Uninstalling the top solution restores the behavior of the solution below it. [learn.microsoft.com/en-us/power-platform/alm/solution-layers-alm](https://learn.microsoft.com/en-us/power-platform/alm/solution-layers-alm)

**What if a solution import fails with a missing dependency error, but the dependency table exists in the environment?**
The dependency may be on a **specific version** or on a **component within the dependency solution** that is not yet present. Fix at the source — add the required components or align versions — then re-export and re-import. Never manually recreate components in the target. [learn.microsoft.com/en-us/power-platform/alm/solution-concepts-alm](https://learn.microsoft.com/en-us/power-platform/alm/solution-concepts-alm)

**What if a canvas app or modern flow is missing after SolutionPackager unpacks the solution?**
You are using the **XML (legacy) format**. Canvas `.msapp` files and modern flows are only supported in the **YAML format**. Switch to `pac solution clone` or ensure the YAML folder structure (`solutions/<Name>/solution.yml`) is present before packing. [learn.microsoft.com/en-us/power-platform/alm/solution-packager-tool](https://learn.microsoft.com/en-us/power-platform/alm/solution-packager-tool)

**What if the pipeline's default Upgrade import behavior is not what I want (e.g., I only want an Update to avoid deleting components)?**
Pipelines do not currently expose an option to choose Update vs. Upgrade — the default is always Upgrade without Overwrite Customizations. For Update semantics (no component deletion), use the **Power Platform Build Tools** `PowerPlatformImportSolution` task in Azure DevOps or GitHub Actions where you have full control over import parameters. [learn.microsoft.com/en-us/power-platform/alm/pipelines](https://learn.microsoft.com/en-us/power-platform/alm/pipelines)
