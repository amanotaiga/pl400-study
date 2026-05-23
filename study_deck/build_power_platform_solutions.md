# Build Power Platform Solutions  

_Exam weight 10–15% · 48 questions across all sets._

---

### 1. A solution includes a custom connector that calls an external OAuth-protected API. The client secret is different in Dev, Test, and Prod, and the team must avoid storing the secret directly in the solution or in plain text configuration.

Which approach should they use?

- **A.** Text environment variable value
- **B.** Per-environment connection reference
- **C.** Secret environment variable ✅
- **D.** Secure inputs and outputs

> **Answer:** C. Secret environment variable

A secret environment variable is the best fit because it is designed to reference secrets stored in Azure Key Vault rather than storing the secret directly in the solution. Microsoft documents that these secret-backed environment variables are intended for use with Power Automate flows and custom connectors, which matches this scenario closely.

This design also keeps the custom connector definition portable across environments while letting each environment resolve its own secret. Microsoft further notes that plain text client secrets in custom connectors are not secure, and that custom connectors use environment variable values at save time, which is why this pattern is more appropriate than a regular text variable.

<sub>Set A · Q27</sub>

---

### 2. A team is packaging a solution that uses a SharePoint site URL in apps and flows and will deploy the same solution through Dev, Test, and Prod. They want to avoid hardcoding environment-specific settings and keep connection handling separate from configuration values.

Which two actions should they take? (Select TWO.)

- **A.** Create environment variables inside the solution ✅
- **B.** Store SQL connection credentials in text variables
- **C.** Use connection references for shared connections ✅
- **D.** Hard-code target URLs in each component
- **E.** Add environment variables for native Dataverse tables

> **Answer:** A. Create environment variables inside the solution · C. Use connection references for shared connections

The correct pair is to create environment variables inside the solution and to use connection references for shared connections. Microsoft’s ALM guidance for environment variables is to separate configuration values from the consuming objects so the same solution can move across environments, while connection references handle connection plumbing separately.

That separation is the key design principle being tested. Environment variables are appropriate for values such as SharePoint site URLs and similar parameters, while connection references address how the solution binds to connections; using both together creates a cleaner and more portable ALM design than hardcoding or overusing variables for things that should remain connection-specific.

<sub>Set A · Q28</sub>

---

### 3. A maker is importing a managed solution into Test and wants to know which environment variable will require a new value during import.

Exhibit 1

Which variable will prompt for a new value during import?

- **A.** API_BaseUrl ✅
- **B.** SupportEmail variable
- **C.** SharePointSite variable
- **D.** RetryProfile variable

> **Answer:** A. API_BaseUrl

API_BaseUrl is the one that will prompt because it has no default value, no value packaged in the solution, and no existing target value. Microsoft states that environment variables without a default value or value prompt for a value during solution import, while other cases are prefilled and labeled according to their source.

The other rows all have something that prevents a required prompt. SupportEmail has a default value, SharePointSite already carries a solution value, and RetryProfile already has a target environment value in addition to a default. That makes A the only row where the import experience must request fresh input from the maker.

<sub>Set A · Q29</sub>

---

### 4. A production solution cloud flow uses an environment variable for an endpoint URL. An admin updates the environment variable directly in Production, but the next flow runs still call the old endpoint.

What is the best explanation and next step?

- **A.** Reimport the managed solution
- **B.** Cycle the flow ✅
- **C.** Recreate the variable record
- **D.** Convert the value into JSON

> **Answer:** B. Cycle the flow

Microsoft documents that when environment variable values are changed directly within an environment rather than through an ALM operation like solution import, solution cloud flows continue using the previous value until the flow is saved or turned off and turned on again. That makes cycling the flow the best immediate corrective action in this scenario.

The important distinction is that the variable update itself may be valid, but the running flow has not refreshed its reference yet. This is a runtime refresh issue, not proof that the variable definition is wrong, which is why recreating the variable or reimporting the entire solution is excessive compared with simply refreshing the flow.

<sub>Set A · Q30</sub>

---

### 5. A team stores an external API base URL in an environment variable inside a solution. They want the Test import to require a new URL while keeping the existing Development value unchanged.

What should they do before exporting the solution?

- **A.** Remove the solution value ✅
- **B.** Set a default value
- **C.** Replace it with a connection reference
- **D.** Convert the variable to JSON

> **Answer:** A. Remove the solution value

Environment variables are solution components that let a solution carry the variable definition while allowing values to differ by environment. If the team removes the current value from the solution before export, the Development environment can keep using its own value, and the target environment can provide a new value during import.

This is the clean ALM pattern when the variable should be re-supplied per environment instead of pushed forward from Development. Microsoft also notes that the import experience surfaces environment variable values and that variables without a default or existing value prompt for input, which is exactly the behavior the team wants here.

<sub>Set A · Q38</sub>

---

### 6. A release manager wants fewer layer conflicts and cleaner upgrades across downstream environments. Recent deployments have been complicated by direct edits to managed components and by solutions carrying more component assets than they actually need.

Which two practices should the team adopt? (Select TWO.)

- **A.** Edit managed components downstream
- **B.** Use segmented solutions ✅
- **C.** Add full table assets by default
- **D.** Rely on Active layer fixes
- **E.** Author changes in source solution ✅

> **Answer:** B. Use segmented solutions · E. Author changes in source solution

Use segmented solutions is correct because Microsoft recommends including only the necessary parts of a component rather than entire tables or oversized asset sets. Their troubleshooting guidance states that unnecessary elements increase solution complexity, introduce multiple managed layers on components, and create more conflicts during updates. Segmentation reduces that risk and makes layers easier to manage.

Author changes in source solution is also correct because Microsoft states that managed components should not be edited directly in downstream environments. Instead, changes should be made in an unmanaged solution in the source environment and then redistributed. That preserves predictable layering and avoids unmanaged customizations overriding managed behavior later.

<sub>Set B · Q5</sub>

---

### 7. A production environment contains a vendor-managed solution. The operations team wants a quick form change, but they also want future vendor updates to apply predictably and the vendor solution to remain removable later. The proposed fix should be judged against all of those requirements.

Problem:

A managed form component must be changed quickly in production without breaking future ALM behavior.

Proposed solution:

Edit the managed component directly in production and rely on Overwrite Customizations during future imports.

Does the proposed solution meet the goal?

- **A.** Yes
- **B.** No ✅

> **Answer:** B. No

No is correct because editing a managed component directly in production creates an unmanaged customization on top of the managed layer. Microsoft states that this unmanaged layer can override updates from the source managed solution, cause inconsistencies across environments, and prevent later deployed changes from being reflected correctly. That directly conflicts with the requirement for predictable future updates.

The proposal also does not preserve a clean managed lifecycle. Microsoft notes that when you edit a managed component, you create a dependency between unmanaged customizations and the managed solution, and that dependency can prevent the managed solution from being uninstalled until the dependency is removed. Overwrite Customizations is not a substitute for clean source-based ALM because it can copy values into the Active layer while leaving the Active layer in place.

<sub>Set B · Q12</sub>

---

### 8. A managed solution update is imported into test, but users still see behavior from an ad-hoc change that was made directly in that environment. The team wants the imported managed value to control runtime behavior again.

Which action should you take first?

- **A.** Stage the upgrade and apply later
- **B.** Remove active customizations ✅
- **C.** Clone a patch from source
- **D.** Export the target solution as managed

> **Answer:** B. Remove active customizations

Remove active customizations is the best first action because unmanaged customizations sit at the top layer and determine runtime behavior for the component. Microsoft’s solution layer guidance explicitly states that unmanaged customizations typically define the effective behavior in downstream environments and can be removed from the solution layers experience when they are sitting above managed layers.

This is the cleanest fix when the problem is an unmanaged Active layer overriding a managed import. A patch or staged upgrade does not remove that top unmanaged layer, and exporting the target environment as managed is not how Dataverse resolves runtime precedence.

<sub>Set B · Q13</sub>

---

### 9. A platform team owns common Dataverse tables that are shared by three business applications. Each app team releases on a different cadence and must extend the common model without changing the shared foundation. The organization also wants clearer import order and fewer cross-team layer conflicts.

Which design should the team choose?

- **A.** Single unmanaged solution across all teams
- **B.** Different publishers with shared components
- **C.** Managed base and app layer ✅
- **D.** Direct target-environment customizations for each app module

> **Answer:** C. Managed base and app layer

Managed base and app layer is the best design because Microsoft recommends a layered approach for modular architectures: build the shared foundation in a base solution, export it as managed, import that managed base into the app-layer development environment, and then author the app-specific unmanaged solution on top of it before exporting that layer as managed. This creates clear dependencies and cleaner managed layering in downstream environments.

That design also supports independent release cadence more safely than putting everything in one unmanaged solution or letting teams customize directly in target environments. Microsoft’s ALM guidance warns that multiple unmanaged solutions in the same development environment can create dependency conflicts, and it recommends using the same publisher across solutions to keep the layering model manageable.

<sub>Set B · Q14</sub>

---

### 10. A synchronous plug-in writes to a restricted audit table whenever a vendor risk level changes. Business users can update the vendor row, but the transaction fails when the audit row is created.

Snippet

Message: Update
Primary table: crb_vendor
Stage: PreOperation
Execution mode: Synchronous
Run in User's Context: Calling User
Filtering attributes: crb_risklevel
Action in code: Create crb_restrictedaudit
Which setting best explains the security failure?

- **A.** Calling user context ✅
- **B.** Missing pre-image column registration
- **C.** PreOperation stage selection
- **D.** Asynchronous step execution mode

> **Answer:** A. Calling user context

The best explanation is Calling User context. When a plug-in step runs in the calling user context, Dataverse applies that user’s privileges to the work done by the plug-in, so a create operation against a restricted audit table will fail if the interactive user does not have permission to create rows there.

Impersonation and execution context are central to security troubleshooting for server-side extensions. Microsoft’s documentation explains that plug-ins can execute under a specified user context, and when they do, the effective privileges of that user govern the operation. That is why this registration setting is the most direct explanation for the failure.

<sub>Set B · Q17</sub>

---

### 11. A finance user can open and edit an account row in a model-driven app. The save fails only when they change a secured credit column.

Exhibit 1

Which control should be reviewed first?

- **A.** Business-unit depth
- **B.** Column security profile ✅
- **C.** Record ownership chain
- **D.** Access team template membership settings

> **Answer:** B. Column security profile

The exhibit points directly to column security. The user already has row access to the account and has Account Write privilege, so the failure is not coming from basic record visibility or table-level write rights. The secured column is the differentiator, and both the user and team profile values show Update as Not Allowed.

Microsoft’s column security documentation makes clear that a column security profile controls which users or teams can read, update, or create values in secured columns. When a user can update the row generally but cannot modify one protected field, the first diagnostic target is the column security profile and its permissions rather than the broader role model.

<sub>Set B · Q18</sub>

---

### 12. Users can open and edit cases that they own. After a recent role redesign, they can no longer reassign those same cases to another salesperson, and the error appears immediately in the app.

What should you fix first?

- **A.** Assign privilege ✅
- **B.** Share privilege
- **C.** Append privilege
- **D.** Organization-level write privilege depth

> **Answer:** A. Assign privilege

The first thing to fix is the Assign privilege. Reassigning a record is a separate security action in Dataverse, and Microsoft’s security model treats Assign as its own privilege alongside Create, Read, Write, Delete, Append, AppendTo, and Share. A user can therefore still open and edit an owned case while being blocked specifically from transferring ownership.

This is a common operational security issue after role redesign because teams often preserve Write while accidentally removing Assign. The symptom pattern in the question is very specific: users can still work with their own records, but ownership transfer fails immediately. That points much more directly to Assign than to a generic row-access or write-depth problem.

<sub>Set B · Q20</sub>

---

### 13. A cloud flow now assigns escalated cases to a central operations team. After the change, users in other business units can open those cases even though no security role depth was widened for the individual users.

Which control should you inspect first?

- **A.** Access team template
- **B.** Owner team roles ✅
- **C.** Manual row shares
- **D.** Environment Admin plus System Customizer roles

> **Answer:** B. Owner team roles

Owner team roles are the first control to inspect because Dataverse access is driven by security roles, and those roles can be assigned to teams as well as users. When records begin getting assigned to a central team, effective access can widen through that team’s role assignments even if the users’ own roles never changed.

This is especially important because only owner and Microsoft Entra group teams can own records, and team ownership changes who is providing the access path for those records. If the automation started reassigning cases to a team that carries broader privileges, the unexpected visibility is most likely coming from the team’s security roles rather than from a hidden change to individual user roles.

<sub>Set B · Q35</sub>

---

### 14. A team upgrades AppCore in production and expects a command label to change immediately. The new label is present in the imported solution, but users still see the older value at runtime.

Exhibit 1

Why is AppCore 2.1 not controlling runtime behavior?

- **A.** Another managed layer is on top ✅
- **B.** An unmanaged base instance exists
- **C.** Overwrite customizations copied value to Active layer
- **D.** Managed properties blocked the import update

> **Answer:** A. Another managed layer is on top

Another managed layer is on top is correct because the exhibit shows SalesExtension above AppCore 2.1 in the layer stack. Microsoft’s troubleshooting guidance explains that when another managed solution is the top layer, updates to a lower managed solution do not become the effective runtime value. The highest applicable layer continues to win.

This is also why Overwrite Customizations would not solve the issue shown in the exhibit. Microsoft states that Overwrite Customizations only copies the incoming value to the Active layer; it does not displace another managed solution that is already the top effective managed layer. In this case, the fix must come from the source of the top managed layer or by changing that managed layering arrangement.

<sub>Set B · Q37</sub>

---

### 15. A customer service app lets users create notes on case records. Users can create both notes and cases, but saving a note against an existing case fails with an insufficient privileges error.

Which privileges must be present to resolve the issue? (Select TWO.)

- **A.** Append on Note ✅
- **B.** Append To on Case ✅
- **C.** Share on the parent case
- **D.** Assign on Note
- **E.** Delete on annotation records

> **Answer:** A. Append on Note · B. Append To on Case

To attach one record to another in Dataverse, you must evaluate the Append and Append To privilege pair. The note is the record being attached, so it requires Append on Note, while the case is the record receiving the association, so it requires Append To on Case.

This is a classic operational security issue because users may already have Create, Read, and Write and still fail on the relationship action itself. Dataverse treats record association as a separate security decision, so missing one side of the Append or Append To pair can block the save even when both rows already exist and are otherwise editable.

<sub>Set B · Q55</sub>

---

### 16. A CoE team wants one governed deployment path that multiple makers can use across Development, Test, UAT, and Production. The design must support approvals, extensibility, and shared pipeline access without forcing each maker to create a separate personal pipeline.

Which approach should you recommend?

- **A.** Platform host personal pipeline
- **B.** Solution import wizard
- **C.** Azure DevOps YAML pipeline
- **D.** Custom host pipeline ✅

> **Answer:** D. Custom host pipeline

A custom host pipeline is the best fit because custom hosts are designed for governed, shared pipeline management. Microsoft documents that admins can create one or more pipelines, associate any number of environments, and share access with people who administer or run pipelines.

This requirement also exceeds the limits of personal pipelines in the platform host. Microsoft documents that personal pipelines are limited to three associated environments, can’t be extended, and can’t be shared with other users; when you need advanced extensibility, shareability, or more than two target environments, you should move to a custom host.

<sub>Set C · Q2</sub>

---

### 17. A stage is already configured for delegated deployment by using a service principal. The team is now building the approval flow that must release the deployment from its pending approval state.

Which two implementation choices are required? (Select TWO.)

- **A.** OnApprovalStarted trigger ✅
- **B.** OnDeploymentRequested trigger
- **C.** UpdateApprovalStatus with delegate connection ✅
- **D.** UpdatePreExportStepStatus action
- **E.** Anonymous custom connector approval endpoint

> **Answer:** A. OnApprovalStarted trigger · C. UpdateApprovalStatus with delegate connection

For a service-principal delegated deployment, Microsoft documents that the approval flow uses the OnApprovalStarted trigger and then calls UpdateApprovalStatus. Microsoft also explicitly states that the UpdateApprovalStatus action must use the service principal’s connection.

This is important because delegated deployments remain pending until the approval automation completes correctly. If you use the wrong trigger or the wrong completion action, the stage does not leave the delegated approval path in the supported way.

<sub>Set C · Q4</sub>

---

### 18. A model-driven app uses a field code component on the Case table. The component updates one existing text column on cases that the signed-in user already owns.

Which privilege combination should the user's Dataverse security role include?

- **A.** Case Create, Write, Delete
- **B.** Case Read, Append, Assign
- **C.** Case Read, Write ✅
- **D.** Case Read, Write, Share, Append To

> **Answer:** C. Case Read, Write

A field code component that edits an existing Case column needs the same core Dataverse privileges the user needs to open the record and save the change. In Dataverse, security roles define what operations users can perform on a table, and Read plus Write is the minimal combination for this scenario. That is the cleanest least-privilege fit because the component is not creating, deleting, assigning, sharing, or relating records.

Least privilege means granting only the operations required for the business task and nothing broader. Microsoft’s security guidance emphasizes minimum required access, and Dataverse role design is built around assigning the specific privileges needed for the app behavior. Here, the component updates an existing value on a record the user already owns, so Case Read and Case Write are sufficient.

<sub>Set C · Q8</sub>

---

### 19. A sales solution uses a dataset code component to display Account data in a model-driven app. Only a specialist group should see the account dataset, and the component must not rely on elevated identities or broad read access for all sellers.

Which approach should you use?

- **A.** Org-level Account Read for sellers
- **B.** System Customizer for sellers
- **C.** Per-record Account sharing
- **D.** Custom specialist team role ✅

> **Answer:** D. Custom specialist team role

The best answer is to create a custom role that grants the specific Account access the code component needs and assign it only to the specialist users or their team. Dataverse security roles are the standard mechanism for controlling which users can read or act on table data, and Microsoft’s security guidance centers on minimum required access. That makes a narrowly scoped custom role the most appropriate least-privilege design.

Using an elevated role or broad tenant-wide access would make the component work, but it would do so by weakening the security model. Record-by-record sharing can solve targeted access problems, but it is higher-overhead and less maintainable than a purpose-built role when an entire specialist group needs the same repeatable access pattern. A custom specialist role is therefore the most secure and operationally sustainable answer.

<sub>Set C · Q11</sub>

---

### 20. A field code component lets users populate the Preferred Branch lookup on Contact records they already own. Users already have Contact Read, Contact Write, and Branch Read through an existing role. The component must support the lookup update without granting delete, assign, or broader rights.

Which two additional privileges should the security role include? (Select TWO.)

- **A.** Contact Delete
- **B.** Contact Append ✅
- **C.** Contact Assign
- **D.** Branch Append To ✅
- **E.** Branch Delete

> **Answer:** B. Contact Append · D. Branch Append To

When a user sets a lookup value, Dataverse treats that as an association between the current record and the target record. Dataverse security concepts define Append and Append To as distinct privileges, and for lookup behavior the current record needs Append while the target table needs Append To. That is why Contact Append and Branch Append To are the required additions here.

This is also the least-privilege answer because it adds only the two privileges needed for the lookup relationship change. The users already have Read and Write where needed, so there is no justification for broader privileges such as Delete or Assign. A well-designed security role should add only the missing relationship privileges that the code component depends on.

<sub>Set C · Q12</sub>

---

### 21. A model-driven app uses a dataset code component on the Account form to show related Invoice records from Dataverse. The component works for administrators, but sales users see an access denied message inside the control. Sales users already have the app role and the required Account privileges, and they must not receive broader permissions than needed.

What is the best fix?

- **A.** System Customizer role
- **B.** Invoice Read privilege ✅
- **C.** Field security profile update
- **D.** Org-level Invoice Delete

> **Answer:** B. Invoice Read privilege

The most likely cause is that the sales users do not have read access to the related Invoice table that the dataset code component is querying. Dataverse security roles control what data operations users can perform per table, so having access to the app and to Account does not automatically grant access to Invoice. Adding Invoice Read is therefore the minimal security-role change that aligns with the component’s runtime behavior.

This is also the least-privilege correction because it grants only the missing operation on the missing table. The scenario explicitly says broader permissions are not acceptable, so elevated customization roles or destructive privileges are poor choices. When a code component reads Dataverse data, the clean fix is to grant the specific table privilege that the user lacks.

<sub>Set C · Q13</sub>

---

### 22. A team enabled Pre-deployment Step Required on a stage named Contoso UAT. They want a cloud flow in the pipelines host to run only when that inserted pre-deployment gate starts for that stage.

Snippet

@equals(triggerOutputs()?['body/OutputParameters/DeploymentStageName'], 'Contoso UAT')
What does the expression do when used as a trigger condition on an OnPreDeploymentStarted flow?

- **A.** Automatic completion of the gate
- **B.** UAT stage filter ✅
- **C.** Target environment reassignment
- **D.** Failed deployment replay logic

> **Answer:** B. UAT stage filter

The expression is a stage-name filter. Microsoft documents that trigger conditions can be used so a flow runs only for a specific pipeline or a specific stage, and gives the same pattern for matching a stage by DeploymentStageName.

That means the condition doesn’t approve, reject, or modify anything by itself. It simply limits the flow so the custom pre-deployment logic runs only when the stage name equals Contoso UAT, which is exactly how you scope extensions cleanly in a shared pipelines host.

<sub>Set C · Q15</sub>

---

### 23. A pipelines administrator enabled Is Delegated Deployment on a stage that uses a service principal. The team must build the approval flow in the pipelines host so approved requests can leave the pending state in the supported order.

Steps

Add Dataverse Perform an unbound action to call UpdateApprovalStatus by using the service principal connection.

Create the cloud flow in a solution within the pipelines host environment.

Insert approval logic and a condition that branches on approve or reject.

Select the OnApprovalStarted trigger.

What is the correct order?

- **A.** 4 → 2 → 3 → 1
- **B.** 2 → 3 → 4 → 1
- **C.** 2 → 4 → 3 → 1 ✅
- **D.** 4 → 3 → 2 → 1

> **Answer:** C. 2 → 4 → 3 → 1

The correct order is to create the flow in the pipelines host first, then select the delegated-approval trigger, then add the approval logic, and finally complete the flow by calling UpdateApprovalStatus with the delegate connection. Microsoft documents this canonical pattern for service-principal delegated deployments in the pipelines host.

This order matters because the flow has to begin in the correct host context and on the correct event, then gather approval outcome, and only then write the decision back to pipelines. Microsoft also explicitly states that UpdateApprovalStatus must use the service principal’s connection, which is why that step belongs after the branch logic rather than before it.

• 2 is first because the approval automation must exist in the pipelines host environment before it can subscribe to the delegated approval event. Microsoft’s documented sequence begins with creating the cloud flow in the pipelines host.

• 4 is second because OnApprovalStarted is the event that begins the delegated approval flow. It is the correct trigger for this extension and comes before the approval-processing logic.

• 3 is third because the flow must capture the approval decision and branch accordingly before it can tell pipelines whether the request is approved or rejected. That business logic sits between the trigger and the final status update.

• 1 is last because UpdateApprovalStatus is the action that writes the final outcome back to pipelines, and Microsoft requires it to use the service principal connection. It therefore follows the approval and condition logic, not the other way around.

<sub>Set C · Q17</sub>

---

### 24. A field code component on Opportunity updates a single score column on opportunities the signed-in user owns. The component does not create records, delete records, or access Quote data.

Exhibit 1

Which role best supports the component with least privilege?

- **A.** Scorer ✅
- **B.** Opportunity Viewer role
- **C.** Opportunity Closer role
- **D.** Admin Lite role

> **Answer:** A. Scorer

The exhibit shows that Scorer is the narrowest role that still provides the exact privileges the code component requires: User-level Read and User-level Write on Opportunity, with no unnecessary Delete or Quote access. Because the component updates a score field on opportunities the signed-in user owns, those two Opportunity privileges are the decisive requirement. That makes Scorer the best least-privilege match.

The other roles either omit a necessary privilege or add more access than the component needs. Least privilege is not satisfied by “a role that works somehow”; it is satisfied by the smallest role that enables the precise data operations required by the app behavior. Based on the exhibit, only Scorer meets that standard cleanly.

<sub>Set C · Q25</sub>

---

### 25. A review board is validating the extension design for a governed pipelines host.

Exhibit 1

Which row is incorrectly mapped?

- **A.** Row 1
- **B.** Row 2
- **C.** Row 3
- **D.** Row 4 ✅

> **Answer:** D. Row 4

Row 4 is incorrect because Microsoft documents that Pre-deployment Step Required starts with OnPreDeploymentStarted, not OnDeploymentCompleted. The matching completion action for that gated step is UpdatePreDeploymentStepStatus, but the wrong start trigger means the row is still invalid overall.

The other three rows match the published extension mappings. Microsoft lists pre-export with OnDeploymentRequested and UpdatePreExportStepStatus, delegated deployment with OnApprovalStarted and UpdateApprovalStatus, and pre-deployment with OnPreDeploymentStarted and UpdatePreDeploymentStepStatus.

<sub>Set C · Q52</sub>

---

### 26. A team is choosing one Azure DevOps design for Power Platform deployments across test and production. They want source-controlled solution assets, automated validation, managed downstream releases, and reduced secret handling overhead.
Which pipeline best matches a robust CI/CD design by using Power Platform Build Tools?

Exhibit 1

- **A.** Pipeline A
- **B.** Pipeline B
- **C.** Pipeline C ✅
- **D.** Pipeline D

> **Answer:** C. Pipeline C

Pipeline C is the strongest Build Tools-based CI/CD design because it combines the major ALM controls Microsoft documents for Azure DevOps automation: export from development, source-control-friendly solution files, validation through Checker, and managed imports into downstream environments. It also aligns with the documented recommendation to use service principal authentication via Workload Identity Federation where possible.

It is also the only option that explicitly handles environment-specific connection references and environment variables through a deployment settings file during import. That combination makes the pipeline both repeatable and production-appropriate, which is the key requirement for CI/CD automation rather than ad hoc deployment.

<sub>Set D · Q4</sub>

---

### 27. A new developer needs an isolated place to build and test apps, flows, Dataverse tables, and custom connectors without using the tenant’s shared default environment. The environment is for that developer’s work, not for a shared business workload.

Which environment type should you recommend?

- **A.** Tenant default environment
- **B.** Subscription-based trial environment
- **C.** Developer environment ✅
- **D.** Production Dataverse environment

> **Answer:** C. Developer environment

A developer environment is the best fit when one developer needs a dedicated, isolated workspace for building and testing Power Platform assets. Microsoft’s Developer Plan provides a free development environment for Power Apps, Power Automate, and Dataverse, and Microsoft explicitly says to use the developer environment instead of the tenant’s default environment for scenarios involving capabilities such as premium and custom connectors.

The other environment types fail the development intent in different ways. The default environment is shared across the tenant, production is intended for permanent business workloads, and trial environments are short-term rather than a stable development home. Microsoft’s environment guidance also says developer environments are intended only for use by the owner, which aligns with the stated requirement.

<sub>Set D · Q11</sub>

---

### 28. A team moves the same solution from development to test and UAT. Several values differ by environment, including an API base URL and a queue name, and the team wants imported flows to bind cleanly in each target environment without manual rewiring.

Which approach should you use?

- **A.** Hard-coded URLs and direct connector bindings
- **B.** Per-environment unmanaged edits
- **C.** Tenant default environment settings
- **D.** Environment variables and connection references ✅

> **Answer:** D. Environment variables and connection references

Environment variables and connection references are the strongest answer because they address the two parts of the requirement together. Environment variables exist to support ALM when a solution moves between environments and only the environment-specific values need to change, while connection references let solution-aware flows and supported app scenarios bind to a target-environment connection during import.

That combination improves repeatability and reduces manual rework during promotion across development, test, and UAT. Microsoft specifically notes that connection references are supplied during solution import so referencing flows can be turned on automatically after the import completes, which is exactly the operational behavior described in the scenario.

<sub>Set D · Q12</sub>

---

### 29. A solution includes a canvas app and several cloud flows that call external services. The team will import the solution from development into test repeatedly and wants a repeatable deployment model with minimal per-environment rework.

Which two actions should the team take? (Select TWO.)

- **A.** Build flows outside solutions
- **B.** Use connection references ✅
- **C.** Store secrets in canvas formulas
- **D.** Configure direct connections per app
- **E.** Use environment variables ✅

> **Answer:** B. Use connection references · E. Use environment variables

The team should use connection references and environment variables together. Connection references support solution-aware connections during import, and environment variables separate environment-specific values from the components that consume them, which is the standard Power Platform ALM pattern for moving solutions across environments.

Those two controls directly improve development-environment management because they let the same solution artifact move between development and downstream environments with cleaner configuration boundaries. That is much more sustainable than editing app formulas, rebuilding connections manually, or keeping flows outside solutions.

<sub>Set D · Q13</sub>

---

### 30. A developer needs to restore a backup from the Dev-A environment into a different environment for investigation. The restore must stay in the same region and must not affect live users.

Exhibit 1

Which environment should be selected as the restore target?

- **A.** QA-SBX ✅
- **B.** Default-AU
- **C.** Dev-A
- **D.** Prod-AU

> **Answer:** A. QA-SBX

QA-SBX is the best target because Microsoft allows restores into sandbox or developer environments, requires the source and target to be in the same region, and the scenario explicitly says the restore must go into a different environment without affecting live users. QA-SBX matches the same-region requirement, is nonproduction, and is not the original source environment.

The exhibit matters because the answer depends on combining multiple constraints rather than just knowing one environment type definition. Default and production are not valid restore targets here, and restoring back onto Dev-A would fail the “different environment” requirement even though the source is itself a developer environment.

<sub>Set D · Q14</sub>

---

### 31. A team uses Azure DevOps to move a managed solution from development to test and production. They want the pipeline to stop before deployment when the solution violates Microsoft best-practice rules, and they want developers to review the analysis output as part of the build process.

Which Build Tools task should they add to the validation stage?

- **A.** Import managed solution task
- **B.** WhoAmI connectivity validation step
- **C.** Export unmanaged solution task
- **D.** Checker task ✅

> **Answer:** D. Checker task

Checker task is the best fit because Microsoft Power Platform Build Tools includes a dedicated quality-check task that runs static analysis against solutions and is intended to identify problematic patterns before deployment. That aligns exactly with a CI/CD validation gate that should fail the pipeline before a downstream import occurs.

This is stronger than using a deployment task or a connectivity task because those do not evaluate solution quality. In a Build Tools-based pipeline, validation belongs in the build or quality stage, while deployment belongs later in release, so the team should use Checker to enforce the gate before moving the artifact forward.

<sub>Set D · Q15</sub>

---

### 32. A team wants every change from the development environment to be committed to source control in a format that supports readable diffs and merge review. They already export the solution in the pipeline, but the repository still receives only a single zip artifact.
Which task should be inserted before the repository staging step?

Snippet

steps:
- task: microsoft-IsvExpTools.PowerPlatform-BuildTools.tool-installer.PowerPlatformToolInstaller@2
  displayName: 'Power Platform Tool Installer'

- task: microsoft-IsvExpTools.PowerPlatform-BuildTools.export-solution.PowerPlatformExportSolution@2
  displayName: 'Power Platform Export Solution'
  inputs:
    authenticationType: PowerPlatformSPN
    PowerPlatformSPN: 'Dev'
    SolutionName: 'ContosoCore'
    SolutionOutputFile: '$(Build.ArtifactStagingDirectory)/ContosoCore.zip'
    Managed: false

- script: git add .
  displayName: 'Stage repository changes'

- **A.** Import managed solution task
- **B.** Unpack Solution ✅
- **C.** Checker analysis task
- **D.** Publish customizations step

> **Answer:** B. Unpack Solution

Unpack Solution is correct because the exported zip must be decomposed into component files before source control can track meaningful differences. Microsoft documents this as a core ALM pattern: export the unmanaged solution, extract it into component files, and then add those files to source control for team development.

That is exactly why the current pipeline produces poor repository output: it exports the solution but never transforms the zip into source-controlled files. Inserting Unpack Solution between export and git add gives the team a CI flow that supports readable reviews, merge handling, and repeatable downstream packaging.

<sub>Set D · Q16</sub>

---

### 33. A release pipeline successfully imports a managed solution into the test environment, but flows remain disconnected and environment variable values are blank after each deployment. The team wants the pipeline to stay fully automated across environments without requiring makers to reopen the solution and configure references manually.

What should you add to the import process?

- **A.** Deployment settings file ✅
- **B.** Manual post-import maker update
- **C.** Post-import publish customizations step
- **D.** Extra export solution stage

> **Answer:** A. Deployment settings file

Deployment settings file is the correct fix because Microsoft documents it as the mechanism for pre-populating connection references and environment variable values during automated solution import. Power Platform Build Tools can use that JSON file as part of the import task so environment-specific values are applied without manual intervention.

This directly addresses the incident in the stem. The import itself is succeeding, but the environment-specific configuration is missing, so the release is incomplete. A deployment settings file turns that missing manual step into repeatable CI/CD behavior and can be stored in source control as part of the ALM process.

<sub>Set D · Q17</sub>

---

### 34. A team wants developer changes captured from the development environment, stored in source control, and then promoted to test as a managed artifact. They want the sequence to follow a standard Build Tools-based ALM flow rather than manual packaging.

Steps

Import the managed solution into Test.

Export the unmanaged solution from Development.

Unpack the exported solution into source-controlled files.

Pack a managed build artifact.

What is the correct order?

- **A.** 2 → 4 → 3 → 1
- **B.** 3 → 2 → 4 → 1
- **C.** 2 → 3 → 4 → 1 ✅
- **D.** 4 → 2 → 1 → 3

> **Answer:** C. 2 → 3 → 4 → 1

The correct order is 2 → 3 → 4 → 1 because CI/CD begins by harvesting the latest customizations from the development environment as an unmanaged solution, then converting that export into component files suitable for source control. After the solution is represented in source-controlled form, the pipeline can create a managed build artifact for downstream release and import that artifact into the target environment.

This sequence also aligns with the broader Build Tools pipeline model of moving from development capture into build and then into release. It avoids manual packaging and preserves a disciplined ALM flow where source control and artifact generation happen before downstream deployment.

• 2 is first because the pipeline must first capture the current solution state from the development environment before it can create source-controlled files or build artifacts.

• 3 is second because the exported solution must be unpacked into component files before the repository can manage diffs, merges, and versioned assets effectively.

• 4 is third because packaging a managed artifact belongs after the source-controlled representation exists and the build is ready to produce a deployable release artifact.

• 1 is last because importing the managed solution is the downstream deployment step, not the source-capture or build-preparation step.

<sub>Set D · Q19</sub>

---

### 35. A release manager tries to restore a recent backup over a production environment after a bad managed solution import. The production environment does not appear as an eligible restore target in the admin center, and the team wants the fastest supported recovery path.

What should the release manager do first?

- **A.** Enable Managed Environments
- **B.** Change the target to sandbox ✅
- **C.** Recreate the environment as a default environment
- **D.** Rebind every connection reference

> **Answer:** B. Change the target to sandbox

The first step is to change the target environment to sandbox because Microsoft does not allow direct restores to production environments. The official guidance says that if you want to restore to production, you must first change the environment type to sandbox, perform the restore, and then change it back to production after the restore is complete.

This is a lifecycle and environment-type problem, not a connector-binding or governance-setting problem. The admin center behavior described in the incident is consistent with Microsoft’s documented restriction that only sandbox environments can be restored to directly.

<sub>Set D · Q35</sub>

---

### 36. A developer added a command bar action that calls a JavaScript web resource from a model-driven app solution. The release team wants the unmanaged source solution to include every required artifact before export.

Which action should you use?

- **A.** Publish all pending customizations
- **B.** Managed patch layering
- **C.** Add required components ✅
- **D.** Connection reference remap strategy

> **Answer:** C. Add required components

Add required components is the best fit because it brings the dependent artifacts that the selected component needs into the same unmanaged solution before export. For dependency management, that is the most direct way to reduce missing-component issues caused by forms, command logic, scripts, columns, or other referenced items being left outside the solution package.

Publishing customizations does not resolve packaging gaps, and connection references address runtime connection binding rather than structural solution-component dependencies. The dependency tools in Power Apps exist specifically to identify what a component uses and what uses it, which is why dependency-aware inclusion is the correct ALM action here.

<sub>Set E · Q11</sub>

---

### 37. A team keeps shared tables, columns, and global choices in one unmanaged solution. They keep the model-driven app, forms, command bar logic, and cloud flows in a second unmanaged solution, and imports into new environments often fail when the second solution arrives first.

They want to reduce deployment fragility and dependency-driven import ordering. What should they do?

- **A.** Document import order
- **B.** Use staged upgrades
- **C.** Move settings to environment variables
- **D.** Consolidate both solutions ✅

> **Answer:** D. Consolidate both solutions

Consolidate both solutions is the best answer because the issue is structural coupling between solution boundaries. Microsoft guidance explicitly warns that dependencies between solutions enforce import order and can cause deployment problems, so bringing tightly related components into one deployable solution reduces that fragility.

This does not mean every organization should always use one giant solution. It means that when one solution cannot stand on its own because it directly depends on tables, columns, or other assets in another solution, the cleaner ALM design is usually to package those coupled assets together rather than rely on a brittle sequence of imports.

<sub>Set E · Q12</sub>

---

### 38. A managed solution import fails in test with a missing dependency for a custom page. The page uses a component library that exists in development, but that library was never added to the source solution, and the team wants the smallest safe fix before the next export.

What should you do next?

- **A.** Add required components ✅
- **B.** Clear the active layer
- **C.** Reassign flow ownership
- **D.** Enable solution upgrade

> **Answer:** A. Add required components

Add required components is the best next step because the failure is caused by a referenced component that exists in development but is absent from the source solution being exported. The safest minimal remediation is to include the missing dependent component in the source unmanaged solution and then re-export the package.

This approach directly addresses the import blocker instead of treating unrelated ALM issues. Missing dependency errors are resolved by restoring or packaging the required components correctly, not by changing ownership, clearing layers, or invoking upgrade semantics that do not supply the missing artifact.

<sub>Set E · Q14</sub>

---

### 39. A release pipeline failed because a managed solution package has a missing dependency. You need the fastest repeatable remediation path in the source environment before the next export.

Steps

Re-export the managed package from the corrected unmanaged solution.

Add the missing component or use Add required components on the dependent item.

Review the missing dependency details for the failing component.

Retry the import in the target environment.

What is the correct order?

- **A.** 2 → 3 → 1 → 4
- **B.** 3 → 1 → 2 → 4
- **C.** 3 → 2 → 1 → 4 ✅
- **D.** 1 → 3 → 2 → 4

> **Answer:** C. 3 → 2 → 1 → 4

The correct remediation flow starts by identifying the exact missing dependency, then correcting the source solution, then rebuilding the deployable package, and finally validating the fix through another import attempt. That sequence keeps diagnosis ahead of remediation and remediation ahead of packaging.

In dependency-related ALM work, exporting too early or retrying too early just repeats the same failure. The source unmanaged solution must first be corrected so the next managed export includes everything required by the dependent component.

• 3 is first because you need the missing dependency details before deciding what component must be added or corrected. Without that information, the fix becomes guesswork. The error details or dependency view tell you which prerequisite is absent. That is the correct diagnostic starting point.

• 2 is second because once the missing component is known, you fix the unmanaged source solution by adding that dependency properly. This is the actual remediation step. Until the source solution is corrected, any new export will carry the same defect. That is why remediation must occur before packaging.

• 1 is third because export comes after the source solution has been corrected. Re-exporting earlier would simply produce another incomplete managed package. Packaging is a downstream ALM action, not the way you discover or resolve the dependency. It belongs after the source fix.

• 4 is last because validation in the target environment should happen only after a corrected package exists. Retrying sooner would not test a real change. Import retry is the confirmation step that proves the dependency issue has been removed. That is why it belongs at the end.

<sub>Set E · Q15</sub>

---

### 40. A release engineer is preparing a fresh target environment. They want to import the ServiceDesk App solution without a missing dependency error.

Exhibit 1

Which solution must be installed first?

- **A.** Core Data solution
- **B.** Shared UX ✅
- **C.** Routing Flow solution
- **D.** No prerequisite solution

> **Answer:** B. Shared UX

Shared UX must be installed first because the exhibit shows that ServiceDesk App uses components from both Core Data and Shared UX, while only Core Data is already present in the target. Since the target already has Core Data, the unmet prerequisite is Shared UX.

This is a classic dependency-order problem. The correct import sequence is dictated by what the dependent solution uses, not by what looks most business-critical. In the exhibit, the app package is not self-sufficient, so the missing referenced UX artifacts need to exist before the app package can import cleanly.

<sub>Set E · Q44</sub>

---

### 41. A feature solution fails to import into test because it references a shared custom connector and a table column delivered by a separate core solution. The team wants to restore the deployment quickly without redesigning the dependency model.

Problem:

The import fails because required dependent components are not present in the target environment.

Proposed solution:

Manually recreate the missing connector and column directly in the test environment instead of importing the core solution or refactoring the dependency.

Does the proposed solution meet the goal?

- **A.** Yes
- **B.** No ✅

> **Answer:** B. No

No. Manually recreating components in the target environment does not properly manage solution dependencies and weakens ALM integrity. Power Platform solutions track dependencies between components, and imports are expected to honor those relationships through the correct dependent solutions or by removing the dependency through supported design changes.

The proposed shortcut may appear to unblock the environment, but it creates drift between source and target and bypasses the tracked solution model. That makes future imports, upgrades, and troubleshooting harder rather than solving dependency management correctly.

<sub>Set F · Q5</sub>

---

### 42. A solution is imported into the test environment and a cloud flow begins failing on a Dataverse action with an error that the principal user is missing a required privilege. The flow uses a connection reference tied to an application user, and the same solution worked in development.

What is the most likely cause?

- **A.** Application user lacks role ✅
- **B.** Alternate key on target table
- **C.** Managed layer blocks privilege
- **D.** Unpublished flow trigger change

> **Answer:** A. Application user lacks role

This is most likely a Dataverse security assignment problem for the identity actually executing the operation. Dataverse access is controlled through security roles, and users or app identities need the appropriate privileges in the target environment; otherwise, privilege errors occur even if the flow and solution import themselves are otherwise valid.

The important clue is that the flow runs through a connection reference tied to an application user in test. If that application user has not been assigned the necessary Dataverse role or equivalent privileges in the target environment, the platform will reject the action with a privilege-related error regardless of whether the solution structure is correct.

<sub>Set F · Q12</sub>

---

### 43. A reviewer app lets staff read Vendor Onboarding records across the organization and create or update Review Note records that they personally own. Reviewers must not edit Vendor Onboarding records, and they must not delete either table.

Exhibit 1

Which role best fits the requirement with least privilege?

- **A.** Role A
- **B.** Role B
- **C.** Role C
- **D.** Role D ✅

> **Answer:** D. Role D

Role D is the least-privilege design that still satisfies all stated requirements. It allows organization-level read access to the primary Vendor Onboarding records while restricting Review Note create, update, and read access to the user scope, and it avoids granting delete privileges.

The key exam decision here is separating the scope of the source table from the scope of the user-authored table. Reviewers need broad visibility into onboarding records, but their note activity should stay limited to records they own, which is exactly the kind of privilege-and-access-level combination Dataverse roles are designed to express.

<sub>Set F · Q14</sub>

---

### 44. A team uses separate development and test environments for a solution that includes a canvas app, a plug-in, and connection references. They want test to validate the packaged artifact and target-environment values without making direct edits to solution components in test.

Steps

Import the managed solution into the test environment and provide target-environment values.

Build and validate the changes in the development environment.

Export the deployable solution artifact from development.

Run end-to-end validation in the test environment.

What is the correct order?

- **A.** 2 → 1 → 3 → 4
- **B.** 3 → 2 → 1 → 4
- **C.** 2 → 3 → 1 → 4 ✅
- **D.** 1 → 2 → 4 → 3

> **Answer:** C. 2 → 3 → 1 → 4

The correct ALM flow is to complete and validate changes in development first, then produce the deployable artifact, then import that artifact into the test environment, and finally run end-to-end validation there. That sequence preserves environment separation and lets test validate the packaged deployment with test-specific values instead of mixing development activity into the target environment.

The main design principle is that test should validate what will actually be deployed, not become a second customization workspace. Microsoft’s ALM guidance emphasizes separate environments and solution-based movement across them, which is exactly what this order reflects.

2 is first because the solution must be completed and validated in the development environment before any deployable package exists. Development is where the source customization work happens, not test.

3 is second because you cannot import to test until you have exported the deployable solution artifact from development. The package is the handoff between environments.

1 is third because once the artifact exists, test is the correct place to import it and apply target-environment values such as connection references or environment-variable values. That keeps the artifact consistent while allowing environment-specific configuration.

4 is last because validation belongs after import, when the solution is running in the target environment with target-specific settings. Running end-to-end checks earlier would not validate the deployed test state.

<sub>Set F · Q15</sub>

---

### 45. A managed solution named ContosoSales is imported into Test and Production. In Test, a maker changed a command bar behavior directly in the environment during a hotfix investigation, and later managed imports no longer change that behavior.

Exhibit 1

What should you do first so that the next managed update can take effect in Test? Select only one answer.

- **A.** Stage the next import as holding
- **B.** Clone the managed solution
- **C.** Remove the unmanaged active layer ✅
- **D.** Rebind the command to a connection reference

> **Answer:** C. Remove the unmanaged active layer

The exhibit shows the key issue: Test has an unmanaged active customization layer sitting above the managed ContosoSales layer. That top unmanaged layer wins at runtime, so importing a newer managed version underneath it does not change the behavior the user sees. The correct first action is to remove the active unmanaged customization so the managed layer can become effective again.

This is exactly the type of ALM problem solution layers are meant to explain. Managed upgrades can update managed layers, but they do not automatically override environment-local unmanaged customizations that sit on top. When you are diagnosing why a managed update appears to “do nothing,” checking for and removing unintended active customizations is usually the right first move.

<sub>Set F · Q17</sub>

---

### 46. A team wants to use Azure DevOps and Power Platform Build Tools to promote a solution from Dev to Test. They want source control to store the unpacked solution and the pipeline to deploy a managed artifact into Test by using deployment settings.

Steps

Import the managed solution artifact into Test.

Commit the unpacked solution files to source control.

Export the unmanaged solution from Dev and unpack it.

Pack the managed solution and publish the build artifact.

What is the correct order?

- **A.** 2 → 3 → 4 → 1
- **B.** 3 → 4 → 2 → 1
- **C.** 4 → 3 → 2 → 1
- **D.** 3 → 2 → 4 → 1 ✅

> **Answer:** D. 3 → 2 → 4 → 1

The correct pipeline flow starts with exporting the unmanaged solution from the development environment and unpacking it so that its files can be versioned properly. After that, those unpacked artifacts belong in source control, which becomes the authoritative build source. From there, the build process packs a managed artifact and publishes it, and the release step imports that managed artifact into Test.

This sequence reflects the standard source-driven ALM model for Power Platform Build Tools. Development stays unmanaged in Dev, source control tracks the unpacked solution, the pipeline produces a managed deployable package, and downstream environments receive managed imports. That pattern supports repeatability, traceability, and environment-specific deployment settings.

• 3 is first because the solution must be exported from Dev and unpacked before source control can store meaningful files for the pipeline.

• 2 is second because the unpacked solution files should be committed before the build stage creates the managed artifact.

• 4 is third because the managed package is built from the source-controlled solution content, not from an ad hoc downstream environment export.

• 1 is last because deployment into Test happens after the managed artifact exists and is ready for release use.

<sub>Set F · Q18</sub>

---

### 47. A canvas app calculates quote totals in a label. The team wants the logic to stay inside one formula, avoid repeated subexpressions, and avoid introducing extra global state.

Snippet

With(
    {
        subtotal: Sum(colLines, Quantity * UnitPrice),
        discount: Coalesce(LookUp(colPromo, Code = txtPromo.Text, Amount), 0),
        shipping: If(tglExpress.Value, 25, 0)
    },
    Max(subtotal - discount + shipping, 0)
)
Which approach is this formula using to keep the logic complex but maintainable? Select only one answer.

- **A.** Persistent reusable app-scoped variable values
- **B.** Named intermediate values ✅
- **C.** Parallel connector call pattern
- **D.** Transactional Patch update scope

> **Answer:** B. Named intermediate values

This formula uses With to define named values that exist only within the scope of the current expression. That makes the formula easier to read and maintain because repeated or logically distinct calculations such as subtotal, discount, and shipping can be referenced clearly without turning them into app-level variables. For complex Power Fx, this is often the cleanest way to structure logic that still belongs in a single property formula.

The important distinction is scope and intent. With is not persisting data, not batching connector calls, and not creating transaction semantics. It is organizing formula logic by introducing local named values, which is especially useful when you want a dense formula to remain understandable and avoid duplicating expensive or messy expressions.

<sub>Set F · Q19</sub>

---

### 48. A team moves the same solution package through development, test, and production. The API host name, queue name, and feature flag differ by environment, but the app and flow definitions must remain unchanged between deployments.

Configuration

ApiBaseUrl: hard-coded in canvas app formula
QueueName: hard-coded in cloud flow action
FeatureToggle: hard-coded in custom page script
DeploymentModel: same managed solution to all environments
Which design should you use?

- **A.** Environment variables ✅
- **B.** Manual post-import edits
- **C.** Connection references everywhere
- **D.** Personal maker connections

> **Answer:** A. Environment variables

Environment variables are designed for exactly this ALM scenario: keep the solution package stable while allowing environment-specific values to change between environments. Microsoft documents them as the mechanism for moving the same application between environments when only key external references or configuration values differ.

This requirement is broader than connector binding alone because it includes arbitrary configuration such as an API base URL, queue name, and feature flag. Connection references help with connector connections, but they do not replace environment variables for general configurable values used across apps, flows, and solution-aware components.

<sub>Set F · Q51</sub>

---
