# Implement Power Apps Improvements  

_Exam weight 10–15% · 35 questions across all sets._

---

### 1. A development team maintains five canvas apps for different business units. Each app needs the same branded header, validation banner, and navigation footer, and future design changes must be applied centrally with minimal per-app rework.

Which component should you include in the technical design?

- **A.** Component library ✅
- **B.** Solution patch
- **C.** Environment variable
- **D.** Custom connector

> **Answer:** A. Component library

A component library is the correct choice because it is specifically designed to store reusable canvas app components that can be shared across multiple apps. This allows the team to define the branded header, validation banner, and navigation footer once and consume those components in each app rather than rebuilding them repeatedly. That directly supports centralized maintenance and consistent user experience across the portfolio.

The key design goal is not just reuse, but reusable UI and behavior inside canvas apps with a central update path. A solution patch is an ALM mechanism, an environment variable stores configuration, and a custom connector integrates external services. None of those components solves the actual problem of building reusable visual and behavioral app elements for multiple canvas apps.

<sub>Set A · Q15</sub>

---

### 2. A company is standardizing its inspection apps. Each canvas app must use the same address picker, status badge, and warning dialog, and the controls must be updated by one platform team without editing every app individually. The controls also need to preserve the same visual behavior across environments after solution deployment.

Which implementation approach is the best fit?

- **A.** Copy controls between apps
- **B.** Build a component library ✅
- **C.** Create app-level variables
- **D.** Use a Dataverse table

> **Answer:** B. Build a component library

A component library is the best fit because it allows the platform team to build reusable components once and distribute them to multiple canvas apps. That supports centralized ownership of the address picker, status badge, and warning dialog while keeping their behavior and styling consistent. It also aligns well with managed solution-based delivery because the reusable components are treated as shared app assets rather than copied fragments.

The scenario is focused on reusable presentation and interaction elements, not on storing data or sharing configuration. Copying controls between apps would immediately introduce duplication and make ongoing updates harder to govern. App-level variables and Dataverse tables can support app logic and data, but neither gives the team a reusable component packaging model for consistent UI elements across many canvas apps.

<sub>Set A · Q16</sub>

---

### 3. A platform team is reviewing four proposed implementation approaches for shared canvas app UI elements. One proposal best matches a requirement for centrally maintained reusable controls across multiple apps.

Exhibit 1

Which proposal should the team choose?

- **A.** Proposal A
- **B.** Proposal B
- **C.** Proposal C ✅
- **D.** Proposal D

> **Answer:** C. Proposal C

Proposal C is the correct answer because the requirement is specifically about centrally maintained reusable controls across multiple canvas apps. The exhibit shows that component library components provide low update effort and high design consistency, which are the two most important decision factors in this scenario. A component library is built to solve exactly this problem by allowing one shared component definition to be consumed by many apps.

The other proposals all suffer from either duplication or manual recreation. Even app-specific local components improve structure inside one app but do not create true cross-app reuse. This question is testing whether the technical design recognizes the difference between “a component exists” and “a component is centrally reusable across multiple apps,” which is a critical distinction when evaluating reusable component libraries.

<sub>Set A · Q21</sub>

---

### 4. A platform team updates a shared button component in a component library and publishes the library. Makers report that several consuming canvas apps still show the old button style in production. The apps themselves were not republished after the new library version was made available.

What is the most likely cause?

- **A.** Missing app update adoption ✅
- **B.** DLP policy restriction
- **C.** Broken connection reference
- **D.** Business unit reassignment

> **Answer:** A. Missing app update adoption

The most likely cause is that the consuming apps have not adopted and republished the updated component library version. Publishing the library makes the updated reusable component available, but the consuming apps still need to take that updated dependency into their own published version. This is a common operational issue with reusable component libraries because the library lifecycle and the app lifecycle are related but not identical.

The scenario is specifically about a UI style update not appearing in production, which points to dependency adoption rather than security, connector, or organizational structure issues. A strong implementation approach for reusable component libraries includes not just building the components, but also planning how consuming apps update, validate, and republish shared component changes.

<sub>Set A · Q22</sub>

---

### 5. A developer is creating a reusable status badge inside a canvas app component library. The component must let each consuming app set the label text while keeping the rendering logic inside the component.

Snippet

// Component custom property
StatusText (Input)

// Label inside the component
lblStatus.Text = StatusText
What does this implementation enable?

- **A.** Per-app text injection ✅
- **B.** Cross-environment DLP inheritance
- **C.** Connector authentication reuse
- **D.** Dataverse row security

> **Answer:** A. Per-app text injection

This implementation enables per-app text injection into the reusable component. The component exposes an input property named StatusText, and the internal label binds to that property. That means each consuming app can pass a different value while the presentation logic remains centralized inside the component definition. This is a common pattern when building reusable component libraries because it separates reusable rendering from app-specific inputs.

The snippet is testing the design principle behind reusable components rather than Power Fx trivia. A reusable component becomes useful when its behavior or display can be parameterized through properties instead of hard-coded per app. That is exactly what the input property accomplishes here: it allows the same status badge component to be reused in multiple places with different text values.

<sub>Set A · Q39</sub>

---

### 6. A maker adds this formula to a button in a canvas app to submit an expense workflow.

Snippet

UpdateContext({busy:true});
ExpenseSubmit.Run(txtExpenseId.Text);
Notify("Submitted");
UpdateContext({busy:false});
Which characteristic applies to this design?

- **A.** Async button-triggered flow ✅
- **B.** In-transaction server logic
- **C.** Triggerless app reference model
- **D.** Label Text invocation pattern

> **Answer:** A. Async button-triggered flow

This is an async button-triggered flow design. Microsoft documents that a control in a canvas app can start a flow, and Microsoft also shows that added flows are referenced from a behavior formula by using the .Run() syntax. The snippet is therefore a standard “button starts flow” implementation pattern from a canvas app.

It is also asynchronous in character, not transactional. Microsoft states that cloud flows are inherently asynchronous, and separately notes that flows started from a canvas app can continue even if Power Apps is closed. That combination is what makes this pattern useful for offloaded business logic after a user action.

<sub>Set B · Q1</sub>

---

### 7. A canvas app submits a field-audit package that must update Dataverse, create a SharePoint file, post to Teams, and let the user continue working immediately.

Which component should implement this business logic?

- **A.** Canvas Power Fx
- **B.** Dataverse business rule
- **C.** Cloud flow ✅
- **D.** Transactional Dataverse plug-in step

> **Answer:** C. Cloud flow

Cloud flow is the best fit because Microsoft positions Power Automate as the asynchronous option for longer-running and more complex sequences of logic, especially when multiple connectors are involved. That matches this requirement exactly: Dataverse, SharePoint, and Teams are all participating, and the user should not have to sit in the app waiting for each downstream action to finish.

This is also the most appropriate answer specifically for logic started from a canvas app. Microsoft documents that a control in a canvas app can start a flow and that the flow can continue even if the user closes Power Apps, which makes cloud flow the right orchestration layer for this kind of offloaded business process.

<sub>Set B · Q21</sub>

---

### 8. A canvas app used a cloud flow successfully for several months. After recent edits, the flow disappears from the app and the previous reference is no longer available. The team confirms the flow had originally been added by using an older version of the Power Apps panel.

What is the best fix?

- **A.** Re-add the flow manually ✅
- **B.** Recreate the solution connection reference
- **C.** Republish the environment metadata
- **D.** Convert it to a scheduled flow

> **Answer:** A. Re-add the flow manually

Re-add the flow manually is the best answer because Microsoft documents this exact issue: flows added by using an older version of the Power Apps panel can become orphaned and removed. Microsoft’s stated fix is to re-add those flows manually, which makes this a direct troubleshooting match rather than an architectural redesign problem.

This question is testing real operational behavior around canvas app and cloud flow integration, not just feature recognition. The right answer comes from knowing that the problem can be with the embedded app reference itself, not necessarily with authentication, the environment, or the flow logic.

<sub>Set B · Q25</sub>

---

### 9. A solution already contains a cloud flow with a Power Apps trigger. You need to invoke it from a button in a canvas app.

Steps

Enter ApprovalFlow.Run() in the button’s formula.

Add the flow from the Power Automate pane.

Test the button in play mode.

Choose the button’s OnSelect behavior property.

What is the correct order?

- **A.** 4 → 2 → 1 → 3
- **B.** 2 → 1 → 4 → 3
- **C.** 2 → 4 → 1 → 3 ✅
- **D.** 1 → 2 → 3 → 4

> **Answer:** C. 2 → 4 → 1 → 3

The correct order is 2 → 4 → 1 → 3. Microsoft documents that you first add the existing flow to the app from the Power Automate pane, and then reference that added flow in the formula bar. The .Run() call is the invocation syntax used after the flow has been added to the app context.

This sequence matters because the app cannot invoke a flow reference that has not yet been added. Microsoft also states that existing flows must meet specific requirements to be addable, including having a Power Apps trigger, and then shows the reference pattern using .Run() from a control formula.

• 2 is first because the flow must be added from the Power Automate pane before it becomes available under the app’s flow references.

• 4 is second because you then target the correct behavior property on the control that should launch the flow.

• 1 is third because the .Run() formula is entered after the flow is available to the app and the behavior property is selected.

• 3 is last because testing comes after the reference has been wired into the button formula.

<sub>Set B · Q26</sub>

---

### 10. A canvas app lets technicians submit equipment updates. The solution must reject invalid status combinations immediately, roll back the transaction if a related Dataverse update fails, and enforce the same rule for every app and endpoint that writes to the table.

Which implementation approach is the best fit?

- **A.** Instant cloud flow orchestration
- **B.** Dataverse plug-in ✅
- **C.** Business rule
- **D.** Delayed timer-control pattern

> **Answer:** B. Dataverse plug-in

Dataverse plug-in is the best answer because Microsoft recommends plug-ins when business logic controls changes to the database, especially when validation must occur in the Dataverse transaction itself. That is exactly what this scenario requires: immediate rejection, rollback on failure, and enforcement across all write paths rather than just one canvas app button.

This question is deliberately testing the boundary between “use a cloud flow from a canvas app” and “do not use a cloud flow here.” Microsoft’s guidance says Power Automate is strong for asynchronous complex sequences, while plug-ins are the centralized control point for transaction-bound database logic and consistent enforcement across apps, flows, and other endpoints.

<sub>Set B · Q64</sub>

---

### 11. A canvas app screen intermittently loads order data slowly after a recent release. In Monitor, the same connector request appears multiple times with multi-second durations, and several entries return HTTP 429 while the browser console stays clean.

What is the most likely cause?

- **A.** Circular control dependency loop
- **B.** Unpublished canvas app version
- **C.** Connector throttling ✅
- **D.** Missing environment role assignment

> **Answer:** C. Connector throttling

HTTP 429 in Monitor points to throttling rather than a rendering issue or a deployment mismatch. When the trace shows repeated connector calls with long durations and explicit 429 responses, the most likely problem is that the app is exceeding the allowed request rate for that connector or downstream service. Monitor is especially useful here because it exposes the call pattern, timings, and response codes in one place instead of leaving you to infer the issue from user symptoms alone.

This is a good example of using the right tool for the right failure domain. A clean browser console reduces the likelihood of a client-side JavaScript failure, while the Monitor trace clearly highlights an integration bottleneck. The troubleshooting path should focus on reducing redundant calls, caching where appropriate, and reshaping app logic so the connector is not invoked excessively during screen load.

<sub>Set C · Q24</sub>

---

### 12. A model-driven app command runs JavaScript that opens a custom page and then calls Dataverse. Users report that clicking the command does nothing in Edge, and you need to confirm whether the click handler fires and whether the outbound request fails, without changing the deployed solution.

Which tool should you use first?

- **A.** Power Apps Monitor session
- **B.** Audit history
- **C.** Solution Checker report
- **D.** Browser DevTools ✅

> **Answer:** D. Browser DevTools

Browser DevTools is the best first tool because the issue is centered on a client-side command click, script execution, and outbound browser request behavior. DevTools lets you immediately inspect the console for runtime errors, verify whether the handler is invoked, and inspect the Network tab for failed requests, status codes, and payload details. That gives you direct evidence about whether the problem is in the click pipeline, the JavaScript, or the request itself.

Monitor is still valuable, but it is not the fastest first step for this exact symptom pattern. The requirement is to confirm browser-side execution and request failure with no solution changes, and DevTools is purpose-built for that. Once the browser-level behavior is understood, you can use Monitor to correlate app events and Dataverse activity more broadly if needed.

<sub>Set C · Q26</sub>

---

### 13. A canvas app search screen returns incomplete results against a large Dataverse table. You start a Monitor session and review the formula below.

Snippet

ClearCollect(
    SearchResults,
    Filter(
        Orders,
        Left(CustomerName, 3) = txtPrefix.Text &&
        Amount > Value(txtMin.Text)
    )
)
Monitor shows a warning that only the first portion of records was queried. Which issue should you investigate?

- **A.** Stale control reference
- **B.** Delegation warning ✅
- **C.** Session cookie expiry
- **D.** Unpublished formula change set

> **Answer:** B. Delegation warning

The key clue is that Monitor reports that only the first portion of records was queried. That is a classic delegation symptom in canvas apps. The formula uses a pattern that can force client-side evaluation, and once a query becomes nondelegable, Power Apps may retrieve only a limited subset of rows before applying the remaining logic locally. The result is incomplete data even though the formula appears to work during small-scale testing.

Monitor is valuable here because it surfaces the delegation behavior at runtime instead of leaving you to infer it from user complaints. The fix path is to review the formula for nondelegable functions or expressions, redesign the query so the data source can process it server-side, and then validate the new behavior in Monitor with a fresh session.

<sub>Set C · Q30</sub>

---

### 14. A canvas app product screen takes several seconds to open. You capture a Monitor session and review the trace summary.

Exhibit 1

Which entry most likely explains the delay?

- **A.** GetProducts call ✅
- **B.** Gallery.Items rule evaluation
- **C.** Products metadata fetch event
- **D.** Header container render path

> **Answer:** A. GetProducts call

The exhibit makes the answer clear because the GetProducts connector call is dramatically slower than every other event in the trace. When a single call takes more than four seconds and the other events complete in milliseconds, that request is the most likely bottleneck driving the poor screen-open experience. Monitor helps by putting timings side by side so you can separate meaningful delays from normal background activity.

This is exactly the kind of troubleshooting decision Monitor is designed to support. Instead of assuming that rendering or formula evaluation is the issue, you use the trace to identify the slowest dependency first. The next step would be to examine the connector call in more detail, including request frequency, returned payload size, and whether the screen is loading more data than it needs up front.

<sub>Set C · Q69</sub>

---

### 15. You are diagnosing a custom page that fails when users submit a record from a model-driven app. You must isolate whether the failure comes from formula logic, browser-side script, or a network call by using Monitor and browser debugging tools.

Steps

Correlate Monitor events with browser console and network details.

Reproduce the failing action.

Retest after isolating the failing request or formula.

Start a fresh Monitor session.

What is the correct order?

- **A.** 2 → 4 → 1 → 3
- **B.** 1 → 4 → 2 → 3
- **C.** 4 → 1 → 2 → 3
- **D.** 4 → 2 → 1 → 3 ✅

> **Answer:** D. 4 → 2 → 1 → 3

The correct order is to begin by starting a fresh Monitor session, then reproduce the failing action, then correlate what Monitor captured with the browser console and Network tab, and finally retest after isolating the specific issue. That sequence preserves clean telemetry, captures the exact failing interaction, and then uses cross-tool evidence to identify whether the fault sits in formula execution, client-side runtime behavior, or the request layer.

This order is operationally strong because it avoids mixing old trace noise with new evidence. It also ensures that you do not start interpreting data before you have reproduced the problem in a controlled session. Once the failure is isolated, you validate the fix with another targeted test rather than assuming the first change solved the right issue.

• 4 is first because you need a clean capture before reproducing the problem, otherwise older events can make the trace harder to interpret.

• 2 is second because the failing behavior must actually occur while the tools are recording it.

• 1 is third because correlation makes sense only after both Monitor and the browser tools have captured the same failing action.

• 3 is last because retesting belongs after you have isolated the likely cause and applied or planned the fix.

<sub>Set C · Q72</sub>

---

### 16. A maker wants a responsive order search experience and shared the following formula design.

Snippet

App.OnStart =
    ClearCollect(
        colOrders,
        Orders
    );

GalleryOrders.Items =
    Filter(
        colOrders,
        StartsWith(CustomerName, txtSearch.Text)
    )
What is the best redesign?

- **A.** Filter Orders in the gallery ✅
- **B.** Increase row limit to 2000
- **C.** Collect inside a ForAll loop
- **D.** SaveData the browser cache

> **Answer:** A. Filter Orders in the gallery

The best redesign is to filter the remote Orders source directly in GalleryOrders.Items instead of first copying the full table into colOrders. Microsoft notes that direct gallery binding to a remote data source keeps payloads small through paging, and delegation lets the source do the filtering work. That is both faster and more scalable than loading the full table up front and then searching locally.

This snippet is also inefficient because it performs a large ClearCollect during App.OnStart, which Microsoft identifies as a common cause of slow app startup. A search experience should generally evaluate the query when needed, not force the app to preload the entire transactional table before the first screen becomes useful. Moving the filter to the gallery keeps startup lighter and preserves delegation opportunities.

<sub>Set D · Q2</sub>

---

### 17. A canvas app must load three small reference lists before users can work on the first screen. The lists are independent and are all required immediately.

Which formula pattern should you use to preload them with the least startup delay?

- **A.** Sequential App.OnStart ClearCollect chain
- **B.** Gallery Search over full collection
- **C.** Concurrent with ClearCollect ✅
- **D.** Repeated per-row LookUp calls

> **Answer:** C. Concurrent with ClearCollect

Concurrent is the best choice when you genuinely need several independent data loads at startup and those loads can happen in parallel. Microsoft documents that Concurrent allows formulas to execute at the same time and that it is commonly used to populate collections, which makes it the strongest fit for preloading a few small lookup datasets that are all needed right away.

This does not mean “preload everything.” Microsoft also recommends keeping startup payloads small and minimizing actions that delay app load, because App.OnStart can block or slow the initial experience. The best design is therefore to preload only the small reference lists that the first screen actually requires, and to avoid turning large transactional tables into startup collections.

<sub>Set D · Q20</sub>

---

### 18. A sales app works with a Dataverse table that contains hundreds of thousands of orders. The maker currently runs ClearCollect(colOrders, Orders) in App.OnStart and then filters colOrders in a gallery. Users report slow startup and incomplete search results.

Which design should you recommend?

- **A.** Increase data row limit to 2000
- **B.** SaveData full Orders cache
- **C.** AddColumns over a local collection
- **D.** Direct StartsWith gallery binding ✅

> **Answer:** D. Direct StartsWith gallery binding

The best redesign is to bind the gallery directly to the remote data source and use a delegable expression such as Filter with StartsWith where appropriate. Microsoft explains that delegation pushes the query work to the data source, and when a gallery is connected directly to a remote source, Power Apps pages data in small increments instead of pulling a large dataset into the client up front. That is exactly what this scenario needs: small payloads, correct results, and better scale.

The existing design is slow because it preloads a large table into a collection during startup and then searches locally. Microsoft warns that OnStart work can delay the first screen, and nondelegable or local-processing patterns can return incomplete results when the table is large. A direct delegable gallery query solves both the startup problem and the correctness problem much more cleanly than collection-first design.

<sub>Set D · Q21</sub>

---

### 19. A canvas app searches a large customer dataset and feels slow in production. You need to keep payloads small and preserve correct results across very large tables.

Which two changes should you make? (Select TWO.)

- **A.** Materialize the full table at startup
- **B.** Use server-side view prefiltering ✅
- **C.** Replace warnings by raising row limit
- **D.** Use In against the remote source
- **E.** Use StartsWith or Filter ✅

> **Answer:** B. Use server-side view prefiltering · E. Use StartsWith or Filter

Using a server-side view to prefilter data is a strong design choice because Microsoft recommends server-side views to present a single queryable structure, prefilter the data you need, and minimize both payload and client-side compute. That makes the app faster and reduces the temptation to build expensive client-side joins and filters.

Using StartsWith or a delegable Filter pattern is the other correct answer. Microsoft specifically recommends expressions that can leverage indexing and server-side processing, and it calls out StartsWith or Filter as preferred patterns over ones that effectively read the entire table. Together, those two changes keep the query delegated and the data volume smaller.

<sub>Set D · Q22</sub>

---

### 20. A published canvas app searches a large Dataverse table as users type in a search box. Users report lag and intermittent failures. In Live monitor, you see many GetRows events and some HTTP 429 responses while users are typing.

What should you change first?

- **A.** Raise data row limit to 2000
- **B.** Set TextInput.DelayOutput to true ✅
- **C.** Move search logic to App.OnStart
- **D.** Enable Debug published app permanently

> **Answer:** B. Set TextInput.DelayOutput to true

DelayOutput is the best first change because Microsoft documents that when DelayOutput is set to true, user input is registered after a short delay, which is useful for postponing expensive operations such as filtering until the user finishes typing. In this scenario, the app is issuing too many requests while the user types, so delaying execution reduces unnecessary query churn without changing the functional search behavior.

Live monitor is the right tool for diagnosing this problem because Microsoft states that it shows event streams, durations, result information, and runtime errors, including failures seen during published app sessions. The 429 responses in Monitor indicate rate limiting from too many requests in a short period, so reducing per-keystroke requests is the most direct and least invasive first fix.

<sub>Set D · Q24</sub>

---

### 21. A canvas app loads three sources during startup. The maker wants the data calls to run in parallel and then set a summary variable after the loads finish.

Snippet

Concurrent(
    ClearCollect(colAccounts, Accounts),
    ClearCollect(colContacts, Contacts),
    Set(varTotal, CountRows(colAccounts) + CountRows(colContacts))
)
What is the best fix?

- **A.** Keep Set inside Concurrent
- **B.** Use a dependent Concurrent branch
- **C.** Set after Concurrent ✅
- **D.** Chain everything with semicolons

> **Answer:** C. Set after Concurrent

Concurrent is designed to evaluate formulas at the same time, which is useful when startup formulas include Dataverse or connector calls. However, formulas inside the same Concurrent block must not depend on one another, because Power Apps does not guarantee the order in which those branches start or finish.

The correct fix is to move the Set call after the Concurrent block so the collections finish loading first and the summary runs afterward. Microsoft’s guidance explicitly notes that formulas after Concurrent can safely depend on formulas inside it because they complete before evaluation continues to the next chained formula.

<sub>Set E · Q16</sub>

---

### 22. A maker is building a label formula that calculates a discount message from several repeated intermediate values. The formula must stay declarative, readable, and local to that property, and the team does not want to create screen or app state just to hold temporary values.

Which approach should you use?

- **A.** Use With ✅
- **B.** Add screen context variables
- **C.** Initialize global variables
- **D.** Reference hidden controls

> **Answer:** A. Use With

With is the best fit because it lets you define named values inside a single formula and then use them within that local scope. Microsoft states that With evaluates a formula for a single record or inline record of named values and is intended to improve readability by dividing complex formulas into smaller named sub-formulas.

This is exactly the pattern needed when a complex Power Fx expression should remain self-contained and declarative. Microsoft also notes that With is preferred over context or global variables for this kind of local calculation because it is easier to understand, self-contained, and usable in declarative formula contexts.

<sub>Set E · Q17</sub>

---

### 23. A gallery must search and filter a Dataverse table that contains more than 1 million rows. The results must stay correct at scale, and the team wants to avoid formulas that silently return incomplete results. Which TWO changes should you make? (Select TWO.)

- **A.** ClearCollect full datasets on start
- **B.** Use delegable Filter predicates ✅
- **C.** AddColumns before server filtering
- **D.** Raise row limit to 2000
- **E.** Remove nondelegable operators ✅

> **Answer:** B. Use delegable Filter predicates · E. Remove nondelegable operators

The two best changes are to keep the query delegable and to remove nondelegable operators from the formula. Microsoft documents that Filter, Search, and LookUp can delegate when the data source and formula support it, and delegation is the key to keeping results correct and performant on very large datasets.

Microsoft also warns that when a query is nondelegable, Power Apps retrieves only the first 500 records by default, or up to 2,000 if the row limit is raised, and then evaluates locally. That means formulas can return incomplete or misleading results on large tables, so removing nondelegable pieces is far more important than simply increasing the row cap.

<sub>Set E · Q19</sub>

---

### 24. A gallery formula nests Filter and AddColumns, and column references become ambiguous between the outer and inner record scopes.

Which Power Fx feature should you use?

- **A.** ThisItem reference
- **B.** As ✅
- **C.** Parent control reference
- **D.** Self property reference

> **Answer:** B. As

The As operator is the best choice because it lets you give the current record a name in record-scope functions and nested formulas. Microsoft documents that As can replace the default ThisItem or ThisRecord name and is used to make formulas easier to understand and to resolve ambiguity when nesting record scopes.

That matters especially in advanced formulas that combine functions such as Filter, AddColumns, and other record-scope operations. Once multiple current records are in play, naming them explicitly with As is the cleanest way to keep references precise and readable.

<sub>Set E · Q21</sub>

---

### 25. A model-driven app main form opens slowly because it loads a large related-record subgrid that most users do not need immediately. Users still need access to the data from the same form.

Which design change should you make first?

- **A.** Additional synchronous plug-in step
- **B.** Additional client business rules
- **C.** Collapsed tab ✅
- **D.** Calculated column refresh logic

> **Answer:** C. Collapsed tab

A collapsed tab is the best first design choice because it reduces the amount of content that must be rendered during the initial form load. When a heavy subgrid is not needed immediately, moving it off the initially expanded area helps improve perceived and actual form responsiveness without removing access to the data.

This is a classic model-driven form optimization decision. It keeps the same form experience, avoids unnecessary pro-code changes, and targets one of the most common causes of slow render time: loading too much nonessential content on first paint. For PL-400 design decisions, the best answer is often the one that reduces initial UI workload with the least architectural disruption.

<sub>Set E · Q22</sub>

---

### 26. A company uses one account form for sales reps and sales managers. The current form includes dashboards, multiple subgrids, and review components that managers need, but most reps use only a small set of core fields and complain about slow load times on mobile networks.

Which design change should you make to improve performance with minimal custom code?

- **A.** Business process flow
- **B.** Editable grid default
- **C.** More tabs with same controls
- **D.** Role-specific forms ✅

> **Answer:** D. Role-specific forms

Role-specific forms are the best answer because they let you deliver a lighter experience to sales reps while preserving richer components for managers. That improves initial load time by reducing unnecessary controls, scripts, and related data components for the users who do not need them.

This is also a strong technical design because it aligns performance optimization with user intent instead of trying to make one overloaded form serve every persona equally. Model-driven app performance often improves when forms are simplified and targeted by security role or app context. The requirement specifically asks for minimal custom code, and role-specific forms satisfy that cleanly.

<sub>Set E · Q23</sub>

---

### 27. A large model-driven app table is used by hundreds of customer service agents. The default landing experience is slow because the first form and the default view both contain more data than most agents need for their first action.

Which two design changes should you make? (Select TWO.)

- **A.** Add more quick view forms
- **B.** Trim default view columns ✅
- **C.** Run Web API on form load
- **D.** Collapse rarely used tabs ✅
- **E.** Enable more lookup views

> **Answer:** B. Trim default view columns · D. Collapse rarely used tabs

Trimming default view columns and collapsing rarely used tabs are the best pair because they reduce the amount of information that has to be rendered immediately in both the list experience and the form experience. That directly targets the first-screen performance problem described in the scenario.

This pair also reflects good model-driven design discipline. Views should show the minimum useful set of columns for the primary task, and forms should not fully expose heavy secondary content at initial load when users do not need it. Together, these changes improve usability and performance without introducing avoidable code or moving the solution into the wrong extension model.

<sub>Set E · Q24</sub>

---

### 28. A developer added JavaScript to an account form to fetch related opportunity data during every load. The data is needed only when users open a secondary tab.

Snippet

function onLoad(executionContext) {
  var formContext = executionContext.getFormContext();

  Xrm.WebApi.retrieveMultipleRecords(
    "opportunity",
    "?$select=name&$filter=_parentaccountid_value eq " + formContext.data.entity.getId()
  ).then(function (result) {
    formContext.ui.setFormNotification(
      "Related opportunities: " + result.entities.length,
      "INFO",
      "oppCount"
    );
  });
}
What is the best change to improve initial form performance?

- **A.** Defer Web API call ✅
- **B.** Move retrieval to onSave event
- **C.** Register another onLoad handler
- **D.** Run same query in ribbon logic

> **Answer:** A. Defer Web API call

Deferring the Web API call is the best change because the data is not required for initial form rendering. When a query is only relevant after a user opens a secondary tab or performs a later action, running it during onLoad adds avoidable latency and script activity to every form open.

This is a strong model-driven performance design principle: do less work during form initialization. Client API code should be limited to what is actually needed for the first interaction. Moving the call to a later user action or tab-driven moment reduces unnecessary network traffic and improves responsiveness for the majority of sessions.

<sub>Set E · Q25</sub>

---

### 29. A sales team opens a model-driven app to review open accounts first thing each morning. The account table contains millions of rows, and the team wants the fastest practical default landing view for daily work.

Exhibit 1

Which view should you set as the default landing view?

- **A.** All Open Accounts
- **B.** My Open Accounts ✅
- **C.** Open Accounts with Related Contacts
- **D.** Regional Accounts Review

> **Answer:** B. My Open Accounts

My Open Accounts is the best default landing view because it combines a narrower result set with fewer displayed columns and a simpler sort pattern. On a very large table, reducing the number of returned rows and keeping the view lightweight helps users reach their first action faster.

The exhibit shows that this option is the most focused operationally. It filters by current owner, avoids related-table columns, and surfaces only six columns. That makes it a better performance design than broader or more complex views, especially when the requirement is a daily default view for individual sellers rather than an analytical review screen.

<sub>Set E · Q26</sub>

---

### 30. A button formula patches each selected row and also tries to maintain a running total inside the same loop. During testing, totals are inconsistent and the authoring environment flags part of the formula as invalid.

What is the best redesign?

- **A.** Maintain a running context variable
- **B.** Wrap the loop in Concurrent
- **C.** ClearCollect totals before Patch
- **D.** Sum outside ForAll ✅

> **Answer:** D. Sum outside ForAll

ForAll is not a safe place to build logic that depends on iteration order or mutable running state. Microsoft states that records in ForAll can be processed in any order and, when possible, in parallel, which means formulas that assume sequential accumulation can produce inconsistent results.

Microsoft also notes that UpdateContext, Clear, and ClearCollect cannot be used inside ForAll, and recommends With for single-record scoped values. The best redesign is to separate the aggregate calculation from the loop, using something like Sum outside ForAll, while keeping per-record logic inside the loop limited to actions or local calculations.

<sub>Set E · Q53</sub>

---

### 31. A canvas app must load three reference tables when the user enters the home screen, and those loads should happen in parallel. The same screen also needs a temporary table containing the numbers 1 through 12 for a month selector. Which two functions should you use? (Select TWO.)

- **A.** Patch
- **B.** Concurrent ✅
- **C.** ParseJSON
- **D.** Sequence ✅
- **E.** ForAll with ClearCollect

> **Answer:** B. Concurrent · D. Sequence

Concurrent is the correct choice when multiple independent formulas or data-loading operations should run in parallel. That helps reduce wait time when the app is fetching separate data sources that do not depend on one another. Sequence is the correct choice for generating a numeric table such as 1 through 12 without manually building a collection row by row.

These two functions solve different but complementary app-logic problems. One improves startup or screen-entry efficiency by parallelizing independent work, while the other generates structured numeric records directly in Power Fx. Using them together reflects the kind of advanced-function judgment Microsoft expects in real canvas-app implementations.

<sub>Set F · Q20</sub>

---

### 32. A development team maintains 12 canvas apps that share the same branded header, validation banner, and navigation controls. They want centralized reuse, support for custom input and output properties, and no custom code requirement. Which artifact should you use? Select only one answer.

- **A.** Component library ✅
- **B.** PCF code component package
- **C.** Custom page
- **D.** Starter canvas app template

> **Answer:** A. Component library

A component library is the best fit when multiple canvas apps need reusable UI elements that can be centrally maintained and consumed across apps. It supports custom properties, encourages consistent behavior and styling, and stays within the low-code canvas-app component model. That makes it the most direct solution for reusable, centrally governed app-building blocks.

The important constraint here is “no custom code requirement.” PCF is powerful, but it is a code-first extensibility model and is unnecessary when the need is shared reusable canvas components. A template can help apps start from a common baseline, but it does not provide the same centralized reuse and update model as a component library.

<sub>Set F · Q21</sub>

---

### 33. A canvas app calls an instant cloud flow to update an order and then display the returned status in a notification. The current flow runs successfully, but the app cannot capture any output from that same call.

Configuration

Trigger: Power Apps (V2)
Inputs:
- orderId : Text
Actions:
- Get row by ID
- Update row
- Compose newStatus
Response action: None
Which change should you make? Select only one answer.

- **A.** When an HTTP request is received plus response
- **B.** Child flow with output parameters
- **C.** Compose action after trigger
- **D.** Respond to a PowerApp or flow ✅

> **Answer:** D. Respond to a PowerApp or flow

When a canvas app calls a cloud flow and needs data returned in the same interaction, the flow must explicitly send a response back to Power Apps. The standard way to do that is to use the Respond to a PowerApp or flow action. Without that response action, the flow may complete successfully, but the app has nothing structured to receive as return data.

This is a common implementation mistake: makers build the trigger and internal actions correctly but forget the return channel. The Compose action creates a value inside the flow, but it does not expose that value back to the caller by itself. Returning outputs to a canvas app requires a response action designed for that app-to-flow call pattern.

<sub>Set F · Q22</sub>

---

### 34. A canvas app intermittently fails during save, and the team needs to inspect connector calls, timings, and control events without rewriting the app. A model-driven app in the same solution has a JavaScript form script error after deployment, and the team needs to inspect the browser console and network activity. Which two tools should you use first? (Select TWO.)

- **A.** App Checker
- **B.** Monitor ✅
- **C.** Solution Checker
- **D.** Browser developer tools ✅
- **E.** Publish all customizations and retest

> **Answer:** B. Monitor · D. Browser developer tools

Monitor is the right first tool for the canvas-app side because it gives detailed runtime visibility into control events, network activity, connector calls, formulas, and timing behavior. For the model-driven app script failure, browser developer tools are the correct first choice because they expose console errors, network requests, script loading behavior, and front-end debugging information directly in the browser.

This question is really about using the right diagnostic surface for the right app type. Canvas apps have a purpose-built troubleshooting tool in Monitor, while model-driven JavaScript problems are commonly investigated through browser-based developer tooling. Choosing the wrong diagnostic path usually delays root-cause analysis because you end up using a static analyzer where a runtime trace is needed.

<sub>Set F · Q23</sub>

---

### 35. A canvas app loads full Customers and Orders tables into collections during App.OnStart, then uses nondelegable filtering patterns against large Dataverse tables. The app also keeps hidden edit forms on another screen, and the related model-driven app view includes many unnecessary columns.

Which change should you make first for the biggest overall performance improvement?

- **A.** Full-table startup collection
- **B.** Hidden preloaded edit forms
- **C.** Delegable on-demand queries ✅
- **D.** Raise the nondelegable row limit to 2000

> **Answer:** C. Delegable on-demand queries

The biggest first improvement is to stop pulling large tables eagerly and instead use delegable queries with on-demand loading. That change attacks the most expensive architectural problem in the scenario: excessive client-side data movement and nondelegable logic against large Dataverse datasets. When filtering and loading can stay server-side and targeted, app startup and interactive performance both improve significantly.

The other performance issues matter, but they are secondary compared with data-access strategy. Hidden forms and wide model-driven views can absolutely hurt performance, yet they do not usually create the same scale problem as loading too much data too early or relying on nondelegable patterns against large sources. In exam terms, the best first fix is the one that removes the dominant performance bottleneck at the data layer.

<sub>Set F · Q53</sub>

---
