# Extend the Platform  

_Exam weight 30–35% · 189 questions across all sets._

---

### 1. A cloud flow calls an external HTTP endpoint that occasionally returns 429 and 502 responses. The team wants the action to recover automatically from temporary failures without adding a separate error branch for every call.

Which control should you configure?

- **A.** Scope container
- **B.** Exponential retry policy ✅
- **C.** Failed terminate action
- **D.** Configure run after

> **Answer:** B. Exponential retry policy

An exponential retry policy is the best fit for transient HTTP failures because Power Automate lets you configure retry policy at the action level, and Microsoft recommends exponential intervals for temporary network or service problems. That directly addresses intermittent 429 and 5xx-style failures without forcing you to build custom branching around every single connector call.

This is also the most targeted control for the requirement. Configure run after handles what happens after an action ends with a particular status, but it does not itself retry the failed action. Scopes help organize logic, and Terminate stops the run, but neither is the primary recovery mechanism for transient faults.

<sub>Set A · Q3</sub>

---

### 2. A developer wants a parameter in the custom connector designer to show a selectable list that is populated by another operation in the same connector.

Snippet

{
  "name": "projectId",
  "in": "query",
  "type": "string",
  "x-ms-dynamic-values": {
    "operationId": "ListProjects",
    "value-path": "id",
    "value-title": "displayName",
    "value-collection": "value",
    "parameters": {}
  }
}
What does this definition enable?

- **A.** Dynamic dropdown options ✅
- **B.** OAuth token exchange
- **C.** Webhook callback registration
- **D.** Automatic retry policy

> **Answer:** A. Dynamic dropdown options

This definition enables dynamic dropdown options for the parameter. Microsoft documents x-ms-dynamic-values as the extension used to provide a list of options for a user to select as input to an operation, and it uses properties such as operationId, parameters, value-collection, value-title, and value-path to map the source response into selectable values.

That means the connector can call ListProjects and surface user-friendly names while still binding the selected underlying identifier to projectId. This is a strong OpenAPI design pattern when an existing REST API already exposes a lookup endpoint that can drive better designer usability.

<sub>Set A · Q4</sub>

---

### 3. A developer wants an Azure Function action to be callable through a custom connector after deployment to Azure. The function should require a function-scoped key rather than allowing anonymous access.

Snippet

[Function("RepairEstimate")]
[OpenApiOperation(operationId: "RepairEstimate")]
[OpenApiSecurity("function_key", SecuritySchemeType.ApiKey, Name = "code", In = OpenApiSecurityLocationType.Query)]
public async Task<HttpResponseData> Run(
    [HttpTrigger(AuthorizationLevel.Function, "post")] HttpRequestData req)
{
    // implementation
}
What must a caller provide when invoking this operation after the function is published to Azure?

- **A.** Microsoft Entra access token
- **B.** Client certificate thumbprint
- **C.** Dataverse connection reference
- **D.** Function key ✅

> **Answer:** D. Function key

Function key is correct because Microsoft documents that AuthorizationLevel.Function requires a function-specific key to access the endpoint. Microsoft also documents that access keys can be supplied in the code query-string parameter or in the x-functions-key header. The snippet reinforces that model by declaring OpenAPI security with the code parameter in the query string.

This is a common design for Azure Function-backed APIs used by custom connectors when shared key authentication is acceptable. The key point is that the function is not anonymous, so a successful call must include the function key after publication to Azure.

<sub>Set A · Q12</sub>

---

### 4. A developer successfully imports an Azure Function-backed API into a custom connector and creates a connection. During testing, the action runs, but the connector exposes no usable output fields and downstream formulas cannot read response properties. The function uses an HTTP trigger, but it does not build an explicit HTTP response body.

What is the best fix?

- **A.** Add Azure Queue output binding
- **B.** Return JSON response ✅
- **C.** Enable custom connector policy
- **D.** Move logic to Dataverse plug-in

> **Answer:** B. Return JSON response

Return JSON response is the best fix because Microsoft documents that the default return value for an HTTP-triggered function in Functions 2.x and higher is HTTP 204 No Content with an empty body unless you modify the HTTP response. If the connector action needs output fields that apps and flows can consume, the function should return an explicit response body rather than relying on the default empty response.

That makes this a function-design issue, not a connector-policy issue. A custom connector can only surface meaningful outputs when the backend API returns a meaningful response contract and payload. For connector actions that should return values to Power Apps or Power Automate, explicit JSON output is the right corrective change.

<sub>Set A · Q17</sub>

---

### 5. A team has an Update plug-in on the account table. The plug-in must normalize the incoming name and telephone1 values before Dataverse writes the row, and the changes must stay in the same transaction as the save request.

Which stage should you choose?

- **A.** PreValidation stage
- **B.** PostOperation stage
- **C.** PreOperation stage ✅
- **D.** Asynchronous PostOperation step

> **Answer:** C. PreOperation stage

PreOperation stage is the correct answer because Microsoft states that it occurs before the main system operation and within the database transaction. Microsoft also explicitly says that if you want to change any values for an entity included in the message, you should do it in PreOperation. That maps directly to normalizing incoming column values before the row is written.

This stage is the best balance for the scenario because the changes are applied before persistence while still remaining part of the same save request. PreValidation is better for early validation and rejection, but PreOperation is the stage Microsoft points to when you need to mutate the incoming entity data that Dataverse is about to process.

<sub>Set A · Q18</sub>

---

### 6. A PreOperation synchronous plug-in calls an external fraud-scoring API during order updates. The fraud score is helpful, but the order save does not need to wait for the score to commit, and users are reporting intermittent save delays when the external service is slow.

Which approach best optimizes performance while still meeting the requirement?

- **A.** Asynchronous plug-in ✅
- **B.** Synchronous PreValidation step
- **C.** RetrieveMultiple plug-in step
- **D.** ExecuteMultipleRequest batching

> **Answer:** A. Asynchronous plug-in

An asynchronous plug-in is the best answer because the transaction does not depend on the fraud score being available before commit. Microsoft states that asynchronous execution runs independently of the main Dataverse operation and improves overall performance and scalability for long-running work that does not need to block the user action.

This is especially important when the logic calls an external service. Microsoft’s guidance for external web service access and plug-in design emphasizes minimizing long waits in plug-ins, and synchronous steps directly affect end-user perceived performance because the save operation must wait for completion.

<sub>Set A · Q19</sub>

---

### 7. A team imports an OpenAPI definition for an existing REST API into a custom connector. One action appears in the definition file, but it doesn’t show in the designer as an output-producing action. The operation has only a default response and no 200 or 201 response schema.

What is the most likely cause?

- **A.** Invalid base URL scheme
- **B.** Duplicate response headers
- **C.** Missing parameter display title
- **D.** No 200 schema ✅

> **Answer:** D. No 200 schema

The most likely cause is the missing successful response schema. Microsoft’s validator guidance says an operation should define an output schema on the 200 or 201 response code, or in x-ms-notification-content for a webhook, for the operation to be visible in the designer as expected. It also states that an operation should have at least one successful response definition.

Because the operation has only a default response and no 200 or 201 schema, the definition doesn’t provide the successful output contract the designer expects. This is a common issue when a raw API definition technically parses but still lacks the schema details needed for a strong connector experience.

<sub>Set A · Q20</sub>

---

### 8. A team wants the Log_Error action to run only when the preceding Call_API action fails or times out. The current configuration is causing the logging path to miss real failures.

Configuration

"Log_Error": {
  "type": "Compose",
  "inputs": "API failure",
  "runAfter": {
    "Call_API": [
      "Succeeded",
      "Skipped"
    ]
  }
}
Which runAfter configuration should replace the current one?

- **A.** ["Succeeded"]
- **B.** ["Failed","TimedOut"] ✅
- **C.** ["Skipped"]
- **D.** ["Succeeded","Skipped","TimedOut"]

> **Answer:** B. ["Failed","TimedOut"]

["Failed","TimedOut"] is correct because Microsoft documents that Run After can be configured based on whether the preceding action succeeded, failed, timed out, or was skipped. If the error branch should run only for true error outcomes from the API call, the relevant statuses are Failed and TimedOut.

The current configuration is wrong because it fires on success and skip states instead of the two statuses the team actually cares about. Replacing it with Failed and TimedOut aligns the branch with real error handling rather than success-path execution.

<sub>Set A · Q24</sub>

---

### 9. A synchronous plug-in sets RegardingObjectId on an activity record during the Update pipeline. The save succeeds, but users later see (No Name) for the lookup display value when the activity is retrieved.

What is the best stage-based fix?

- **A.** Add a post image alias
- **B.** Increase execution order
- **C.** Switch to async PostOperation
- **D.** Move the assignment to PreValidation ✅

> **Answer:** D. Move the assignment to PreValidation

Move the assignment to PreValidation is the best answer because Microsoft documents this as a known issue for ActivityPointer.RegardingObjectId. When that lookup is set in the PreOperation stage, Dataverse does not add the name value, and the retrieved activity can show (No Name). Microsoft lists moving the lookup assignment to PreValidation as one of the documented workarounds.

This is a good example of why the execution pipeline stage matters beyond simple timing. Two stages can both appear to be “before save,” but the resulting behavior can still differ materially for a specific platform behavior. In this case, the stage choice directly affects whether Dataverse populates the display name as expected.

<sub>Set A · Q31</sub>

---

### 10. An Azure Function already has a managed identity enabled and can acquire a Microsoft Entra token in Azure. However, every Dataverse Web API call returns 403 Forbidden. The team wants app-only access with least privilege and no user sign-in.

What should an administrator do in Power Platform first?

- **A.** Create app user with roles ✅
- **B.** Add delegated API permissions
- **C.** Share a maker connection
- **D.** Store the Function key in Key Vault

> **Answer:** A. Create app user with roles

The first Power Platform action is to create an application user for the managed identity in the target environment and assign the required Dataverse security roles. Microsoft’s admin guidance explicitly states that when creating an application user, you can enter an Azure Managed Identity Application ID, choose the business unit, and assign security roles. Without that application user and role assignment, the identity can authenticate but still lack Dataverse authorization.

This question separates authentication from authorization. The Function’s managed identity can successfully obtain a token, but Dataverse access still depends on an application user and Dataverse security roles in the environment. That is why a 403 in this scenario points to Dataverse authorization configuration rather than Function host settings or delegated user permissions.

<sub>Set A · Q32</sub>

---

### 11. A non-interactive Dataverse data integration app uses the Web API to process large record volumes. The team wants the retry policy to maximize throughput without ignoring Microsoft guidance for service protection limits.

Which two decisions should be included in the implementation? (Select TWO.)

- **A.** Wait for Retry-After ✅
- **B.** Resubmit immediately on 429
- **C.** Gradually raise request rate ✅
- **D.** Show raw limit text
- **E.** Assume batch bypasses limits

> **Answer:** A. Wait for Retry-After · C. Gradually raise request rate

The correct answers are to wait for Retry-After and to gradually raise the request rate. Microsoft says non-interactive clients should wait for the duration to pass before retrying, and it also recommends starting with a lower number of requests and gradually increasing until service protection limits begin to appear. That approach keeps the retry-after period lower and improves total throughput.

This combination reflects the practical design of a resilient bulk client. The app should treat service protection responses as transient conditions, honor the platform’s wait instruction, and tune throughput progressively rather than spiking traffic aggressively. Microsoft also notes that batch operations are not a way to bypass entitlement limits, so the retry strategy still needs to be deliberate even when batching is used.

<sub>Set A · Q33</sub>

---

### 12. A plug-in must reject an invalid update as early as possible. The design should cancel before the main operation and avoid the heavier rollback cost of cancelling later in the transaction.

Which stage should you register?

- **A.** PreOperation stage
- **B.** PreValidation stage ✅
- **C.** Synchronous PostOperation step
- **D.** Asynchronous PostOperation step

> **Answer:** B. PreValidation stage

PreValidation stage is the best answer because Microsoft states that, for the initial operation, this stage occurs before the main system operation and provides an opportunity to cancel the operation before the database transaction. That makes it the preferred stage when the goal is to stop invalid work as early as possible.

Microsoft also recommends throwing InvalidPluginExecutionException preferably in the PreValidation stage when you need to cancel an operation. That guidance exists because cancelling later, while inside the transaction, causes rollback overhead and is less efficient than rejecting the request up front.

<sub>Set A · Q37</sub>

---

### 13. A developer is tracing a plug-in and wants the branch that runs in the PostOperation stage after the main operation has completed.

Snippet

if (context.Stage == 10)
{
    tracing.Trace("Branch A");
}
else if (context.Stage == 20)
{
    tracing.Trace("Branch B");
}
else if (context.Stage == 40)
{
    tracing.Trace("Branch C");
}
Which condition identifies the supported PostOperation stage?

- **A.** context.Stage == 40 ✅
- **B.** context.Stage == 20
- **C.** context.Stage == 10
- **D.** context.Stage == 50

> **Answer:** A. context.Stage == 40

context.Stage == 40 is correct because Microsoft documents that valid stage values include 10 for PreValidation, 20 for PreOperation, and 40 for PostOperation. That means the branch checking for 40 is the one that corresponds to the supported PostOperation stage.

This also aligns with Microsoft’s message-processing guidance: before the main operation, plug-ins work with InputParameters, and after the main operation, in PostOperation, OutputParameters contain the response results. So the branch associated with 40 is the branch that lines up with PostOperation behavior after the core operation has completed.

<sub>Set A · Q41</sub>

---

### 14. You are authoring an OpenAPI definition for an existing REST API that will be imported as a custom connector. A path parameter named customerId must appear in the designer with a clear user-facing title such as Customer ID.

Which property should you add?

- **A.** summary
- **B.** x-ms-summary ✅
- **C.** description
- **D.** x-ms-visibility

> **Answer:** B. x-ms-summary

x-ms-summary is the correct property because Microsoft documents it as the title for an entity and says it applies to parameters and response schema. That is the extension used to give a parameter a user-friendly display title in the connector experience.

By contrast, summary applies to operations, not parameters. description gives more detailed explanatory text, and x-ms-visibility controls whether an operation or parameter is shown as important, advanced, or internal. The design requirement here is specifically about the parameter’s display title, so x-ms-summary is the best fit.

<sub>Set A · Q43</sub>

---

### 15. A developer is refining an OpenAPI definition for an existing REST API before importing it as a custom connector. The goal is to improve how operations and parameters appear in the designer without changing the backend API behavior.

Which two additions best support that goal? (Select TWO.)

- **A.** operationId
- **B.** summary ✅
- **C.** x-ms-trigger
- **D.** x-ms-summary ✅
- **E.** x-ms-notification-url

> **Answer:** B. summary · D. x-ms-summary

summary and x-ms-summary are the best pair because Microsoft documents summary as the title for an operation and x-ms-summary as the title for a parameter or response schema entity. Together, they improve how the connector is presented to makers without changing the underlying API contract.

This is exactly the kind of refinement a developer makes when building an OpenAPI definition for connector usability rather than transport behavior. The REST API can stay functionally the same while the connector becomes clearer and more approachable in the designer.

<sub>Set A · Q45</sub>

---

### 16. A team reviews a plug-in that intermittently shows inconsistent behavior under load. They suspect the implementation pattern is contributing to both concurrency risk and slower execution.

Snippet

public class AccountPlugin : IPlugin
{
    private IOrganizationService service;
    private IPluginExecutionContext context;

    public void Execute(IServiceProvider serviceProvider)
    {
        context = (IPluginExecutionContext)serviceProvider.GetService(typeof(IPluginExecutionContext));
        var factory = (IOrganizationServiceFactory)serviceProvider.GetService(typeof(IOrganizationServiceFactory));
        service = factory.CreateOrganizationService(context.UserId);

        if (context.MessageName == "Update")
        {
            var task = new Entity("task");
            task["subject"] = "Follow-up";
            service.Create(task);
        }
    }
}
Which change should you make first?

- **A.** Stateless plug-in class ✅
- **B.** Static cached service factory
- **C.** Parallel task creation
- **D.** PostOperation RetrieveMultiple step

> **Answer:** A. Stateless plug-in class

The first change should be to make the plug-in class stateless. Microsoft states that classes implementing IPlugin should not use member fields or properties to store per-invocation state, because the platform caches plug-in instances and can reuse them across executions, which creates thread-safety and data-consistency risks.

In this snippet, both the execution context and organization service are stored in instance fields, which is exactly the pattern Microsoft warns against. Keeping state local to the Execute method is the documented way to avoid concurrency bugs and reduce the chance of unstable runtime behavior under load.

<sub>Set A · Q46</sub>

---

### 17. A developer is using an Azure Function managed identity to call Dataverse through ServiceClient. The code compiles, but token acquisition fails for app-only authentication.

Snippet

var credential = new ManagedIdentityCredential();

var service = new ServiceClient(
    new Uri(dataverseUrl),
    async (instanceUri) =>
    {
        var token = await credential.GetTokenAsync(
            new TokenRequestContext(new[] { $"{instanceUri}/user_impersonation" }));
        return token.Token;
    },
    true,
    logger);
What should you change?

- **A.** Use CrmServiceClient with ADAL
- **B.** Add /api/data/v9.2 to the scope
- **C.** Switch to InteractiveBrowserCredential
- **D.** Use $"{instanceUri}/.default" ✅

> **Answer:** D. Use $"{instanceUri}/.default"

The required change is to use the /.default scope. Microsoft’s Dataverse OAuth guidance states that for confidential-client scenarios, the correct scope is <environment-url>/.default, while user_impersonation is for public-client delegated flows. A managed identity in an Azure Function is an app-only workload, so /.default is the correct scope format.

The ServiceClient pattern itself is valid because Microsoft documents a constructor overload where the caller manages authentication and supplies a function that returns the access token on demand. In this snippet, the problem is not ServiceClient; it is the delegated scope being used for an app-only managed-identity call.

<sub>Set A · Q47</sub>

---

### 18. Operations reviews Dataverse plug-in metrics after users report slow grids and delayed form loads. The team wants to redesign the single step most likely to improve interactive responsiveness first.

Exhibit 1

Which step should they redesign first?

- **A.** ContactGridFilter ✅
- **B.** AccountScore sync step
- **C.** CaseAudit async step
- **D.** LeadValidate create step

> **Answer:** A. ContactGridFilter

ContactGridFilter is the best first redesign target because it combines the highest-risk characteristics for user-facing slowness: RetrieveMultiple, synchronous execution, long runtime, and an external service call. Microsoft specifically warns that synchronous plug-ins on Retrieve and RetrieveMultiple can cause unresponsive model-driven apps, slow client interactions, and browser issues.

The other steps are less urgent for interactive responsiveness. AccountScore and LeadValidate are synchronous but relatively fast, while CaseAudit runs asynchronously and therefore does not directly block the user’s save or load experience in the same way. That makes A the most impactful first optimization choice from the exhibit.

<sub>Set A · Q48</sub>

---

### 19. A developer is exposing a serverless calculation API to Power Apps by using a custom connector. The connector must invoke the operation on demand by sending an HTTP request.

Which trigger should the Azure Function use?

- **A.** HTTP trigger ✅
- **B.** Storage queue trigger
- **C.** Timer schedule trigger
- **D.** Azure Service Bus trigger

> **Answer:** A. HTTP trigger

HTTP trigger is the best fit because Azure Functions uses the HTTP trigger for functions that are invoked with HTTP requests, which is exactly the interaction model a custom connector wraps. Microsoft describes custom connectors as wrappers around REST or SOAP APIs, and the HTTP trigger is the Azure Functions trigger designed to expose serverless APIs over HTTP.

The other triggers are event-driven or scheduled patterns rather than request/response API endpoints. For a custom connector action that must be called from Power Apps or Power Automate like a normal API operation, the function should be built as an HTTP endpoint.

<sub>Set A · Q51</sub>

---

### 20. A developer is starting from a new C# Azure Functions project and wants to surface the API through a Power Platform custom connector with minimal manual definition work. The plan is to generate OpenAPI metadata from the function and then use that definition in the connector.

Steps

Publish the function app to Azure

Install the Azure Functions OpenAPI extension

Add an HTTP trigger endpoint with OpenAPI definitions

Download or import the OpenAPI definition into the custom connector

What is the correct order?

- **A.** 3 → 2 → 1 → 4
- **B.** 1 → 2 → 3 → 4
- **C.** 2 → 3 → 1 → 4 ✅
- **D.** 2 → 1 → 4 → 3

> **Answer:** C. 2 → 3 → 1 → 4

The correct order is 2 → 3 → 1 → 4. Microsoft’s Azure Functions OpenAPI guidance shows installing the OpenAPI extension first, then adding an HTTP trigger endpoint that includes OpenAPI definitions, then publishing the function app to Azure, and then downloading the OpenAPI definition file for downstream use. Microsoft’s custom connector guidance then uses that OpenAPI file to create the connector.

This order matters because the connector import depends on the API definition, and the API definition depends on the function being built with the OpenAPI extension and annotated endpoint metadata. Publishing before the function has the proper OpenAPI surface leaves nothing useful to import into the connector.

• 2 is first because the OpenAPI extension must be installed before the function project can expose discoverable OpenAPI metadata from the endpoint.

• 3 is second because the HTTP trigger endpoint and its OpenAPI definitions are the API surface the connector will later describe and import.

• 1 is third because publishing happens after the function endpoint has been implemented and documented.

• 4 is last because the custom connector uses the resulting OpenAPI definition file after the API has been prepared and published.

<sub>Set A · Q53</sub>

---

### 21. A team is building an Azure Function-backed API for use in Power Apps and Power Automate. They want the operation names, request bodies, and response shapes to be discoverable from the function itself so the custom connector can be created with minimal manual definition work.

Which development approach should they choose?

- **A.** Storage queue output binding
- **B.** API Management named value configuration
- **C.** Azure Functions OpenAPI extension ✅
- **D.** Dataverse custom API

> **Answer:** C. Azure Functions OpenAPI extension

Azure Functions OpenAPI extension is the best answer because Microsoft documents that you can install the OpenAPI extension, add an HTTP trigger endpoint that includes OpenAPI definitions, and then download the OpenAPI definition file. Microsoft also documents that custom connectors can be created from an OpenAPI definition, which describes the API’s operations and data structures.

That makes this the cleanest development approach when the goal is to make the function app easier to surface as a custom connector with less manual re-entry of actions, parameters, and responses. It keeps the API description aligned with the function implementation and supports a connector-creation flow built around OpenAPI import.

<sub>Set A · Q54</sub>

---

### 22. A synchronous Update request has plug-in steps registered in each available pipeline stage. The developer wants to reason about the order in which the request moves through the pipeline before the response is returned.

Steps

PostOperation step runs

PreValidation step runs

Main Dataverse operation runs

PreOperation step runs

What is the correct order?

- **A.** 4 → 2 → 3 → 1
- **B.** 2 → 4 → 3 → 1 ✅
- **C.** 2 → 3 → 4 → 1
- **D.** 4 → 3 → 2 → 1

> **Answer:** B. 2 → 4 → 3 → 1

The correct order is 2 → 4 → 3 → 1. Microsoft documents that PreValidation occurs before the main system operation, PreOperation occurs before the main system operation and within the database transaction, and PostOperation occurs after the main system operation. That means the pipeline must pass through PreValidation first, then PreOperation, then the core Dataverse operation, and finally PostOperation.

This order matters because each stage has a different purpose. Early rejection is suited to PreValidation, in-transaction entity mutation is suited to PreOperation, and response shaping or post-core logic happens in PostOperation. Understanding the sequence helps a developer place logic in the stage that matches its intent instead of forcing everything into one plug-in step.

• 2 is first because PreValidation is the earliest stage for the initial operation and occurs before the main system operation.

• 4 is second because PreOperation occurs after PreValidation but still before the main Dataverse operation, and Microsoft recommends it when you need to change entity values in the request.

• 3 is third because the Dataverse core operation sits between the pre-stages and PostOperation. Microsoft describes the pre/post naming relative to that main operation.

• 1 is last because PostOperation occurs after the main system operation.

<sub>Set A · Q58</sub>

---

### 23. A team wants several Azure Functions to share the same identity and keep the same Dataverse access even if one Function App is deleted and recreated. They want to avoid secrets.

Which identity type should they use?

- **A.** Entra app with client secret
- **B.** System-assigned identity
- **C.** User-assigned identity ✅
- **D.** Connection string authentication

> **Answer:** C. User-assigned identity

A user-assigned managed identity is the best fit because it is a standalone Azure resource that can be assigned to multiple Azure resources. Microsoft’s Azure Functions and App Service guidance states that a user-assigned identity is managed separately from the app and can be reused across multiple resources, which matches the requirement to preserve the same identity across recreated Function Apps.

A system-assigned identity would not meet the stability requirement here because it is tied to the individual app instance and is deleted when that app is deleted. Since the goal is shared, reusable, secretless authentication to Dataverse from Azure Functions, user-assigned identity is the more durable design.

<sub>Set A · Q59</sub>

---

### 24. An Azure Function has two user-assigned managed identities attached. The team must authenticate to Dataverse by using the identity that already has a Dataverse application user and security role. They want deterministic production authentication.

Configuration

IdentityType: UserAssigned
CredentialClass: DefaultAzureCredential
ManagedIdentityClientId:
DataverseUrl: https://contoso.crm.dynamics.com
ServiceClientMode: AccessTokenCallback
Environment: Production
What should you change first?

- **A.** Use ManagedIdentityCredential with client ID ✅
- **B.** Change scope to delegated user_impersonation permissions
- **C.** Add a Dataverse connection reference
- **D.** Switch to system-assigned identity

> **Answer:** A. Use ManagedIdentityCredential with client ID

The best first change is to use ManagedIdentityCredential and specify the client ID of the intended user-assigned managed identity. Microsoft’s Azure-hosted .NET guidance says that when an app runs in Azure, you should use ManagedIdentityCredential, and for user-assigned identities you can configure the specific client ID, resource ID, or object ID. That directly matches a Function App with multiple user-assigned identities where one exact identity must be selected.

This also improves determinism in production. Microsoft’s Azure Identity guidance says that once an app is deployed to Azure, you should understand its authentication requirements and prefer a specific credential such as ManagedIdentityCredential rather than relying on the broader DefaultAzureCredential chain. That makes A the strongest production-focused fix.

<sub>Set A · Q60</sub>

---

### 25. A team is building a .NET worker that performs large Dataverse updates through the Organization service. The solution must handle service protection API limit errors with minimal custom retry code and should follow Microsoft’s preferred client approach.

Which implementation approach is the best fit?

- **A.** OrganizationServiceProxy
- **B.** Raw SOAP client wrapper
- **C.** ServiceClient ✅
- **D.** Browser JavaScript loop

> **Answer:** C. ServiceClient

ServiceClient is the best answer because Microsoft specifically recommends using PowerPlatform.Dataverse.Client.ServiceClient or CrmServiceClient for .NET SDK-based applications that need to manage service protection API limit errors. Microsoft also states that these clients automatically pause and resend the request after the Retry-After duration.

This makes ServiceClient the strongest implementation choice when the requirement is to implement retry handling with minimal custom code. By contrast, Microsoft says OrganizationServiceProxy is deprecated and recommends replacing it with ServiceClient or CrmServiceClient, so choosing the older proxy would move the design away from the documented retry-handling approach.

<sub>Set A · Q61</sub>

---

### 26. A cloud flow uses a Try scope and a Catch scope. The Catch scope must email support with a link to the current run and identify which first-level actions inside Try failed.

Which two expressions or features should you use? (Select TWO.)

- **A.** result('Try') ✅
- **B.** workflow() ✅
- **C.** outputs('Try')
- **D.** Fixed retry policy
- **E.** actions('Try')

> **Answer:** A. result('Try') · B. workflow()

result('Try') is correct because Microsoft documents that result() returns an array of results from the top-level actions inside a scoped action such as a Scope. That makes it the right function when the Catch scope needs to inspect which first-level actions inside the Try scope failed and extract their status or output details.

workflow() is also correct because Microsoft documents that it returns metadata about the current workflow run, including run information and tags that can be used to build a run URL or include contextual details in notifications. That is exactly what the Catch email needs when support should be able to jump directly into the failing run.

<sub>Set A · Q63</sub>

---

### 27. A finance flow performs several update actions that must stay grouped for readability and troubleshooting. If that main processing group fails or times out, a separate error-handling group must run, and the design should remain easy to extend later with a cleanup section.

Which implementation approach should you choose?

- **A.** Fixed retries on actions
- **B.** Child flow with response
- **C.** Parallel branch notifications
- **D.** Scopes with Configure run after ✅

> **Answer:** D. Scopes with Configure run after

Scopes with Configure run after are the best design because Microsoft explicitly recommends scopes for grouping related actions and for building try/catch/finally-style patterns. A main processing scope can represent the Try block, an error-handling scope can be configured to run after failure or timeout, and a later cleanup scope can be added with its own run-after settings.

This approach also matches the operational goals in the stem. Scopes improve organization, expose a single status for the grouped block, and work directly with run-after conditions to drive alternative paths such as catch or finally behavior. That makes them more maintainable than scattering the same logic across unrelated actions or branches.

<sub>Set A · Q64</sub>

---

### 28. An Update plug-in runs synchronously and calls an external scoring service on every account change. Users experience slow saves, and the business confirms that the score does not have to be available before the record update succeeds.

Which two changes should you make? (Select TWO.)

- **A.** RetrieveMultiple registration
- **B.** Async plug-in mode ✅
- **C.** Parallel HTTP tasks in Execute
- **D.** Filtering attributes ✅
- **E.** ExecuteTransactionRequest batching

> **Answer:** B. Async plug-in mode · D. Filtering attributes

The best pair is Async plug-in mode and Filtering attributes. Making the step asynchronous removes the noncritical scoring call from the interactive save path, and filtering attributes ensures the plug-in runs only when the relevant account columns are included in the update request.

These two changes attack both major sources of latency in the scenario: unnecessary executions and unnecessary synchronous waiting. Microsoft guidance supports both patterns as core plug-in performance practices when logic is not required to block the transaction and when Update steps should run only for specific columns.

<sub>Set A · Q65</sub>

---

### 29. A cloud flow has a Try scope and a Catch scope. When the main work fails, the Catch scope logs the error and sends an email successfully, so the overall run now appears as Succeeded in monitoring dashboards even though the business transaction failed.

What is the best fix?

- **A.** Add Terminate with Failed ✅
- **B.** Increase retry count
- **C.** Use secure outputs
- **D.** Move logging to parallel branch

> **Answer:** A. Add Terminate with Failed

Add Terminate with Failed is the best fix because Microsoft documents that the Terminate action stops the run and can return a specific final status, including Failed. When a Catch path successfully handles the logging and notification work, the run can otherwise appear successful unless you explicitly end the workflow with the intended failed status.

This is exactly the right use of Terminate in an error-handling pattern. The business transaction failed, and the flow’s final status should reflect that for monitoring, resubmission decisions, and operational reporting. Logging the error is useful, but it does not automatically preserve the failed run state.

<sub>Set A · Q66</sub>

---

### 30. A team receives an existing REST API specification from an external vendor. The file is OpenAPI 3.0, and the team wants to import it into Power Apps as a custom connector with minimal redesign effort. The implementation approach must stay aligned to the current connector import requirements.

Which approach should the team use?

- **A.** Import the OpenAPI 3.0 file
- **B.** Rebuild the connector from blank
- **C.** Convert the definition to OpenAPI 2.0 ✅
- **D.** Replace it with a SOAP description

> **Answer:** C. Convert the definition to OpenAPI 2.0

The team should convert the definition to OpenAPI 2.0 before import. Microsoft’s current custom connector documentation says the OpenAPI definition must be in OpenAPI 2.0 format, formerly Swagger, and explicitly says OpenAPI 3.0 definitions aren’t supported for this import path.

That makes conversion the best implementation approach when the goal is to preserve the existing REST API description while still using the import workflow. Rebuilding from blank is possible, but it adds unnecessary manual effort when the source API already has a machine-readable contract.

<sub>Set A · Q68</sub>

---

### 31. A team is deploying an Azure Function that will create Dataverse rows with app-only permissions. They want secretless authentication in Azure and do not want to rely on interactive sign-in or maker-owned connections.

Which two actions are required? (Select TWO.)

- **A.** Configure delegated user_impersonation scope
- **B.** Enable the Function managed identity ✅
- **C.** Store a Dataverse client secret in Function App settings
- **D.** Create a Dataverse app user with roles ✅
- **E.** Add a connection reference to the solution

> **Answer:** B. Enable the Function managed identity · D. Create a Dataverse app user with roles

The two required actions are to enable a managed identity on the Function App and to create a Dataverse application user for that identity with appropriate security roles. Microsoft’s Azure Functions guidance explains how to add a managed identity to the Function App, while Power Platform admin guidance explains that application users can be created for Azure Managed Identity Application IDs and then assigned Dataverse security roles. Together, those steps provide the Azure-side identity and the Dataverse-side authorization.

This is the core secretless app-to-app pattern for Azure Functions calling Dataverse. The Function needs a managed identity so Azure can issue tokens without stored secrets, and Dataverse needs an application user plus roles so the identity can perform the required operations in the environment.

<sub>Set A · Q70</sub>

---

### 32. A synchronous Update plug-in recalculates account risk data. Users report slow saves even when they change unrelated columns such as phone number.

Which registration change should you make first?

- **A.** Filtering attributes ✅
- **B.** PreValidation update step registration
- **C.** PostOperation synchronous update step
- **D.** Secure and unsecure configuration

> **Answer:** A. Filtering attributes

Filtering attributes are the best first optimization because an Update step without filtering attributes can execute for every update request, even when the changed column is irrelevant to the plug-in logic. Microsoft explicitly recommends including filtering attributes so update plug-ins run only when the relevant columns are present in the request payload.

This is a higher-value first change than moving stages or adjusting configuration because it directly reduces unnecessary executions. Microsoft also notes that synchronous plug-ins add time to the operation and that plug-ins should run only when necessary and complete as quickly as possible.

<sub>Set A · Q71</sub>

---

### 33. A custom integration uses the Dataverse Web API and occasionally receives HTTP 429 responses during bulk processing. The retry policy must use the platform-provided wait duration instead of a guessed delay.

Which response detail should the client use?

- **A.** Retry-After header ✅
- **B.** Remaining burst request header
- **C.** OData version response header
- **D.** Default cache retry setting

> **Answer:** A. Retry-After header

The correct answer is Retry-After header because Microsoft documents that when Dataverse returns a 429 Too Many Requests response through the Web API, the response includes a Retry-After header that contains the number of seconds the caller should wait before retrying. That header is the platform-provided retry duration for Web API limit handling.

This is the key implementation detail for API limit retry policies in PL-400-style integrations. The retry policy should not invent its own fixed pause when the platform has already supplied the correct wait time for recovery. Microsoft’s guidance also notes that the retry duration varies based on the demand placed on the service, so using the provided value is more accurate than using a hard-coded guess.

<sub>Set A · Q73</sub>

---

### 34. A developer is building a custom retry handler for Dataverse Web API calls.

Snippet

static IAsyncPolicy<HttpResponseMessage> GetRetryPolicy(Config config)
{
    return HttpPolicyExtensions
      .HandleTransientHttpError()
      .OrResult(r => r.StatusCode == HttpStatusCode.TooManyRequests)
      .WaitAndRetryAsync(
         retryCount: config.MaxRetries,
         sleepDurationProvider: (count, response, context) =>
         {
             if (response.Result.Headers.Contains("Retry-After"))
             {
                 var seconds = int.Parse(
                     response.Result.Headers.GetValues("Retry-After").First());
                 return TimeSpan.FromSeconds(seconds);
             }

             return TimeSpan.FromSeconds(Math.Pow(2, count));
         });
}
What does this retry policy do when Dataverse returns HTTP 429?

- **A.** Honor Retry-After, then back off ✅
- **B.** Retry without waiting
- **C.** Ignore 429 responses
- **D.** Use fixed one-second pauses

> **Answer:** A. Honor Retry-After, then back off

This policy honors the Retry-After header when present and falls back to exponential backoff when it is absent. Microsoft’s Dataverse guidance includes a similar example that handles transient HTTP errors and TooManyRequests, reads the Retry-After header if available, and otherwise uses Math.Pow(2, count) to determine the fallback delay.

That makes this snippet a strong implementation pattern for a custom Web API retry policy. It treats 429 as a transient condition, follows the platform-provided wait time first, and still has a fallback behavior for cases where the response does not include that header. This matches Microsoft’s documented sample pattern for custom retry handling.

<sub>Set A · Q74</sub>

---

### 35. A canvas app triggers a custom middle-tier service that calls the Dataverse Web API. During peak usage, the service receives 429 responses and immediately returns the raw error payload to the app, while the app still allows the user to tap the same action repeatedly. The result is a poor user experience and more throttled requests.

What change is the best fit for the retry design?

- **A.** Show server-busy state ✅
- **B.** Raise client concurrency
- **C.** Increase batch size
- **D.** Bypass retry handling

> **Answer:** A. Show server-busy state

The best change is to show a server-busy state and prevent repeated submissions while the request is being retried. Microsoft says interactive applications should not simply display the raw service protection error to the user, and it recommends showing that the server is busy while retrying the request. Microsoft also says not to allow users to submit more requests until the previous request is complete.

This is the correct user-experience implementation of an API limit retry policy for an interactive flow. The retry logic still needs to respect the service protection timing, but the interface should absorb that complexity and prevent users from amplifying the throttling problem by repeatedly firing the same action.

<sub>Set A · Q76</sub>

---

### 36. A team is defining a Dataverse custom API for a controlled internal operation. The main plug-in must be the only logic that runs for the message, and other developers must not be able to register extra steps that change behavior or cancel execution.

Which setting should you configure for the message?

- **A.** Is Private
- **B.** None ✅
- **C.** Async Only
- **D.** Sync and Async

> **Answer:** B. None

AllowedCustomProcessingStepType = None is the correct choice when the plug-in configured for the custom API must be the only logic that runs for that operation. Microsoft states that this option prevents other developers from registering additional steps that could trigger other logic, modify behavior, or cancel the operation.

This is the best fit when the custom API is meant to expose a tightly controlled capability rather than a customizable business process. Async Only still allows post-operation detection logic, and Sync and Async allows the message to be extended in the same way as many standard Dataverse messages.

<sub>Set B · Q2</sub>

---

### 37. A developer wants a custom API to be available as a workflow action. The current message settings are shown below.

Configuration

Unique Name: contoso_CalculateExposure
Binding Type: Global
Is Function: Yes
Enabled for Workflow: Yes
Response Property Type: String
Allowed Custom Processing Step Type: None
Which change is required to make this message valid for workflow use?

- **A.** Add a Target parameter
- **B.** Disable private metadata
- **C.** Bind the message to account
- **D.** Use an action message ✅

> **Answer:** D. Use an action message

The required fix is to use an action message rather than a function. Microsoft states that when WorkflowSdkStepEnabled is true, the custom API cannot be a function, so Is Function must be false for the message to be callable in the workflow designer.

The String response type shown here is supported for workflow-enabled custom APIs, so the blocking issue is not the output type. The invalid part of the configuration is specifically the combination of workflow enablement with Is Function = Yes.

<sub>Set B · Q11</sub>

---

### 38. A connector action calls an API path parameter that can contain embedded slashes because it accepts a repository-style path such as team/docs/specs. The backend expects the separator characters to remain encoded all the way through the call.

Which OpenAPI extension should you use on that path parameter?

- **A.** x-ms-trigger
- **B.** x-ms-capabilities
- **C.** x-ms-summary
- **D.** x-ms-url-encoding ✅

> **Answer:** D. x-ms-url-encoding

x-ms-url-encoding is the correct answer because Microsoft documents it as the extension that controls whether a path parameter uses single or double URL encoding. The documentation also states that if the field is missing, the default is single encoding, so this is the extension you add when you need explicit encoding behavior on a path parameter.

This is exactly the kind of OpenAPI extension decision that affects runtime behavior rather than connector cosmetics. The question is not about display text, trigger behavior, or connector-level capabilities; it is about how the current path parameter is encoded before the request is sent, and Microsoft maps that behavior directly to x-ms-url-encoding.

<sub>Set B · Q15</sub>

---

### 39. A custom connector will call a third-party API that requires each user to sign in and obtain a bearer token. The security team also wants user access to remain revocable without rotating a shared secret for everyone.

Which authentication type should you configure?

- **A.** No authentication
- **B.** Basic authentication
- **C.** API key authentication
- **D.** OAuth 2.0 ✅

> **Answer:** D. OAuth 2.0

OAuth 2.0 is the best fit because the connector needs per-user sign-in and token-based access. Microsoft’s custom connector security settings support No authentication, Basic authentication, API key authentication, and OAuth 2.0, and OAuth is the model where the user signs in during connection creation and the resulting authorization token is sent on requests through the Authorization header.

That makes OAuth 2.0 the right design when you need identity-aware access instead of a shared static credential. It aligns with the requirement that access can be revoked per user, because the connection is based on the user’s authenticated session rather than on one common password or API key reused across all makers and end users.

<sub>Set B · Q19</sub>

---

### 40. An integration must create an account, two contacts, and a follow-up task on standard tables. If any one operation fails, all previously completed writes must roll back, and the requests must run in a defined order.

Which approach should you use?

- **A.** Parallel CreateMultipleRequest calls
- **B.** Web API $batch without a change set
- **C.** UpsertMultiple on an elastic table
- **D.** ExecuteTransactionRequest ✅

> **Answer:** D. ExecuteTransactionRequest

ExecuteTransactionRequest is the right choice because Microsoft documents it as the SDK mechanism for executing two or more requests in a single database transaction. The requests run in the order they appear, and if any request fails, the completed data changes in that transaction are undone.

That lines up exactly with the requirements in the scenario: ordered execution plus all-or-none rollback across multiple related writes. The Web API equivalent would be a $batch change set, but among the listed options the SDK feature that directly satisfies the requirement is ExecuteTransactionRequest.

<sub>Set B · Q24</sub>

---

### 41. A publisher is preparing a managed solution that contains an internal custom API. The API should not be advertised in the Web API metadata for downstream developers, and execution must require an approved privilege.

Which two settings should the publisher configure? (Select TWO.)

- **A.** Is Private = Yes ✅
- **B.** Binding Type = Global
- **C.** WorkflowSdkStepEnabled = Yes
- **D.** Execute Privilege Name ✅
- **E.** AllowedCustomProcessingStepType = None

> **Answer:** A. Is Private = Yes · D. Execute Privilege Name

IsPrivate = Yes is correct because Microsoft states that private custom APIs are hidden from the Web API $metadata document and from documentation/code-generation discovery scenarios. This is the setting that controls whether the message is advertised publicly to downstream developers.

ExecutePrivilegeName is also correct because Microsoft documents that this property specifies the privilege required to execute the custom API. Although developers outside Microsoft cannot create a brand-new custom privilege just for the API, they can require an existing privilege name or use privileges associated with a custom table.

<sub>Set B · Q29</sub>

---

### 42. A plug-in must read the request payload that triggered the event and also pass a custom flag to a later step in the same pipeline.

Which two execution-context members should the plug-in use? (Select TWO.)

- **A.** OwningExtension
- **B.** InputParameters ✅
- **C.** PostEntityImages
- **D.** CorrelationId
- **E.** SharedVariables ✅

> **Answer:** B. InputParameters · E. SharedVariables

InputParameters is correct because Microsoft identifies it as one of the most important execution-context properties and uses it to expose the request message data that triggered the event. For example, the Target entity for many messages is read from InputParameters.

SharedVariables is also correct because Microsoft documents it as the collection for passing data from the API or one plug-in step to another later in the pipeline. Together, these two context members solve the exact requirement in the question: read the triggering payload and hand off custom state to a subsequent step.

<sub>Set B · Q38</sub>

---

### 43. A synchronous Update plug-in runs in PreOperation and compares target["creditlimit"] to the existing value. In testing, the code fails whenever the user updates another field and leaves creditlimit unchanged, because the target entity does not contain that column.

What is the best fix?

- **A.** Read ParentContext instead
- **B.** Move the step to async PostOperation
- **C.** Register a pre-entity image with creditlimit ✅
- **D.** Read OutputParameters after save

> **Answer:** C. Register a pre-entity image with creditlimit

Registering a pre-entity image with the required columns is the best fix because Microsoft explains that the Target in the execution context exposes request data, and for update operations that request commonly contains only the changed values. Microsoft also recommends pre-images as the better practice when you need existing values without performing an extra retrieve.

This preserves the plug-in’s original intent and stage. The logic still runs in PreOperation, remains in the transaction pipeline, and now has a reliable snapshot of the pre-update value available through the execution context.

<sub>Set B · Q39</sub>

---

### 44. A team is defining a Dataverse custom API that must execute only the main plug-in logic associated to the message. Other developers must not be able to register extra steps that change behavior, cancel the operation, or add interception logic.

Which Allowed Custom Processing Step Type should you configure?

- **A.** None ✅
- **B.** Async Only
- **C.** Sync and Async
- **D.** Is Private

> **Answer:** A. None

None is the correct choice because Microsoft documents that AllowedCustomProcessingStepType = None should be used when the plug-in specified for the custom API is the only logic that should run for the operation. It explicitly prevents other developers from registering more processing steps that could modify behavior or cancel execution.

This is the safest configuration when the custom API represents a controlled capability that should not be extended through additional synchronous or asynchronous pipeline registrations. Async Only still allows extra asynchronous registrations, and Sync and Async removes the restriction entirely.

<sub>Set B · Q40</sub>

---

### 45. A flow posts order data to a third-party endpoint that sometimes returns HTTP 429 and intermittent 5xx responses. The team wants the action to recover from temporary failures without repeatedly hammering the service at the same interval.

Configuration

Action: HTTP
Method: POST
Retry Policy: None
Timeout: PT1M
Failure pattern: 429 and 5xx responses
Which change should you make?

- **A.** Secure outputs
- **B.** Fixed interval retry
- **C.** Exponential retry ✅
- **D.** Run after = has failed

> **Answer:** C. Exponential retry

Exponential retry is the best change because Microsoft’s Power Automate guidance says retry policies help workflows recover from transient network or service failures and that exponential retry policies are preferred. The interval increases over time, which gives the external system more time to recover and reduces the chance of repeatedly hammering the endpoint at a constant pace.

The designer documentation also confirms that Retry Policy is configured on the action’s Settings tab and that you can choose none, fixed, or exponential behavior. Since the current policy is None, the action has no built-in transient-fault recovery at all.

<sub>Set B · Q41</sub>

---

### 46. A team is building a custom connector for an internal API that accepts only app-only OAuth tokens. The connector must run unattended overnight, and the team does not want an interactive user sign-in to create or maintain the connection.

Which limitation blocks this design?

- **A.** Missing refresh endpoint URL
- **B.** API key authentication restriction
- **C.** Client credentials unsupported ✅
- **D.** Microsoft Entra tenant mismatch

> **Answer:** C. Client credentials unsupported

The blocking limitation is that client credentials grant type is not supported by custom connectors. Microsoft’s connection parameter documentation explicitly notes that while OAuth 2.0 is supported, client credentials grant is currently not supported for custom connectors.

That matters here because the scenario is asking for unattended, app-only access with no interactive user sign-in. That is exactly the pattern typically associated with client credentials, so the connector authentication design fails at the grant-model level before you even get to more detailed endpoint or tenant configuration questions. This is an inference from the requirement combined with Microsoft’s stated product limitation.

<sub>Set B · Q42</sub>

---

### 47. A developer wants to record runtime diagnostics from inside a sandboxed plug-in.

Snippet

IPluginExecutionContext context =
    (IPluginExecutionContext)serviceProvider.GetService(typeof(IPluginExecutionContext));

var target = (Entity)context.InputParameters["Target"];

var tracing =
    (?)serviceProvider.GetService(typeof(?));

tracing.Trace("Message={0}, Stage={1}", context.MessageName, context.Stage);
Which type should replace both ? placeholders?

- **A.** IOrganizationService
- **B.** IOrganizationServiceFactory
- **C.** ITracingService ✅
- **D.** IServiceEndpointNotificationService

> **Answer:** C. ITracingService

ITracingService is the correct type because Microsoft’s tracing guidance says you first extract the tracing service object from the passed execution context and then call Trace to write diagnostic information. That is the standard pattern for recording runtime details that help diagnose plug-in failures or unexpected behavior.

This is a direct execution-context usage question because the plug-in is already using IPluginExecutionContext to access message data and stage information, and it then acquires the tracing service from the service provider to log what is happening during execution. Microsoft specifically recommends this approach for debugging and operational diagnostics in plug-ins.

<sub>Set B · Q43</sub>

---

### 48. A connector is being configured with Generic OAuth 2.0 for a third-party identity provider. The developer wants to complete the initial sign-in redirect and exchange the authorization result for an access token.

Which two endpoint values must be configured? (Select TWO.)

- **A.** Parameter label
- **B.** Authorization URL ✅
- **C.** API key name
- **D.** Refresh URL
- **E.** Token URL ✅

> **Answer:** B. Authorization URL · E. Token URL

Authorization URL and Token URL are the two required endpoint values for the initial OAuth sign-in and token exchange flow. Microsoft’s custom connector documentation lists both as required OAuth inputs, along with other values such as client ID and client secret, when configuring OAuth 2.0 in the Security tab.

The Authorization URL is used to send the user to the identity provider for consent and sign-in, and the Token URL is used to obtain the access token after authorization. Refresh URL is related to renewing an expired token later, not to the initial redirect-plus-exchange sequence asked for in the stem.

<sub>Set B · Q44</sub>

---

### 49. A custom connector is being configured for a vendor API that requires the secret in an x-api-key request header. Makers should enter the key when they create the connection, and the connector should then send it on each request.

Configuration

Authentication type: API Key
Parameter label: VendorKey
Parameter location: Query
Backend requirement: x-api-key header
Connection experience: User enters key at creation time
What should you change first?

- **A.** Header parameter location ✅
- **B.** OAuth 2.0 identity provider
- **C.** Username and password labels
- **D.** Anonymous connection setting

> **Answer:** A. Header parameter location

The first change is to switch the API key parameter location from Query to Header. Microsoft’s custom connector documentation states that for API key authentication, the Parameter location field determines whether the key is sent in headers or in the query string when the request is made.

Because the backend explicitly expects x-api-key in a request header, leaving the connector configured for Query means the key will be transported in the wrong place. The connection experience itself is already compatible with API key auth, so the primary defect is not the auth type but the transport location of the secret.

<sub>Set B · Q45</sub>

---

### 50. A non-interactive data sync application is pushing large volumes of updates into Dataverse. The goal is to maximize throughput without mis-handling service protection limits.

Which two actions should you take? (Select TWO.)

- **A.** Start with batch sizes near 1,000 immediately
- **B.** Send parallel requests up to the recommended DOP ✅
- **C.** Keep Azure affinity enabled for all workers
- **D.** Surface raw 429 errors directly to users
- **E.** Honor the Retry-After value before retrying ✅

> **Answer:** B. Send parallel requests up to the recommended DOP · E. Honor the Retry-After value before retrying

Microsoft recommends sending requests in parallel and using the environment’s recommended degree of parallelization, or DOP, to guide how much concurrency to use. That is one of the main throughput levers for bulk work.

Microsoft also says service protection limit handling must respect the wait period returned by the platform. For Web API clients, that is the Retry-After header; for SDK clients it is exposed in error details. Honoring that value is part of a resilient bulk client design.

<sub>Set B · Q46</sub>

---

### 51. A connector must support two sign-in choices: Basic authentication for legacy tenants and API key authentication for newer tenants. A developer tries to do this in the Custom Connector Wizard, but each save leaves the connector with just one active authentication choice.

What should the developer use to implement supported multi-auth?

- **A.** Postman import
- **B.** Policy templates
- **C.** Wizard security tab
- **D.** Connectors CLI ✅

> **Answer:** D. Connectors CLI

The developer should use the Microsoft Power Platform Connectors CLI. Microsoft’s multi-auth documentation says multiple authentications are defined through connectionParameterSets in apiProperties.json, and it also states that the Custom Connector Wizard does not currently support enabling multiple authentications on a custom connector.

That is why the wizard keeps collapsing the design back to a single authentication path. The supported implementation route is to define the multi-auth structure in apiProperties.json and use the CLI-based workflow rather than expecting the standard wizard UI to author that configuration.

<sub>Set B · Q47</sub>

---

### 52. A solution architect needs a custom API that recalculates entitlement data for one selected account record. The caller must invoke the message in the context of a single row rather than as a global utility operation or a collection-wide request.

Which message design should you configure?

- **A.** Global action
- **B.** Entity function
- **C.** Entity action ✅
- **D.** EntityCollection action

> **Answer:** C. Entity action

An entity-bound action is the best fit because the operation applies to one specific record of a specific table, and Dataverse supports BindingType = Entity for operations that accept a single record as a parameter. Because this is an operation that performs work rather than a read-style function requirement, an action is the natural message shape here.

Microsoft also notes that when you select Entity binding, a Target request parameter of type EntityReference is created automatically. That reinforces that the intended design pattern for one-record context is an entity-bound message, not a global message with a manually simulated record parameter.

<sub>Set B · Q49</sub>

---

### 53. A connector author wants two behaviors in the OpenAPI definition. First, one parameter must show a dynamic picklist populated from another operation, even when parameter references are ambiguous. Second, a response schema must be discovered dynamically when references point to properties inside parameters.

Which two extension pairs should the author use? (Select TWO.)

- **A.** x-ms-summary and x-ms-visibility
- **B.** x-ms-trigger and x-ms-trigger-hint
- **C.** x-ms-dynamic-values and x-ms-dynamic-list ✅
- **D.** x-ms-notification-url and x-ms-notification-content
- **E.** x-ms-dynamic-schema and x-ms-dynamic-properties ✅

> **Answer:** C. x-ms-dynamic-values and x-ms-dynamic-list · E. x-ms-dynamic-schema and x-ms-dynamic-properties

C is correct because Microsoft documents x-ms-dynamic-values as the way to populate a selectable list of values for a parameter, and it also states that when references are ambiguous or point to properties within parameters, you should add x-ms-dynamic-list alongside it. The validator guidance reinforces this by explicitly calling out x-ms-dynamic-list as required for ambiguous references and for property references within parameters.

E is also correct because Microsoft documents x-ms-dynamic-schema for dynamically discovering a parameter or response schema, and then states that when references are ambiguous or point to properties within parameters, x-ms-dynamic-properties should be added alongside it. That pairing is the documented way to future-proof and disambiguate dynamic schema references in those cases.

<sub>Set B · Q50</sub>

---

### 54. A connector author wants a required parameter to be hidden from the maker experience because the value is supplied automatically.

Snippet

{
  "name": "api-version",
  "in": "query",
  "type": "string",
  "required": true,
  "x-ms-visibility": "internal"
}
What must be added to make this extension usage valid?

- **A.** A default value ✅
- **B.** An x-ms-summary value
- **C.** An x-ms-trigger value
- **D.** A value-collection value

> **Answer:** A. A default value

A default value must be added because Microsoft explicitly states that for parameters marked internal and required, you must provide default values. That rule exists because the user will not see the parameter in the designer, so the platform still needs a value source if the parameter is mandatory.

This is a good example of extending the OpenAPI definition to shape the designer experience without breaking the request contract. x-ms-visibility can hide a parameter from the user, but Microsoft’s rule means you cannot hide a required parameter unless the definition also ensures a usable value is already present.

<sub>Set B · Q51</sub>

---

### 55. A connector import fails validation after the author adds x-ms-dynamic-values directly to a body parameter definition. The validator reports that dynamic extensions aren't allowed on the body parameter.

What is the best fix?

- **A.** Replace it with x-ms-trigger-hint
- **B.** Move the extension into the body schema ✅
- **C.** Add x-ms-capabilities to the connector root
- **D.** Convert the operation to OpenAPI 3.0

> **Answer:** B. Move the extension into the body schema

B is correct because Microsoft’s validator guidance explicitly says that dynamic extensions are not allowed on the body parameter and that they should be placed in the schema instead. That is a direct fix for the exact error pattern in the scenario.

The OpenAPI-extension documentation aligns with that rule by showing dynamic values and dynamic schema usage attached within schema structures when appropriate, rather than leaving them on the body parameter wrapper. The correction is structural placement, not a change in connector feature type.

<sub>Set B · Q52</sub>

---

### 56. A custom connector imports successfully, but the maker wants a friendlier display label for a request field named cust_id without changing the underlying parameter name.

Which OpenAPI extension should you add?

- **A.** summary
- **B.** description
- **C.** x-ms-summary ✅
- **D.** x-ms-visibility

> **Answer:** C. x-ms-summary

x-ms-summary is the correct extension because Microsoft documents it as the title for an entity, and it applies to parameters and response schema fields. That is the extension used to show a friendlier label such as “Customer ID” while keeping the actual parameter name unchanged in the definition.

This question is testing the distinction between operation titles and field titles. Microsoft states that summary applies to operations, while x-ms-summary applies to parameters and response schema entities, so x-ms-summary is the right extension when the goal is to improve the user-facing label of a field inside the custom connector UI.

<sub>Set B · Q54</sub>

---

### 57. A maker created a custom API as a global message and saved it in a solution. Later, the design changes and the team now needs the API to be entity-bound to account, but the binding fields are no longer editable.

What is the best fix?

- **A.** Update the bound table name
- **B.** Create a new custom API ✅
- **C.** Recreate the request parameters
- **D.** Register a different plug-in type

> **Answer:** B. Create a new custom API

Creating a new custom API is the correct fix because Microsoft documents that key custom API properties such as BindingType and BoundEntityLogicalName cannot be changed after they are saved. When the original message shape is wrong, the supported remediation is to delete and recreate the API with the intended design.

This is why Microsoft advises planning the custom API design carefully before saving it. Once the immutable fields are committed, later solution updates cannot be used to change those saved properties either.

<sub>Set B · Q56</sub>

---

### 58. An Azure Function must load 300,000 new rows into the same standard Dataverse table. The rows are already validated, and the process does not need alternate-key existence checks before insert.

Which API should you prefer first?

- **A.** ExecuteMultipleRequest
- **B.** Web API $batch
- **C.** CreateMultipleRequest ✅
- **D.** Upsert with alternate keys

> **Answer:** C. CreateMultipleRequest

CreateMultipleRequest is the best first choice because Microsoft recommends using Dataverse bulk operation APIs when you can, and CreateMultiple is specifically designed to create multiple rows of the same type in a single request. That makes it the most direct fit for a large insert workload into one standard table.

It is also a better fit than Upsert here because the scenario already says the rows are new and do not require existence checks. Microsoft notes that Upsert is useful when you do not know whether a record exists, but it carries a performance penalty compared with Create when you already know the row is new.

<sub>Set B · Q57</sub>

---

### 59. Two services update the same account row. The second service uses the original ETag that it retrieved earlier.

Snippet

PATCH /api/data/v9.2/accounts(00aa00aa-bb11-cc22-dd33-44ee44ee44ee) HTTP/1.1
If-Match: W/"72965013"
Content-Type: application/json

{
  "telephone1": "555-0002",
  "revenue": 6000000
}
If another process already changed the row and the ETag is now different, what should this request return when optimistic concurrency is working correctly?

- **A.** 412 Precondition Failed ✅
- **B.** 409 Conflict
- **C.** 304 Not Modified
- **D.** 429 Too Many Requests

> **Answer:** A. 412 Precondition Failed

The expected result is 412 Precondition Failed. Microsoft’s conditional operations guidance shows that when a PATCH request uses If-Match with an outdated ETag, the request fails because the current record version no longer matches the version the client retrieved earlier.

That is the point of optimistic concurrency in Dataverse: stop a client from overwriting changes made by another process after the row was read. Microsoft also notes that this capability depends on optimistic concurrency support for the table.

<sub>Set B · Q58</sub>

---

### 60. A cloud flow in a support environment must invoke a Dataverse custom API that isn't associated with any table row. The connection already has permission in the target environment, and the team wants to stay within the supported Microsoft Dataverse connector actions.

Which action should you configure?

- **A.** Execute a changeset request
- **B.** Update a row in selected environment
- **C.** Perform a bound action in selected environment
- **D.** Perform an unbound action in selected environment ✅

> **Answer:** D. Perform an unbound action in selected environment

Perform an unbound action in selected environment is the best answer because Microsoft documents unbound actions as static operations that aren't bound to a table and are performed on the environment rather than on a specific row. Microsoft also lists Perform an unbound action among the Dataverse actions that support the Environment parameter for connecting to other environments.

This is the right configuration choice because the custom API in the scenario is global rather than row-bound. If the operation isn't tied to a single table or row, you should configure an unbound Dataverse action rather than a row update or a bound action.

<sub>Set B · Q59</sub>

---

### 61. A PreOperation plug-in calculates a derived value and a later PostOperation step must reuse that value without recalculating it. The design should use execution-context data rather than a custom table write.

Which execution-context member should you use?

- **A.** ParentContext
- **B.** OutputParameters
- **C.** SharedVariables ✅
- **D.** OwningExtension

> **Answer:** C. SharedVariables

SharedVariables is the right answer because Microsoft documents it as the execution-context collection used to pass data from the API or one plug-in step to a later step in the execution pipeline. It is specifically intended for sharing values across steps without persisting them elsewhere.

This is exactly the use case in the question: compute once in PreOperation, then read later in PostOperation. SharedVariables lets the plug-in keep the logic inside the pipeline and avoid unnecessary writes or extra retrieval logic.

<sub>Set B · Q60</sub>

---

### 62. A team wants the best performance for a flow that reads Dataverse accounts in the same environment as the app and data source.

Configuration

Action: List rows from selected environment
Environment: (Current)
Table name: accounts
Select columns: name,revenue
Filter rows: revenue gt 1000000
Which statement is correct?

- **A.** Uses native direct integration ✅
- **B.** Requires a custom base URL value
- **C.** Routes through another environment connector path
- **D.** Ignores Dataverse table permissions

> **Answer:** A. Uses native direct integration

A is correct because Microsoft recommends deploying flows in the same environment as the data and apps they connect to for best performance. Microsoft also states that when the Environment parameter is set to (Current), the Dataverse connector is optimized to connect directly to Dataverse through a native integration.

This configuration therefore matches the documented best-practice path. It keeps the action in the current environment, uses a supported Dataverse action, and avoids the additional connector-platform routing Microsoft describes for cross-environment access.

<sub>Set B · Q61</sub>

---

### 63. A flow processes invoices from a shared mailbox. The team wants the flow to start only when the incoming message is already approved, and they want to avoid unnecessary runs and request consumption.

Which feature should you configure on the trigger?

- **A.** Trigger conditions ✅
- **B.** Condition action
- **C.** Run after
- **D.** Terminate action

> **Answer:** A. Trigger conditions

Trigger conditions are the best fit because they stop the flow from starting unless the expression evaluates to true. Microsoft states that trigger conditions reduce unnecessary runs and Power Platform request consumption, and if the trigger condition is not met, the flow is not triggered and no run history is logged.

A Condition action is evaluated after the trigger has already started the flow. That means it can still create unnecessary runs, which is exactly what the scenario wants to avoid. The requirement is not just logical branching; it is pre-run filtering at the trigger boundary.

<sub>Set B · Q63</sub>

---

### 64. A Dataverse flow should run only when an incident row is updated and the update request includes either prioritycode or statuscode. The flow must also run only when the saved row ends up in an Approved state, and unrelated edits must not start the flow.

Which trigger configuration should you choose?

- **A.** Change type + Scope
- **B.** Select columns + Filter rows ✅
- **C.** Delay until + Run as
- **D.** Condition action + Terminate

> **Answer:** B. Select columns + Filter rows

Select columns plus Filter rows is the best design because these two settings solve different parts of the requirement. Microsoft states that Select columns defines which updated columns should cause the flow to run, while the filter expression further narrows the run so it occurs only when the OData-style expression evaluates to true after the Dataverse change is saved.

That makes this the cleanest way to prevent unrelated updates from starting the flow while still enforcing the final row-state rule. Change type and scope are necessary trigger parameters in many cases, but they do not provide the same precision as combining column-based trigger filtering with an OData filter expression.

<sub>Set B · Q65</sub>

---

### 65. A telemetry ingestion service writes high-volume sensor data to an elastic table. The developer grouped the writes inside a Web API change set because the business expected one bad row to roll back the whole set, but some rows still persisted and the operation was not atomic.

What should you change first?

- **A.** Increase rows per request
- **B.** Avoid elastic-table transactions ✅
- **C.** Use ExecuteMultiple in a plug-in
- **D.** Add synchronous validation steps

> **Answer:** B. Avoid elastic-table transactions

The first change is to stop assuming elastic tables provide transaction semantics like standard tables. Microsoft states that elastic tables do not support grouping requests in a single database transaction by using ExecuteTransactionRequest or a Web API $batch change set, and currently those grouped operations can complete without being atomic.

For elastic tables, the optimization model is throughput rather than transactional rollback. Microsoft’s bulk guidance says there is no transaction benefit in sending very large elastic-table bulk requests, and recommends smaller request sizes with parallel execution for maximum throughput.

<sub>Set B · Q66</sub>

---

### 66. An Update plug-in must compare the previous and incoming values of creditlimit before the row is saved. The team wants to avoid an extra retrieve call for performance reasons and keep the logic in the transaction pipeline.

Which approach should you use?

- **A.** Read ParentContext for the old value
- **B.** Read OutputParameters["Target"]
- **C.** Query Dataverse inside the plug-in
- **D.** Register a pre-entity image ✅

> **Answer:** D. Register a pre-entity image

A pre-entity image is the best answer because Microsoft recommends defining a pre-image when a PreValidation or PreOperation plug-in needs the prior values of columns. The registration guidance explicitly says this is a better practice than issuing an extra retrieve for performance.

This also matches how the execution context is meant to be used. The Target in InputParameters for an update usually contains only the changed values, while entity images provide the before or after snapshot data you register the step to capture.

<sub>Set B · Q67</sub>

---

### 67. A cloud flow calls an external API that intermittently returns transient network and service failures. The same flow is also receiving too many irrelevant trigger events because filtering currently happens inside the flow after the trigger fires.

Which two changes should you implement? (Select TWO.)

- **A.** Fixed retry policy
- **B.** Trigger conditions ✅
- **C.** Run after rules
- **D.** Exponential retry policy ✅
- **E.** Condition action

> **Answer:** B. Trigger conditions · D. Exponential retry policy

Trigger conditions are correct because Microsoft states they reduce unnecessary runs by preventing the flow from starting when the condition is not met. This helps reduce request consumption and keeps irrelevant events out of run history entirely. That directly addresses the trigger-filtering problem described in the scenario.

Exponential retry policy is also correct because Microsoft recommends retry policies for transient failures and specifically notes that exponential retry intervals are preferred. The reason is that they increase the wait between retries over time, which improves the chance of recovery and helps avoid overwhelming the target system.

<sub>Set B · Q68</sub>

---

### 68. A flow must run only for updates to an incident row, not for creates or deletes. It should react when prioritycode or statuscode is included in the update request, and it should continue only when the saved row meets an active-state filter.

Which two settings should you configure? (Select TWO.)

- **A.** Set Select columns to prioritycode,statuscode ✅
- **B.** Set Change type to Create and Delete
- **C.** Set Filter rows to statecode eq 0 ✅
- **D.** Monitor N:N relationship updates
- **E.** Use Select columns on a virtual table

> **Answer:** A. Set Select columns to prioritycode,statuscode · C. Set Filter rows to statecode eq 0

A is correct because Microsoft documents Select columns as the setting that defines which columns should cause the When a row is added, modified or deleted trigger to run when they are included in the update request. Microsoft also states that this property applies to the Update condition.

C is also correct because Microsoft documents Filter rows as an OData-style filter expression that refines the trigger so the flow runs only when the expression evaluates to true after the change is saved in Dataverse. That makes it the right setting for applying a post-save state filter such as statecode eq 0.

<sub>Set B · Q69</sub>

---

### 69. A Dataverse flow uses the When a row is added, modified, or deleted trigger with Change type set to Modified. The maker added a filter expression so the flow runs only when statuscode is Approved, but the flow still starts when users save unrelated field changes on rows that are already approved.

What is the best fix?

- **A.** Narrow Scope
- **B.** Add trigger conditions
- **C.** Change to Create
- **D.** Set Select columns ✅

> **Answer:** D. Set Select columns

Set Select columns is the best fix because Microsoft documents that Select columns defines which updated columns should cause the Dataverse trigger to run. Without it, any update to a row that already satisfies the filter expression can still start the flow, because the filter expression is evaluated after the change is saved.

This is exactly the distinction between filter expression and filter columns. Filter rows helps decide whether the saved row meets the business rule, while Select columns controls whether specific updated fields should trigger evaluation in the first place. Using both together is the correct precision pattern for this scenario.

<sub>Set B · Q70</sub>

---

### 70. Users must run a cloud flow from a model-driven app view for one or more selected case rows. The flow should start from the Dataverse connector and receive the selected row data as trigger output.

Which trigger should you configure?

- **A.** When an action is performed
- **B.** When a row is added, modified or deleted
- **C.** When a row is selected ✅
- **D.** Recurrence

> **Answer:** C. When a row is selected

When a row is selected is the correct trigger because Microsoft documents it as the Dataverse trigger that lets users run a flow for one or more selected rows in a model-driven app view. The trigger also exposes the selected row columns and the triggering user details as dynamic content for later steps in the flow.

This is different from row-change and action-based triggers. The requirement is a user-initiated run from the model-driven app command surface for selected records, which matches the selected-row trigger exactly.

<sub>Set B · Q71</sub>

---

### 71. A developer is testing a Dataverse Web API request from a custom .NET client. The request must authenticate by using OAuth instead of a legacy header pattern.

Snippet

GET https://contoso.crm.dynamics.com/api/data/v9.2/accounts?$top=1
Authorization: Basic dGVzdDp0ZXN0
Accept: application/json
What should replace the Authorization value?

- **A.** Bearer access token ✅
- **B.** Signed subscription key header
- **C.** ASP.NET session auth cookie
- **D.** Embedded client secret value

> **Answer:** A. Bearer access token

The request should carry an OAuth access token as a bearer token in the Authorization header. Microsoft’s Dataverse guidance says you must use OAuth for Web API authentication, and Microsoft’s custom connector OAuth troubleshooting guidance specifically tells you to verify that the token is sent in the Authorization header prefixed by bearer.

That makes a bearer access token the correct replacement for a Basic header. The point of the change is not just syntactic; it shifts the call into the supported Dataverse OAuth model so the request carries a valid access token issued by Microsoft Entra ID.

<sub>Set C · Q9</sub>

---

### 72. A synchronous Update plug-in iterates through related rows and submits them by using ExecuteMultipleRequest inside Execute. During peak usage, users report slow saves, blocking, and intermittent transaction errors.

What is the best fix?

- **A.** Enable plug-in trace logging
- **B.** Avoid batch requests here ✅
- **C.** Move the logic to async
- **D.** Swallow OrganizationService faults

> **Answer:** B. Avoid batch requests here

The best fix is to stop using batch request types such as ExecuteMultipleRequest inside the plug-in. Microsoft explicitly says not to use batch request types in plug-ins and workflow activities, and notes that user experience degradation and timeout errors can occur when they are used in synchronous operations.

This guidance exists because batching in a plug-in does not solve the problem developers usually think it solves. Microsoft explains that batch requests are for client-side latency reduction, while plug-ins already run close to the server, and the requests inside the batch are still executed sequentially. In a synchronous step, the plug-in is already inside the transaction context, so batching increases complexity and blocking risk instead of improving the design.

<sub>Set C · Q10</sub>

---

### 73. A team adds custom code to a custom connector so it can transform payloads before forwarding requests to a private line-of-business API. They plan to reach that API through the on-premises data gateway, but testing fails after the connector is enabled.

What is the best explanation?

- **A.** Scripts require connector certification before testing
- **B.** Gateway doesn't support custom code ✅
- **C.** Multiple script files must be uploaded
- **D.** The backend must expose SOAP metadata

> **Answer:** B. Gateway doesn't support custom code

The best explanation is that Microsoft explicitly states that custom code cannot currently be used with the on-premises data gateway. That means the design fails because of a documented platform limitation, not because of a small bug in the script itself.

This is why the issue appears during implementation rather than at the point of enabling the code editor. The connector can still be defined successfully, but the chosen architecture combines custom code with a gateway scenario that Microsoft says is unsupported.

<sub>Set C · Q18</sub>

---

### 74. A developer writes custom code to forward the incoming request to the backend and then transform the response body. The code works in a simple local test, but the team wants the implementation aligned to Microsoft’s recommended connector pattern.

Snippet

public class Script : ScriptBase
{
    public override async Task<HttpResponseMessage> ExecuteAsync()
    {
        using (var client = new HttpClient())
        {
            var response = await client.SendAsync(this.Context.Request);
            return response;
        }
    }
}
What is the best fix?

- **A.** Move HttpClient into a static field
- **B.** Return CreateJsonContent immediately
- **C.** Wrap SendAsync in Task.Run
- **D.** Use Context.SendAsync instead ✅

> **Answer:** D. Use Context.SendAsync instead

The best fix is to use Context.SendAsync. Microsoft documents this method on IScriptContext and says to use it to send requests instead of HttpClient.SendAsync. That makes it the recommended connector-specific execution path when custom code needs to forward a request.

This is a design-quality question rather than a pure compile-time question. Microsoft also notes in the FAQ that creating your own HTTP client is currently possible, but the recommended approach is this.Context.SendAsync, which is why replacing the direct HttpClient call is the strongest answer.

<sub>Set C · Q23</sub>

---

### 75. A custom connector must reshape the backend response and call another endpoint to fetch extra lookup data before returning the final payload. Existing policy templates do not cover the full transformation.

Which approach should you design?

- **A.** Postman collection import
- **B.** Custom code ✅
- **C.** OpenAPI extension metadata
- **D.** Codeless policy template

> **Answer:** B. Custom code

Custom code is the correct choice because Microsoft states that custom code transforms request and response payloads beyond the scope of existing policy templates. The same documentation also states that these transformations can include sending external requests to fetch additional data, which matches the requirement in the stem.

This is also the strongest answer because when code is used, it takes precedence over the codeless definition. Microsoft explicitly says that in this case the code executes and the request is not automatically sent to the backend through the codeless definition path, which is exactly the kind of control needed for a full transformation scenario.

<sub>Set C · Q29</sub>

---

### 76. A support team registers a synchronous plug-in step that creates a related follow-up record when a case is created. The case creators do not have privileges to create the related record, and you must avoid broadening their security roles.

Which step setting should you change in the Plug-in Registration Tool?

- **A.** Primary and Secondary Entity values
- **B.** Secure Configuration string
- **C.** Execution Order value
- **D.** Run in User's Context ✅

> **Answer:** D. Run in User's Context

The best answer is Run in User's Context. In the Plug-in Registration Tool, that step setting controls impersonation for the registered step, and the default is Calling User. Microsoft’s guidance states that if the calling user lacks the privileges needed by the step, you can set the step to run as a different user who has those privileges.

This is the most targeted registration change because it solves the privilege gap at the step level instead of expanding the permissions of every end user who triggers the event. It keeps the fix anchored in step registration behavior, which is exactly what the Plug-in Registration Tool is designed to configure.

<sub>Set C · Q35</sub>

---

### 77. A synchronous Update plug-in must set a calculated column on the same row before Dataverse writes the row. The change must participate in the same transaction and must not trigger a second Update operation.

Which stage should you register?

- **A.** PostOperation stage
- **B.** PreValidation stage
- **C.** PreOperation stage ✅
- **D.** Asynchronous PostOperation step

> **Answer:** C. PreOperation stage

PreOperation stage is the best fit because Microsoft documents that it occurs before the main system operation and within the database transaction, and specifically says that if you want to change values for an entity included in the message, you should do it there. That aligns exactly with a plug-in that must set field values before the row is written and keep the change in the same transaction.

PostOperation is later in the pipeline, and Microsoft explicitly warns against applying changes to the entity in that stage because it will trigger a new Update event. PreValidation is primarily the stage for early validation and cancellation before the main transaction, while asynchronous PostOperation runs outside the database transaction. Those alternatives are plausible, but they do not match the requirement as precisely as PreOperation.

<sub>Set C · Q36</sub>

---

### 78. A custom connector uses OAuth 2.0 to call an external API from Power Apps. Connections work for about 60 minutes and then consistently fail with 401 until users recreate the connection. You verified in Postman that the token endpoint returns an access token and the API call succeeds with that token.

What should you check next?

- **A.** Connection reference ownership setting
- **B.** Refresh URL configuration ✅
- **C.** Gateway cluster region mapping
- **D.** Environment DLP policy action

> **Answer:** B. Refresh URL configuration

The next thing to check is the refresh URL configuration. Microsoft’s custom connector OAuth troubleshooting guidance says that after you verify token acquisition and a successful API call, you should validate the refresh flow and then confirm that the connector’s token URL and refresh URL are correctly configured, or that the refresh URL matches the token URL when a separate refresh endpoint is not used.

The symptom also fits that diagnosis because the connection works until the original access token expires and then starts returning consistent 401 responses. Microsoft lists this kind of time-based failure pattern as a common OAuth troubleshooting symptom for custom connectors.

<sub>Set C · Q37</sub>

---

### 79. A developer writes the following plug-in to track execution data. The plug-in sometimes behaves unpredictably after repeated executions in the same environment.

Snippet

using Microsoft.Xrm.Sdk;
using System;
using System.Collections.Generic;

public class CreditHoldPlugin : IPlugin
{
    private readonly List<Guid> processedIds = new();

    public void Execute(IServiceProvider serviceProvider)
    {
        var context = (IPluginExecutionContext)
            serviceProvider.GetService(typeof(IPluginExecutionContext));

        processedIds.Add(context.CorrelationId);
    }
}
Which change best aligns this plug-in with supported design guidance?

- **A.** Remove member state ✅
- **B.** Register a pre image alias
- **C.** Change the step to PostOperation
- **D.** Move tracing into constructor

> **Answer:** A. Remove member state

The correct fix is to remove member state and keep the plug-in stateless. Microsoft states that when implementing IPlugin, you should not use member fields and properties for per-invocation state, and that all invocation-specific information should be taken from the execution context.

Microsoft also explains why: the platform caches and reuses plug-in class instances for performance. A member field like processedIds can therefore persist data across invocations, which creates thread-safety, memory, and data-consistency risks. Using local variables inside Execute instead of mutable member state is the supported design.

<sub>Set C · Q39</sub>

---

### 80. You already wrote a plug-in class that recalculates a score on Update. The logic should run only when annualrevenue is included in the request, and it must compare the incoming value with the previous value by using a pre image.

Steps

Add a pre image containing annualrevenue and the current score.

Add the assembly and step components to an unmanaged solution.

Register an Update step with annualrevenue as a filtering attribute.

Register the assembly in the target environment.

What is the correct order?

- **A.** 3 → 1 → 4 → 2
- **B.** 4 → 1 → 3 → 2
- **C.** 4 → 3 → 2 → 1
- **D.** 4 → 3 → 1 → 2 ✅

> **Answer:** D. 4 → 3 → 1 → 2

The correct order is 4 → 3 → 1 → 2. You must register the assembly before Dataverse can create a step that points to a class in that assembly. After that, you register the Update step and set filtering attributes so the plug-in runs only when the relevant attribute is included in the update payload.

Next, you add the pre image to that step, because entity images are configured on the registered step itself. The solution move comes last because plug-in assemblies and SDK message processing steps are solution components, and Microsoft notes that if you try to add a step before the assembly is already part of the solution, required-component handling comes into play.

• 4 is first because the step cannot exist until the target assembly is registered in the environment. The platform needs that assembly registration before it can bind a step to the plug-in type. Without the assembly, there is nothing for the step to reference. This is the foundational registration action.

• 3 is second because filtering attributes are part of the Update step registration. Microsoft recommends including filtering attributes so the plug-in does not fire on every update event. Since the requirement is to react only when annualrevenue is in the request, that belongs directly on the step. You set that before refining the step further with images.

• 1 is third because a pre image is configured on an existing step, not independently of it. Microsoft describes pre and post images as step-level configuration and explains their availability based on stage and operation. Once the Update step exists, you can attach the pre image alias and the needed columns. That gives the plug-in the old values without an extra retrieve.

• 2 is last because the finished registration artifacts are what you want to distribute through ALM. Microsoft states that plug-in assemblies and SDK message processing steps are solution components and also notes the dependency relationship between them when adding steps to a solution. Moving them after registration keeps the solution package aligned with the completed design. It is the cleanest deployment sequence.

<sub>Set C · Q40</sub>

---

### 81. A team registers an Update step for the Account table. The plug-in is intended to run only when the name column is included in the update, but users report that it fires on every account save.

Configuration

Message: Update
Primary Entity: account
Stage: PreOperation
Execution Mode: Synchronous
Filtering Attributes: accountid,name
Run in User's Context: Calling User
Which change should you make?

- **A.** Change the stage to PostOperation
- **B.** Remove accountid from Filtering Attributes ✅
- **C.** Change the execution mode to Asynchronous
- **D.** Set Execution Order to 1

> **Answer:** B. Remove accountid from Filtering Attributes

The correct change is to remove accountid from Filtering Attributes. Microsoft’s registration guidance states that for Update steps, filtering attributes limit execution to cases where those columns are included in the request, but the primary key is always included in update operations. Including the primary key therefore defeats the intended filtering and causes the step to run far more often than expected.

This is a registration-quality issue rather than a pipeline-stage or async-choice issue. The step is already registered on the correct message and entity, but the filter definition is too broad because it includes a column that is always present. The best fix is to keep the step targeted to the business column that matters and avoid unnecessary executions for performance reasons.

<sub>Set C · Q41</sub>

---

### 82. A plug-in must compare the previous and new values of an Account column after an update is completed. You want the registration to provide both snapshots through entity images.

Exhibit 1

Which row should you use?

- **A.** Row A
- **B.** Row B
- **C.** Row C ✅
- **D.** Row D

> **Answer:** C. Row C

Row C is the correct choice because an Update step registered in PostOperation can use both a Pre Image and a Post Image. Microsoft’s registration guidance explains that entity-image availability depends on both the message and the pipeline stage, and specifically notes that for an Update step in PostOperation you can have both image types.

That makes Row C the only registration in the exhibit that cleanly supports comparing before-and-after values after the update completes. The other rows all violate a documented image-availability rule, so they would not provide the image combination the plug-in logic requires.

<sub>Set C · Q43</sub>

---

### 83. A team has two synchronous Update steps on the Contact table in the same stage. After import, one environment applies the validation step first and another applies the enrichment step first, even though the registrations appear identical in the Plug-in Registration Tool.

What is the best fix?

- **A.** Set distinct Execution Order values ✅
- **B.** Move one step to PreValidation
- **C.** Add Secure Configuration data
- **D.** Add more Filtering Attributes

> **Answer:** A. Set distinct Execution Order values

The best fix is to assign distinct Execution Order values to the two steps. Microsoft’s registration guidance states that execution order determines the order in which steps are applied within a stage from lowest to highest, and it also warns that if multiple steps use the same execution-order value, the actual order is not guaranteed and can be random.

This is a classic registration problem, not a code defect. The inconsistent behavior is caused by ambiguous sequencing in the step metadata, so the clean solution is to define a deterministic order in the Plug-in Registration Tool rather than changing stages or adding unrelated settings.

<sub>Set C · Q45</sub>

---

### 84. You have compiled a new Dataverse plug-in and must register it with the Plug-in Registration Tool and prepare it for transport through solutions.

Steps

Add the step registration to an unmanaged solution.

Register the plug-in assembly in the Plug-in Registration Tool.

Register the message processing step.

Add the assembly to an unmanaged solution.

What is the correct order?

- **A.** 2 → 4 → 1 → 3
- **B.** 4 → 2 → 3 → 1
- **C.** 2 → 4 → 3 → 1
- **D.** 2 → 3 → 4 → 1 ✅

> **Answer:** D. 2 → 3 → 4 → 1

The correct order is 2 → 3 → 4 → 1. First, you register the assembly in the Plug-in Registration Tool. Next, you register the message processing step that points to the plug-in type. After those registrations exist, you add the assembly to an unmanaged solution, and then you add the step registration as a solution component for distribution. Microsoft’s guidance states that PRT registers the assembly and step, that PRT does not let you choose a solution during registration, and that assemblies and steps must then be added to an unmanaged solution for transport.

This order keeps dependencies intact. A step depends on the registered assembly, and a solution that carries the step should also include the required assembly component. Following the sequence in this order prevents missing-component problems and aligns with how Dataverse treats plug-in assemblies and SDK message processing steps as solution components.

• 2 is first because the assembly must exist in Dataverse before a step can reference the plug-in type it contains.

• 3 is second because step registration defines the message, table, stage, and runtime behavior for the already-registered plug-in type.

• 4 is third because PRT adds the new assembly to the default solution first, so you then move that assembly into the unmanaged solution you plan to transport.

• 1 is last because the step is also a solution component, and adding it after the assembly preserves the dependency chain cleanly.

<sub>Set C · Q46</sub>

---

### 85. A team wants to centralize customer validation logic so five different parent flows can call the same reusable flow. The solution must remain easy to transport across environments, and the parent-child link should survive solution export and import without manually updating URLs.

Which design should you recommend?

- **A.** Call an HTTP-triggered flow by URL
- **B.** Keep all actions in each parent flow
- **C.** Import the child later into another solution
- **D.** Create both flows directly in one solution ✅

> **Answer:** D. Create both flows directly in one solution

The best design is to create both the parent and child flows directly in the same solution. Microsoft’s documentation states that the parent flow should be built in the same solution as the child flow, and when the solution is exported and imported into another environment, the new parent and child flows are automatically linked without needing URL changes.

Microsoft also separately recommends creating the parent flow and all child flows directly in the same solution, because importing a flow into a solution can lead to unexpected results. That makes the shared-solution design the strongest ALM choice for reusable child flow logic.

<sub>Set C · Q47</sub>

---

### 86. A backend API requires an api-version query string value on each request. The connector designers do not want makers to supply that value as an action parameter.

Which policy template should you use?

- **A.** Set request or response header
- **B.** Route request to same endpoint
- **C.** Add or update body property
- **D.** Set query string parameter ✅

> **Answer:** D. Set query string parameter

Set Query String Parameter is the best fit because Microsoft documents that this template adds or updates a request query string parameter at runtime. That matches a design where the connector should inject api-version without exposing it as a user-supplied action input.

This is a strong out-of-the-box runtime-policy use case because the request shape needs to be adjusted just before the backend call is made. It does not require routing to a different path, rewriting the host, or mutating a JSON body, so the query-string template is the most direct and maintainable choice.

<sub>Set C · Q48</sub>

---

### 87. A team wants a reusable child flow that accepts an input, performs validation, returns a result to the caller, and is then invoked from a parent flow. Both flows must follow the supported solution-aware child flow pattern.

Steps

Add a response action and define the outputs to return.

Create the parent flow in the same solution and add Run a Child Flow.

Create the child as an instant cloud flow with Manually trigger a flow.

Add child flow inputs and the reusable validation logic.

What is the correct order?

- **A.** 3 → 4 → 1 → 2 ✅
- **B.** 2 → 3 → 4 → 1
- **C.** 3 → 1 → 4 → 2
- **D.** 4 → 3 → 2 → 1

> **Answer:** A. 3 → 4 → 1 → 2

The correct order is 3 → 4 → 1 → 2. Microsoft’s child flow guidance starts with creating the child flow in a solution as an Instant cloud flow that uses Manually trigger a flow. After that, you define the child inputs, build the child logic, and then add a response action so the child can return outputs to the parent. Only then do you build the parent in the same solution and call the child with Run a Child Flow.

That order is important because the parent consumes the child flow’s defined inputs and outputs. Microsoft explicitly says that after you select the child flow in the parent, you see the inputs defined in the child flow and can use any outputs returned by that child flow. This means the child contract should exist before wiring it into the parent.

• 3 is first because the documented child flow pattern begins by creating the child flow inside a solution as an instant cloud flow with the Manually trigger a flow trigger. Without that, the flow is not shaped correctly to act as a child flow. This step establishes the reusable unit before anything can call it.

• 4 is second because Microsoft says the inputs you define on the trigger are passed from the parent flow to the child flow. The reusable logic also belongs in the child before the response contract is finalized. This step defines what the child needs to do with the incoming data.

• 1 is third because after building the child logic, Microsoft says you need to return data to the parent flow by using Respond to a Power App or flow or Response and then define the outputs. That response contract comes after the logic is built and before the parent is wired to consume it.

• 2 is last because the parent flow is then built in the same solution and uses Run a Child Flow to call the already defined child. Microsoft states that after you select the child flow, the parent sees the child’s inputs and can use its outputs. That dependency makes the parent wiring the last step in the sequence.

<sub>Set C · Q49</sub>

---

### 88. A custom connector must call a region-specific backend host. The region is chosen in a connection parameter when the user creates the connection, and the same operation definitions must work across all regions without duplicating actions.

Which policy template should you use?

- **A.** Set query string parameter
- **B.** Set host URL ✅
- **C.** Route request to same endpoint
- **D.** Set request header at runtime

> **Answer:** B. Set host URL

Set Host URL is the correct template because Microsoft documents that it replaces the host URL with a URL generated from a template and that the URL template can use expressions over connection parameters, query parameters, or headers. That exactly matches a connector whose backend host changes by region at runtime based on the connection settings.

This is also the clearer design than route-based alternatives because the requirement is about changing the backend host, not just the relative path on an already selected host. Using a host template keeps the OpenAPI operation surface stable while letting runtime policy decide which regional service endpoint should receive the request.

<sub>Set C · Q53</sub>

---

### 89. A connector uses a policy template to stamp a request header from a connection parameter.

Snippet

{
  "template": "setheader",
  "name": "x-contoso-region",
  "value": "@connectionParameters('region', 'global')",
  "existsAction": "override",
  "policySection": "Request"
}
An operation already sends x-contoso-region=emea, and the connection parameter region is apac. What reaches the backend?

- **A.** The header is removed
- **B.** The header stays emea
- **C.** The header becomes apac ✅
- **D.** The header becomes global

> **Answer:** C. The header becomes apac

The header becomes apac. Microsoft documents that Set HTTP Header can use expressions for the header value, including connection parameters, and that the override action replaces the existing header value with the value from the policy template. Because the policy runs on Request, the backend receives the updated header before the call is sent.

The default value of global would matter only if the referenced connection parameter were absent or unresolved in a way that caused the default branch of the expression to be used. In this scenario, the connection parameter has a concrete value of apac, so the runtime policy evaluates to that value and overwrites the existing request header.

<sub>Set C · Q54</sub>

---

### 90. A developer is reviewing which runtime policy template should be applied for several custom connector requirements.

Exhibit 1

Which row is incorrectly mapped?

- **A.** Row 4 ✅
- **B.** Row 2
- **C.** Row 3
- **D.** Row 1

> **Answer:** A. Row 4

Row 4 is the mismatch. Microsoft documents that Route Request routes incoming requests to a specified endpoint on the same service and uses a relative new-path template. That means it is a same-service path-routing template, not a host-switching template. Changing from api.contoso.com to eu.api.contoso.com is a host-level change and therefore is not correctly solved by Route Request.

The other rows align to the documented template purposes: Set Query String Parameter adds or updates request query values, Route Request is appropriate for redirecting to another relative path on the same service, and Set Host URL is the host-replacement template for dynamic backend selection. This is exactly the kind of PL-400 distinction that separates path routing from host routing.

<sub>Set C · Q55</sub>

---

### 91. A custom connector must send Accept: application/json to a legacy API. The developer added a Set HTTP Header policy, but the backend still does not receive the header on successful calls. The current configuration runs the policy on Response.

What is the best fix?

- **A.** Run the policy on Request ✅
- **B.** Replace it with Set Property
- **C.** Change exists action to skip
- **D.** Move the logic to test connection

> **Answer:** A. Run the policy on Request

The best fix is to run the policy on Request. Microsoft documents that Set HTTP Header can run on Request, Response, or Failure, and specifically states that Request means the policy runs before the request is sent to the backend API. If the goal is to ensure the outbound request includes Accept: application/json, the header must be injected on the request path, not after the response arrives.

This is a runtime-behavior issue rather than a connector-definition issue. The policy template itself is correct, but it is scoped to the wrong execution section, so the header change occurs too late to influence the backend call. That is why the fix is to change the policy section rather than replacing the template.

<sub>Set C · Q56</sub>

---

### 92. A connector has six actions. Only one action needs custom code to change the outgoing request shape and wrap the successful backend response, while the remaining actions should stay codeless to reduce design risk.

Which design should you use?

- **A.** Apply code to every action
- **B.** Recreate the connector from scratch
- **C.** Use a codeless policy template
- **D.** Scope code per operation ✅

> **Answer:** D. Scope code per operation

Microsoft documents that after you add code to a custom connector, you can select the actions and triggers to which the code applies. If no operation is selected, the code applies to all operations, so the best design for this scenario is to scope the code to the one operation that actually needs transformation.

This approach is also cleaner because it keeps the other actions on the codeless path. That aligns with the requirement to reduce design risk and keep unnecessary operations from being affected by transformation logic they do not need.

<sub>Set C · Q57</sub>

---

### 93. A single custom connector contains several actions, and different actions require different transformation logic. You want a supported code design that keeps all actions in one connector instead of splitting the solution across multiple connectors.

Which two choices should you include? (Select TWO.)

- **A.** Upload one script per action
- **B.** Branch on Context.OperationId ✅
- **C.** Use one script file ✅
- **D.** Create one connector per action
- **E.** Store per-action logic in policy templates

> **Answer:** B. Branch on Context.OperationId · C. Use one script file

Microsoft states that only one script file per custom connector is supported. That means a supported multi-operation design must keep the logic in a single file rather than trying to upload separate script files for each action.

Microsoft also documents Context.OperationId, and the sample code uses it to branch to different handlers based on the operation defined in the OpenAPI description. Together, one script file plus branching on Context.OperationId is the supported way to handle different transformation behavior for multiple actions in the same connector.

<sub>Set C · Q58</sub>

---

### 94. A team is building a JavaScript single-page app that is hosted outside Dataverse and calls the Dataverse Web API directly. The design must support cross-origin requests and modern Microsoft Entra authentication without placing secrets in browser code.

Which approach should you use?

- **A.** Ribbon command token reuse
- **B.** Embedded client secret with fetch
- **C.** MSAL.js with Dataverse CORS ✅
- **D.** Basic auth gateway proxy

> **Answer:** C. MSAL.js with Dataverse CORS

MSAL.js with Dataverse CORS support is the best answer because Microsoft documents this as the pattern for JavaScript single-page applications that call Dataverse across domain boundaries. Dataverse specifically enables CORS for SPAs, and the Web API guidance points JavaScript SPA implementations to MSAL.js for authentication.

This also meets the security requirement because secrets should not be embedded in browser code. The documented SPA approach relies on modern Entra-based OAuth patterns rather than hiding a confidential credential in client-side JavaScript, which would be insecure and operationally brittle.

<sub>Set C · Q59</sub>

---

### 95. A user-facing web app will authenticate signed-in users to Dataverse by using OAuth. The team wants the app prepared correctly for delegated user access and does not want insecure shortcuts.

Which two actions should you take? (Select TWO.)

- **A.** Enable anonymous Web API access
- **B.** Use Office365 auth type
- **C.** Register an app in Entra ID ✅
- **D.** Store a client secret in browser code
- **E.** Grant Access Dynamics 365 delegated permission ✅

> **Answer:** C. Register an app in Entra ID · E. Grant Access Dynamics 365 delegated permission

You need to register the application in Microsoft Entra ID and grant the delegated Dataverse permission for user-based access. Microsoft’s Dataverse guidance states that app registration is required before an app can authenticate and access business data, and it also says that when the authenticated user performs operations, the app must have the Access Dynamics 365 as organization users delegated permission.

These two actions establish the supported OAuth foundation for delegated access to Dataverse. They directly align the app with Microsoft’s current Dataverse authentication model instead of depending on older auth types or insecure client-side credential storage.

<sub>Set C · Q60</sub>

---

### 96. A cloud flow receives an optional Approver input from a form. If the input is blank or contains only spaces, the flow must use the manager email instead in a single Compose step.

Which expression pattern should you implement?

- **A.** coalesce with trim and fallback
- **B.** first with split
- **C.** if with empty(trim()) ✅
- **D.** contains with indexOf

> **Answer:** C. if with empty(trim())

if with empty(trim()) is the best pattern because trim() removes leading and trailing whitespace, empty() returns true for an empty string, and if() returns one value when the Boolean test is true and another when it is false. That makes it the safest single-expression approach when the input might be null, blank, or just spaces.

This is also the cleaner flow-step implementation because Compose can create a single output from multiple inputs, including expressions. Using one Compose expression avoids adding unnecessary branching when the requirement is simply to normalize one value before later actions consume it.

<sub>Set C · Q62</sub>

---

### 97. A flow receives a semicolon-delimited Tags field such as HR;IT;Legal. The design must show the first tag in a Compose step, but return None when the field is blank, without adding an extra Condition action.

Which expression pattern should you use?

- **A.** nested branch with Compose
- **B.** if with split and empty ✅
- **C.** coalesce with split and fallback
- **D.** substring with indexOf

> **Answer:** B. if with split and empty

The correct pattern is if with empty and split. Microsoft documents that if() returns one value or another based on a Boolean expression, empty() checks whether a string, array, or object is empty, and split() returns an array of substrings based on a delimiter. Together, those functions let one expression return None for an empty field or the first tag when values exist.

This is a better flow-step design than adding an extra branching action because the requirement is still just value shaping. Microsoft’s data-operations guidance states that Compose can create a single output from multiple inputs, including expressions, which is exactly the role it serves here.

<sub>Set C · Q63</sub>

---

### 98. A flow stores Amount as text and Country as a user-entered string that might arrive as AU, au, or Au. The flow must continue only when Amount is greater than 1000 and Country equals au regardless of casing.

Which two function combinations are required? (Select TWO.)

- **A.** split + first + last
- **B.** guid + concat
- **C.** int + greater ✅
- **D.** formatDateTime + substring
- **E.** toLower + equals ✅

> **Answer:** C. int + greater · E. toLower + equals

int + greater is required because Microsoft documents that int() converts a string version of an integer into an actual integer, and greater() checks whether the first value is greater than the second. Since Amount arrives as text, the flow needs numeric conversion before doing a reliable greater-than comparison.

toLower + equals is also required because Microsoft documents that toLower() converts a string to lowercase, and equals() checks whether two inputs are equivalent. That lets the flow normalize AU, au, or Au before performing the equality test against the constant au.

<sub>Set C · Q64</sub>

---

### 99. A developer uses a Compose step to build a routing code for downstream actions.

Snippet

@if(
  and(
    greater(int(outputs('Get_row')?['body/Amount']), 999),
    equals(toLower(outputs('Get_row')?['body/Region']), 'apac')
  ),
  concat('AP-', formatDateTime(outputs('Get_row')?['body/CreatedOn'], 'yyyyMMdd')),
  'STANDARD'
)
The runtime values are:

Amount = 1500

Region = APAC

CreatedOn = 2026-01-15T08:00:00Z

What is the output?

- **A.** STANDARD
- **B.** AP-15/01/2026
- **C.** APAC-20260115
- **D.** AP-20260115 ✅

> **Answer:** D. AP-20260115

The output is AP-20260115. Microsoft documents that int() converts the text 1500 into an integer, greater() returns true when the first value is greater than the second, toLower() converts APAC to apac, and equals() then returns true for the region check. Because both tests inside and() are true, the if() expression returns the true branch rather than STANDARD.

That true branch uses concat() and formatDateTime(). Microsoft documents that formatDateTime() returns a timestamp in the specified format, and with yyyyMMdd the date portion becomes 20260115. concat() then prefixes that value with AP-, producing AP-20260115.

<sub>Set C · Q65</sub>

---

### 100. A company wants to prevent order creation when a required compliance flag is missing. Users must see a clear message immediately, and the rejection should happen as early as possible to avoid unnecessary rollback cost.

Which implementation approach should you use?

- **A.** Asynchronous PostOperation step
- **B.** Synchronous PreOperation step
- **C.** Business rule plus notification
- **D.** Synchronous PreValidation step ✅

> **Answer:** D. Synchronous PreValidation step

A synchronous PreValidation plug-in is the best choice because Microsoft states that if you need to reject an operation, you should ideally do that in a synchronous plug-in registered in the PreValidation stage. That stage usually occurs before the main database transaction, so rejecting the request there avoids the extra work and cost of rolling back a transaction later.

It also fits the user-experience requirement. Microsoft documents that when a synchronous plug-in throws InvalidPluginExecutionException, the user sees the provided message in the app. That makes PreValidation the strongest design when the business logic must stop the save immediately and show a meaningful error to the user.

<sub>Set C · Q66</sub>

---

### 101. A flow uses this expression in a Compose step to populate reviewer comments: coalesce(triggerBody()?['comments'], 'No comments'). Users often submit the form with the comments field left blank, and the Compose output still appears blank instead of showing No comments.

What is the best fix?

- **A.** if with empty(trim()) ✅
- **B.** coalesce after substring
- **C.** first with split
- **D.** trigger condition rewrite

> **Answer:** A. if with empty(trim())

The best fix is if with empty(trim()). Microsoft documents that coalesce() returns the first non-null value, but empty strings are not null. Microsoft also documents that trim() removes surrounding whitespace and empty() returns true for an empty string. Together, those functions correctly handle blank and whitespace-only comments before deciding whether to return the fallback text.

This is the right correction inside a flow step because the problem is not that the expression is in the wrong action type; it is that the chosen fallback function does not treat blank strings the way the requirement needs. A single Compose expression can still solve it cleanly once the blank-string behavior is handled explicitly.

<sub>Set C · Q67</sub>

---

### 102. A scheduled integration writes shipment data to Dataverse every 15 minutes. It runs without a signed-in user and must authenticate by using the application’s own identity.

Which OAuth approach should you use?

- **A.** Authorization code flow with PKCE
- **B.** On-behalf-of delegation flow
- **C.** Browser implicit token flow
- **D.** Client credentials flow ✅

> **Answer:** D. Client credentials flow

The client credentials flow is the best fit because the process runs as a confidential client and authenticates by using the application’s own credentials rather than impersonating a user. Microsoft’s identity platform documentation describes client credentials as the OAuth flow for service-to-service calls where the app uses its own identity, and Dataverse documentation also calls out OAuth as the preferred authentication method for modern scenarios.

This is also the most secure design for a background job because it avoids forcing a stored user context into an unattended process. Microsoft recommends protecting the app credential carefully and notes that certificate-based authentication is supported for higher assurance in these server-to-server scenarios.

<sub>Set C · Q68</sub>

---

### 103. A maker wants a reusable flow that can be selected from the Run a Child Flow action in a parent flow. The child flow is already inside a solution.

Which trigger must the child flow use?

- **A.** Recurrence
- **B.** Manually trigger a flow ✅
- **C.** When an HTTP request is received
- **D.** When a row is added

> **Answer:** B. Manually trigger a flow

A child flow must use Manually trigger a flow to be selectable by the Run a Child Flow action. Microsoft’s child flow guidance states that child flows must have the Manually trigger a flow trigger, and the parent flow can then call them from the built-in Run a Child Flow action.

This design is what makes the flow solution-aware and reusable inside Power Automate’s parent-child pattern. Other triggers can be valid for normal cloud flows, but they do not meet the documented requirement for a flow that is meant to act as a child flow in this pattern.

<sub>Set C · Q70</sub>

---

### 104. A maker cannot find a reusable flow in the Run a Child Flow picker. The goal is to let a parent flow call it by using the supported child flow pattern, not by using HTTP.

Which two design requirements must be met? (Select TWO.)

- **A.** The child must use Manually trigger a flow ✅
- **B.** The child must use an HTTP request trigger
- **C.** The parent must be in the same solution ✅
- **D.** The child must run from My flows
- **E.** The parent and child should be in different solutions

> **Answer:** A. The child must use Manually trigger a flow · C. The parent must be in the same solution

The child flow must use Manually trigger a flow, because Microsoft explicitly states that child flows shown in the Run a Child Flow action must have that trigger. Without it, the flow does not meet the required child-flow shape.

The parent must also be in the same solution as the child. Microsoft’s child flow documentation says to build the parent flow in the same solution, and the reusable-code guidance repeats the recommendation to create the parent and child flows directly in the same solution. Those two requirements together are what enable the supported discovery and reuse pattern.

<sub>Set C · Q71</sub>

---

### 105. A child flow uses SharePoint and Outlook actions and is called from a parent flow in a solution. The parent can see the child flow, but test runs fail with an error saying the flow can't be used as a child workflow because child workflows support embedded connections.

What is the best fix?

- **A.** Add a recurrence trigger to the child
- **B.** Move the parent out of the solution
- **C.** Use embedded connections in the child ✅
- **D.** Replace the child with an HTTP trigger

> **Answer:** C. Use embedded connections in the child

The best fix is to configure the child flow to use embedded connections. Microsoft’s child flow guidance says that when a child flow uses anything other than built-in actions or the Microsoft Dataverse connector, you must edit Run only users and select Use this connection for each connection instead of Provided by run-only user.

Microsoft also states that connections cannot currently be passed from the parent flow to the child flow, and if you do not embed the child flow’s connections, you receive an error saying that child workflows support only embedded connections. That wording matches the incident exactly, which makes this the strongest fix.

<sub>Set C · Q73</sub>

---

### 106. A maker enters a GitHub URL while creating a custom connector because the API definition is stored in a repository. The import request reaches the address, but the returned content is an HTML repository page and no operations are generated.

What should you do first?

- **A.** Use the raw OpenAPI URL ✅
- **B.** Rebuild it as a PCF control
- **C.** Export a managed solution
- **D.** Register a custom API

> **Answer:** A. Use the raw OpenAPI URL

Use the raw OpenAPI URL because the connector import process needs the actual API definition content, not the rendered repository webpage. If the supplied GitHub address points to the HTML viewing page instead of the raw definition document, the importer cannot parse paths and operations correctly.

This is a classic import-source mismatch. The problem is not that GitHub is unsupported; it is that the wrong representation of the GitHub-hosted file was provided. The first correction is to point the import step at the raw OpenAPI document itself.

<sub>Set D · Q18</sub>

---

### 107. A canvas app submits a request that can take several minutes to finish. The team does not want the caller to wait for completion, but they do want a standard way to track progress and retrieve final status later.

Snippet

[Function("StartOrderProcess")]
public static async Task<HttpResponseData> StartOrderProcess(
    [HttpTrigger(AuthorizationLevel.Function, "post")] HttpRequestData req,
    [DurableClient] DurableTaskClient client)
{
    string instanceId =
        await client.ScheduleNewOrchestrationInstanceAsync("OrderOrchestrator");

    return await client.CreateCheckStatusResponseAsync(req, instanceId);
}
What is the main benefit of this pattern for the Power Platform caller?

- **A.** Immediate final result
- **B.** Async status polling ✅
- **C.** Transaction rollback support
- **D.** Client-side offline caching

> **Answer:** B. Async status polling

Async status polling is correct because this pattern starts a durable orchestration instance and returns a check-status response instead of waiting for the full workload to complete inside the original HTTP request. Microsoft documents Durable Functions management APIs and HTTP features for starting orchestrations and then querying their status afterward, which is exactly the behavior this snippet enables.

That is the right pattern for Power Platform callers when work may continue beyond the safe lifetime of a single synchronous request. Instead of forcing the app or flow to block until completion, the caller gets a tracking-friendly response and the orchestration continues durably in the background.

<sub>Set D · Q23</sub>

---

### 108. A claims-processing solution starts from a Dataverse event and must call multiple external services before writing the final outcome back to Dataverse. The work can run for several minutes, must survive retries and restarts, and users need a way to check progress without holding open the original request.

Which implementation should you recommend?

- **A.** Power Automate cloud flow
- **B.** PostOperation plug-in
- **C.** Client API script
- **D.** Durable Functions orchestration ✅

> **Answer:** D. Durable Functions orchestration

Durable Functions orchestration is the best fit because Microsoft documents Durable Functions as an Azure Functions extension for building reliable, stateful workflows where the runtime manages state, checkpoints, retries, and recovery so workflows can run reliably for long periods. That matches the exact requirements in the stem: multi-step processing, long duration, resilience, and status-aware execution outside the original request path.

It is also the strongest Power Platform design choice here because the work should not remain tied to a Dataverse transaction or UI session. Microsoft’s comparison guidance distinguishes Azure Functions as a code-oriented serverless compute service, and Durable Functions specifically as the code-first way to build orchestrations when you need long-running, stateful behavior rather than short in-transaction logic.

<sub>Set D · Q30</sub>

---

### 109. A plug-in registered on the Update message must compare the incoming Target value with the previous stored value before the core operation is written. The team wants to avoid an extra Dataverse retrieve for performance reasons.

Which image should you configure?

- **A.** Post Image on Create step
- **B.** No image; retrieve current row in code
- **C.** Pre Image on Update step ✅
- **D.** Post Image on Delete step

> **Answer:** C. Pre Image on Update step

A Pre Image on an Update step is the best fit because the execution context for Update contains the changed values in Target, not a full copy of the original row. Microsoft specifically recommends using a pre-entity image when you need the previous value during an update comparison, rather than issuing an extra retrieve in plug-in code.

This also aligns with the timing requirement. A Pre Image gives you a snapshot of the primary table before the core operation, and Microsoft exposes that snapshot through PreEntityImages in the execution context. That is exactly the data shape you need when the comparison must happen before the write completes.

<sub>Set D · Q34</sub>

---

### 110. You are reviewing an Update plug-in that compares selected values before and after an operation. The goal is to keep execution efficient and make image access reliable.

Which two design choices should you make? (Select TWO.)

- **A.** Register only required columns in each image ✅
- **B.** Select all columns for future reuse
- **C.** Use the entity alias to read the image ✅
- **D.** Replace images with an OrganizationService retrieve on every execution
- **E.** Expect a Pre Image on Create

> **Answer:** A. Register only required columns in each image · C. Use the entity alias to read the image

Registering only the required columns is the correct performance choice. Microsoft warns that the default behavior when creating an entity image is to select all columns and says not to use that default because it negatively affects performance. The image should contain only the columns that the plug-in logic actually needs.

Using the entity alias to read the image is also correct. Microsoft explains that when you define an entity image, you specify an alias and then use that alias as the key when accessing PreEntityImages or PostEntityImages in code. That is the supported implementation pattern for reliable image access.

<sub>Set D · Q36</sub>

---

### 111. A developer wants to compare the old and saved name values during an account update.

Snippet

if (context.MessageName == "Update")
{
    var before = context.PreEntityImages["acc"];
    var after = context.PostEntityImages["acc"];

    var oldName = before.GetAttributeValue<string>("name");
    var newName = after.GetAttributeValue<string>("name");
}
The step is registered on Update, PreOperation, and currently has only a Pre Image with alias acc.
What registration change is required?

- **A.** Add a second Pre Image
- **B.** Use PostOperation with Post Image ✅
- **C.** Read ParentContext instead
- **D.** Keep PreOperation and query the row after save

> **Answer:** B. Use PostOperation with Post Image

The missing piece is the Post Image on a PostOperation step. Microsoft states that Post Images represent the row after the core operation has completed, and that you can only have a Post Image for steps registered in the PostOperation stage. Because the code wants both before and after, the current registration cannot satisfy the design.

The alias part of the code is already fine because Microsoft expects images to be accessed by the alias defined at registration time. The real issue is image availability, not syntax. Moving the step to PostOperation and adding a Post Image is the registration change that makes the after snapshot available through context.PostEntityImages["acc"].

<sub>Set D · Q37</sub>

---

### 112. A team needs a plug-in registration that compares original and saved values after an Update completes. The plug-in should minimize payload size and avoid unnecessary retrieves.

Exhibit 1

Which candidate is the best fit?

- **A.** Candidate A — Update PostOperation ✅
- **B.** Candidate B — Update PreOperation all columns
- **C.** Candidate C — Create PostOperation with both images
- **D.** Candidate D — Delete PostOperation with both images

> **Answer:** A. Candidate A — Update PostOperation

Candidate A is the best fit because it uses the Update message, the PostOperation stage, and both a Pre Image and a Post Image with a narrow column list. Microsoft states that on an Update step registered in PostOperation you can have both image types, and it also warns that images should include only the columns required by the plug-in logic. That is exactly what Candidate A does.

The other candidates each violate a key rule. Candidate B uses all columns and places the step in PreOperation even though the requirement is to compare original and saved values after completion. Candidate C expects a Pre Image on Create, and Candidate D expects a Post Image on Delete, both of which Microsoft says are not available.

<sub>Set D · Q40</sub>

---

### 113. A development lead wants the team to stop hand-building connector actions whenever an existing API contract already exists. They want to use supported import entry points that align directly with existing definition sources rather than unrelated Power Platform artifacts.

Which TWO starting points directly support importing an existing API definition into a custom connector? (Select TWO.)

- **A.** Plug-in registration data
- **B.** Managed solution deployment package
- **C.** GitHub OpenAPI source ✅
- **D.** Connection reference record
- **E.** Azure service target ✅

> **Answer:** C. GitHub OpenAPI source · E. Azure service target

GitHub OpenAPI source and Azure service target are the two best answers because both align to supported starting points for bringing existing API definitions into a custom connector workflow. They represent real definition origins rather than unrelated deployment or runtime artifacts.

This distinction matters in ALM and maintainability. A connector import path should begin from the actual API description or service-backed definition source, not from surrounding platform metadata that exists for packaging, registration, or environment binding.

<sub>Set D · Q41</sub>

---

### 114. A development team already maintains a valid OpenAPI document for an internal REST API in a GitHub repository. They want to create a custom connector with the least manual operation design work and keep the definition aligned to the existing source artifact.

Which import source should they use?

- **A.** Blank connector design wizard
- **B.** Dataverse custom API
- **C.** Manual request setup
- **D.** GitHub OpenAPI import ✅

> **Answer:** D. GitHub OpenAPI import

GitHub OpenAPI import is the best fit because the team already has the API definition stored in GitHub and wants to reuse that existing artifact directly. This avoids recreating operations, request schemas, and response metadata by hand inside the custom connector designer.

This is exactly the scenario where definition import is stronger than manual authoring. The connector should start from the source-controlled API description so the imported actions reflect the documented contract instead of a separately maintained manual version.

<sub>Set D · Q43</sub>

---

### 115. A team exposes business logic through an Azure-hosted API and wants to generate the starting connector definition directly from that Azure implementation path. They do not want to download and manage a separate definition file first if the platform can derive the connector from the Azure service path.

Which starting point should they choose?

- **A.** GitHub repository import
- **B.** Azure service import ✅
- **C.** Blank custom connector wizard
- **D.** Virtual table provider

> **Answer:** B. Azure service import

Azure service import is the best answer because the requirement is specifically to start from an Azure-hosted implementation without first switching to a separate manual definition workflow. When the API is already represented through a supported Azure service path, importing from Azure is the most direct and operationally aligned starting point.

This is stronger than a blank connector because the team wants existing service metadata to drive the initial connector definition. It is also stronger than GitHub in this case because the stem emphasizes starting from the Azure service itself, not from a repository-managed OpenAPI file.

<sub>Set D · Q44</sub>

---

### 116. A developer receives an API contract from another team and wants to reuse it as the starting point for a custom connector instead of creating actions manually. The file already describes paths, operations, and a security scheme.

Snippet

swagger: '2.0'
info:
  title: Expense API
  version: '1.0'
host: api.contoso.com
basePath: /v1
schemes:
  - https
paths:
  /expenses:
    get:
      operationId: GetExpenses
      responses:
        '200':
          description: Success
securityDefinitions:
  api_key:
    type: apiKey
    name: x-api-key
    in: header
Which connector creation approach best matches this artifact?

- **A.** Azure service selector
- **B.** Blank custom connector wizard
- **C.** OpenAPI file import ✅
- **D.** Plug-in assembly registration

> **Answer:** C. OpenAPI file import

OpenAPI file import is correct because the snippet is an API definition artifact that already describes the service contract. It includes the structural elements a custom connector import flow expects, such as paths, operations, and security metadata, so it should be reused directly rather than recreated manually.

This is the exact value of importing from an existing definition. The developer can start from the described contract and then refine connector metadata if needed, instead of rebuilding the same operation surface from scratch in the designer.

<sub>Set D · Q46</sub>

---

### 117. A team is building a custom API whose main logic runs in a Dataverse plug-in. The operation accepts scalar inputs, updates multiple Dataverse rows, and must be callable from a cloud flow without selecting a bound row first.

Which custom API design should the team choose?

- **A.** Entity-bound custom Function
- **B.** Global custom Function
- **C.** Private custom Action
- **D.** Global Action ✅

> **Answer:** D. Global Action

The best choice is Global Action. The scenario says the operation updates data, which rules out a Function because Microsoft defines a Function as an HTTP GET operation that returns data without making changes. The scenario also says it must be callable from a cloud flow, and Microsoft states that the Microsoft Dataverse connector currently enables performing actions, so if the operation must be performed by using Power Automate, the custom API should be created as an Action.

It should also be Global because the scenario explicitly says the caller should not need to select or pass a bound row first. Microsoft documents that custom APIs can be composed as Global when you do not need entity or entity-collection binding. That makes Global Action the cleanest design for an unbound, data-changing operation that will be invoked from a cloud flow.

<sub>Set D · Q47</sub>

---

### 118. A developer is implementing the main operation for a custom API. The custom API defines EstimatedValue as a request parameter and ApprovalResult as a response property.

Snippet

var context =
    (IPluginExecutionContext)serviceProvider.GetService(typeof(IPluginExecutionContext));

var amount = (Money)context.InputParameters["EstimatedValue"];
var approved = amount.Value <= 5000m;

context.InputParameters["ApprovalResult"] = approved;
What is the best fix?

- **A.** Write ApprovalResult to OutputParameters ✅
- **B.** Move EstimatedValue into SharedVariables
- **C.** Return ApprovalResult in PostEntityImages
- **D.** Read ApprovalResult from ParentContext first

> **Answer:** A. Write ApprovalResult to OutputParameters

The fix is to write the response property to OutputParameters. Microsoft documents that custom API request parameter values are included in InputParameters, and the values for response properties must be set in OutputParameters. The current code reads the request correctly but writes the response into the wrong collection.

That distinction is important in Dataverse plug-in development generally, not just for custom APIs. Microsoft’s execution-context guidance identifies InputParameters and OutputParameters as two of the most important collections in the execution context. In this case, the custom API response contract is populated through OutputParameters, so the code should set context.OutputParameters["ApprovalResult"] = approved;.

<sub>Set D · Q48</sub>

---

### 119. A team wants to expose one plug-in-backed custom API as a workflow action. They do not want to redesign the request or response contract after creation.

Exhibit 1

Which design can be enabled for workflow without redesign?

- **A.** ScoreAccount
- **B.** ReserveStock ✅
- **C.** BatchScore
- **D.** ExportOrders

> **Answer:** B. ReserveStock

ReserveStock is the only design that fits Microsoft’s workflow restrictions for custom APIs. Microsoft states that when Enabled for Workflow is true, the custom API cannot be a Function, and the supported request and response property types are limited to a specific list. Microsoft also states that EntityReference can be used only when the custom API is bound to an entity, which is exactly what the exhibit shows for ReserveStock.

The other three designs each violate a documented workflow limitation. ScoreAccount is invalid because it is a Function, BatchScore is invalid because EntityCollection is not supported, and ExportOrders is invalid because StringArray is not supported. The exhibit matters because the answer depends on matching multiple contract properties to the workflow rules, not on any single column alone.

<sub>Set D · Q49</sub>

---

### 120. A developer attached a plug-in type directly to a custom API as the main operation. The custom API was created with Allowed Custom Processing Step Type set to Sync and Async, and the team now needs both Plug-in Profiler debugging and secure step configuration.

What should the developer do next?

- **A.** Enable Async Only processing
- **B.** Register a PreValidation step
- **C.** Use a PostOperation step ✅
- **D.** Set secure configuration on the main operation plug-in

> **Answer:** C. Use a PostOperation step

The best next step is to use a PostOperation step. Microsoft states that the main stage implementation for the custom API plug-in is not currently available in the Plug-in Registration Tool for profiler-based debugging, and the documented workaround is to register the plug-in type on the PostOperation stage of the message created for the custom API.

Microsoft also states that you cannot pass secure or unsecure configuration to the main-operation plug-in for the custom API. The documented workaround is again to register the plug-in on the PostOperation stage, where step configuration works as usual. Because the API in the scenario was created with Sync and Async custom processing steps allowed, this workaround is available; Microsoft also notes that this setting cannot be changed after the custom API is saved.

<sub>Set D · Q50</sub>

---

### 121. An external system identifies account rows by the accountnumber alternate key. The integration must update the existing row and must fail if no matching row exists. Which request design should you use?

- **A.** POST to entity set with deep insert
- **B.** PATCH with If-None-Match: *
- **C.** DELETE by alternate key
- **D.** PATCH with If-Match: * ✅

> **Answer:** D. PATCH with If-Match: *

PATCH is the Web API method used for updating table rows, and Dataverse treats a PATCH request against a keyed URL as an upsert unless you force update-only behavior. Microsoft states that adding If-Match: * ensures the PATCH request is treated as an Update operation and returns 404 Not Found when no matching row exists.

That makes this the best design when the caller knows an alternate key and must never create a new row by accident. Alternate keys are specifically intended for integration scenarios where the primary key is unknown, and the Web API supports using them directly in the request URL for PATCH, POST, and DELETE operations.

<sub>Set D · Q51</sub>

---

### 122. A fulfillment integration must submit 18 mixed Dataverse operations in one HTTP call. The set includes creates, updates, and deletes on standard tables, and the business requires all operations to succeed or fail together.

Which approach should you use?

- **A.** Deep insert on one root POST
- **B.** $batch with a change set ✅
- **C.** Parallel PATCH requests
- **D.** GET requests inside $batch

> **Answer:** B. $batch with a change set

A $batch request with a change set is the correct design because Microsoft states that batch requests can group multiple operations into a single HTTP request, and change sets allow those grouped operations to be included as a single transaction. That directly matches the requirement for one HTTP call and all-or-nothing behavior across mixed create, update, and delete operations.

Deep insert is easier when the problem is creating related rows in one operation, but this scenario includes mixed CRUD operations rather than one create graph. Microsoft explicitly distinguishes batch requests from deep insert and notes that creating associated entities in one operation is a separate pattern, which is why a transactional change set is the stronger fit here.

<sub>Set D · Q52</sub>

---

### 123. A nightly integration uses PATCH against alternate-key URLs so that missing rows can be created and existing rows can be updated. The caller must also tell whether Dataverse created or updated the row, while keeping the response as small as possible.

Which two request choices should you make? (Select TWO.)

- **A.** Repeat alternate key columns in body
- **B.** Add Prefer: return=representation ✅
- **C.** Add If-Match: *
- **D.** Omit $select from the URL
- **E.** Add $select=accountid ✅

> **Answer:** B. Add Prefer: return=representation · E. Add $select=accountid

Prefer: return=representation is required because Microsoft states that, for POST and PATCH, it causes Dataverse to return data and changes the status behavior so the caller can distinguish 201 Created from 200 OK. That directly supports the requirement to know whether the operation created or updated the row.

$select=accountid is the complementary design choice because Microsoft recommends limiting returned columns to optimize performance, and the upsert guidance specifically warns that return=representation adds an extra retrieve operation. Using a minimal $select keeps the response small while still returning enough information to identify the affected row.

<sub>Set D · Q53</sub>

---

### 124. A developer shared the following request used to synchronize an account by alternate key.

Snippet

PATCH /api/data/v9.2/accounts(accountnumber='ACC-1001') HTTP/1.1
Accept: application/json
OData-MaxVersion: 4.0
OData-Version: 4.0
Content-Type: application/json

{
  "name": "Alpine Ski House"
}
The team wants this request to fail instead of creating a new row when no matching account exists. What should you add?

- **A.** If-Match: * ✅
- **B.** If-None-Match: *
- **C.** Prefer: return=representation
- **D.** primarycontactid@odata.bind

> **Answer:** A. If-Match: *

If-Match: * is the required change because Microsoft states that a PATCH request against a keyed Web API URL behaves like an upsert unless this header is included. When If-Match: * is present and no resource matches the key values in the URL, Dataverse returns 404 Not Found instead of creating a row.

That is exactly the safeguard the team wants. The alternate key in the URL is already a supported way to identify the target row, so the missing design element is not the resource reference but the header that forces update-only semantics.

<sub>Set D · Q54</sub>

---

### 125. A team is deciding whether a new background process should be implemented as a Durable Functions-based workload instead of client logic, business rules, or transaction-bound server logic. The process must continue reliably across waits and resume later when an outside system sends a callback.

Which TWO requirements most strongly support Durable Functions for this design? (Select TWO.)

- **A.** Stateful checkpointed workflow ✅
- **B.** Form tab visibility rules
- **C.** External event resumption ✅
- **D.** Synchronous Dataverse validation
- **E.** Column recommendation logic

> **Answer:** A. Stateful checkpointed workflow · C. External event resumption

Stateful checkpointed workflow and external event resumption are the two strongest indicators because Microsoft documents Durable Functions as a way to build reliable, stateful workflows, and it specifically supports waiting for external events to update an orchestration instance. Those are core Durable capabilities and directly match the problem described in the stem.

The other requirements point to different extension points. UI changes and guidance belong closer to the app experience, while synchronous validation belongs in transaction-bound server logic. Durable Functions becomes the best answer when the workload must persist state over time, survive waits, and resume later without relying on a continuously open request.

<sub>Set D · Q56</sub>

---

### 126. A finance team has an Update plug-in that runs in PostOperation and publishes an integration event when creditlimit changes. The event payload must include both the old value and the saved value, and the design must avoid unnecessary service calls.

Which image design should you use?

- **A.** Target entity and SharedVariables
- **B.** Pre Image with an extra retrieve
- **C.** Post Image on a PreOperation step
- **D.** Pre and Post Images ✅

> **Answer:** D. Pre and Post Images

Pre and Post Images are the best design because the requirement is to include both the old value and the saved value from the same update execution. Microsoft documents that Pre Images represent the row before the main operation and Post Images represent the row after the main operation, which makes them the natural before-and-after pair for this pattern.

The stage choice in the scenario also matters. Microsoft states that for an Update step registered in PostOperation, you can have both a Pre Image and a Post Image, and that using images is more efficient than retrieving the row just to compare attributes. That matches the integration requirement and the performance constraint at the same time.

<sub>Set D · Q57</sub>

---

### 127. A model-driven app calls an HTTP-triggered Azure Function that performs document generation and downstream reconciliation. Users start receiving HTTP 502 errors when the processing reaches about four minutes, even though the function keeps running after the response fails.

What should you do first?

- **A.** Durable HTTP async pattern ✅
- **A.** Durable HTTP async pattern is the correct choice because it allows the Azure Function to continue running even after the initial HTTP response has failed. This pattern ensures that the function can complete its processing without being interrupted by the HTTP 502 errors, providing a more reliable and robust solution for long-running processes. ✅
- **B.** Raise functionTimeout and keep HTTP synchronous
- **B.** Raise functionTimeout and keep HTTP synchronous may not be the most effective solution in this scenario. Increasing the function timeout may help prevent premature termination of the function, but it does not address the underlying issue of HTTP 502 errors and may not provide a scalable solution for long-running processes.
- **C.** Client-side polling plus retry
- **C.** Client-side polling plus retry involves the client continuously polling the function and retrying the request if it fails. While this approach may help mitigate the impact of HTTP 502 errors, it does not address the root cause of the issue and may introduce additional complexity to the solution.
- **D.** PreOperation Dataverse plug-in
- **D.** PreOperation Dataverse plug-in is not directly related to resolving HTTP 502 errors in an Azure Function. PreOperation plug-ins in Dataverse are used for executing custom business logic before the data is saved to the database and are not suitable for handling long-running processes in an external function.

> **Answer:** A. Durable HTTP async pattern

Durable HTTP async pattern is the best first fix because Microsoft documents a hard 230-second response limit for HTTP-triggered functions due to Azure Load Balancer behavior. Microsoft explicitly recommends async patterns for long-running functions and returning a location where the caller can check status instead of keeping the original HTTP request open.

That makes this a design-placement issue, not just a timeout-setting issue. If a Power Platform caller needs to start long-running work, the safer pattern is to defer the actual processing and return status information immediately, allowing the durable backend workflow to continue independently.

<sub>Set D · Q58</sub>

---

### 128. A Power Platform solution must start a long-running fulfillment process without blocking the original caller. The design must return quickly, run durable backend work, and write the final outcome back to Dataverse after processing completes.

Steps

Update the Dataverse process record with the final outcome.

Start the durable orchestration from the incoming request.

Return a tracking/status response to the caller.

Run activity functions, retries, and any external waits.

What is the correct order?

- **A.** 3 → 2 → 4 → 1
- **B.** 4 → 2 → 3 → 1
- **C.** 2 → 3 → 4 → 1 ✅
- **D.** 2 → 4 → 1 → 3

> **Answer:** C. 2 → 3 → 4 → 1

The correct order is 2 → 3 → 4 → 1. First, the request starts the durable orchestration. Next, the caller receives a tracking or status response immediately. Then the orchestration runs its activities, retries, and waits as needed, and only after the backend work completes does the solution write the final result back to Dataverse.

This sequence matches Microsoft’s durable long-running pattern more closely than holding the caller open until everything is finished. The orchestration is started asynchronously, status can be queried later, and durable runtime features handle the long-running workflow before the final state is persisted for the Power Platform solution.

• 2 is first because the orchestration must be scheduled before there is any instance to monitor or any durable workflow to execute. Microsoft documents orchestration start as the action that writes a message to the configured durable backend and initiates the async process.

• 3 is second because the caller should get a status-capable response immediately after startup rather than waiting for the entire long-running workload to complete in the original request. This is the durable async pattern Microsoft recommends for long-running HTTP scenarios.

• 4 is third because the actual long-running work, retries, timers, and external waits happen inside the orchestration after it has been started and after the caller has already been released. Microsoft documents retries, timers, and external events as orchestration features for these longer workflows.

• 1 is last because the final Dataverse update represents the completed outcome of the backend process, not the start of it. Persisting the final result belongs at the end of the orchestration path.

<sub>Set D · Q59</sub>

---

### 129. A team wants a Dataverse action in a cloud flow to run by using a non-human identity. The Microsoft Entra app registration already exists.

Which component must you create in the target environment before the Dataverse connection can use that identity?

- **A.** Environment security group membership
- **B.** Connection reference in solution
- **C.** Dataverse application user ✅
- **D.** Tenant-wide admin consent grant

> **Answer:** C. Dataverse application user

For Dataverse actions in cloud flows, the service principal by itself isn't enough. Microsoft documents that you must create an application user in Dataverse and associate it to the Microsoft Entra service principal before the Dataverse connection can authenticate in the environment by using that identity.

This is the key environment-level identity bridge. The Entra app registration gives you the tenant identity, but the Dataverse application user is what lets that identity exist inside the environment and receive Dataverse permissions for tables and operations.

<sub>Set D · Q60</sub>

---

### 130. A non-solution cloud flow uses existing OAuth connections. The current owner is leaving the organization, and the team wants a Microsoft Entra service principal application user to own and run the flow instead. The flow must continue using its existing connections after the ownership change.

What should you do before changing the owner?

- **A.** Convert the flow to a managed solution
- **B.** Add the service principal as a co-owner
- **C.** Assign Environment Maker and retry ownership
- **D.** Share connections with the app user ✅

> **Answer:** D. Share connections with the app user

Microsoft documents that for a non-solution flow, the connections must be shared with the service principal application user so the flow can successfully run after the ownership change. That is the specific step that preserves connection usability for a non-solution cloud flow.

This is also one of the main distinctions between solution and non-solution flow behavior in the service-principal guidance. Microsoft further notes that a service principal application user can own and run a flow, but the preparation steps include connection sharing for non-solution flows before the flow is turned on under that owner.

<sub>Set D · Q61</sub>

---

### 131. A developer is preparing a Dataverse connection in a cloud flow by using Connect with service principal.

Which two identity objects must already exist? (Select TWO.)

- **A.** Microsoft Entra service principal ✅
- **B.** Dataverse application user ✅
- **C.** Environment security group
- **D.** Flow co-owner assignment
- **E.** Premium per-user Power Automate license

> **Answer:** A. Microsoft Entra service principal · B. Dataverse application user

Microsoft’s Dataverse connection guidance requires both the Microsoft Entra service principal and the Dataverse application user associated to that service principal. The Entra service principal provides the app identity in the tenant, and the Dataverse application user represents that identity inside the environment where the flow runs.

Those are the two identity objects that make the pattern work. Microsoft then instructs you to grant the application user sufficient Dataverse permissions and use the Dataverse connector option to connect with a service principal, which builds on those prerequisites rather than replacing them.

<sub>Set D · Q62</sub>

---

### 132. A team changed the owner of a non-solution cloud flow to a service principal application user. The flow uses an existing OAuth connection.

Configuration

Flow type: Non-solution cloud flow
Owner: contoso-flow-sp-appuser
Connection type: OAuth
Connection shared with app user: No
Flow status: Turned on
What should you change first?

- **A.** Add a connection reference to the solution
- **B.** Share the connection with the app user ✅
- **C.** Add the service principal as co-owner
- **D.** Recreate the flow as an instant flow

> **Answer:** B. Share the connection with the app user

The configuration shows the critical issue directly: the flow is non-solution, uses an OAuth connection, and that connection hasn't been shared with the service principal application user. Microsoft states that non-solution flows require connections to be shared with the service principal application user so the flow can run successfully under that owner.

This is also consistent with Microsoft’s connection-reference guidance, which notes that OAuth connections can be explicitly shared with a user representing a service principal. In this case, the ownership change happened, but the connection-sharing prerequisite did not.

<sub>Set D · Q63</sub>

---

### 133. A non-solution cloud flow was transferred to a service principal application user and then turned on. The Dataverse steps still fail at runtime. The team confirms that the Microsoft Entra app exists, the Dataverse application user exists, and the application user already has a Dataverse security role.

What should you check first?

- **A.** Grant Microsoft Graph delegated permissions
- **B.** Reassign the flow to a licensed human owner
- **C.** Add the application user as a co-owner
- **D.** Share the connection with the app user ✅

> **Answer:** D. Share the connection with the app user

Given that the Entra app, Dataverse application user, and Dataverse security role are already in place, the most likely remaining gap for a non-solution flow is connection sharing. Microsoft’s service-principal-owned-flow guidance says that non-solution flows require the connections to be shared with the service principal application user so the flow can run successfully.

This troubleshooting sequence is important because teams often verify the identity objects and Dataverse permissions first, but the runtime still fails if the connection itself is not shared. Microsoft separates environment identity setup from connection enablement, and both have to be correct for the non-solution pattern to work.

<sub>Set D · Q64</sub>

---

### 134. A cloud flow calls a payroll API. The response contains salary and bank-account data, and support staff who review failed runs must not see that returned content in run history.

Which setting should you enable on the action?

- **A.** Exponential retry policy
- **B.** Static results setting
- **C.** Secure outputs ✅
- **D.** Action tracked properties

> **Answer:** C. Secure outputs

Secure outputs is the best answer because Microsoft documents that the Secure inputs and Secure outputs feature ensures sensitive information isn't visible in run history or audit logs. In the designer, these are Security settings on the action, and Secure outputs is the control that protects the returned data from being exposed when someone inspects the run.

This question is specifically about protecting response content after the action runs, not about reliability or diagnostics. Retry policy affects transient-failure handling, static results are for testing behavior, and tracked properties add observability metadata; none of those settings redact a sensitive response payload from run history.

<sub>Set D · Q65</sub>

---

### 135. A solution-aware cloud flow posts to an external API. The base URL varies by environment, the client secret must be rotated centrally, and the team does not want to edit the flow after deployment.

Which design should the team choose?

- **A.** Text environment variable with current value
- **B.** Secure outputs on HTTP action
- **C.** Hard-coded header secret
- **D.** Key Vault secret variable ✅

> **Answer:** D. Key Vault secret variable

A Key Vault secret variable is the best design because Microsoft documents that environment variables are used to separate configuration from the components that consume it across environments, and that the Secret data type is backed by Azure Key Vault. Microsoft also states that the actual secret stays in Azure Key Vault while the environment variable references the secret location.

That directly matches all three constraints in the stem: environment-specific values, centralized secret management, and no need to edit the flow after deployment. Microsoft’s guidance also recommends avoiding highly sensitive data stored directly in ordinary environment variables and using Azure Key Vault for secure secret handling instead.

<sub>Set D · Q66</sub>

---

### 136. A manual cloud flow accepts a password from the user and then calls a connector that returns a session token. The team wants to reduce exposure of both the inbound secret and the returned token in run history.

Which two actions should the team take? (Select TWO.)

- **A.** Copy the password into Compose
- **B.** Use Sensitive text input ✅
- **C.** Store the password as Text variable
- **D.** Enable Secure outputs ✅
- **E.** Track the token value

> **Answer:** B. Use Sensitive text input · D. Enable Secure outputs

The correct pair is B and D. Microsoft says some inputs like passwords should be omitted from logs and documents the use of sensitive text inputs for confidential values. Microsoft also says Secure inputs and Secure outputs prevent sensitive connector content from being shown in logs and run history.

These two controls cover both exposure points in the scenario. The password is best handled as sensitive input at entry, while the returned session token should be protected by secure outputs on the action that receives it.

<sub>Set D · Q67</sub>

---

### 137. You created a custom API and registered the assembly that contains the class for the main operation. You now need Dataverse to invoke that class when the custom API message runs.

Which field should you set?

- **A.** Execute Privilege Name
- **B.** Allowed Custom Processing Step Type
- **C.** Plug-in Type ✅
- **D.** Bound Entity Logical Name

> **Answer:** C. Plug-in Type

The correct field is Plug-in Type. Microsoft states that after you register the assembly, you set the Plugin Type lookup on the custom API so it points to the registered type that implements the main operation. Microsoft also states that if you do not set PluginTypeId, users can still invoke the custom API, but there is no main-operation plug-in logic to process the request.

That is the key distinction in this question. Execute Privilege Name secures execution, Allowed Custom Processing Step Type controls whether other steps can be registered, and Bound Entity Logical Name defines binding context for non-global APIs. None of those settings associates the custom API with the compiled class that performs the main operation.

<sub>Set D · Q68</sub>

---

### 138. A team uses the same solution cloud flow in development, test, and production. They want the API credential stored securely and rotated without changing the flow logic.

Configuration

Environment variable: ERP_ApiKey
Data type: Text
Default value: 7f3b...
Current value: 9a1d...
Used in: HTTP Authorization header
Which change best improves the design?

- **A.** Secret environment variable ✅
- **B.** Text variable with retry policy
- **C.** Connection reference swap
- **D.** Compose action copy

> **Answer:** A. Secret environment variable

The best change is Secret environment variable. Microsoft documents that environment variables support a Secret data type, and when Secret is selected, Azure Key Vault is the supported secret store that Power Platform uses for this pattern. Microsoft also states that the actual secret remains in Azure Key Vault while the environment variable references the secret location.

That makes this a direct improvement over the configuration shown, where a sensitive credential is being stored as Text and used in an HTTP authorization header. A secret-backed environment variable keeps the credential in the correct store while preserving the ALM advantages of environment variables across environments.

<sub>Set D · Q69</sub>

---

### 139. A maker creates a Secret environment variable backed by Azure Key Vault. In a solution cloud flow, the variable does not appear in the dynamic content selector, and the maker assumes the secret variable was created incorrectly.

What should the maker do next?

- **A.** Convert the variable to Text
- **B.** Reopen the flow designer
- **C.** Use RetrieveEnvironmentVariableSecretValue ✅
- **D.** Add a second current value

> **Answer:** C. Use RetrieveEnvironmentVariableSecretValue

The maker should use RetrieveEnvironmentVariableSecretValue. Microsoft documents that environment variables referencing Azure Key Vault secrets are not currently available from the dynamic content selector for use in Power Automate flows. Microsoft also provides the supported flow pattern: call the Dataverse Perform an unbound action action named RetrieveEnvironmentVariableSecretValue, then use the returned EnvironmentVariableSecretValue in the downstream step.

This is why the missing dynamic-content token does not mean the secret variable is broken. It is a current platform limitation with a documented workaround, and Microsoft further recommends enabling secure outputs on that retrieval action and secure inputs and outputs on the consuming HTTP action to avoid exposing the secret in run history.

<sub>Set D · Q70</sub>

---

### 140. A custom integration retrieves active accounts through the Dataverse Web API. Support traces show that each response body is much larger than expected, even though the consumer uses only accountid, name, and the primary contact lookup value.

What should you change first?

- **A.** Add Prefer: return=representation
- **B.** Replace GET with POST
- **C.** Add $select=accountid,name,_primarycontactid_value ✅
- **D.** Move the request into $batch

> **Answer:** C. Add $select=accountid,name,_primarycontactid_value

The best first fix is to add $select so the query returns only the properties the integration actually uses. Microsoft explicitly states that when you query data, you should limit the amount of data returned to optimize performance, and that omitting $select causes Dataverse to return all properties.

This is also the lowest-risk change because it reduces payload size without changing the logical result set. The query guidance further notes that $top and paging control row counts, but column trimming through $select is the direct answer when the issue is oversized response bodies caused by unnecessary properties.

<sub>Set D · Q73</sub>

---

### 141. A data integration process receives customer rows from an ERP system. The process knows the ERP account number, but it does not know the Dataverse primary key, and the design must create missing rows or update existing rows without first running a separate existence check.

Which Organization service approach should you use?

- **A.** RetrieveRequest then UpdateRequest
- **B.** CreateRequest with fixed GUID
- **C.** ExecuteMultipleRequest batch
- **D.** UpsertRequest ✅

> **Answer:** D. UpsertRequest

UpsertRequest is the best choice because Microsoft documents that Upsert is designed for integration scenarios where you do not know whether the Dataverse row already exists. Instead of retrieving first and then deciding whether to create or update, Upsert lets the platform do that decision as part of the operation.

This becomes especially useful when the external system has a stable business identifier and Dataverse is configured with an alternate key. Microsoft’s guidance for alternate keys explains that they are used to reference records when you do not know the Dataverse primary key value, which matches this scenario directly.

<sub>Set E · Q5</sub>

---

### 142. A team is exposing an internal Azure App Service API through a custom connector. The API is protected by Microsoft Entra ID, and each user must authenticate with their own identity rather than using a shared static secret. The design must stay inside the supported custom connector security model.

Which authentication type should you configure?

- **A.** API key in request header
- **B.** OAuth 2.0 with Entra ID ✅
- **C.** Basic authentication over TLS
- **D.** No auth with IP filtering

> **Answer:** B. OAuth 2.0 with Entra ID

OAuth 2.0 with Microsoft Entra ID is the correct choice because Microsoft documents this as the supported pattern for connecting a custom connector to an Entra-protected API. The connector security setup uses Entra app registration details and a connector redirect URI to complete delegated sign-in.

That matches the scenario because the requirement is per-user sign-in to an Azure service, not a shared credential model. API key and basic authentication approaches do not satisfy the user-identity requirement in the same way, and “no auth” clearly fails the service protection requirement.

<sub>Set E · Q13</sub>

---

### 143. A solution needs two Azure Functions. One must receive Dataverse server events pushed directly to a webhook endpoint. The other must run at 02:30 UTC every weekday to archive stale integration records.

Which two triggers should you implement? (Select TWO.)

- **A.** Blob trigger binding
- **B.** HTTP trigger endpoint ✅
- **C.** Service Bus topic listener
- **D.** Event Hubs stream processor
- **E.** Timer trigger schedule ✅

> **Answer:** B. HTTP trigger endpoint · E. Timer trigger schedule

The correct pair is HTTP trigger endpoint and timer trigger schedule. Microsoft documents HTTP triggers as the pattern for building serverless APIs and responding to webhooks, while timer triggers are the mechanism for running a function on a schedule. Those two requirements appear separately in the scenario, so the solution needs one of each.

This question is really about matching the trigger to the event source. A direct webhook call from Dataverse is an HTTP-trigger scenario, while a weekday archive job is a scheduled-execution scenario. Choosing Service Bus or Event Hubs would make sense only if those services were the actual upstream event source, which they are not here.

<sub>Set E · Q18</sub>

---

### 144. A team already created a secret environment variable that references an Azure Key Vault secret. In the cloud flow designer, the maker cannot pick that secret directly from the standard dynamic content list, but the flow still must use the secret at runtime without exposing it in run history.

Which flow action pattern should you use?

- **A.** HTTP action with static password
- **B.** Current Value field lookup
- **C.** Azure Key Vault list secrets
- **D.** RetrieveEnvironmentVariableSecretValue ✅

> **Answer:** D. RetrieveEnvironmentVariableSecretValue

RetrieveEnvironmentVariableSecretValue is the best answer because Microsoft documents that environment variables referencing Azure Key Vault secrets are not currently available directly from the dynamic content selector in Power Automate flows. Microsoft then shows the supported pattern: use the Microsoft Dataverse Perform an unbound action action, select RetrieveEnvironmentVariableSecretValue, and pass the environment variable unique name.

This also aligns with the security requirement in the scenario. Microsoft’s example explicitly turns on Secure Outputs for the secret retrieval action and then enables Secure Inputs and Secure Outputs on the downstream HTTP action so the secret does not appear in run history. That makes this the documented retrieval pattern for a flow that uses a Key Vault-backed secret environment variable.

<sub>Set E · Q20</sub>

---

### 145. A synchronous Update plug-in calculates a short internal routing code for the same row that triggered the event. The value must be committed as part of the same transaction, and the design should avoid an extra Organization service update against that same row.

Which approach should you use?

- **A.** Async PostOperation step
- **B.** Use service.Update on the same row
- **C.** Send a custom API request
- **D.** Change Target in PreOperation ✅

> **Answer:** D. Change Target in PreOperation

Changing the Target entity in PreOperation is the best design because Microsoft documents that if you want to change values for the entity included in the message, PreOperation is the right stage. That lets the updated value participate in the same core operation instead of issuing a second Update request through the Organization service.

This is also the most efficient choice for the stated constraints. PreOperation runs within the transaction, and adding an extra Organization service call for the same row would extend transaction work unnecessarily and increase the chance of re-entry or avoidable pipeline overhead.

<sub>Set E · Q35</sub>

---

### 146. A plug-in needs to change one column on the current account row and should avoid unnecessary payload.

Snippet

IPluginExecutionContext context =
    (IPluginExecutionContext)serviceProvider.GetService(typeof(IPluginExecutionContext));

IOrganizationServiceFactory serviceFactory =
    (IOrganizationServiceFactory)serviceProvider.GetService(typeof(IOrganizationServiceFactory));

IOrganizationService service =
    serviceFactory.CreateOrganizationService(context.UserId);

Entity updateAccount = new Entity("account")
{
    Id = context.PrimaryEntityId
};

updateAccount["creditonhold"] = true;

service.Update(updateAccount);
What is the main design advantage of this Organization service pattern?

- **A.** Pipeline bypass behavior
- **B.** Sparse update payload ✅
- **C.** Automatic privilege elevation
- **D.** Metadata lock enforcement

> **Answer:** B. Sparse update payload

This pattern is primarily valuable because it sends a sparse update payload. Microsoft’s Update(Entity) guidance shows creating a new Entity with the logical name and Id, then setting only the columns that actually change before calling Update, which keeps the operation focused on the intended attributes.

That is a strong plug-in design choice when the code already knows which field must be changed. It avoids retrieving a full row just to update one value, and it keeps the Organization service operation aligned to the minimum required data.

<sub>Set E · Q36</sub>

---

### 147. A team must stamp a derived internal code on the same row during an Update operation. The design must keep the change in the same transaction and minimize extra Organization service work.

Exhibit 1

Which design should you choose?

- **A.** Alpha candidate ✅
- **B.** Beta candidate row
- **C.** Gamma implementation choice
- **D.** Delta registration pattern

> **Answer:** A. Alpha candidate

Alpha is the best answer because it changes the incoming row in PreOperation without issuing an extra Organization service update for that same row. Microsoft’s plug-in registration guidance states that if you want to change values for the entity included in the message, PreOperation is the appropriate stage, and the execution-context guidance explains that InputParameters can be modified to affect behavior depending on the registered stage.

The exhibit also shows why the other candidates are weaker. The moment you add an extra service.Update in synchronous pipeline stages, you extend in-transaction work, and Microsoft’s transaction guidance explicitly notes that requests from plug-ins in PreOperation or PostOperation occur within the transaction.

<sub>Set E · Q38</sub>

---

### 148. A contact Update plug-in uses the Organization service to create a follow-up task. Users can update contacts successfully, but some runs fail when the task create operation starts because those users do not have create privileges on tasks. The business requires the plug-in to keep creating the task without granting every caller broader permissions.

What should you change first?

- **A.** Async step registration
- **B.** InitiatingUserId override
- **C.** Step impersonation ✅
- **D.** Client-side Web API call

> **Answer:** C. Step impersonation

Step impersonation is the best first change because Microsoft documents that a plug-in step can be configured with Run in User’s Context, and that this is specifically relevant when the calling user does not have privileges required by operations in the step. That lets the Organization service run under a designated user with the needed rights instead of forcing broader privileges onto every caller.

This is also the cleanest fix for the stated requirement because it keeps the logic in the plug-in and aligns the Organization service execution identity to the intended security model. Microsoft also documents that context.UserId follows the user account defined by the step registration, while other impersonation choices such as InitiatingUserId are different runtime decisions.

<sub>Set E · Q39</sub>

---

### 149. You already created a root catalog for the solution and a second-level catalog that represents the category. You now need to expose one specific custom API under that category as a Dataverse business event.

Which record type should you create?

- **A.** Parent catalog lookup
- **B.** Message processing step
- **C.** CatalogAssignment ✅
- **D.** Plug-in assembly record

> **Answer:** C. CatalogAssignment

CatalogAssignment is the correct answer because Dataverse uses the Catalog table to create the two-level hierarchy, and then uses the CatalogAssignment table to specify which tables, custom APIs, or custom process actions are exposed as events within a category. After the root catalog and category exist, the assignment record is the configuration element that makes the specific event available under that category.

This distinction matters in PL-400 scenarios because creating the hierarchy is not enough by itself. The hierarchy organizes the solution and its categories, while the assignment is what actually exposes the chosen custom API or table event to subscribers and downstream tooling.

<sub>Set E · Q40</sub>

---

### 150. A support solution uses a user-owned custom Case Review table. The team wants a Power Automate flow to run whenever a record is shared, but they do not want to add new synchronous logic just to detect that security operation.

Which approach should you use?

- **A.** Create a custom connector trigger
- **B.** Register an Azure Service Bus endpoint
- **C.** Add a synchronous GrantAccess plug-in
- **D.** Catalog the user-owned table ✅

> **Answer:** D. Catalog the user-owned table

Cataloging the user-owned table is the best answer because when a table is assigned to a business-event category, Dataverse automatically includes supported bound operations for that table. For user-owned tables, this includes security-related operations such as GrantAccess, ModifyAccess, and RevokeAccess, which is exactly the event family described in the scenario.

This is a strong fit when the requirement is event discovery and asynchronous automation rather than synchronous interception. Microsoft’s business-events guidance specifically uses GrantAccess as an example of an event that can be exposed by cataloging the relevant table, enabling downstream automation without forcing a new synchronous detection layer.

<sub>Set E · Q41</sub>

---

### 151. A maker says a Dataverse action exists in the solution, but it still does not appear in the Dataverse When an action is performed trigger in Power Automate. The root catalog and category already exist.

Which two changes should you make? (Select TWO.)

- **A.** Grant read access to Plug-in Assembly, Plug-in Type, and Step tables
- **B.** Register a synchronous PostOperation step
- **C.** Create a CatalogAssignment for the action ✅
- **D.** Set IsPrivate to true before import
- **E.** Grant read access to Custom API, Process, and SDK Message ✅

> **Answer:** C. Create a CatalogAssignment for the action · E. Grant read access to Custom API, Process, and SDK Message

The two correct changes are to create a CatalogAssignment for the action and ensure the user has the required read permissions. Microsoft states that flows can trigger from a Dataverse action only when that action is included in both a Catalog and a Category, and the catalog-assignment model is what places the action there. Microsoft also notes that users outside the Environment Maker role need read access to Custom API, Process, and SDK Message to view the catalog data in the trigger.

This is a common configuration gap because developers often create the action and the catalog structure but forget either the assignment record or the security needed for discovery. Business events are not just about defining the operation; they also depend on making the event visible through catalog configuration and accessible through role privileges.

<sub>Set E · Q42</sub>

---

### 152. A team wants a Dataverse operation that acts purely as a business event. External subscribers should respond after the operation completes, the operation should be callable from Power Automate, and no main-operation plug-in logic is required.

Configuration

Is Function: No
Binding Type: Global
AllowedCustomProcessingStepType: Async Only
Plugin Type: (none)
Which interpretation best matches this configuration?

- **A.** Nonextensible sync message
- **B.** Custom API event ✅
- **C.** Entity-bound validation function
- **D.** Fully customizable pre-cancel business operation

> **Answer:** B. Custom API event

This configuration matches a custom API used as a business event. Is Function: No means the operation is an action rather than a function, and Microsoft states that the Dataverse connector currently enables performing actions, which is the right choice when Power Automate must invoke or respond to the operation. AllowedCustomProcessingStepType: Async Only is the option Microsoft specifically recommends for the business-events pattern.

Leaving the main Plugin Type empty also fits the event-only pattern. Microsoft explains that a custom API can be used as a business event without any plug-in logic, allowing the API to exist primarily as a notification point that subscribers respond to asynchronously after successful completion.

<sub>Set E · Q43</sub>

---

### 153. A developer created a custom API and added it to the correct catalog category. The flow author can see the category in the Dataverse When an action is performed trigger, but the specific operation still does not appear. The custom API has no main-operation plug-in, and the user already has the right read privileges.

What is the most likely cause?

- **A.** AllowedCustomProcessingStepType is Async Only
- **B.** Main-operation plug-in is blank
- **C.** Binding Type is Entity Collection
- **D.** Is Function is Yes ✅

> **Answer:** D. Is Function is Yes

The most likely cause is that the custom API was created as a function instead of an action. Microsoft states that the Dataverse connector currently enables performing actions, and if you need the operation to be used with Power Automate, the custom API should be created as an action. A function therefore fits the symptom of an operation that exists technically but does not appear where the flow author expects it.

The other details in the scenario intentionally remove common distractions. Microsoft explicitly says a custom API can still be invoked even when no main-operation plug-in is specified, and Async Only is actually the recommended processing-step option for the business-events pattern rather than a blocker.

<sub>Set E · Q46</sub>

---

### 154. Your code must perform a Dataverse operation that is exposed as an SDK message request class rather than as a common helper method on IOrganizationService.

Which Organization service method should you use?

- **A.** Retrieve method
- **B.** Associate method
- **C.** Execute ✅
- **D.** RetrieveMultiple method

> **Answer:** C. Execute

Execute is the correct answer because specialized Dataverse message operations are sent through the Organization service by using OrganizationRequest and OrganizationResponse classes. Microsoft documents that the common IOrganizationService methods are the quickest and easiest way to perform most common data operations, while message-based operations are performed through the SDK request/response model.

This is the key distinction the question is testing. If you are performing a common row operation such as create, retrieve, update, delete, or query, the direct helper methods are usually the natural choice. When the operation is exposed as a request message, the Organization service entry point is Execute.

<sub>Set E · Q47</sub>

---

### 155. A .NET integration retrieves a very large set of case rows by using RetrieveMultiple. The design must avoid pulling unnecessary data and must retrieve all matching rows predictably across successive requests.

Which two changes should you make? (Select TWO.)

- **A.** Use ColumnSet(true)
- **B.** Specify needed columns ✅
- **C.** Set ReturnResponses = true
- **D.** Use paging cookie ✅
- **E.** Increase TopCount only

> **Answer:** B. Specify needed columns · D. Use paging cookie

Specifying only the needed columns and using the paging cookie are the correct pair. Microsoft’s Dataverse guidance says queries should avoid AllColumns = true and should retrieve only the columns actually required. Microsoft also documents that paging with the returned paging cookie is the recommended way to retrieve consecutive pages of a large result set in a performant manner.

Together, these two changes improve both efficiency and correctness. A narrow ColumnSet reduces transferred data and server work, while the paging cookie supports consistent retrieval of large multi-page result sets rather than depending on a one-shot fetch pattern.

<sub>Set E · Q48</sub>

---

### 156. A developer says the following Organization service query is a good default pattern for account retrieval.

Snippet

QueryExpression query = new("account")
{
    ColumnSet = new ColumnSet(true)
};

query.Criteria.AddCondition("statecode", ConditionOperator.Equal, 0);

EntityCollection results = service.RetrieveMultiple(query);
What is the main problem with this query design?

- **A.** All columns retrieved ✅
- **B.** Server paging disabled
- **C.** Dataverse security bypassed
- **D.** Alias generation suppressed

> **Answer:** A. All columns retrieved

The main problem is that new ColumnSet(true) retrieves all columns. Microsoft’s Dataverse best-practice guidance explicitly identifies both ColumnSet.AllColumns = true and new ColumnSet(true) as problematic patterns because they instruct the platform to issue a SELECT * style query across the data included in the plan.

That makes this a poor default Organization service pattern. Even when the filter itself is valid, the query should request only the columns that the code actually needs. Narrowing the ColumnSet is a foundational Dataverse query optimization rather than an optional cleanup step.

<sub>Set E · Q49</sub>

---

### 157. A synchronous plug-in approves an order and then uses service.Execute(new ExecuteTransactionRequest(...)) to update 200 related rows. Users report slow saves and intermittent timeout or blocking during peak usage.

What should you change first?

- **A.** Set ReturnResponses false
- **B.** Add more requests to batch
- **C.** Switch to ColumnSet(true)
- **D.** Remove batch request type ✅

> **Answer:** D. Remove batch request type

You should remove the batch request type from the plug-in first. Microsoft’s Dataverse best-practice guidance explicitly says not to use ExecuteMultipleRequest or ExecuteTransactionRequest within the context of a plug-in or workflow activity. Microsoft positions those batch message types for client applications, not for code already running inside the Dataverse execution pipeline.

This matches the symptoms in the scenario. Microsoft’s ExecuteTransaction guidance explains that it executes multiple requests in a single database transaction, and Microsoft’s best-practice note warns about database blocking for atomic batch transactions. Using that pattern inside synchronous pipeline logic is exactly the kind of design that can lengthen user save time and increase contention.

<sub>Set E · Q51</sub>

---

### 158. An Azure Function exposes a REST API that must be reused from both Power Apps and Power Automate. The development team already has a machine-readable API contract and wants to avoid manually creating every action and parameter.

Which artifact should you import when creating the custom connector?

- **A.** ARM deployment template
- **B.** Power Platform solution package
- **C.** OpenAPI 2.0 definition ✅
- **D.** OpenAPI 3.0 document file

> **Answer:** C. OpenAPI 2.0 definition

A custom connector is a wrapper around a REST or SOAP API, and one supported way to create it is by importing an API definition. Microsoft’s custom connector import guidance states that the definition used for this flow must be in OpenAPI 2.0 format, which is why that is the correct choice here.

This is the best fit for an Azure service API that is already documented and ready to be consumed by Power Apps and Power Automate. It preserves operations, parameters, and request/response structure without forcing the maker to define the connector manually from scratch.

<sub>Set E · Q52</sub>

---

### 159. A team exports an API from Azure API Management to Power Platform as a custom connector. The API works in Postman, but browser-based calls from Power Apps fail with cross-origin errors. Which TWO changes are required for the browser-based scenario? (Select TWO.)

- **A.** Switch the connector to HTTP
- **B.** Enable APIM CORS policy ✅
- **C.** Regenerate the subscription key
- **D.** Set an Origin header policy ✅
- **E.** Rebuild the connector as SOAP

> **Answer:** B. Enable APIM CORS policy · D. Set an Origin header policy

Microsoft’s API Management guidance for Power Platform custom connectors says browser-based clients such as Power Apps and Power Automate require two policy-side changes. The API must allow the Power Platform origin through CORS, and the custom connector must send an Origin header that matches the allowed origin.

That is why the correct pair is enabling the APIM CORS policy and setting an Origin header policy in the custom connector. The issue is not the API contract itself or the subscription key; it is the browser-origin behavior of the Power Platform client.

<sub>Set E · Q54</sub>

---

### 160. A developer wants to create a custom connector for an Azure service by importing this API description.

Snippet

{
  "openapi": "3.0.1",
  "info": {
    "title": "OrdersApi",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://orders-api.azurewebsites.net"
    }
  ]
}
What should the developer change before import?

- **A.** Convert it to OpenAPI 2.0 ✅
- **B.** Add a redirect URI policy template
- **C.** Replace servers with ARM resources
- **D.** Publish it through Event Grid

> **Answer:** A. Convert it to OpenAPI 2.0

The problem is the definition format. Microsoft’s import guidance for custom connectors states that the OpenAPI file used for this flow must be in OpenAPI 2.0 format, and OpenAPI 3.0 definitions are not supported for this scenario.

Because of that, the right correction is to convert the Azure service definition to OpenAPI 2.0 before importing it into Power Apps or Power Automate. This is a connector-definition issue, not a runtime behavior issue.

<sub>Set E · Q55</sub>

---

### 161. A developer configures a custom connector for an Entra-protected Azure service. The user can reach the Microsoft sign-in screen, but connection creation fails after the redirect back to Power Platform. Testing the token flow in Postman succeeds when the same client ID, client secret, and expected redirect URI are used.

What is the best fix?

- **A.** Rotate the client secret
- **B.** Remove the OAuth scope
- **C.** Correct the redirect URI ✅
- **D.** Switch to API key auth

> **Answer:** C. Correct the redirect URI

The strongest fix is to correct the redirect URI. Microsoft’s Entra authentication guidance for custom connectors says the connector generates a redirect URL that must be added to the app registration, and the OAuth troubleshooting guidance tells you to validate the token flow with the same client ID, client secret, and redirect URI as the connector.

Because Postman works when the expected redirect URI is used, the failure after the Power Platform redirect strongly points to mismatch or misregistration of that redirect URI in the custom connector or the Entra app registration. That is a much tighter explanation than rotating credentials or changing the auth model.

<sub>Set E · Q56</sub>

---

### 162. A Dataverse solution posts remote execution context data to an Azure Service Bus queue whenever high-value account records are updated. The team wants an Azure Function to process the backlog asynchronously and does not want to maintain a permanently listening relay process.

Which trigger should you implement?

- **A.** Blob trigger with polling
- **B.** Timer trigger with schedule
- **C.** HTTP trigger endpoint
- **D.** Service Bus trigger ✅

> **Answer:** D. Service Bus trigger

A Service Bus trigger is the best answer because Azure Functions uses that trigger to respond to messages from a Service Bus queue or topic. That lines up directly with the architecture in the scenario, where Dataverse posts runtime data to Azure Service Bus and the function should react when messages arrive.

Microsoft’s Dataverse-to-Azure guidance also states that with a queue endpoint contract, a listener does not have to be actively listening all the time. That makes the queue-plus-Service-Bus-trigger pattern a strong fit for asynchronous, backlog-driven processing in Power Platform solutions.

<sub>Set E · Q57</sub>

---

### 163. A Dataverse plug-in must perform data operations by using the same effective user as the current plug-in execution context. The code already has an IOrganizationServiceFactory instance.

Which service-factory choice should you use?

- **A.** null userId parameter
- **B.** context.InitiatingUserId value
- **C.** Guid.Empty value ✅
- **D.** ServiceClient connection string

> **Answer:** C. Guid.Empty value

Guid.Empty is the best choice because, when CreateOrganizationService is called inside a plug-in, Guid.Empty maps to the same user as IPluginExecutionContext.UserId. That is the standard way to get an IOrganizationService that follows the current execution user context instead of switching to SYSTEM or explicitly impersonating another user.

This matters because Organization service operations inside plug-ins should usually respect the intended execution identity for the step. Microsoft documents that null means SYSTEM in plug-ins, while InitiatingUserId explicitly switches to the user who originally caused the action, which is a different design choice.

<sub>Set E · Q58</sub>

---

### 164. A production Azure Function archives completed approval records every five minutes. After scale events, the function sometimes runs immediately, and the team also wants missed schedules tracked across instance restarts.

Configuration

type: timerTrigger
schedule: "0 */5 * * * *"
runOnStartup: true
useMonitor: false
Which change best meets the requirement?

- **A.** runOnStartup false; useMonitor true ✅
- **B.** Keep startup execution and switch to TimeSpan scheduling
- **C.** runOnStartup true; useMonitor true
- **D.** Leave startup enabled and keep the current schedule inline

> **Answer:** A. runOnStartup false; useMonitor true

The best change is to set runOnStartup to false and useMonitor to true. Microsoft warns that runOnStartup causes the function to run whenever the runtime starts, including restarts and scale-out events, and says it should rarely, if ever, be enabled in production. Microsoft also states that useMonitor persists schedule occurrences so the schedule is maintained correctly across restarts.

That combination directly matches both requirements in the question. Turning off startup execution removes the unwanted extra runs, while enabling monitoring supports durable schedule tracking for a five-minute recurrence, which is exactly the kind of schedule Microsoft describes for timer monitoring behavior.

<sub>Set E · Q60</sub>

---

### 165. A team registered an Azure Function URL as a Dataverse webhook endpoint for update events on a custom table. The function app is healthy, but no event payloads arrive, and the developer later notices the function was created from a timer-trigger template instead of a webhook-oriented template.

What is the most likely cause?

- **A.** Incorrect WEBSITE_TIME_ZONE setting
- **B.** Timer trigger configuration ✅
- **C.** Unpublished OpenAPI custom connector
- **D.** Missing Event Hubs consumer group

> **Answer:** B. Timer trigger configuration

The most likely cause is that the function uses a timer trigger instead of an HTTP trigger. Microsoft documents webhooks as Dataverse sending server events to an external web application, and Azure Functions uses HTTP triggers to build endpoints that respond to webhooks. A timer trigger cannot receive inbound POST requests from Dataverse.

This is a classic trigger-to-source mismatch. The function app itself can be healthy and still never receive the event because the wrong trigger model was chosen at design time. For direct Dataverse webhook delivery, the function needs an HTTP endpoint, not scheduled execution.

<sub>Set E · Q61</sub>

---

### 166. A solution-aware cloud flow and a custom connector must use the same API secret across environments. The actual secret value must stay outside Power Platform, and the solution component should reference the secret location rather than store the secret itself.

Which component should you use?

- **A.** Text environment variable
- **B.** Azure Key Vault connector
- **C.** Secret environment variable ✅
- **D.** Secure string parameter

> **Answer:** C. Secret environment variable

A secret environment variable is the best answer because Microsoft documents that environment variables can reference secrets stored in Azure Key Vault and make those secrets available for use in Power Automate flows and custom connectors, while the actual secret remains in Azure Key Vault. That matches the requirement that the solution component reference the secret without storing the secret value inside the flow or solution artifact.

This is also the strongest ALM-oriented design for the scenario. Microsoft’s guidance explains that the environment variable stores the reference information while the secret itself stays in Key Vault, and it distinguishes current/default values from the solution metadata pattern used for environment-aware deployment. That makes the secret environment variable a better fit than directly wiring a connector call into every consuming component.

<sub>Set E · Q62</sub>

---

### 167. A maker says a Key Vault-backed secret environment variable was configured correctly, but saving it still fails with an authorization-related validation error.

Configuration

Environment variable data type: Secret
Secret store: Azure Key Vault
Permission model: Azure RBAC
Maker role on vault: Key Vault Reader
Dataverse role on vault: Key Vault Reader
Vault tenant: Same as Power Platform
Which change should you make?

- **A.** Azure Key Vault Contributor role
- **B.** Key Vault Secrets User ✅
- **C.** Text environment variable value
- **D.** Current value in solution

> **Answer:** B. Key Vault Secrets User

The correct change is to use Key Vault Secrets User. Microsoft’s current guidance specifically notes that earlier instructions used Key Vault Reader, but now both users and Microsoft Dataverse need Key Vault Secrets User so they can retrieve secrets successfully. The configuration already shows same-tenant alignment and Azure RBAC, so the role assignment is the missing piece.

This also fits the reported symptom. Microsoft documents that user access validation happens in the background and that a save can fail with a message saying the user is not authorized to read secrets from the Azure Key Vault path. That is consistent with Reader-level setup that has not been updated to the current secret-retrieval role requirement.

<sub>Set E · Q63</sub>

---

### 168. A cloud flow authenticates to a downstream service by using a Key Vault-backed secret environment variable. Security rotates the secret by creating a new version in Azure Key Vault, but dependent components continue failing until someone intervenes manually.

What should you add to automate the update path?

- **A.** Event Grid + NotifyEnvironmentVariableSecretChange ✅
- **B.** Scheduled flow with secret history
- **C.** Manual current value refresh
- **D.** Secure outputs on HTTP action

> **Answer:** A. Event Grid + NotifyEnvironmentVariableSecretChange

The best answer is Event Grid + NotifyEnvironmentVariableSecretChange. Microsoft documents a specific pattern for secret-version changes: use a Power Automate cloud flow with an Azure Event Grid trigger that listens for the Key Vault SecretNewVersionCreated event, and then call the Dataverse unbound action NotifyEnvironmentVariableSecretChange. Microsoft also documents that the NotifyEnvironmentVariableSecretChange action is limited to Power Automate flows triggered by Azure Event Grid for this Key Vault event.

This is the strongest design because it responds to secret rotation as an event rather than relying on a manual or polling-based workaround. The requirement is to keep dependent components aligned when a new Key Vault secret version is created, and Microsoft’s documented mechanism is precisely this Event Grid plus Dataverse action combination.

<sub>Set E · Q64</sub>

---

### 169. A Power Platform solution must run an Azure Function every night at 01:00 UTC to reconcile orphaned staging rows in Dataverse. The run must occur even when no user opens the app and no external system sends a message.

Which trigger should you use?

- **A.** HTTP trigger
- **B.** Event Hubs trigger
- **C.** Timer trigger ✅
- **D.** Service Bus trigger

> **Answer:** C. Timer trigger

A timer trigger is the best fit because Azure Functions uses timer triggers to run code on a schedule. Microsoft also states that each function has exactly one trigger, so the correct design is to choose the trigger that matches scheduled execution rather than an inbound event source.

The other trigger types in this question all depend on something external arriving first, such as an HTTP request, a Service Bus message, or an Event Hubs event. Because the requirement explicitly says the job must run on a clock-based schedule with no inbound event dependency, a timer trigger is the correct implementation choice.

<sub>Set E · Q67</sub>

---

### 170. A maker creates a secret environment variable that references Azure Key Vault, but the save fails for some users and the cloud flow cannot retrieve the secret during execution. You confirm that the vault exists and the secret name is correct.

Which two Azure role assignments must be present? (Select TWO.)

- **A.** Makers: Key Vault Reader
- **B.** Dataverse: Key Vault Secrets User ✅
- **C.** Flow owners: Key Vault Administrator role
- **D.** Makers: Key Vault Secrets User ✅
- **E.** Dataverse: Environment Maker role

> **Answer:** B. Dataverse: Key Vault Secrets User · D. Makers: Key Vault Secrets User

The correct pair is Dataverse: Key Vault Secrets User and Makers: Key Vault Secrets User. Microsoft documents that users who create or use environment variables of type secret must have permission to retrieve the secret contents, and it specifically directs you to assign the Key Vault Secrets User role. Microsoft also states that Azure Key Vault must have the Key Vault Secrets User role granted to the Dataverse service principal so Dataverse can retrieve the secret.

This is an important distinction because Microsoft notes that previous instructions often used Key Vault Reader, but that is no longer sufficient for this scenario. The current guidance explicitly calls out the role change and recommends ensuring both the user side and the Dataverse application identity can retrieve secrets.

<sub>Set E · Q71</sub>

---

### 171. A backend API requires a static x-region header on every request. Makers must not type that value manually, and the connector should inject it consistently at runtime.

Configuration

Connector auth: API key
Operation path: /customers
Backend host: api.contoso.com
Required backend header: x-region=au
Maker input for x-region: Not allowed
Which approach should you use? Select only one answer.

- **A.** Connection reference override
- **B.** Swagger response transform policy
- **C.** Set header policy ✅
- **D.** Custom API wrapper

> **Answer:** C. Set header policy

A set header policy is the best fit because the requirement is to inject a fixed header value at runtime without forcing app makers to supply it manually. Policy templates exist specifically to reshape outbound requests or inbound responses in a reusable connector-level way, which keeps the calling experience cleaner and more consistent across apps and flows.

This is a runtime-behavior concern, not a Dataverse extensibility concern. The connector already has the right basic API surface; it just needs controlled request mutation before sending traffic to the backend. A policy template solves that directly and centrally instead of pushing the responsibility into every consuming app.

<sub>Set F · Q8</sub>

---

### 172. A custom connector must call an external API on behalf of each signed-in user. The API requires delegated user consent, centrally managed token issuance through Microsoft Entra ID, and the ability to stop relying on manually stored bearer tokens.

Problem:

The connector must support delegated user access to the external API.

Proposed solution:

Configure API key authentication in the connector, store each user's bearer token in Dataverse, and inject that token into requests through a policy template.

Does the proposed solution meet the goal?

- **A.** Yes
- **B.** No ✅

> **Answer:** B. No

No. The proposed solution does not meet the goal because API key authentication is not delegated OAuth authentication, and manually storing bearer tokens in Dataverse is the opposite of the intended token-management model. The requirement explicitly calls for user-delegated access through Microsoft Entra ID, which means the connector should use an OAuth-based flow that obtains and refreshes tokens through the identity platform rather than treating tokens as stored application data.

This design is also weak operationally and from a security perspective. Delegated OAuth gives the platform a structured way to obtain consent, issue tokens, and manage token lifetime in an identity-aware manner. Manually persisting bearer tokens and replaying them through policies creates avoidable risk and undermines the whole reason OAuth is being required in the first place.

<sub>Set F · Q10</sub>

---

### 173. A developer finished a Dataverse plug-in class in Visual Studio and needs to register it for an Account update event. The team wants the step configured correctly before validating the behavior in the environment.

Steps

Test the target table event in Dataverse.

Register the assembly that contains the plug-in class.

Register the step for the Dataverse message and primary table.

Configure step details such as stage, mode, and images if needed.

What is the correct order?

- **A.** 3 → 2 → 4 → 1
- **B.** 2 → 4 → 3 → 1
- **C.** 2 → 3 → 4 → 1 ✅
- **D.** 4 → 2 → 3 → 1

> **Answer:** C. 2 → 3 → 4 → 1

The correct flow starts by registering the assembly, because Dataverse must first know about the compiled plug-in class before any step can reference it. After the assembly exists in the platform, you register the step against the correct message and primary table, and then refine the registration with the needed stage, execution mode, filtering attributes, or images. Testing comes last, because there is nothing meaningful to validate until both the assembly and step registration are complete.

This sequence matches how the Plug-in Registration Tool works operationally. Assemblies are the deployable plug-in containers, while steps are the event subscriptions that tell Dataverse when and how to invoke the plug-in. Images and execution details are step-level concerns, so they are configured after the step exists and before the final validation run.

• 2 is first because the assembly must be available in Dataverse before a step can be tied to its plug-in type.

• 3 is second because the event subscription is created after the platform knows about the assembly and plug-in class.

• 4 is third because stage, mode, filtering attributes, and images are step configuration details, not assembly registration details.

• 1 is last because the registration should be complete before you trigger the Account update and verify the behavior.

<sub>Set F · Q13</sub>

---

### 174. A plug-in must block account updates when a custom compliance rule fails. The business wants the operation rejected as early as possible, and the design should avoid unnecessary transaction rollback cost.

Which stage should you choose?

- **A.** PostOperation async
- **B.** PreOperation stage
- **C.** PostOperation stage
- **D.** PreValidation stage ✅

> **Answer:** D. PreValidation stage

PreValidation is the best stage when the goal is to reject an operation as early as possible. Microsoft states that if you want to cancel an operation, you should detect the condition in PreValidation and throw InvalidPluginExecutionException, because canceling before the request reaches the main database transaction avoids the heavier cost of rollback within the transaction.

This is exactly the kind of stage-selection decision PL-400 tests: not just whether a stage exists, but why it is the right stage for a specific business outcome. PreOperation and PostOperation are within the transaction, while PostOperation asynchronous execution happens after the main operation completes and cannot prevent the original save from committing.

<sub>Set F · Q35</sub>

---

### 175. A PreOperation plug-in calculates a normalized external identifier that a later PostOperation plug-in in the same pipeline must reuse. The team wants to avoid another Dataverse query and does not want to persist the intermediate value on the table.

Which execution context feature should you use?

- **A.** SharedVariables ✅
- **B.** OutputParameters
- **C.** ParentContext
- **D.** CorrelationId

> **Answer:** A. SharedVariables

SharedVariables is the correct execution context feature for passing data from one step to another later in the same pipeline. Microsoft documents SharedVariables as a ParameterCollection that plug-ins can add to, read, or modify so that subsequent steps can access the shared data.

This is better than issuing another query because the value is already known inside the pipeline and can be passed forward explicitly. It also keeps the temporary value out of the table schema while still allowing a later step to consume it, which is exactly the pattern Microsoft shows for passing values from pre-stage logic to post-stage logic.

<sub>Set F · Q36</sub>

---

### 176. A rule must validate invoice data for every caller that writes to Dataverse, including model-driven apps, canvas apps, Power Automate, and external integrations. The check must run server-side and participate in the transaction so invalid data never commits.

Which implementation approach should you use?

- **A.** Real-time cloud flow
- **B.** Synchronous plug-in ✅
- **C.** Client API script
- **D.** Business rule

> **Answer:** B. Synchronous plug-in

A synchronous plug-in is the strongest choice because it executes server-side in the Dataverse event pipeline and can enforce the rule regardless of which client or integration submitted the request. Microsoft documents plug-ins as custom code executed in response to data processing events, which makes them the correct platform extension point when business logic must apply consistently across all callers.

The key constraint is transactional enforcement. Client-side and app-level options can improve user experience, but they do not guarantee that every caller is blocked. A synchronous plug-in can inspect the request in the pipeline and reject it before the invalid write is committed, which is exactly what the requirement demands.

<sub>Set F · Q37</sub>

---

### 177. A plug-in must compare the old and new values of creditlimit after an account update, and it must do so without issuing another retrieve call. The team wants the registration that gives access to both the before and after snapshots in a supported way.

Exhibit 1

Which proposal should you choose?

- **A.** Proposal 1
- **B.** Proposal 2
- **C.** Proposal 3 ✅
- **D.** Proposal 4

> **Answer:** C. Proposal 3

Proposal 3 is the supported design. Microsoft documents that for an Update operation registered in PostOperation, you can have both a Pre Image and a Post Image, which is exactly what you need when comparing old and new values after the main operation completes.

This is also the preferred performance-aware approach because Microsoft recommends using entity images instead of issuing a fresh retrieve when you need values that were not included in the operation payload. The documentation explicitly says that retrieving current values with IOrganizationService in these scenarios is not a good practice for performance, and that a pre-entity image is the better practice.

<sub>Set F · Q39</sub>

---

### 178. A plug-in updates a phone number on an account. The current code retrieves several columns, changes one field, and then updates the retrieved entity object directly.

Snippet

Entity account = service.Retrieve(
    "account",
    accountId,
    new ColumnSet("name", "telephone1", "address1_city", "creditlimit"));

account["telephone1"] = newPhoneNumber;
service.Update(account);
Which revision is the best fit?

- **A.** Retrieve all columns first
- **B.** Use ExecuteTransactionRequest
- **C.** Delete and recreate row
- **D.** Create stub Entity and update changed column ✅

> **Answer:** D. Create stub Entity and update changed column

The best practice is to create a new Entity instance, set the row ID, populate only the columns that are changing, and then call Update. Microsoft’s update guidance explicitly says that when updating a row you should include only the columns you are changing, because updating a previously retrieved entity can trigger unnecessary events and make unchanged columns appear updated in auditing.

This question also tests proper Organization service usage beyond simple syntax recall. Microsoft documents IOrganizationService as the core interface for data operations such as Retrieve, Update, and Execute, but the recommended pattern is still to retrieve only needed columns and update only the changed columns for correctness and performance.

<sub>Set F · Q40</sub>

---

### 179. A synchronous plug-in runs on every account update and calls an external scoring API before the save completes. Users report that saves are slow, average execution time is over six seconds, and the business does not require the score to appear immediately after the save.

Which change should you make first?

- **A.** Move API call to async PostOperation ✅
- **B.** Add batch requests in plug-in
- **C.** Retrieve all columns before call
- **D.** Register duplicate sync step

> **Answer:** A. Move API call to async PostOperation

The best first change is to move the long-running external call to an asynchronous PostOperation step. Microsoft’s performance guidance recommends keeping plug-in execution to no more than about two seconds and says that if a plug-in requires more time, asynchronous execution should be considered first because it improves responsiveness and scalability.

This change matches the scenario because the score is not required immediately as part of the save transaction. Once that constraint is removed, asynchronous execution becomes the strongest platform-fit answer: users are no longer blocked during the save, and the external dependency is moved out of the synchronous request path.

<sub>Set F · Q41</sub>

---

### 180. A team needs a solution-aware Dataverse message that can be invoked from app logic and external callers. The operation must accept structured input parameters, return an output value, and run server-side validation logic inside Dataverse without exposing a separate external REST wrapper.

Which component should you implement? Select only one answer.

- **A.** Bound action
- **B.** Custom API ✅
- **C.** Custom connector
- **D.** Cloud flow trigger

> **Answer:** B. Custom API

A custom API is the best fit because it creates a first-class Dataverse message with defined input and output parameters that can be invoked consistently and secured inside the platform. It is designed for scenarios where you want message-based server-side behavior and often pairs naturally with a plug-in implementation behind the custom API for validation, orchestration, or business logic.

The important distinction is that the requirement is not just “run some logic.” The team wants a Dataverse-native message surface that is solution-aware, parameterized, and callable through platform mechanisms. That is exactly the niche custom APIs fill, whereas connectors and flows are integration surfaces rather than Dataverse message definitions.

<sub>Set F · Q42</sub>

---

### 181. A maker is defining a custom connector from an OpenAPI document. The API operation is intended to call /orders/{orderId}, but the current definition does not model that path correctly.

Snippet

openapi: 3.0.1
paths:
  /orders/{orderId}:
    get:
      operationId: GetOrder
      parameters:
        - name: orderId
          in: query
          required: false
          schema:
            type: string
      responses:
        "200":
          description: OK
Which change best fixes the definition? Select only one answer.

- **A.** Dynamic values extension mapping
- **B.** Header parameter for orderId
- **C.** Inline request-body schema
- **D.** Required path parameter ✅

> **Answer:** D. Required path parameter

The path /orders/{orderId} declares orderId as a path token, so the parameter must be modeled as a path parameter and must be required. Leaving it as an optional query parameter makes the OpenAPI definition inconsistent with the route template and can cause the generated connector operation to be modeled incorrectly.

This is a core OpenAPI design issue rather than a Power Platform runtime bug. When defining REST operations for custom connectors, the path, parameter location, and required flag all need to align precisely with the target API contract. If they do not, the connector surface can look valid at a glance but still generate the wrong runtime call shape.

<sub>Set F · Q43</sub>

---

### 182. A custom connector uses OAuth 2.0 to connect to a secured API. Users reach the sign-in page and complete consent, but the callback fails with a redirect URI mismatch error from Microsoft Entra ID.

What should you change first? Select only one answer.

- **A.** Register the connector redirect URI ✅
- **B.** Add a header policy template
- **C.** Republish the custom connector
- **D.** Move the client secret to Key Vault

> **Answer:** A. Register the connector redirect URI

A redirect URI mismatch during the OAuth callback is a strong sign that the identity provider does not recognize the reply URL being used by the connector. The first thing to fix is the redirect URI registration in the app registration so that the connector callback URL exactly matches what the provider expects. Without that alignment, sign-in can appear to progress correctly but still fail at the token return stage.

This is specifically an OAuth configuration problem, not a generic connector publishing or runtime policy issue. Policy templates shape requests and responses after authentication is working, while secret storage choices do not resolve a callback URL validation failure. The authentication handshake itself must be corrected first.

<sub>Set F · Q44</sub>

---

### 183. A team has an HTTP-triggered Azure Function that calculates pricing and must be reused from both Power Apps and Power Automate. Makers want a discoverable low-code surface with named actions, centralized authentication, and no repeated raw HTTP call logic inside each app or flow.

What should you build? Select only one answer.

- **A.** Webhook endpoint registration
- **B.** Dataverse custom API
- **C.** PCF code component
- **D.** Custom connector ✅

> **Answer:** D. Custom connector

A custom connector is the right choice because it exposes the Azure Function as a reusable Power Platform integration surface with defined actions, parameters, and authentication. That allows makers to call the function through a governed, friendly interface in both canvas apps and flows instead of hand-authoring repeated HTTP logic in every solution component.

The other options solve different extension problems. The requirement is not to add UI rendering, register event subscriptions, or create a Dataverse-native message. It is to package an external Azure service as a reusable Power Platform connector surface, which is exactly what custom connectors are designed to do.

<sub>Set F · Q46</sub>

---

### 184. A solution includes browser-based form scripting and a separate .NET integration service. The team wants the browser layer to perform standard client-side CRUD and query operations, while the server-side integration can use SDK-style messages when needed. Which two approaches should you use? (Select TWO.)

- **A.** Use browser scripts to load the Organization service assemblies
- **B.** Use Web API for client-side CRUD and OData queries ✅
- **C.** Use entity images to replace retrieve operations over Web API
- **D.** Use the legacy SOAP endpoint for all new external integrations
- **E.** Use Organization service in .NET for SDK messages ✅

> **Answer:** B. Use Web API for client-side CRUD and OData queries · E. Use Organization service in .NET for SDK messages

The Dataverse Web API is the normal choice for browser-based CRUD and query work, especially when client-side code needs standard HTTP/OData access patterns. The Organization service remains relevant in .NET server-side code when SDK-style messages, strongly typed requests, or certain server-oriented patterns are required. Those two choices align the right API surface to the right execution context.

This is a classic PL-400 distinction. Web API is the modern HTTP-based surface for general data access and is especially natural in web and JavaScript contexts, while the Organization service is an SDK-oriented .NET surface suited to server-side code and message-based operations. Good developers choose between them based on runtime context and capability needs, not habit.

<sub>Set F · Q47</sub>

---

### 185. A batch integration that writes to Dataverse starts failing intermittently during peak load. The failures are HTTP 429 responses, and the team wants the fastest safe recovery pattern without making the throttling worse.

What should the integration do next?

- **A.** Fixed retry loop
- **B.** Higher parallelism
- **C.** Disable retries
- **D.** Honor Retry-After ✅

> **Answer:** D. Honor Retry-After

Honor Retry-After is the best answer because Dataverse service protection errors explicitly tell the caller how long to wait before sending more requests. Microsoft documents that Web API 429 responses include a Retry-After header, and resilient clients should wait and retry instead of immediately resubmitting requests.

This is especially important in bulk workloads because Microsoft notes that bulk-operation projects place extraordinary demand on server resources and should be designed to handle service protection limit errors as transient faults. Increasing request pressure instead of respecting the wait interval usually makes the situation worse rather than better.

<sub>Set F · Q48</sub>

---

### 186. A process must update 60 related Dataverse rows as one logical unit. The team wants fewer HTTP round trips, but if any single update fails, none of the updates can be committed.

Which implementation approach should you choose?

- **A.** Parallel PATCH calls
- **B.** $batch change set ✅
- **C.** Execute child flows
- **D.** Sequential single-row update requests

> **Answer:** B. $batch change set

A Web API $batch request that uses a change set is the best fit because Microsoft documents that change sets let multiple operations be included as a single transaction. Microsoft also states that when operations are inside a change set, they are atomic, so if one fails, completed operations in that change set are rolled back.

This design also reduces HTTP chatter because Microsoft documents batch APIs as grouping multiple operations into a single request for greater efficiency, while still allowing the architect to tune batch size and concurrency for best results. It is the strongest answer when the requirement combines transaction semantics with request-efficiency goals.

<sub>Set F · Q49</sub>

---

### 187. A Power Platform solution must run a nightly reconciliation job, respond to event-driven messages during the day, and call Azure Key Vault without storing secrets in code or configuration. One branch of the workload can run for several minutes and must survive transient interruptions.

Which design should you recommend?

- **A.** Real-time plug-in + app secret
- **B.** Scheduled cloud flow + connector key
- **C.** Azure Function + managed identity ✅
- **D.** JavaScript web resource + environment variable

> **Answer:** C. Azure Function + managed identity

Azure Functions with managed identity is the best design because Azure Functions supports trigger-based execution for scheduled and event-driven workloads, while managed identity lets the function app access Microsoft Entra-protected resources like Azure Key Vault without storing credentials. Microsoft documents both the trigger model in Azure Functions and the use of managed identities for Azure Functions apps to reach protected resources securely.

For the long-running branch, durable execution is the stronger pattern than ad hoc request/response logic. Microsoft documents Durable Task and Durable Functions as a fit for long-running processes and stateful orchestration that must persist progress across interruptions, which maps cleanly to the scenario’s reliability requirement.

<sub>Set F · Q52</sub>

---

### 188. A flow must start when a Dataverse custom API that is exposed as a business event is invoked. Which Dataverse trigger should you configure? Select only one answer.

- **A.** When an action is performed ✅
- **B.** When a row is added, modified or deleted
- **C.** Perform a bound action
- **D.** Get a row

> **Answer:** A. When an action is performed

When an action is performed is the correct trigger because Microsoft documents Dataverse business events as being exposed asynchronously through the Dataverse connector by using the When an action is performed trigger. That is the documented trigger pattern for action-style business events and custom API-driven event exposure.

The other named items are either row-change triggers or actions, not the trigger that starts the flow for this event style. Microsoft’s Dataverse flow integration overview separates connector triggers from connector actions, and it lists bound and unbound actions as actions that are performed inside a flow, not the trigger that starts it.

<sub>Set F · Q54</sub>

---

### 189. A solution-aware parent flow already retrieves its ERP secret from Azure Key Vault through an environment variable reference. The team now wants to reuse the same ERP-call logic across six automations and ensure the sensitive payload does not appear in run history. Which two changes should you make? (Select TWO.)

- **A.** Hardcoded API key
- **B.** Child flow wrapper ✅
- **C.** Fixed retry burst loop
- **D.** Secure inputs/outputs ✅
- **E.** Plain-text Compose logging step

> **Answer:** B. Child flow wrapper · D. Secure inputs/outputs

Child flows are the right reuse mechanism because Microsoft documents them as reusable components that can be called from multiple parent flows, helping keep large automations modular and maintainable. That matches the requirement to centralize the same ERP-call logic for six separate automations.

Secure inputs and outputs are the right protection mechanism because Microsoft documents them as the feature that prevents sensitive data from appearing in run history and audit-style views. Since the secret source is already handled through Azure Key Vault-backed environment variable references, the next best security step for the execution path is to mask the sensitive payload in flow history.

<sub>Set F · Q55</sub>

---
