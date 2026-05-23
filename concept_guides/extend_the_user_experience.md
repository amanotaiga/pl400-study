# PL-400 Exam: Extend the User Experience — Concept Study Guide

---

## 1. PCF Code Components — Lifecycle Methods

PCF controls implement either **StandardControl** or **ReactControl**. Understanding which lifecycle method handles which responsibility is the most heavily tested topic in this domain.

### StandardControl Lifecycle

| Method | Responsibility | Key Facts |
|---|---|---|
| `init` | Initialize the component instance | Best place to start remote/metadata requests; receives `container: HTMLDivElement` for DOM rendering |
| `updateView` | React to changed property-bag values | Called when field value, dataset, dimensions, visibility, metadata, or offline state change; primary rendering step |
| `getOutputs` | Return changed bound values to the framework | Called by the framework **after** `notifyOutputChanged()` is raised; returns `IOutputs` |
| `destroy` | Clean up and release resources | Called when component is removed from DOM; remove event listeners, close WebSockets, prevent memory leaks |

**Correct PCF lifecycle order (field control):** `init` → `updateView` → `getOutputs` → `destroy`

### ReactControl vs StandardControl

| Aspect | StandardControl | ReactControl |
|---|---|---|
| `init` signature | Receives `container: HTMLDivElement` | Does NOT receive a container parameter |
| `updateView` return | `void` | Returns a `ReactElement` |
| DOM rendering | Component appends elements to container | Framework renders React tree |
| Use case | Direct DOM manipulation | React-based components |

**Common trap:** Writing a class that implements `ReactControl` but keeps the `StandardControl`-style `init` signature (with `container`) or a void `updateView`. The fix is to drop the container parameter and return a `ReactElement` from `updateView`.

### Key lifecycle decision rules

- **Remote network calls at startup** → `init` (not `updateView`)
- **Render/re-render UI** → `updateView`
- **Return bound value after user edits** → call `notifyOutputChanged()` then return value from `getOutputs()`
- **Cleanup (listeners, WebSockets)** → `destroy`
- **Dataset values** → handle in `updateView`, not `init`

---

## 2. PCF Manifest Configuration

The manifest (`ControlManifest.Input.xml`) declares properties, resources, and capabilities. Manifest mistakes are a common source of exam questions.

### Property Usage Types

| Usage | Meaning | When to use |
|---|---|---|
| `bound` | Reads and writes a Dataverse column value | Field component that can change the column |
| `input` | Read-only maker-configurable value | Configuration the maker sets in designer; no writeback |
| `output` | Value emitted by the component | Supplemental outputs beyond a single bound field |

**Decision rule:** If a maker provides a configurable placeholder text that the component should read but never save to Dataverse, use `input`. If users edit a value through the component and it must flow back to the Dataverse column, use `bound` (with `notifyOutputChanged` + `getOutputs`).

### Resource Declarations

| Resource element | Purpose |
|---|---|
| `<code>` | TypeScript/JavaScript entry point |
| `<css>` | Custom styling for the rendered control |
| `<resx>` | Localized strings for maker-facing and UI text |

### Special Manifest Elements

- **`external-service-usage`**: Required when a canvas-app code component connects directly to an external REST endpoint. Controls that use an external service are classified as **premium**.
- **`feature-usage`**: Declares Device API (camera, barcode, etc.) and other advanced features the component will use. Required before calling device methods. **Only supported for model-driven apps**, not canvas apps — using it in a canvas-app manifest will be rejected.
- **`data-set`**: If the manifest contains at least one dataset, properties of type `Lookup.Simple` must be nested **inside** the `data-set` element, not declared as top-level properties.

---

## 3. PCF Deployment & Packaging

### Deployment Flow (correct order)

1. Implement the control logic (Device, Utility, Web API features)
2. Build the PCF project (`msbuild` or `pac pcf push` for dev iteration)
3. Create a solution project (`pac solution init`) and add a reference to the PCF project (`pac solution add-reference`)
4. Build the solution project and import the resulting solution ZIP into Dataverse

**`pac pcf push`** is for rapid iteration in development only — it pushes directly to a dev environment and does not produce a portable solution.

### Canvas-App Enablement

Importing a solution containing a PCF control is not sufficient for canvas usage. The **Power Apps component framework feature must be explicitly enabled** in each target environment before makers can add code components inside canvas apps.

### ALM: Modern Commands in Solutions

When exporting a solution containing modern commands, the following components must also be included:
- **Power Fx commands** → depend on a **Dataverse component library** (must be in the solution)
- **JavaScript commands** → depend on a **JavaScript web resource** (must be in the solution)

---

## 4. PCF APIs — Host Support and Usage

### context APIs availability

| API | Model-Driven | Canvas |
|---|---|---|
| `context.webAPI` | Supported | Not supported |
| `context.device` (barcode, camera) | Supported (mobile) | Supported (mobile) |
| `context.utils.lookupObjects` | Supported | Varies — check docs |

**Decision rule:** If a PCF control uses `context.webAPI` for Dataverse CRUD, **restrict it to model-driven hosts**. Deploying the same component to canvas will throw at runtime because `context.webAPI` is not available in canvas apps.

### Local test harness limitations

`npm start` (browser test harness) does NOT support:
- `context.device` methods (barcode, camera)
- `context.utils.lookupObjects` and other Utility/Navigation methods
- Features declared in `feature-usage`

**Fix:** Deploy to Dataverse and test there — do not interpret harness exceptions as proof of a code bug.

### Device API

- Use `context.device.getBarcodeValue()` for native barcode/camera capture on mobile.
- Device API methods **must be declared** in `feature-usage` in the manifest before use.
- Available for both model-driven and canvas apps on mobile clients.

### Utility API

- Use `context.utils.lookupObjects()` to open the platform's native lookup dialog from inside a PCF component — preferred over building custom dialogs or calling unsupported Xrm methods directly.

---

## 5. Client Scripting — Form Events and Registration

### Form Event Registration: Designer vs Code

| Event | Preferred registration | Notes |
|---|---|---|
| `OnLoad` | Form Events tab (designer) | Standard form-open handler; visible in form customization |
| `OnSave` | Form Events tab (designer) | Stable validation routines; visible in form customization |
| `OnChange` (attribute) | `attribute.addOnChange` in code | Used when dynamically wiring at runtime |
| `PreSearch` (lookup) | `addPreSearch` in code (from OnLoad) | Not surfaced in designer; must be attached at runtime |
| Runtime OnSave | `formContext.data.addOnSave` in code | When handler must be attached dynamically |

**Key rule:** If the team wants handler registration to be **visible in form customization**, use the form Events tab. If the event is not surfaced in the designer (e.g., `PreSearch`) or must be attached dynamically, attach in code.

### Execution Context — Most Tested Gotcha

- When configuring a form event handler in the designer, you **must check "Pass execution context as first parameter"** if the function uses `executionContext.getFormContext()`.
- If this is not selected, `executionContext` is `undefined` at runtime — the code may be correct but the handler wiring is broken.
- **Use `formContext` (from `executionContext.getFormContext()`)**, not the deprecated `Xrm.Page`, for all current code targeting v9+.

### `setValue` Does Not Fire OnChange

```javascript
// After setting a value programmatically, call fireOnChange explicitly
attribute.setValue(newValue);
attribute.fireOnChange(); // required to trigger existing OnChange handlers
```

### Shared Handler + getEventSource

When one handler is registered on multiple columns, use `executionContext.getEventSource()` to determine which column triggered the event — without hard-coding column names.

### addOnChange Registration Trap

Calling `addOnChange` inside an `OnLoad` handler causes duplicate handler registrations on each save-and-refresh cycle. **Fix:** conditionally call `addOnChange` (check data load state with `getEventArgs`) so the same callback is not registered multiple times.

### formContext vs Xrm.Page

| | `formContext` | `Xrm.Page` |
|---|---|---|
| Status | Current (recommended) | Deprecated |
| Works in editable grids | Yes | No |
| Obtained via | `executionContext.getFormContext()` | Global static reference |

---

## 6. Xrm.WebApi — Client-Side Dataverse Access

### Key Methods

| Method | Purpose |
|---|---|
| `Xrm.WebApi.retrieveRecord(logicalName, id, options)` | Retrieve a single record |
| `Xrm.WebApi.retrieveMultipleRecords(logicalName, query)` | Retrieve multiple records (OData or FetchXML) |
| `Xrm.WebApi.createRecord` / `updateRecord` | Create/update records |
| `Xrm.WebApi.online.execute` | Invoke custom APIs, actions, or functions |

### online.execute

- Used to call **unbound custom APIs** and inspect the response payload.
- **`online` prefix means online-only** — will fail in mobile offline mode.
- Not a CRUD helper; use it when invoking actions/functions rather than simple record operations.

### Mobile Offline Limitations

- `Xrm.WebApi.online.execute` → not supported offline.
- OData query string filters against `MultiSelectPicklist` columns → not supported offline.
- **Fix for MultiSelectPicklist offline:** switch to FetchXML.

### Performance Best Practice

Always add `$select` to limit returned columns when calling `retrieveRecord` or `retrieveMultipleRecords`. Without `$select`, all columns are returned.

---

## 7. Modern Commanding (Power Fx) in Model-Driven Apps

### Power Fx Visibility Formulas

| Scenario | Formula |
|---|---|
| Show when rows selected in grid | `CountRows(Self.Selected.AllItems) > 0` |
| Show when exactly one row selected | `CountRows(Self.Selected.AllItems) = 1` |
| Show based on record edit permission | `RecordInfo(Self.Selected.Item, RecordInfo.EditPermission)` |
| Show based on table create permission | `DataSourceInfo(TableName, DataSourceInfo.CreatePermission)` |

**Decision rule:** `RecordInfo` = record-specific permissions; `DataSourceInfo` = table-wide permissions.

### Power Fx Commands — Tooling Entry Point Trap

Power Fx options ("Run formula" and "Show on condition from formula") are **only available when editing commands from within the modern app designer**, not from the Solutions area or Tables area. If those options appear greyed out, the fix is to open the command editor from the app designer.

### When Power Fx Is Not Supported

**Custom-page dialog commands** (opening a custom page as a dialog) currently support **JavaScript only**. Power Fx is not supported for that pattern. Use a JavaScript library + function.

### Solution Dependencies for Modern Commands

| Command type | Required solution component |
|---|---|
| Power Fx action | Dataverse component library |
| JavaScript action | JavaScript web resource |

Both must be added to the solution before export.

---

## 8. Custom Page Navigation (navigateTo)

### Core API

```javascript
Xrm.Navigation.navigateTo(pageInput, navigationOptions)
```

- `pageInput.pageType` must be `"custom"` for custom pages (not `"entityrecord"`).
- `pageInput.name` = logical name of the custom page.
- `pageInput.entityName` and `pageInput.recordId` = optional context passed into the custom page via `Param("entityName")` and `Param("recordId")`.
- **`recordId` must be a GUID** — validated at URL startup. Passing a business key (e.g., customer number) here causes failures.

### Navigation Targets

| `target` value | Behavior |
|---|---|
| `1` (inline) | Replaces current page (full-page navigation) |
| `2` (dialog) | Opens custom page on top of current page (overlay dialog) |

**Decision rule:** When an agent is reviewing an account and should open a guided review **without leaving the current form**, use `target: 2` (dialog). Use `target: 1` only when full-page replacement is acceptable.

### pageInput Properties Location

`entityName` and `recordId` go in `pageInput` (context for the page). Dialog title, position, and width go in `navigationOptions` (controls how the page opens).

---

## 9. Business Rules vs JavaScript vs PCF — When to Use What

| Capability | Business Rule | Client Script (JS) | PCF Component |
|---|---|---|---|
| No-code/low-code field logic | Best fit | Possible but overkill | Not applicable |
| Runs server-side (without browser) | Yes | No | No |
| Requires execution context/form API | No | Yes | Via `context` |
| Custom UI rendering | No | Limited | Yes |
| Reusable across apps/forms | Limited | Via web resource | Yes (solution component) |
| Lookup pre-filtering at search time | No | Yes (`addPreSearch`) | Via Utility API |
| Requires deployment packaging | No | Web resource upload | Solution ZIP import |

**Common trap:** Questions may offer "move to a business rule" as a fix for client scripting problems. Business rules cannot replace JavaScript when the logic requires execution context, Web API calls, or event source inspection.

---

## 10. Quick-Fire Facts

- `getOutputs` is called by the framework in response to `notifyOutputChanged()` — this is how bound PCF values flow back to Dataverse.
- A PCF `StandardControl` **requires** all four lifecycle methods: `init`, `updateView`, `getOutputs`, `destroy`. A missing `updateView` means the control never refreshes when values change.
- `feature-usage` in the manifest is for **model-driven apps only** — using it in a canvas-app PCF manifest is invalid.
- `external-service-usage` in the manifest makes a canvas-app PCF control **premium**.
- `pac solution add-reference` is the CLI step that links a PCF project into a solution project for packaging.
- `Xrm.WebApi.online.execute` = for calling custom APIs and actions; `online` = requires server connectivity.
- `fireOnChange()` must be called explicitly after `setValue()` to trigger existing OnChange handlers.
- `executionContext.getEventSource()` returns the column object that triggered an OnChange event — use this in shared handlers.
- `addPreSearch` must be registered in code (typically from an `OnLoad` handler); it is not surfaced in the form designer.
- For mobile offline + MultiSelectPicklist queries: use FetchXML, not OData.
- To enable PCF code components in canvas apps: the environment feature must be **explicitly enabled** per environment.
- `CountRows(Self.Selected.AllItems) > 0` is the standard Power Fx visibility formula for "show when rows are selected."

---

## 11. Common Traps

1. **executionContext undefined**: Handler uses `executionContext.getFormContext()` but "Pass execution context as first parameter" was not checked in the designer. Fix: enable that option in handler configuration.

2. **ReactControl with container parameter**: Implementing `ReactControl` but keeping the `StandardControl`-style `init` signature. Fix: remove the container parameter and return `ReactElement` from `updateView`.

3. **pageType wrong for custom pages**: Using `pageType: "entityrecord"` when opening a custom page. Fix: use `pageType: "custom"`.

4. **recordId is not a GUID**: Passing a business key or alternate identifier as `recordId` in custom page navigation. Fix: use proper GUID or a different parameter.

5. **online.execute in offline scenarios**: Using `Xrm.WebApi.online.execute` in a command that field workers run in mobile offline mode. Fix: architectural redesign — this API requires server connectivity.

6. **Power Fx command options greyed out**: Trying to configure "Run formula" or "Show on condition" from Solutions/Tables area. Fix: open from the modern app designer.

7. **Lookup.Simple outside data-set**: When a manifest has a `data-set` element, `Lookup.Simple` properties must be nested inside it, not declared at the top level.

8. **addOnChange called unconditionally in OnLoad**: Registers the handler again on every save-refresh cycle, causing duplicate firings. Fix: conditionally call `addOnChange` based on load state.

9. **context.webAPI in canvas PCF**: Using `context.webAPI` in a PCF component that is also added to a canvas app. Fix: restrict to model-driven host or redesign to avoid web API from the component.

10. **feature-usage in canvas manifest**: `feature-usage` is model-driven only. A canvas-app PCF manifest that includes this element will be rejected.

11. **setValue without fireOnChange**: Setting a value programmatically and expecting OnChange handlers to run automatically. Fix: call `attribute.fireOnChange()` after `setValue()`.

12. **destroy not implemented**: PCF component registers browser listeners in `init` but never removes them. Fix: implement `destroy` to unregister all external listeners and subscriptions.

---

## Deeper Exam Detail

This section contains deeper API detail, fuller method lists, lifecycle nuances, and edge-case decision rules. Each claim is sourced directly from Microsoft Learn documentation.

---

### PCF: Full context object surface area

The `context` object passed into every PCF lifecycle method exposes the following top-level namespaces. Availability varies by host (model-driven vs. canvas):

| Namespace | Model-Driven | Canvas | What it provides |
|---|---|---|---|
| `context.parameters` | Yes | Yes | All manifest-declared properties as typed objects |
| `context.webAPI` | Yes | No | Dataverse CRUD + execute (same shape as Xrm.WebApi) |
| `context.device` | Yes | Yes (mobile) | captureAudio, captureImage, captureVideo, getBarcodeValue, getCurrentPosition, pickFile |
| `context.utils` | Yes | Yes (partial) | lookupObjects, getEntityMetadata, hasEntityPrivilege, openFile, openUrl, openAlertDialog, openConfirmDialog |
| `context.navigation` | Yes | Yes | openForm, openUrl, openAlertDialog, openConfirmDialog, openFile, openWebResource |
| `context.factory` | Yes | Yes | createPopup, getPopupService |
| `context.formatting` | Yes | Yes | formatCurrency, formatDecimal, formatInteger, formatLanguage, formatTime, parseDateFromInput |
| `context.userSettings` | Yes | Yes | userId, userName, languageId, timeZoneUtcOffsetMinutes, securityRoles |
| `context.client` | Yes | Yes | getClient() (Web/Mobile/Outlook), getFormFactor() (Desktop/Tablet/Phone), isOffline() |
| `context.mode` | Yes | Yes | isControlDisabled, isVisible, allocatedHeight, allocatedWidth |
| `context.resources` | Yes | Yes | getResource, getString (accesses .resx strings) |
| `context.updatedProperties` | Yes | Yes | Array of property names that changed — use in updateView to render selectively |

Source: https://learn.microsoft.com/en-us/power-apps/developer/component-framework/reference/

**Decision rule — selective rendering:** Inside `updateView`, check `context.updatedProperties` before doing expensive re-renders. If only `"layout"` changed (resize), skip data re-fetch.

---

### PCF: ReactControl ("virtual") — deeper details

ReactControl uses `control-type="virtual"` in the manifest (not `"standard"`). The `<resources>` block must declare `<platform-library>` elements instead of bundling React/Fluent yourself:

```xml
<resources>
  <code path="index.ts" order="1" />
  <platform-library name="React" version="16.14.0" />
  <platform-library name="Fluent" version="9.46.2" />
</resources>
```

Key differences from `StandardControl`:

- The manifest `control-type` attribute is `"virtual"`, not `"standard"`. Changing this value alone does **not** convert an existing control — you must rebuild from the `react` template (`pac pcf init -fw react`).
- `ReactControl.init` has no `div`/container parameter. Signature: `init(context, notifyOutputChanged, state)`.
- `ReactControl.updateView(context)` returns a `ReactElement` — the framework owns mounting/unmounting.
- React and Fluent libraries are **not bundled** in the control package; they are provided by the platform at runtime. This means bundle size is significantly smaller.
- Platform loads React 17.0.2 at runtime for model-driven apps even if the manifest declares 16.14.0. Canvas loads 16.14.0. Write code compatible with both.
- ReactControl is **not supported in Power Pages** — only canvas and model-driven apps.
- You cannot convert an existing StandardControl to ReactControl by editing the manifest — a new project from the `react` template is required.

Source: https://learn.microsoft.com/en-us/power-apps/developer/component-framework/react-controls-platform-libraries

---

### PCF: feature-usage — complete `uses-feature` name list

The `<feature-usage>` element (model-driven only) wraps one or more `<uses-feature>` children. The recognized `name` attribute values are:

- `Device.captureAudio`
- `Device.captureImage`
- `Device.captureVideo`
- `Device.getBarcodeValue`
- `Device.getCurrentPosition`
- `Device.pickFile`
- `Utility`
- `WebAPI`

If `required="true"` and the host does not support the feature, the component will not load. Omitting a feature from this list and then calling it at runtime is unsupported and will fail silently or throw.

Source: https://learn.microsoft.com/en-us/power-apps/developer/component-framework/manifest-schema-reference/feature-usage

---

### Client API: formContext object model — full sub-object breakdown

`formContext` is the recommended replacement for the deprecated `Xrm.Page`. It provides two top-level objects:

**`formContext.data`**

| Sub-object / method | Purpose |
|---|---|
| `formContext.data.entity` | Methods for the record: `getId()`, `getEntityName()`, `getIsDirty()`, `save()`, plus `attributes` collection |
| `formContext.data.entity.attributes` | Collection of all columns on the form — access with `.get("fieldname")` |
| `formContext.data.process` | Business process flow interaction: `getActiveProcess()`, `getActiveStage()`, `moveNext()`, `movePrevious()` |
| `formContext.data.attributes` | Non-table-bound attributes (header/footer fields) |
| `formContext.data.addOnLoad` / `removeOnLoad` | Dynamically add/remove OnLoad handlers at runtime |
| `formContext.data.save(options)` | Programmatic save; accepts `{ saveMode: 1 }` for Save, `{ saveMode: 2 }` for SaveAndClose |
| `formContext.data.refresh(save)` | Refreshes form data; if `save=true` saves first |

**`formContext.ui`**

| Method / property | Purpose |
|---|---|
| `formContext.ui.tabs` | Collection of all tabs — use `.get("tabname").setVisible(bool)` |
| `formContext.ui.controls` | Collection of all controls — use `.get("controlname")` |
| `formContext.ui.quickForms` | Collection of all quick view controls |
| `formContext.ui.formSelector` | `.getCurrentItem()` returns current form; `.items` lists all available forms |
| `formContext.ui.navigation.items` | Collection of left-nav items |
| `formContext.ui.setFormNotification(msg, level, id)` | Shows a banner notification at form level (level: `"ERROR"`, `"WARNING"`, `"INFO"`) |
| `formContext.ui.clearFormNotification(id)` | Removes a specific form notification by its id |
| `formContext.ui.getFormType()` | Returns: 0=Undefined, 1=Create, 2=Update, 3=ReadOnly, 4=Disabled, 6=BulkEdit |
| `formContext.ui.refreshRibbon(refreshAll)` | Forces command bar to re-evaluate visibility/enable rules |
| `formContext.ui.close()` | Closes the form |
| `formContext.ui.getViewPortHeight()` / `getViewPortWidth()` | Returns current viewport dimensions in pixels |
| `formContext.ui.setFormEntityName(name)` | Sets the entity name displayed in the form header |
| `formContext.ui.footerSection` | **Removed** in October 2021 (2021 Release Wave 2) — do not reference |

Note: `formContext.ui.navigation` and `formContext.ui.formSelector` are **not available in Dynamics 365 for tablets**.

Source: https://learn.microsoft.com/en-us/power-apps/developer/model-driven-apps/clientapi/clientapi-form-context  
Source: https://learn.microsoft.com/en-us/power-apps/developer/model-driven-apps/clientapi/reference/formcontext-ui

---

### Client API: Execution context — async usage restrictions

The execution context object (and the `formContext` derived from it) is only **guaranteed valid during the synchronous portion of the event handler**. Holding a reference across async boundaries is unsafe:

- **Promise `.then()` callback**: The form may have navigated away by the time the promise resolves. `formContext.getAttribute("name").getValue()` may return `null`.
- **`async/await` after an `await` statement**: The synchronous event has already completed; context state may be stale.
- **`setTimeout` / `setInterval`**: Context is valid only during the original synchronous execution — deferred callbacks that use the captured `formContext` reference may behave unexpectedly.

**Pattern:** Capture all values you need from `formContext` synchronously at the top of the handler before any async call. Pass those captured values into the async chain rather than closing over `formContext` itself.

Source: https://learn.microsoft.com/en-us/power-apps/developer/model-driven-apps/clientapi/clientapi-execution-context

---

### Client API: OnSave event — full behavior and async support

**Trigger conditions for OnSave** (more exhaustive than most guides list):

1. User clicks Save or Refresh in the command bar — even when no data has changed.
2. `formContext.data.entity.save()` is called in code — even when no data has changed.
3. User navigates away with unsaved data.
4. AutoSave fires (30 seconds after last change, when AutoSave is enabled).
5. `formContext.data.save()` is called with unsaved data.
6. `formContext.data.refresh(true)` is called with unsaved data.

**Exception:** OnSave and PostSave handlers do **not** fire for appointment, recurring appointment, or service activity records — the platform uses the `Book` message instead of `Create`/`Update` for these.

**getSaveMode() return values** (use inside OnSave to detect why the save is happening):

| Value | Meaning |
|---|---|
| 1 | Save |
| 2 | SaveAndClose |
| 5 | Deactivate |
| 6 | Reactivate |
| 7 | Send (email) |
| 15 | Disqualify |
| 16 | Qualify |
| 47 | Assign |
| 58 | Save as Completed (Activity) |
| 59 | SaveAndNew |
| 70 | AutoSave |

**Cancelling a save:** Call `executionContext.getEventArgs().preventDefault()` synchronously inside the OnSave handler. `preventDefault()` cannot be called inside an async callback — it must be called before the first `await`.

**Async OnSave handlers:**
- An OnSave handler that returns a `Promise` makes the event asynchronous — the platform waits for the promise to settle before saving.
- Default timeout: **10 seconds per promise**. Five handlers each returning a promise = up to 50 seconds total wait.
- If a handler times out or the promise rejects, the save continues unless `preventDefault()` was already called.
- To disable the 10-second timeout for a specific handler (e.g., waiting for user input in a dialog), call `context.getEventArgs().disableAsyncTimeout()` **before any `await` statement**.
- Async OnSave must be **enabled per app** via the app Settings > Features > "Async onSave handler" toggle.
- Wrap multiple concurrent async calls in `Promise.all()` and return the single combined promise rather than registering multiple handlers that each return individual promises.

Source: https://learn.microsoft.com/en-us/power-apps/developer/model-driven-apps/clientapi/reference/events/form-onsave

---

### Client API: Xrm.WebApi — complete method list and offline behavior

**Top-level `Xrm.WebApi` methods** (work in both online and offline mode; source is online server when online, offline data store when offline):

| Method | Signature summary |
|---|---|
| `createRecord(entityLogicalName, data)` | Returns promise with `{ entityType, id }` |
| `deleteRecord(entityLogicalName, id)` | Returns promise with `{ entityType, id, name }` |
| `retrieveRecord(entityLogicalName, id, options)` | options = OData `$select`/`$expand` string |
| `retrieveMultipleRecords(entityLogicalName, options, maxPageSize)` | Returns `{ entities: [], nextLink }` |
| `updateRecord(entityLogicalName, id, data)` | Returns promise with `{ entityType, id }` |
| `isAvailableOffline(entityLogicalName)` | Returns boolean — is this table in the offline profile and currently available? |
| `execute(request)` | Only on `Xrm.WebApi.online` — see below |
| `executeMultiple(requests)` | Only on `Xrm.WebApi.online` — batch execute |

**`Xrm.WebApi.online.execute(request)` — request object structure:**

The `request` object must expose a `getMetadata()` method on its **prototype** (not on the instance). The `getMetadata()` return value requires:

| Property | Type | Values |
|---|---|---|
| `operationType` | Number | `0` = Action, `1` = Function, `2` = CRUD |
| `operationName` | String | Name of the action/function, or: `"Create"`, `"Retrieve"`, `"Update"`, `"Delete"`, `"Associate"`, `"Disassociate"` |
| `boundParameter` | String or null | `null` = unbound; `"entity"` = bound to a table; `undefined` = CRUD |
| `parameterTypes` | Object | Keyed by parameter name; each entry has `typeName` and `structuralProperty` (0-5) |

`operationType` structural property enum: `0`=Unknown, `1`=PrimitiveType, `2`=ComplexType, `3`=EnumerationType, `4`=Collection, `5`=EntityType.

The response object from `execute` includes: `ok` (boolean), `status` (number), `statusText`, `headers`, `url`, `json()` (Promise resolving to parsed body), `text()` (Promise resolving to string). The `body` and `type` properties are deprecated.

`executeMultiple` is available only on `Xrm.WebApi.online` and batches multiple action/function/CRUD requests in a single call.

Source: https://learn.microsoft.com/en-us/power-apps/developer/model-driven-apps/clientapi/reference/xrm-webapi  
Source: https://learn.microsoft.com/en-us/power-apps/developer/model-driven-apps/clientapi/reference/xrm-webapi/online/execute

---

### Modern commanding: Power Fx `Self.Selected` object — full property list

The `Self` object in Power Fx commands exposes the current selection context:

| Property | Type | Description |
|---|---|---|
| `Self.Selected.Item` | Record | One selected record. Returns Blank when no selection or when `SelectionMax <> 1`. |
| `Self.Selected.AllItems` | Table | All selected records. Returns empty table when nothing selected. |
| `Self.Selected.State` | Enum | `Edit`=0, `New`=1, `View`=2 |
| `Self.Selected.Unsaved` | Boolean | True if selected record(s) have unsaved changes. Always false when AutoSave is true (the default). |

**AutoSave behavior:** By default, commands save the form buffer before executing — the form is saved on behalf of the maker before the Power Fx formula runs. Any save errors are surfaced in the form UI, not in the formula. JavaScript commands historically required explicit save calls at the start; Power Fx eliminates that boilerplate.

**Power Fx functions explicitly not supported with commanding** (key subset for exam awareness):

`Back()`, `Collect()`, `Clear()`, `Set()`, `UpdateContext()`, `LoadData()`, `SaveData()`, `Exit()`, `Param()`, `User()`, `ResetForm()`, `SubmitForm()`, `ViewForm()`, `ScanBarcode()`, `Print()`, `Language()`

**Unsupported platform contexts:** Power Fx commands do **not** run in:
- Dynamics 365 app for Outlook
- Model-driven apps hosted inside a Portal

**Dataverse-only data source:** When writing Power Fx formulas in the command designer, Microsoft Dataverse is the only directly supported data source. For external data connections, use a custom page.

**Single component library per app:** Each model-driven app supports only one Power Fx command component library. Multiple libraries cause the error "Unable to initialize component manager. There are multiple component libraries associated with your app." Resolution: remove duplicate `AppElement` records for the app via Power Automate + Dataverse.

Source: https://learn.microsoft.com/en-us/power-apps/maker/model-driven-apps/commanding-use-powerfx  
Source: https://learn.microsoft.com/en-us/power-apps/maker/model-driven-apps/command-designer-limitations

---

### Modern commanding: Power Fx Navigate function patterns

The Power Fx `Navigate()` function in commands supports several target forms:

```
Navigate( myCustomPage )                              // custom canvas page by name
Navigate( Accounts )                                  // default view of Accounts table
Navigate( 'Accounts (Views)'.'My Active Accounts' )  // specific system view
Navigate( Gallery1.Selected )                         // default form for a specific record
Navigate( Defaults(Accounts) )                        // new record form (create mode)
```

For navigation scenarios not covered by Power Fx `Navigate()` (e.g., opening dialogs with custom options, setting target=2 for overlay), JavaScript and `Xrm.Navigation.navigateTo` remain the only option.

Source: https://learn.microsoft.com/en-us/power-apps/maker/model-driven-apps/commanding-use-powerfx

---

### Edge-case decision rules ("What if..." scenarios)

**What if a PCF control needs to call `context.webAPI` but must also run in canvas?**
`context.webAPI` is model-driven only. If canvas support is required, remove the `webAPI` call from the PCF component and have the canvas app pass data in via `input` properties instead — or use separate model-driven and canvas variants of the component. Do not use `feature-usage` to declare `WebAPI` and then deploy to canvas; the declaration is ignored and the call will throw at runtime.

**What if an OnSave handler needs to wait for a user confirmation dialog before allowing the save?**
Return a Promise from the handler (requires Async OnSave to be enabled in app settings). Call `context.getEventArgs().disableAsyncTimeout()` before the first `await` to prevent the 10-second timeout from firing prematurely. Call `preventDefault()` synchronously if the user cancels.

**What if the command bar needs to check a column value on the selected record for visibility?**
Use `Self.Selected.Item.'Column Name'` in the Power Fx Visible formula (e.g., `Self.Selected.Item.'Account Rating' > 20`). This only works when exactly one record is selected — `Self.Selected.Item` returns Blank when multiple records are selected or `SelectionMax <> 1`.

**What if a JavaScript web resource is referenced from a command but the solution is exported without it?**
The command will fail at runtime with a missing resource error. JavaScript commands require their backing JavaScript web resource to be included in the same solution. The same rule applies to Power Fx commands and their component library.

**What if a PCF control's `updateView` is computationally expensive and fires too often?**
Check `context.updatedProperties` at the start of `updateView`. If the array contains only `"layout"` or other non-data properties, skip the expensive computation and return early. Only re-render when data-relevant properties have changed.

**What if you need to trigger a custom API from client script in both online and offline mode?**
There is no offline equivalent of `Xrm.WebApi.online.execute`. If the action must work offline, the operation must be queued locally using a custom offline strategy (e.g., storing a pending operation in offline data that syncs when connectivity is restored). There is no built-in "offline execute" API.

**What if a ReactControl ("virtual") PCF is added to Power Pages?**
It is not supported. React controls and platform libraries only work in canvas and model-driven apps. Use a StandardControl for Power Pages targets.

Source (consolidated from all above Microsoft Learn pages).
