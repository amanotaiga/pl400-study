# Create a Technical Design  

_Exam weight 10–15% · 67 questions across all sets._

---

### 1. A development team must integrate a Power Platform solution with an external API from multiple environments. The design must keep secrets out of app code and must allow endpoint and environment-specific settings to change without editing the solution logic.

Problem:

The current architecture does not separate environment-specific configuration from reusable solution components.

Proposed solution:

Create a custom connector with an API key embedded directly in the connector definition, and reuse the same imported configuration across all environments.

Does the proposed solution meet the goal?

- **A.** Yes
- **B.** No ✅

> **Answer:** B. No

The proposed solution does not meet the goal because it embeds sensitive information directly into the connector design and does not properly separate reusable solution logic from environment-specific configuration. A sound technical architecture would avoid hard-coded secrets and would use environment-aware design elements so that endpoint values and related settings can vary safely across development, test, and production. The proposal fails both the secret-handling requirement and the configuration-separation requirement.

A stronger design would externalize environment-specific values and use a safer secret-management pattern rather than embedding credentials directly into a deployable component definition. In PL-400 architecture terms, the team must identify not just the integration component, but also the correct surrounding implementation approach for configuration, identity, and deployment portability. That is why the proposal is plausible, but still insufficient.

<sub>Set A · Q1</sub>

---

### 2. A model-driven app creates inspection records for contractors. A supervisor must grant a contractor access to one specific record without changing the contractor’s broader privileges in the app.

Which design element should you use?

- **A.** Row sharing ✅
- **B.** Business unit reassignment
- **C.** Owner team role update
- **D.** DLP policy modification

> **Answer:** A. Row sharing

Row sharing is the best fit because the requirement is about granting access to a single record without expanding the user’s general security scope. That is exactly the design impact of row sharing in Dataverse: it supplements existing access for a specific row rather than changing the wider authorization model for the user or their app role. In a technical design, this lets the solution component remain secure by default while still supporting exceptional collaboration.

The other security features operate at broader scopes. Business units shape organizational boundaries, team roles affect access patterns across groups, and DLP policies govern connector/data movement boundaries rather than record-level visibility. The design decision here is to choose the narrowest security mechanism that satisfies the collaboration requirement, and that points to row sharing.

<sub>Set A · Q2</sub>

---

### 3. A customer service solution will be used by regional support agents in Australia, New Zealand, and Singapore. Each region must keep its records separated from the others, new agents join and leave frequently, and access maintenance must avoid repeated per-user privilege assignment.

Which implementation approach is the best fit for the technical design?

- **A.** Per-user row sharing
- **B.** Team-based access model ✅
- **C.** Single root business unit
- **D.** Tenant DLP exception

> **Answer:** B. Team-based access model

A team-based access model is the best fit because the requirement emphasizes shared access patterns with frequent membership changes. Teams allow the design to attach security behavior to a group rather than managing the same privileges individually for each user. That reduces administrative overhead and keeps the security model aligned to the way the operational team actually works.

The scenario also requires regional separation, which is often combined with business-unit structure, but the key implementation approach being tested here is how to manage access for rotating users efficiently. Per-user sharing does not scale well for ongoing operations, a single root business unit weakens separation, and DLP has nothing to do with role-based record visibility. The right architectural conclusion is that solution components used by rotating groups should be designed around teams rather than repeated user-level grants.

<sub>Set A · Q5</sub>

---

### 4. A canvas app uses Dataverse and a custom connector that calls an external claims service. The environment has strict DLP governance, support staff work as rotating groups, and the design must avoid granting broad record access directly to each individual user.

Which two decisions should be included in the technical design? (Select TWO.)

- **A.** Assign access through teams ✅
- **B.** Depend on record-by-record sharing
- **C.** Validate connector DLP grouping ✅
- **D.** Collapse all business units
- **E.** Replace roles with DLP policy

> **Answer:** A. Assign access through teams · C. Validate connector DLP grouping

Assigning access through teams is correct because the scenario describes rotating support groups, which means group-based authorization is a better fit than repeated user-by-user privilege maintenance. Validating connector DLP grouping is also correct because the app depends on Dataverse and an external connector working together, and DLP policy can directly block or constrain that component interaction. Both decisions are architectural because they affect whether the solution components can operate as intended in production.

This question is testing the ability to assess impact across two different security layers at once. Teams affect how users receive access to records and privileges, while DLP affects how app and flow components can combine connectors and move data. A strong technical design must evaluate both layers early instead of treating security as a late deployment concern.

<sub>Set A · Q7</sub>

---

### 5. An Azure Function runs every 15 minutes to synchronize approved supplier records into Dataverse. The design must avoid interactive sign-in, must resume efficiently from the last successful cycle, and must minimize unnecessary reads.

Which two design choices should you recommend? (Select TWO.)

- **A.** OAuth client credentials flow ✅
- **B.** Poll all candidate rows each run
- **C.** Store client secret in app settings
- **D.** Enable Dataverse change tracking ✅
- **E.** Delegated interactive user sign-in

> **Answer:** A. OAuth client credentials flow · D. Enable Dataverse change tracking

OAuth client credentials flow is the correct authentication direction because this is a server-to-server integration running in Azure. Microsoft documents OAuth with Microsoft Entra ID as the Dataverse authentication model, and service-to-service patterns should avoid delegated interactive sign-in for unattended workloads.

Enabling Dataverse change tracking is the correct synchronization design choice because it lets the integration retrieve only what changed since the last synchronization point. That directly supports resume efficiency and minimizes wasteful reads, which is exactly what the scenario is testing.

<sub>Set A · Q9</sub>

---

### 6. A solution architect reviews four security-related design proposals. One proposal does not address the stated requirement and should be changed.

Exhibit 1

Which workstream should be revised?

- **A.** Escalation review
- **B.** Regional service partitioning
- **C.** Rotating approval squad
- **D.** Claims integration flow ✅

> **Answer:** D. Claims integration flow

The claims integration flow should be revised because adding a security role does not solve a DLP restriction. DLP policies govern whether connectors can be used together in apps and flows, so a blocked pairing remains blocked regardless of the Dataverse privileges granted to a user or team. From a technical design perspective, this means the proposed component does not address the actual security feature causing the limitation.

The other rows are aligned to their requirements. Row sharing is appropriate for narrowly scoped record access, business units help create structural data separation, and team-based role assignment supports stable privileges for changing groups. The exhibit is testing whether the architect can distinguish between connector-governance impact and record-authorization impact, which is a common source of weak solution design.

<sub>Set A · Q10</sub>

---

### 7. A model-driven app assigns inspection records to an owner team. New inspectors are added to the team and can open the app, but they still cannot read the team-owned inspection records. No DLP changes were made, and no individual record shares exist.

What is the most likely cause?

- **A.** Business unit mismatch
- **B.** Missing team privileges ✅
- **C.** Expired row share
- **D.** Blocked connector pairing

> **Answer:** B. Missing team privileges

The most likely cause is missing team privileges. Adding a user to an owner team does not help unless the team’s security model grants the required read access to the relevant table and records. In a design and troubleshooting context, this is an important consequence of using teams as a solution component: membership and privileges work together, and membership alone is not enough.

The other options do not fit the incident as closely. The scenario says there are no individual row shares to expire, and DLP is unrelated to reading Dataverse records in a model-driven app. A business-unit issue can affect access in some designs, but the clearest direct explanation for team-owned records being invisible to new team members is that the team-based privilege model is incomplete.

<sub>Set A · Q11</sub>

---

### 8. A sales solution stores orders in Dataverse. Each order change must be published to multiple Azure-based consumers, message bursts must be absorbed without blocking users, and downstream listeners might be temporarily offline.

Which integration design should you recommend?

- **A.** Dataverse webhook to Azure Function
- **B.** Synchronous plug-in to Azure Function
- **C.** Azure Service Bus endpoint ✅
- **D.** Dataverse custom API

> **Answer:** C. Azure Service Bus endpoint

Azure Service Bus endpoint is the best fit because the requirement is outbound event publishing from Dataverse to Azure with high burst tolerance and offline consumer resilience. Microsoft documents that Azure Service Bus integration is designed to relay Dataverse request context to Azure listeners, and Service Bus provides the durable queueing model that helps absorb spikes and decouple producers from consumers.

A webhook is strong when Dataverse needs to send an HTTP POST directly to an external web application, including cases where synchronous handling is useful. However, the requirement here is not immediate inline callback behavior. It is queue-backed, high-scale fan-out style integration, which is where Service Bus is the stronger design choice.

<sub>Set A · Q13</sub>

---

### 9. A team is choosing an outbound integration pattern for Dataverse account updates. The requirement states that message bursts are expected, consumers can process later, and listener downtime must not cause immediate message loss.

Exhibit 1

Which pattern should the team choose?

- **A.** Pattern A — Webhook
- **B.** Pattern B — Web API pull
- **C.** Pattern C — Service Bus relay
- **D.** Pattern D — Service Bus queue ✅

> **Answer:** D. Pattern D — Service Bus queue

Pattern D is the best fit because the exhibit shows it is the option with durable queueing and delayed consumer processing. That aligns directly with the stated need to absorb bursts and tolerate listener downtime without forcing immediate processing. Azure Service Bus queue-based integration is designed for exactly that kind of decoupled outbound event flow from Dataverse to Azure consumers.

The other exhibit rows each miss a required property. A webhook is direct and can be synchronous, which is useful in other scenarios, but it does not provide durable queueing. A polling design shifts the integration model entirely. A relay requires an actively listening endpoint rather than a durable store-and-process-later pattern.

<sub>Set A · Q14</sub>

---

### 10. A solution architect reviews four planned workstreams and their proposed implementation approach. One proposal does not align with the stated requirement and should be revised.

Exhibit 1

Which workstream should be revised?

- **A.** Inventory read model
- **B.** Telemetry ingestion design
- **C.** Case submission action
- **D.** Ribbon visibility ✅

> **Answer:** D. Ribbon visibility

The ribbon visibility workstream should be revised because a plug-in step is not the best implementation approach for command visibility that must be evaluated during user interaction. Command visibility belongs in the user experience layer, typically through command bar logic such as Power Fx or JavaScript depending on the app and command design. A server-side plug-in is the wrong architectural component for this requirement because it does not naturally own interactive command rendering decisions.

The other three mappings are aligned to their requirements. Virtual tables fit source-owned external data, elastic tables fit high-volume Dataverse-backed data, and Custom API fits reusable server-side operations with a deliberate callable surface. This exhibit is testing whether the technical design correctly maps requirement type to component boundary, which is a core architecture-analysis skill in PL-400.

<sub>Set A · Q40</sub>

---

### 11. A solution must call an external Azure-hosted validation service before Dataverse commits an update to a sensitive table. The response from the external service must be considered in the same transaction path, and delayed processing is not acceptable.

Problem:

Design an outbound integration that lets Dataverse wait for external validation before the record is committed.

Proposed solution:

Register an Azure Service Bus endpoint and publish the event from Dataverse to that endpoint.

Does the proposed solution meet the goal?

- **A.** Yes
- **B.** No ✅

> **Answer:** B. No

No is correct because Azure Service Bus integration from Dataverse is asynchronous in this context and is intended for decoupled message delivery to Azure listeners. The requirement here is fundamentally different: Dataverse must wait for an external validation result in the same transaction path before commit. That is not what the Service Bus pattern is for.

Microsoft documentation distinguishes this from webhooks, which can be registered on synchronous or asynchronous steps and send an HTTP POST payload to an external application. When the design needs immediate external participation in the event pipeline, a webhook-style approach is the closer fit than Service Bus.

<sub>Set A · Q42</sub>

---

### 12. An Azure-hosted integration receives customer updates from an ERP system. The ERP owns the business identifier, and the integration must create or update Dataverse rows without first looking up Dataverse GUID values.

Which design should you use?

- **A.** Create with GUID mapping
- **B.** Upsert with alternate keys ✅
- **C.** Duplicate detection batch create
- **D.** Webhook with retry policy

> **Answer:** B. Upsert with alternate keys

Upsert with alternate keys is the most appropriate design because alternate keys let Dataverse identify rows by business columns instead of requiring the Dataverse primary key. Microsoft explicitly positions alternate keys for integration scenarios where the external system has its own identifier and the Dataverse GUID is not known in advance.

Using Upsert with that alternate key makes the integration idempotent and simplifies the inbound design. A single request can create the row when it does not exist or update it when it already exists, which is exactly what you want for Azure-based inbound synchronization patterns.

<sub>Set A · Q44</sub>

---

### 13. A solution will be deployed from development to test and production by using managed solutions. External endpoints, queue names, and connection owners differ by environment, and the design must minimize manual rework during deployment.

Which two elements should you include in the technical architecture? (Select TWO.)

- **A.** Hard-coded connector IDs
- **B.** Connection references ✅
- **C.** Environment variables ✅
- **D.** Unmanaged test customizations
- **E.** Per-app JavaScript constants

> **Answer:** B. Connection references · C. Environment variables

Connection references and environment variables are the correct pair because they separate deployable solution logic from environment-specific values and bindings. Connection references allow flows and apps to bind to connectors in a transportable way, while environment variables let the architecture store values such as endpoints, queue names, or other configurable settings without hard-coding them into the solution. Together, they support cleaner ALM and reduce deployment friction across environments.

This is exactly the kind of architectural decomposition that strong PL-400 designs require: identify which parts of the solution are stable components and which parts are environment-specific configuration. By placing connection bindings and variable values into the correct solution-aware components, the implementation becomes easier to move, easier to maintain, and less fragile during managed deployments.

<sub>Set A · Q49</sub>

---

### 14. A solution includes both canvas apps and model-driven apps. Users in both app types must invoke the same server-side business operation, and that operation must validate input, create multiple Dataverse records, and call an external REST endpoint from a centrally managed implementation.

Which component is the best primary implementation approach?

- **A.** Reusable child cloud flow
- **B.** Custom API ✅
- **C.** Command bar JavaScript
- **D.** Real-time workflow process

> **Answer:** B. Custom API

A Custom API is the strongest primary implementation approach when the architecture requires a reusable server-side operation with a well-defined message contract. It is designed for developers who need controlled invocation patterns, centralized logic, and integration-friendly execution inside the Dataverse platform. That makes it a strong design component when multiple client experiences must call the same business operation consistently.

A child cloud flow can be part of some architectures, but it is not the cleanest primary building block when the requirement is an application-grade server-side operation that behaves like a platform message. Command bar JavaScript is client-side and tied to UI contexts rather than being a shared server-side contract. Real-time workflow processes are also less aligned with modern extensibility patterns for this type of reusable operation. In architecture analysis terms, the requirement is not just “run logic,” but “identify the right reusable component boundary,” and Custom API fits that boundary best.

<sub>Set A · Q56</sub>

---

### 15. A model-driven app must display current inventory data from an external SQL system. The source system remains the system of record, and the data must be visible in Dataverse-driven experiences without being copied into Dataverse.

Which component should you include in the technical design?

- **A.** Standard Dataverse table
- **B.** Elastic Dataverse table
- **C.** Virtual table ✅
- **D.** Scheduled dataflow import

> **Answer:** C. Virtual table

A virtual table is the best fit when the technical architecture requires Dataverse-based experiences to surface external data without physically storing that data in Dataverse. It allows the app to present source-owned information in forms, views, and related experiences while keeping the external system as the authoritative store. That makes it a strong architecture choice when duplication is explicitly not desired.

A standard or elastic table would move the design toward data persistence inside Dataverse, which conflicts with the stated requirement. A scheduled import would also create duplicated data and introduce freshness gaps. From a design-analysis perspective, the requirement is really about matching the component type to the ownership, latency, and storage model of the data, and that points directly to a virtual table.

<sub>Set A · Q62</sub>

---

### 16. A team plans to expose an internal Azure App Service API to a canvas app and a cloud flow. The API must stop using long-lived shared secrets, and each connection must authenticate through the platform-supported connector security model.

Configuration

Security type: API Key
API key location: Header
Header name: x-api-key
Secret source: Environment variable
Used by: Canvas app, cloud flow
Backend API: Azure App Service
Which authentication strategy should replace this design?

- **A.** Basic auth with Key Vault secret
- **B.** Dataverse row sharing
- **C.** Anonymous access with network allowlist
- **D.** OAuth 2.0 with Entra ID ✅

> **Answer:** D. OAuth 2.0 with Entra ID

D is correct because the current design is still a shared-secret design. Microsoft’s custom connector guidance supports Microsoft Entra ID and OAuth for REST APIs, which moves the solution from key-based access toward identity-based access through the connector security model.

The important distinction is that moving an API key into an environment variable changes where the secret is stored, but not the underlying authentication pattern. The requirement says to stop using long-lived shared secrets, so the replacement has to change the identity strategy itself, not just the storage location of the same credential.

<sub>Set B · Q3</sub>

---

### 17. A developer attached the same script library to many model-driven forms. The team wants to standardize the pattern, but the behavior must remain reusable and resilient to platform UI changes.

Snippet

function onLoad(executionContext) {
    const formContext = executionContext.getFormContext();
    const amount = formContext.getAttribute("new_amount").getValue();

    document.getElementById("promoBanner").style.display =
        amount > 10000 ? "block" : "none";
}
Which redesign should you recommend?

- **A.** Business rule visibility logic
- **B.** Shared JavaScript helper library
- **C.** PCF code component ✅
- **D.** Hosted HTML web resource

> **Answer:** C. PCF code component

A PCF code component is the best redesign because the current script is being used to drive reusable UI behavior rather than simple form orchestration. The snippet depends on DOM manipulation, which is brittle as a long-term reusable pattern. A PCF control gives the team a supported component model for rendering and behavior, along with properties, lifecycle hooks, and solution packaging.

The important design distinction is that client scripting is best for form events and page logic, while reusable custom UI should generally move into a component model. A shared JavaScript library may centralize the code, but it would still preserve the same weak architectural pattern around DOM coupling. A business rule is too limited for this kind of custom rendered UI, and an HTML web resource is still a less modern and less integrated reusable control strategy than PCF.

<sub>Set B · Q4</sub>

---

### 18. A product team is comparing reusable component patterns for upcoming features. One planned feature must present a custom lookup-like experience now in a model-driven app and later in a canvas app without redesigning the component.

Exhibit 1

Which candidate should be selected?

- **A.** Candidate A — canvas component
- **B.** Candidate B — shared JavaScript library
- **C.** Candidate C — hosted HTML web resource
- **D.** Candidate D — PCF code component ✅

> **Answer:** D. Candidate D — PCF code component

Candidate D is correct because the exhibit shows it is the only option that combines cross-host scope with high UI flexibility and a true component-style configuration model. The requirement is not just to reuse logic, but to design a reusable custom control that can start in a model-driven app and later move into a canvas app without being redesigned. That immediately eliminates the host-specific patterns.

The exhibit is intentionally comparing three different reuse philosophies: canvas-only reuse, form-script reuse, and hosted custom page reuse. Those can all be valid in narrower situations, but they do not satisfy this specific requirement set as well as a PCF code component. The typed manifest property model is also a strong signal that the design is meant to behave as a reusable component rather than a page script or host-specific fragment.

<sub>Set B · Q6</sub>

---

### 19. A solution requires a reusable input experience for both model-driven and canvas apps. The control must render custom UI, expose configurable properties, and be packaged as part of the solution lifecycle.

Which component should you recommend?

- **A.** Canvas component
- **B.** PCF code component ✅
- **C.** JavaScript web resource library
- **D.** Hosted HTML web resource

> **Answer:** B. PCF code component

A PCF code component is the best fit when you need a reusable custom UI element that behaves like a real app component rather than a page-level script. PCF is designed for typed properties, controlled rendering, lifecycle management, and solution-based deployment. It is the Microsoft platform-native option for building reusable controls that can participate in app design instead of being bolted on around the edges.

The requirement to support both model-driven and canvas app use cases is the decisive constraint. Canvas components are excellent inside canvas apps, but they do not solve the broader cross-host component requirement. JavaScript libraries and HTML web resources can support behavior or custom pages, but they are weaker architectural choices for a reusable control that must be packaged, configured, and reused as a component across Power Apps solution designs.

<sub>Set B · Q8</sub>

---

### 20. A production environment hosts a model-driven app for employees and an unattended synchronization worker. Employees must be admitted to the environment by group membership, while the worker must keep a nonhuman identity with the minimum Dataverse privileges required.

Which two design actions should you include? (Select TWO.)

- **A.** Environment security group ✅
- **B.** Application user with custom role ✅
- **C.** Shared maker-owned connection reference
- **D.** System Administrator for integration user
- **E.** API key in client script

> **Answer:** A. Environment security group · B. Application user with custom role

A is correct because Microsoft recommends using security groups to control which licensed users can be members of a particular environment. That is the right control when the requirement is environment admission by group membership, because it determines who can access the environment at the boundary before you get into table-level or app-level privileges.

B is also correct because the unattended worker needs a nonhuman identity plus minimum Dataverse privileges. Microsoft’s Dataverse guidance requires creating an application user and associating it with a security role, and Dataverse security roles are the supported authorization model for scoping what that identity can do.

<sub>Set B · Q9</sub>

---

### 21. An Azure DevOps release uses a service principal to deploy solution assets and then runs a .NET job that calls the Dataverse Web API. Token acquisition from Microsoft Entra ID succeeds, but every Dataverse request returns HTTP 403 in the target environment.

What is the most likely cause?

- **A.** Conditional access blocked sign-in
- **B.** Missing Dataverse app-user role assignment ✅
- **C.** DLP policy blocked connector
- **D.** Missing connection reference and environment variable bindings

> **Answer:** B. Missing Dataverse app-user role assignment

B is the best answer because the sign-in step has already succeeded. That means authentication against Microsoft Entra ID is working, so the remaining issue is most likely Dataverse authorization in the target environment. Microsoft’s Dataverse guidance requires creating an application user and associating it with a security role, so a missing or incorrect role assignment is the most plausible explanation here.

This is an authentication-versus-authorization distinction. The workload can have a valid token and still be denied by Dataverse if the corresponding application identity is not correctly authorized in that environment. That conclusion is an inference from Microsoft’s documented requirement for application users and role assignment, and it matches the symptom pattern much better than the other options.

<sub>Set B · Q10</sub>

---

### 22. A team is designing a reusable address capture experience. A PCF control will handle the UI, while form-specific automation must stay easy to change across several model-driven forms.

Which two design decisions best support reuse and maintainability? (Select TWO.)

- **A.** Embed form navigation inside PCF
- **B.** Expose manifest input properties ✅
- **C.** Query host DOM selectors directly
- **D.** Use shared formContext helpers ✅
- **E.** Hard-code table and column names per form event

> **Answer:** B. Expose manifest input properties · D. Use shared formContext helpers

Exposing manifest input properties is correct because reusable PCF controls should be configurable instead of assuming a single table, field, or behavior pattern. That allows the same component package to be used in different contexts while still letting app designers pass values and settings into the control. It is a core part of making a code component genuinely reusable rather than merely repeatable.

Using shared formContext helpers is also correct because it keeps host-specific client scripting outside the component and makes orchestration logic easier to maintain across forms. That separation of concerns is exactly what good Power Apps design should aim for: the control owns UI behavior, while shared client scripting handles form events and contextual orchestration. This avoids pushing unrelated host logic into the component and preserves cleaner reuse boundaries.

<sub>Set B · Q22</sub>

---

### 23. A canvas app and a cloud flow must call an internal Azure-hosted REST API. Each employee must be authorized as themselves, conditional access and MFA must still apply, and the team does not want shared secrets distributed across environments.

Which authentication strategy is the best fit?

- **A.** Custom connector with Entra OAuth 2.0 ✅
- **B.** Custom connector with API key header
- **C.** Basic auth in connector
- **D.** Dataverse custom API

> **Answer:** A. Custom connector with Entra OAuth 2.0

A custom connector secured with Microsoft Entra OAuth 2.0 is the best fit because Microsoft’s connector guidance supports using Microsoft Entra ID to authenticate a custom connector against a REST API, and that pattern preserves user-based sign-in rather than relying on a shared secret. It aligns naturally with requirements such as MFA and conditional access because the user is authenticating through the identity provider rather than through a static key.

This is also the best authorization strategy because the requirement says employees must be authorized as themselves. API-key and basic-auth designs authenticate the connector or a stored credential, not the individual employee in the same way. The goal here is not just “secure storage of a secret”; it is delegated user identity with enterprise controls.

<sub>Set B · Q48</sub>

---

### 24. A business unit is standardizing six canvas apps used by different makers. They need a reusable header-and-filter block that can be configured with input properties, updated centrally, and adjusted by low-code developers without rebuilding a compiled control.

Which design should you choose?

- **A.** Canvas component library ✅
- **B.** PCF control packaged in solution
- **C.** JavaScript web resource bundle
- **D.** Model-driven custom page

> **Answer:** A. Canvas component library

A canvas component library is the best answer because the requirement is centered on reuse across multiple canvas apps with low-code maintainability. Component libraries let teams create shared components, publish updates centrally, and expose configurable properties that app makers can consume without managing compiled artifacts. That directly matches the goal of reusable UI building blocks for canvas development.

The key constraint is that updates should remain easy for low-code developers. A PCF control can be powerful, but it introduces a pro-code build and packaging workflow that the scenario explicitly does not want. JavaScript bundles and custom pages are also misaligned because the requested artifact is a reusable canvas app UI block, not a model-driven extension pattern or page-hosting construct.

<sub>Set B · Q53</sub>

---

### 25. A finance solution includes an unattended Azure process that must write invoices to Dataverse every 15 minutes. The identity must remain stable when staff change roles, and the component must receive only the privileges it needs.

Which identity model should you recommend for this component?

- **A.** Interactive user account
- **B.** Shared maker-owned connection reference
- **C.** Dataverse application user ✅
- **D.** Environment Maker plus System Customizer role

> **Answer:** C. Dataverse application user

A Dataverse application user is the best fit for a noninteractive component because it gives the workload a dedicated application identity in the environment rather than tying execution to a human account. Microsoft documents that application users are created from Microsoft Entra app registrations and then assigned Dataverse security roles, which is exactly the pattern you want when the requirement is stable ownership plus least-privilege access.

This is an authentication-and-authorization decision, not just a permissions decision. The authentication side is the Microsoft Entra application identity; the authorization side is the Dataverse security role assigned to that application user. That separation is what makes the design resilient to staff turnover and keeps privileges scoped to the component instead of to a person.

<sub>Set B · Q62</sub>

---

### 26. A solution architect wants to minimize custom development and use native platform capability wherever it cleanly satisfies the requirement.

Which two requirements can be met with out-of-the-box functionality in Microsoft Power Platform? (Select TWO.)

- **A.** Synchronous REST validation on save
- **B.** Business process flow ✅
- **C.** Embedded external chart library
- **D.** 15-second ERP recalculation loop
- **E.** Approval flow ✅

> **Answer:** B. Business process flow · E. Approval flow

Business process flows are built to guide users through staged business processes in a consistent step-by-step experience on records. Approval flows are also a native pattern in Power Automate, where built-in approval actions can handle human sign-off scenarios without requiring a custom approval engine.

The key architectural skill here is recognizing where the platform already has a first-class capability and where a requirement crosses into extension territory. Guided stages on records and routed approvals are strong examples of native functionality, while synchronous external validation, embedded external visualization logic, and tight polling-style recalculation usually push the design toward custom integration or code.

<sub>Set C · Q1</sub>

---

### 27. A project team is reviewing candidate out-of-the-box designs before approving any custom work.

Exhibit 1

Which row is not fully satisfied by the proposed out-of-the-box choice?

- **A.** Row 4 ✅
- **B.** Row 2
- **C.** Row 1
- **D.** Row 3

> **Answer:** A. Row 4

Row 4 is the mismatch. Formula columns are an out-of-the-box Dataverse feature, but Microsoft documents that formula columns do not display values when the app is in mobile offline mode, so that proposed choice does not fully satisfy the stated requirement.

The other rows are reasonable native matches: rollup columns aggregate related data, duplicate detection rules help identify potential duplicates, and business process flows guide users through staged processes on forms. The exhibit is testing whether you can spot the point where an apparently native feature stops meeting the actual constraint.

<sub>Set C · Q3</sub>

---

### 28. A sales app needs a modern command on the account main form that opens a custom page and is visible only when Status = Active. The architects want an out-of-the-box approach, but the same command definition must be reused across three separate apps without rebuilding it in each app.

Problem:

Design a solution that stays inside supported modern command designer functionality and still lets the team reuse the exact same command definition across multiple apps.

Proposed solution:

Use command designer and Power Fx in one app, then add that same command component library directly to the other apps.

Does the proposed solution meet the goal?

- **A.** Yes
- **B.** No ✅

> **Answer:** B. No

No. The proposed solution is close, because the modern command designer and Power Fx are the right out-of-the-box tools for creating model-driven commands and visibility logic. However, Microsoft documents a key limitation: commands and the command component library created from one app cannot simply be added directly to different apps.

That means the proposal fails the full requirement, even though part of the design is directionally correct. This is a classic technical design judgment test: a feature may cover most of the scenario, but if one stated reuse constraint is not satisfied, then the overall proposal is not sufficient.

<sub>Set C · Q5</sub>

---

### 29. A developer must prevent users from creating a Dataverse account record when a required tax registration value is missing. The validation must run on the server, apply regardless of which app or integration creates the record, and reject the request before the main database transaction whenever possible.

The developer should register a ____.

- **A.** Synchronous PreValidation plug-in ✅
- **B.** Asynchronous PostOperation plug-in
- **C.** Client-side business rule
- **D.** Power Automate cloud flow approval

> **Answer:** A. Synchronous PreValidation plug-in

Synchronous PreValidation plug-in is the correct answer because it can run server-side before the main Dataverse database transaction. This makes it appropriate for validation logic that must block an invalid create request before the platform commits the operation.

This is a 9/10 PL-400 distinction because several Power Platform tools can apply business logic, but they do not run at the same point or with the same enforcement strength. For server-side validation that must apply consistently across apps, APIs, imports, and integrations, a Dataverse plug-in registered in the appropriate event pipeline stage is the strongest fit.

<sub>Set C · Q6</sub>

---

### 30. An account table needs a value that sums estimated revenue from related open opportunities. The value must be available in Dataverse and across apps without custom code.

Which approach should you recommend?

- **A.** JavaScript form handler
- **B.** Cloud flow aggregation job
- **C.** Rollup column ✅
- **D.** Synchronous plug-in step

> **Answer:** C. Rollup column

A rollup column is the best out-of-the-box fit because it is designed to aggregate values from related records and expose that value as part of the Dataverse data model. That matches a requirement to total open opportunity amounts at the account level without introducing custom client code or server-side extensions.

This kind of design decision is about exhausting native platform capability before moving to custom development. When the requirement is a persisted aggregate over related rows, rollup columns are the Microsoft-native first choice and usually give a cleaner technical design than plug-ins, scripts, or scheduled automation.

<sub>Set C · Q7</sub>

---

### 31. A custom connector will call a third-party REST API. Each maker must sign in with their own identity, and the service authorizes requests per user token.

Which authentication type should you design for the connector?

- **A.** API key in header
- **B.** Basic authentication
- **C.** OAuth 2.0 ✅
- **D.** No authentication mode

> **Answer:** C. OAuth 2.0

OAuth 2.0 is the best design choice because custom connectors support it as a first-class authentication type, and the user signs in during connection creation so the connector can obtain an access token for that user. The platform then sends that authorization token on requests, which matches a per-user authorization model.

The other supported authentication types are real options, but they fit different designs. API key, Basic authentication, and No authentication do not match a connector requirement where every maker must authenticate as themselves and the backend authorizes actions per user token.

<sub>Set C · Q14</sub>

---

### 32. A service desk team uses a model-driven app. When Escalated = Yes and Priority = High, Resolution Due Date must become required and a recommendation must appear telling the agent to notify the duty manager. The design must avoid custom code and apply across all case forms.

Which approach should you recommend?

- **A.** Client API script on form
- **B.** Cloud flow with approval action
- **C.** Plug-in on Update message
- **D.** Entity-scoped business rule ✅

> **Answer:** D. Entity-scoped business rule

An entity-scoped business rule is the strongest out-of-the-box answer because business rules can evaluate conditions and take actions such as setting requirement levels and showing business recommendations. Using entity scope also aligns with the requirement that the behavior apply across all forms for the table rather than on just one specific form.

This is exactly the kind of requirement that should be screened for native capability before custom extension is chosen. The needed logic is form-oriented, declarative, and table-bound, so a business rule gives the cleanest technical design with lower implementation and support overhead than code or automation.

<sub>Set C · Q27</sub>

---

### 33. A managed solution contains flows that use a custom connector across DEV, TEST, and PROD. The connection must be rebound during solution import, and connector properties such as host or login endpoints must vary by environment without redesigning each flow action.

Which two design choices should you include? (Select TWO.)

- **A.** Hard-code URLs in each flow
- **B.** Use a connection reference ✅
- **C.** Export the flows outside the solution
- **D.** Use connector environment variables ✅
- **E.** Duplicate the connector per flow

> **Answer:** B. Use a connection reference · D. Use connector environment variables

A connection reference should be part of the design because Microsoft documents it as the solution component that points to a connection for a specific connector. Solution-aware flows bind to the connection reference rather than directly to the connection, and a connection is supplied for those references during import into the target environment.

Environment variables should also be part of the design because Microsoft documents them for solution custom connectors to update key properties such as Host, Base URL, Client ID, Client Secret, Login Url, and Refresh Url. That makes them the right mechanism for environment-specific connector settings while the connection reference handles the runtime binding.

<sub>Set C · Q33</sub>

---

### 34. A development team already maintains a formal API contract in source control. They want the custom connector design to stay aligned with that contract and to support connector-specific metadata such as operation visibility and user-facing summaries.

Which approach should you recommend?

- **A.** Build each action manually in the designer
- **B.** Use a connection reference for the contract
- **C.** Configure operations from environment variables
- **D.** Import an OpenAPI 2.0 definition ✅

> **Answer:** D. Import an OpenAPI 2.0 definition

Importing an OpenAPI 2.0 definition is the strongest design choice because Microsoft documents OpenAPI import as a native way to create a custom connector, and it specifically requires OpenAPI 2.0 rather than OpenAPI 3.0. That keeps the connector aligned to the maintained API contract instead of recreating actions manually.

It also supports the requirement to control maker experience through connector-specific metadata. Microsoft documents extensions such as x-ms-visibility, which are used to control how operations and parameters appear to users, so an OpenAPI-based design is the most maintainable fit here.

<sub>Set C · Q38</sub>

---

### 35. A team is refining an OpenAPI definition for a custom connector. They want a required query parameter to stay hidden from makers in the designer.

Snippet

{
  "name": "api-version",
  "in": "query",
  "required": true,
  "type": "string",
  "x-ms-visibility": "internal"
}
What change is required to make this design valid?

- **A.** Add a default value ✅
- **B.** Replace the field with x-ms-summary
- **C.** Move the field to the response schema
- **D.** Mark the field as x-ms-dynamic-values

> **Answer:** A. Add a default value

This design needs a default value because Microsoft’s OpenAPI extension guidance states that when a parameter is both internal and required, you must provide a default value. Otherwise, the maker cannot see the parameter and also cannot supply the required input.

That rule is specifically about connector design quality, not just display polish. x-ms-visibility controls whether a maker sees a parameter, and once the parameter is hidden, the connector definition itself must provide the value path for any required input.

<sub>Set C · Q50</sub>

---

### 36. A team added custom code to a custom connector so it can transform requests before they reach an internal API. They plan to run the connector through the on-premises data gateway, and the connector definition saves successfully, but the design fails during testing.

What is the best explanation?

- **A.** Certification is required before testing
- **B.** Custom code isn't gateway-supported ✅
- **C.** Basic auth is required for scripts
- **D.** Model-driven apps are required

> **Answer:** B. Custom code isn't gateway-supported

The best explanation is that Microsoft documents custom code as not currently supported with the on-premises data gateway. That makes this a design limitation, not a minor configuration issue in the connector definition.

This is why the connector can appear valid at design time and still fail as an implementation approach. The problem is the architectural combination of custom code plus gateway usage, so the fix is to redesign the connector pattern rather than tweak a small setting.

<sub>Set C · Q61</sub>

---

### 37. A model-driven app needs immediate feedback while a user edits a form. The logic does not need to run for imports or background integrations.

Snippet

function setApproval(executionContext) {
  const formContext = executionContext.getFormContext();
  const amount = formContext.getAttribute("new_amount").getValue() || 0;

  formContext.getAttribute("new_needsapproval").setValue(amount > 10000);
  formContext.ui.tabs.get("tab_finance").setVisible(amount > 10000);
}
Where should this logic remain?

- **A.** Client script ✅
- **B.** Table business rule
- **C.** PreValidation plug-in step
- **D.** Dataverse cloud flow

> **Answer:** A. Client script

This snippet is clearly model-driven Client API logic. It uses executionContext, gets formContext, reads a column value, writes another value, and manipulates form UI by showing or hiding a tab, which is squarely in the client-side scripting space.

The stem also says the logic is about immediate feedback during editing and does not need to run for imports or integrations. That combination strongly favors client-side placement rather than a plug-in or flow, and the tab-level UI manipulation makes it a stronger match for script than for a business rule.

<sub>Set D · Q1</sub>

---

### 38. A team needs reusable server-side logic that calculates shipping risk scores from Dataverse data. Makers must be able to adjust the logic without a .NET deployment, and the logic will be called on demand from both a canvas app and a cloud flow. Which component should you recommend?

- **A.** Synchronous PreOperation plug-in step
- **B.** Unbound custom API backed by plug-in
- **C.** Dataverse Power Fx function ✅
- **D.** Model-driven form JavaScript handler

> **Answer:** C. Dataverse Power Fx function

A Dataverse Power Fx function is the best fit because the requirement is for reusable, on-demand, server-side logic that can be invoked from Power Platform components without forcing a .NET-heavy implementation model. Microsoft’s architecture guidance positions Power Fx functions as a low-code way to extend Dataverse business logic for scenarios that are not overly complex and that benefit from reuse across apps and flows.

The other components solve different design problems. Plug-ins are strongest when logic must run automatically in the event pipeline, and custom APIs are better when you need a developer-defined message surface with richer .NET capabilities, deeper diagnostics, or more complex implementation control. Here, the main drivers are maker maintainability and simple on-demand reuse, which point directly to a Power Fx function.

<sub>Set D · Q5</sub>

---

### 39. Your integration team must expose a single operation named SubmitCompliancePackage to external .NET code and to Power Automate. The operation accepts a structured payload, must return controlled error details, and requires telemetry from server-side .NET code. It must not depend on a specific table event.

Which component should you design first?

- **A.** Dataverse Power Fx function
- **B.** Synchronous table event plug-in registration
- **C.** Client-side JavaScript command handler
- **D.** Unbound custom API ✅

> **Answer:** D. Unbound custom API

An unbound custom API is the right starting point because the requirement is for an explicit Dataverse operation with its own callable contract, not for logic that fires because a row event occurred. Microsoft documents custom APIs as developer-defined APIs in Dataverse that can be called from code or from Power Automate, which matches the stated caller model exactly.

This scenario also asks for structured request handling, controlled server-side behavior, and .NET-based telemetry and error handling. Microsoft’s architecture guidance specifically points to Dataverse custom APIs when the use case needs more complex business logic, advanced capabilities, and richer operational control than a low-code Power Fx function is intended to provide.

<sub>Set D · Q6</sub>

---

### 40. You are standardizing a reusable order-submission capability so canvas apps, custom pages, and cloud flows can invoke the same server-side operation. The internal Dataverse tables might change later, but callers must keep a stable contract.

Which two design choices should you make? (Select TWO.)

- **A.** Define request and response parameters ✅
- **B.** Register the logic as a model-driven form OnLoad handler
- **C.** Expose an unbound custom API ✅
- **D.** Depend on client-side Set and Notify
- **E.** Reuse a business rule for server execution

> **Answer:** A. Define request and response parameters · C. Expose an unbound custom API

The stable-contract requirement is the key clue. An unbound custom API lets you define a specific Dataverse operation that callers invoke directly, instead of forcing them to depend on internal table operations or UI mechanics. Microsoft documents custom APIs as callable operations in Dataverse that can be used from code or Power Automate, which makes them ideal when you want a reusable contract across multiple callers.

Defining request and response parameters is equally important because the API contract is what protects consumers from internal implementation changes. Parameters formalize the input and output surface, which is precisely how you preserve a stable integration boundary while retaining freedom to change underlying tables or execution details later.

<sub>Set D · Q7</sub>

---

### 41. A developer hands you the following class and says it should back a reusable Dataverse operation invoked explicitly by clients rather than by Create or Update events.

Snippet

public class SubmitOrderPlugin : IPlugin
{
    public void Execute(IServiceProvider serviceProvider)
    {
        var context = (IPluginExecutionContext)serviceProvider
            .GetService(typeof(IPluginExecutionContext));

        if (context.MessageName != "contoso_SubmitOrder")
        {
            return;
        }

        // operation logic
    }
}
Which component is this plug-in most likely designed to support?

- **A.** Unbound custom API ✅
- **B.** Dataverse Power Fx function
- **C.** Form command JavaScript
- **D.** Synchronous table event plug-in step

> **Answer:** A. Unbound custom API

The key design clue is context.MessageName != "contoso_SubmitOrder". A custom API creates a custom message in Dataverse, and Microsoft documents that custom APIs are commonly paired with plug-ins to implement the underlying operation logic. A plug-in that checks for a custom message name strongly indicates that it is backing a custom API rather than a standard table pipeline event.

The snippet also uses IPlugin, which means the implementation is a compiled C# Dataverse plug-in rather than a low-code Power Fx artifact or a client-side script. Microsoft’s plug-in documentation describes plug-ins as compiled classes implementing IPlugin, while Dataverse plug-ins are used to enforce business logic directly within Dataverse. Together, those details make an unbound custom API the best design interpretation.

<sub>Set D · Q9</sub>

---

### 42. A solution architect is classifying four candidate logic components for a new Dataverse-based solution. Use the exhibit to determine which candidate is the best fit for a Power Fx function.

Exhibit 1

Which design choice is the best fit?

- **A.** Candidate A — synchronous plug-in
- **B.** Candidate B — Dataverse Power Fx function ✅
- **C.** Candidate C — unbound custom API backed by plug-in
- **D.** Candidate D — PreOperation plug-in step

> **Answer:** B. Candidate B — Dataverse Power Fx function

Candidate B is the Power Fx function case because it is explicitly invoked, reusable across apps and flows, simple enough to stay in a low-code model, and intended to be maintained by makers. Microsoft’s architecture guidance recommends Power Fx functions when the business logic is not overly complex, when you want reusable server-side logic, and when you prefer a low-code approach without requiring advanced .NET capabilities.

The other rows point to different Dataverse code components. Candidate C is the custom API pattern because it needs a formal callable operation surface, structured payload handling, diagnostics, and .NET extensibility. Candidates A and D are event-pipeline patterns, which is where traditional Dataverse plug-ins are strongest because they execute in response to specific platform events and support direct pipeline control.

<sub>Set D · Q10</sub>

---

### 43. A team wants to keep some logic close to the user experience instead of moving it into server-side code or automation.

Which TWO requirements most strongly support client-side or business-rule implementation rather than plug-ins, cloud functions, or Power Automate? (Select TWO.)

- **A.** Universal write enforcement across apps and integrations
- **B.** Immediate field visibility changes ✅
- **C.** External REST call with retry
- **D.** Bulk import validation
- **E.** Form recommendation and validation ✅

> **Answer:** B. Immediate field visibility changes · E. Form recommendation and validation

Immediate UI reactions and guided form behavior belong closest to the app experience. Client scripting exists for model-driven form logic such as showing or hiding elements and responding to user actions, while business rules are intended for common logic and validations without writing code.

By contrast, universal enforcement, bulk-processing validation, and external integration calls push the design toward server-side logic or cloud-based processing. Those cases need coverage beyond a single form session and often require event-pipeline handling, automation, or custom compute rather than UI-layer logic.

<sub>Set D · Q25</sub>

---

### 44. A developer used a Dataverse-triggered cloud flow to reject invalid discount combinations by updating the row after save and notifying the owner. Users can still create invalid rows through Excel import and custom integrations, and downstream processes occasionally read the bad data before the flow corrects it.

What should you do?

- **A.** Table business rule
- **B.** PreValidation plug-in ✅
- **C.** OnSave form script
- **D.** After-save custom API

> **Answer:** B. PreValidation plug-in

The failure happens because the logic was implemented as downstream automation instead of request-time validation. Dataverse row-change flows run after the data event that triggered them, so they are useful for follow-up processing but not for universally preventing invalid data from being written in the first place.

A PreValidation plug-in is the best correction because it runs in the Dataverse event pipeline before the core operation completes and applies to all callers, including imports and integrations. That solves both problems in the stem: universal enforcement and stopping invalid data before downstream consumers can see it.

<sub>Set D · Q42</sub>

---

### 45. A sales solution must send each submitted quote to an external pricing engine that can take up to 40 seconds to respond. The result is not required before the Dataverse row is saved, and the team wants retry control, custom code, and minimal effect on form responsiveness.

Where should the core business logic run?

- **A.** Cloud flow with retry policy
- **B.** OnSave client script
- **C.** Synchronous PostOperation plug-in
- **D.** Azure Function ✅

> **Answer:** D. Azure Function

Architecture Best Practices for Azure Functions

A cloud flow can orchestrate Dataverse-driven automation, but the stem specifically favors custom code and serverless execution for an external engine call with greater implementation control. Client-side code would hurt user experience and fail to cover non-UI callers, while a synchronous plug-in is the wrong place for a 40-second dependency because it keeps the Dataverse request path waiting.

<sub>Set D · Q45</sub>

---

### 46. An order total must be recalculated whenever line items change. The logic must block invalid updates from model-driven apps, flows, imports, and custom integrations, and it must run during the Dataverse operation rather than after it completes. Which implementation should you recommend?

- **A.** Table business rule
- **B.** Client API script
- **C.** PreOperation plug-in ✅
- **D.** Cloud flow with trigger

> **Answer:** C. PreOperation plug-in

A PreOperation plug-in is the best fit because the requirement is universal server-side enforcement during the Dataverse operation itself. Plug-ins are registered on Dataverse events and are designed for business logic that must run independently of any specific app UI, including requests coming from integrations and automation.

A table business rule can handle some validation and no-code logic, and client scripting is useful for model-driven form behavior, but neither is the best answer for transaction-bound logic that must consistently apply to every caller. A cloud flow triggered by Dataverse is also the wrong placement here because it runs as downstream automation rather than as in-transaction validation.

<sub>Set D · Q55</sub>

---

### 47. A procurement team stores supplier master data in Azure SQL, and that system must remain the system of record. Users need to see current supplier rows inside a model-driven app and use them in Dataverse forms without building a scheduled synchronization process. Data duplication must be minimized.

Which approach should you use?

- **A.** Standard table with scheduled sync
- **B.** Elastic table with plug-in sync
- **C.** Custom connector in canvas app
- **D.** Virtual table ✅

> **Answer:** D. Virtual table

A virtual table is the best answer because the external system must remain the source of truth and the data needs to appear in Dataverse-driven experiences without copying it into native Dataverse storage. That is the exact design space for virtual tables: surfacing external data as Dataverse tables while avoiding replication.

The other options all introduce the wrong tradeoff. Standard and elastic tables would move the design toward persisted Dataverse storage plus synchronization logic, which the scenario explicitly tries to avoid. A connector can call the external system, but it does not model that external data as Dataverse table data within the model-driven experience in the same way a virtual table does.

<sub>Set E · Q1</sub>

---

### 48. A team is deciding whether to model an external capability as Dataverse data or access it directly from Power Apps and Power Automate. Which TWO requirements are the strongest indicators that a connector should be used directly instead of modeling the external system as Dataverse table data? (Select TWO.)

- **A.** Dataverse row ownership
- **B.** Live SaaS actions ✅
- **C.** External system remains master ✅
- **D.** Complex relational reporting inside Dataverse
- **E.** Synchronous transaction pipeline participation

> **Answer:** B. Live SaaS actions · C. External system remains master

A connector is the strongest fit when the solution must call or act on an external API or SaaS capability directly and when the external platform remains the master system for the interaction. “Live SaaS actions” points to direct API operations, and “External system remains master” points away from persisting and governing the data as native Dataverse business data. Those two together are the clearest connector signals in this set.

The other choices all point more strongly toward Dataverse-native storage and execution patterns. Row ownership, relational reporting inside Dataverse, and synchronous transaction participation are all characteristics that fit standard tables far better than connector-first designs. Even when connectors are involved in the broader solution, they are not the right answer when the workload fundamentally depends on Dataverse transactional behavior and relational data management.

<sub>Set E · Q2</sub>

---

### 49. A solution architect is reviewing four candidate workloads for the next release.

Exhibit 1

Which workload should be implemented as a virtual table?

- **A.** SQL catalog workload ✅
- **B.** High-volume IoT event workload
- **C.** Planner task workload
- **D.** Internal warranty case workload

> **Answer:** A. SQL catalog workload

The SQL catalog workload is the virtual table candidate because the external database remains the system of record, the data needs to appear in Dataverse-style experiences, and the design explicitly wants to avoid duplication. That is the classic pattern for a virtual table: external data represented as Dataverse table data without copying it into native storage.

The other exhibit rows map to different design choices. The IoT event workload points to elastic tables because of the heavy append pattern and very large scale. The Planner task workload points more strongly to a connector because the requirement is frequent external operations rather than modeling the data as Dataverse business data. The warranty case workload belongs in a standard table because it is internal Dataverse data with full security, auditing, and normal CRUD expectations.

<sub>Set E · Q4</sub>

---

### 50. A sales automation must start whenever a Dataverse order row is created or updated. Users must not run it manually, and the process cannot wait for a schedule.

Which automation should you design?

- **A.** Instant cloud flow
- **B.** Scheduled cloud flow
- **C.** Automated cloud flow ✅
- **D.** Desktop flow with gateway

> **Answer:** C. Automated cloud flow

An automated cloud flow is the correct design because the trigger is event-based. The requirement is to react to a Dataverse create or update event without user initiation and without waiting for a timer-based schedule. That maps directly to an automated cloud flow, which is built to start from a system event such as a Dataverse row change.

This is also the cleanest technical design because it keeps the automation aligned to the business event instead of adding unnecessary orchestration. A manual trigger would add user dependency, a scheduled trigger would add latency, and a desktop flow would introduce a very different execution model that is not needed for a standard Dataverse-driven automation. For PL-400 design questions, the best answer is usually the trigger model that most directly matches the event source and execution requirement.

<sub>Set E · Q6</sub>

---

### 51. A solution contains three cloud flows that all perform the same case-escalation sequence and send the same downstream notifications. The design must keep the logic in one place, remain solution-aware across environments, and avoid updating three separate flows whenever the escalation logic changes.

Which component should you design into the automation solution?

- **A.** Custom connector policy template
- **B.** Plug-in on Dataverse event
- **C.** Business process flow stage
- **D.** Child flow ✅

> **Answer:** D. Child flow

A child flow is the best design because it centralizes reusable automation logic and allows multiple parent cloud flows to call the same implementation. That directly satisfies the requirement to keep the escalation process in one place. When the logic changes, the team updates the child flow once instead of modifying several separate automations.

This is also the most natural cloud-flow design choice because the requirement is about reuse inside Power Automate, not about moving the logic into a completely different extensibility model. A plug-in would shift the implementation to server-side code and a different lifecycle, while a business process flow is focused on guided stages rather than reusable automation execution. In exam terms, child flow is the best fit when the problem is shared orchestration inside a solution-aware automation design.

<sub>Set E · Q7</sub>

---

### 52. A cloud flow in a managed solution calls an external shipping API. The design must support different endpoints after solution import, and the flow must avoid hard-coded connection bindings across environments.

Which two design choices should you include? (Select TWO.)

- **A.** Hard-code endpoint URLs in actions
- **B.** Use environment variables ✅
- **C.** Store secrets in Compose actions
- **D.** Create one unmanaged flow per environment
- **E.** Use connection references ✅

> **Answer:** B. Use environment variables · E. Use connection references

Environment variables and connection references are the correct pair because they solve two different but related ALM design concerns. Environment variables let the solution carry values that change by environment, such as endpoints or non-secret configuration. Connection references let the flow use solution-aware connection bindings so the imported automation can be associated with the correct connection in each target environment.

Together, these two controls produce a design that is maintainable, portable, and aligned to managed solution deployment. Hard-coded values and directly bound connections create fragile automations that break or require manual editing after import. PL-400 questions often separate candidates who know cloud flows from candidates who know how to design them for real ALM movement, and this pair is the strongest design answer for that distinction.

<sub>Set E · Q8</sub>

---

### 53. A Dataverse-triggered cloud flow updates the same account row after calculating a routing code. The team adds the following trigger condition before enabling the flow.

Snippet

@not(equals(triggerOutputs()?['body/cr6f8_processed'], true))
What is the main design purpose of this condition?

- **A.** Prevent self-trigger recursion ✅
- **B.** Enforce row-level privileges
- **C.** Cache connector access tokens
- **D.** Increase retry throughput

> **Answer:** A. Prevent self-trigger recursion

This trigger condition is intended to prevent the flow from repeatedly triggering itself after it updates the same Dataverse row. If the flow writes back to the row and marks cr6f8_processed as true, future updates that match that state will not trigger another run. That is a common design pattern for avoiding recursion or endless reprocessing in Dataverse-triggered cloud flows.

The key design idea is that the condition filters execution before the flow begins running. That is much cleaner than letting every update start a run and then trying to exit later with branch logic. In automation design, especially when the same record is updated by the flow, preventing unnecessary invocations at the trigger level improves reliability, reduces noise, and lowers the risk of loops.

<sub>Set E · Q9</sub>

---

### 54. An automated cloud flow reserves inventory in an external API whenever an order row is added to Dataverse. During peak imports, duplicate reservations appear because multiple runs process overlapping updates before the external system can complete its reservation, and the API is not idempotent.

What should you change first?

- **A.** Increase retry count
- **B.** Add business rule
- **C.** Limit trigger concurrency ✅
- **D.** Enable child flow retries

> **Answer:** C. Limit trigger concurrency

Limiting trigger concurrency is the best first design change because the stated failure pattern is caused by overlapping flow runs against a downstream system that cannot safely handle parallel duplicate requests. Reducing the number of simultaneous trigger executions helps serialize processing and prevents multiple runs from racing through the same reservation logic at the same time. That addresses the design flaw most directly.

This does not magically make a non-idempotent external API perfect, but it is the most appropriate first correction based on the evidence in the scenario. A retry change could make duplicates worse, a business rule would not govern external call concurrency, and child flow retries do not solve contention at the trigger level. In cloud-flow design, concurrency control is often the first lever when duplicate downstream effects are caused by parallel execution rather than by bad business data.

<sub>Set E · Q10</sub>

---

### 55. A team modeled inspection records as a virtual table because the source system already held the data. After rollout, technicians report that record-centric platform behaviors expected by the business are missing, and solution reviewers note that the design should support core Dataverse-style business data behavior rather than a projection over an external source. The source system is no longer required to remain the master.

What is the best design correction?

- **A.** Add connector policy templates
- **B.** Use a standard table ✅
- **C.** Switch to elastic table
- **D.** Keep virtual table and custom cache

> **Answer:** B. Use a standard table

The best correction is to use a standard table because the design has shifted from “surface external data without replication” to “treat these rows as native business data with Dataverse-centric behavior.” Once the external system no longer needs to remain the master and the solution expects core record behavior, a standard table becomes the appropriate architectural choice.

Elastic tables are still a specialized fit for massive-scale, high-throughput scenarios rather than ordinary record-centric business data. A connector or a cached virtual-table pattern also misses the core correction because those patterns remain oriented around external access, not native Dataverse persistence and modeling. The issue here is not performance tuning of the virtual design; it is that the wrong table pattern was chosen.

<sub>Set E · Q50</sub>

---

### 56. A field service solution must ingest bursty device telemetry from thousands of endpoints. The app needs low-latency writes and recent-event queries, but it does not require complex relational joins or transactional business logic across tables.

Which option should you use for the data store?

- **A.** Standard table
- **B.** Virtual table with cache
- **C.** Elastic table ✅
- **D.** Shared connector operations

> **Answer:** C. Elastic table

Elastic tables are the best fit when the requirement is high-volume, horizontally scalable storage with fast read and write throughput. This scenario is centered on bursty telemetry ingestion, rapid growth, and lightweight access patterns rather than rich relational behavior. That aligns directly with the intended use of elastic tables.

A standard table would be a better choice if the workload required strong relational modeling, complex joins, or transactional behavior across tables and plug-ins. A virtual table is for surfacing external data without replicating it into Dataverse, and a connector is for calling external operations rather than acting as the primary high-scale Dataverse data store.

<sub>Set E · Q70</sub>

---

### 57. A reusable operation must validate request data, execute in Dataverse, and be callable as a Dataverse message from code and from flows. Which implementation approach should you use? Select only one answer.

- **A.** Custom connector
- **B.** Cloud flow
- **C.** JavaScript web resource
- **D.** Custom API ✅

> **Answer:** D. Custom API

Custom API is the correct implementation approach because it is purpose-built for creating your own Dataverse operation surface. Microsoft documents custom APIs as a way to extend the Dataverse API with custom messages, typically backed by server-side business logic when needed.

The other options solve adjacent problems but not this one. Custom connectors wrap external REST or SOAP APIs, cloud flows orchestrate automation after triggers, and JavaScript web resources target client behavior in the app experience rather than defining a Dataverse message.

<sub>Set F · Q2</sub>

---

### 58. A finance automation uses a mission-critical cloud flow that must keep running even when administrators change roles or leave the company. The same internal REST API must also be callable from both Power Automate and a canvas app, and the API must use Microsoft Entra ID rather than embedded credentials.

Which design should you recommend?

- **A.** User-owned flow + API key custom connector
- **B.** Service principal flow + Entra ID connector ✅
- **C.** Shared mailbox owner + basic auth connector
- **D.** Personal flow owner + environment variable secret

> **Answer:** B. Service principal flow + Entra ID connector

The best design is a service-principal-owned flow combined with a custom connector secured through Microsoft Entra ID. Microsoft documents service principal application users as the right approach when flows are mission critical and should be insulated from individual owner lifecycle changes, and Microsoft also documents Entra ID as a recommended authentication model for custom connectors and Dataverse-connected applications.

This design also supports cleaner authorization boundaries. The non-human identity can be granted least-privilege access through the right application-user and connector permissions, while the API authentication model remains centralized and avoids embedding secrets in app formulas or relying on a named person’s account.

<sub>Set F · Q3</sub>

---

### 59. An order-discount rule must reject invalid values whether records are created from a model-driven app, an import, or an external integration. The validation must run synchronously before the row is committed and must not depend on any specific form.

Which place should you implement the logic?

- **A.** Form business rule
- **B.** Client API script
- **C.** Cloud flow
- **D.** PreOperation plug-in ✅

> **Answer:** D. PreOperation plug-in

A PreOperation plug-in is the best fit because the logic must run on the server before the main system operation is committed, and it must apply regardless of the entry channel. Microsoft’s event framework guidance makes clear that PreOperation runs before the main operation within the transaction, and Dataverse plug-ins are designed for performant server-side business logic.

The other choices are too channel-specific or too late in the lifecycle. Business rules and client scripting are tied more closely to app experiences, while a cloud flow is asynchronous automation rather than the strongest choice for synchronous in-transaction validation before commit.

<sub>Set F · Q4</sub>

---

### 60. A model-driven app uses JavaScript to disable a Discount field when the Status column changes to Closed. Users report that the form behaves correctly, but integrations updating the same table through the Dataverse Web API can still save discount values after the status is closed.

What is the best explanation?

- **A.** The script must be moved to a custom connector
- **B.** The field needs DLP classification
- **C.** The logic runs client-side, not server-side ✅
- **D.** The table must be converted to elastic

> **Answer:** C. The logic runs client-side, not server-side

The best explanation is that the current logic is client-side. Microsoft’s client scripting guidance describes JavaScript web resources as form-event-based logic in model-driven apps, which means that behavior can work perfectly in the interactive UI while remaining invisible to other write paths such as integrations and API calls.

To enforce the rule across all channels, the logic must move to a server-side enforcement point such as Dataverse pipeline logic. This is the core distinction between client-side experience logic and server-side business logic in Power Platform solution design.

<sub>Set F · Q6</sub>

---

### 61. A field service solution must store tens of millions of telemetry rows per month with bursty write throughput and automatic cleanup after a retention period. The data is mostly append-heavy, and complex relational joins are not the priority.

Which table type should you choose?

- **A.** Standard relational table
- **B.** Elastic table ✅
- **C.** Virtual table over SQL
- **D.** Out-of-box activity table

> **Answer:** B. Elastic table

Elastic table is the best fit because Microsoft documents elastic tables for very large datasets, horizontal scaling, high throughput, and real-time workloads. The scenario explicitly signals bursty volume, append-heavy writes, and retention-oriented behavior, all of which align strongly with elastic-table design guidance.

The other options fit different patterns. Standard tables are stronger where relational modeling and transactional consistency dominate, virtual tables are for externally sourced data without replication, and activity tables are for activity-shaped business data such as tasks or appointments rather than telemetry ingestion.

<sub>Set F · Q7</sub>

---

### 62. A sales team uses both model-driven apps and canvas apps. They need the same reusable date-and-status selector in both experiences, and the control must support custom rendering and packaged reuse without copying logic into each app.

Which approach should you recommend? Select only one answer.

- **A.** Canvas component library control
- **B.** Business rule logic
- **C.** PCF code component ✅
- **D.** JavaScript web resource control

> **Answer:** C. PCF code component

A PCF code component is the best fit when you need a reusable custom control that can be packaged and used in Power Apps with richer UI behavior than standard controls. Microsoft positions Power Apps component framework for professional developers to build code components for both model-driven and canvas apps, which directly matches the cross-experience reuse requirement here.

Canvas components and component libraries are useful for reuse inside canvas apps, but they do not give you the same cross-surface component model for model-driven apps. Because the requirement explicitly spans both canvas and model-driven experiences, the most natural Microsoft-platform answer is a PCF control rather than an app-level canvas reuse pattern or a form script workaround.

<sub>Set F · Q9</sub>

---

### 63. Your team is importing a custom connector for an internal REST API. Each user must sign in with their own Microsoft Entra identity, and the connector must avoid a shared static secret.

Snippet

{
  "swagger": "2.0",
  "securityDefinitions": {
    "api_key": {
      "type": "apiKey",
      "name": "x-api-key",
      "in": "header"
    }
  },
  "security": [
    {
      "api_key": []
    }
  ]
}
Which change best meets the requirement?

- **A.** API key header
- **B.** Basic authentication
- **C.** Anonymous connector policy
- **D.** OAuth 2.0 ✅

> **Answer:** D. OAuth 2.0

A custom connector that must let each user sign in with their own identity should use OAuth 2.0 rather than an API key model. Microsoft’s custom connector guidance supports authenticated APIs, and OpenAPI-based connector definitions are intended to describe the connector’s security model so the platform can prompt users to authorize appropriately.

The snippet currently defines an apiKey scheme, which implies a shared key-style authentication model rather than delegated per-user sign-in. That makes it the wrong design for a requirement centered on individual user identity and avoiding shared secrets.

<sub>Set F · Q11</sub>

---

### 64. A model-driven app command must invoke server-side validation and return a calculated approval result to the caller immediately. The operation will be called from multiple clients, and the team wants a formal Dataverse message contract with input and output parameters.

Which approach should you use?

- **A.** Instant cloud flow action
- **B.** Dataverse custom API ✅
- **C.** Client-side business rule
- **D.** Timer-triggered Azure Function

> **Answer:** B. Dataverse custom API

A Dataverse custom API is the strongest design because it gives you an explicit Dataverse operation surface with defined request and response parameters. Microsoft documents custom APIs as the right way to expose reusable operations, and they are commonly paired with plug-ins when you need server-side logic executed inside the platform.

The requirement is not just “run some logic.” It is “provide a reusable Dataverse message contract that multiple callers can invoke and receive an immediate result from.” That is why a custom API is a better answer than a flow, a client-side rule, or a timer-based Azure integration pattern.

<sub>Set F · Q28</sub>

---

### 65. A canvas app that uses Dataverse is shared with a Microsoft Entra group, and users can launch the app. However, they still cannot read Account rows, and a related automation design is blocked because Dataverse and Twitter connectors are in conflicting DLP groups.

Which statement best describes the impact?

- **A.** App sharing and DLP don't replace Dataverse security ✅
- **B.** Owner teams bypass DLP and row security
- **C.** Access teams grant roles across business units
- **D.** Business units override connector classification

> **Answer:** A. App sharing and DLP don't replace Dataverse security

This is the best statement because app sharing and DLP solve different problems from Dataverse row access. Microsoft states that canvas apps can be shared with users or groups, but access is still subject to Dataverse security roles; Microsoft also states that DLP policies classify connectors and control which business data can be shared across connectors.

So the users can be allowed to open the app while still lacking permission to the underlying Dataverse rows, and the automation can be blocked independently by DLP connector-group rules. That combined effect is exactly what the scenario describes, making option A the accurate impact assessment.

<sub>Set F · Q33</sub>

---

### 66. A sales team needs to show or hide fields, enforce simple validation, and display guidance on forms. The rules change frequently, and the project wants to avoid custom code unless a requirement clearly demands it.

Problem:

Implement fast-changing validation and guidance logic with minimal code.

Proposed solution:

Create a business rule on the Dataverse table.

Does the proposed solution meet the goal?

- **A.** Yes ✅
- **B.** No

> **Answer:** A. Yes

Yes is correct because business rules are specifically intended for common logic and validation scenarios without writing code or creating plug-ins. Microsoft’s guidance describes business rules as a simple way to implement and maintain fast-changing logic, which matches the requirements in the scenario very closely.

This is exactly the kind of requirement where out-of-the-box functionality should be preferred over custom development. The requirement does not mention complex external calls, custom Dataverse messages, or cross-channel server enforcement that would force a plug-in or other pro-code extension.

<sub>Set F · Q38</sub>

---

### 67. A solution architect reviews four proposed mappings before build starts.

Exhibit 1

Which row maps the requirement to the most appropriate solution component?

- **A.** Row 1
- **B.** Row 2
- **C.** Row 3 ✅
- **D.** Row 4

> **Answer:** C. Row 3

Row 3 is the best mapping because a custom API is the right Dataverse-native component when you need to expose a reusable operation as a message that developers and flows can call. Microsoft documents custom API as a way to extend the Dataverse API with your own operation, and it is commonly paired with plug-in logic when the operation needs server-side behavior.

The other rows mismatch the requirement to the component. Virtual tables are for surfacing external data without replication, client-side JavaScript is for form behavior rather than universal server enforcement, and command-bar-driven user experiences are handled through app-command customization rather than a cloud flow trigger as the primary UI component.

<sub>Set F · Q45</sub>

---
