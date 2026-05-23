# Develop Integrations  

_Exam weight 10–15% · 42 questions across all sets._

---

### 1. A Dataverse event is being published to Azure by using a service endpoint registered in the Plug-in Registration Tool. The contract type is One-way. The listener application is frequently offline overnight, and the related async system jobs eventually fail after multiple retries.

Which change is the best fit if the team wants Dataverse to continue publishing events without requiring an actively listening endpoint at all times?

- **A.** Switch to Queue ✅
- **B.** Switch to Two-way
- **C.** Use a synchronous step
- **D.** Register a WebHook instead

> **Answer:** A. Switch to Queue

Queue is the best fit because Microsoft states that a queue contract does not require a listener to be actively listening for messages at the endpoint. In contrast, a one-way contract requires an active listener, and if none is present Dataverse retries the post with increasing intervals until the async system job is eventually aborted and marked failed.

This makes queue the right durability-oriented correction for the incident described. The problem is not that Dataverse cannot raise the event, but that the chosen contract type assumes a live listener. Moving to a queue changes the delivery model to one that better tolerates listener downtime.

<sub>Set A · Q34</sub>

---

### 2. A developer is testing a Dataverse synchronization routine that uses an alternate key on accountnumber. The first call creates the row, and the same entity instance is then sent again after changing the account name.

Snippet

var account = new Entity("account", "accountnumber", "0003");
account["name"] = "New Account";

var response1 = (UpsertResponse)svc.Execute(
    new UpsertRequest { Target = account });

account["name"] = "Updated Account";

var response2 = (UpsertResponse)svc.Execute(
    new UpsertRequest { Target = account });
What does the second response indicate?

- **A.** New row created
- **B.** Alternate key removed
- **C.** Existing row updated ✅
- **D.** Table metadata refreshed

> **Answer:** C. Existing row updated

The second response indicates that the existing row was updated. Microsoft’s SDK documentation shows this exact pattern: the first upsert creates the account row, and the second upsert updates it because the same accountnumber alternate key matches an existing record. Microsoft also shows that RecordCreated is true on the first call and false on the second.

This is one of the clearest demonstrations of how UpsertRequest supports data synchronization. The integration can keep sending the same externally keyed record, and Dataverse resolves whether the operation should insert or update based on the presence of a matching row.

<sub>Set A · Q50</sub>

---

### 3. A team wants Dataverse to send event data to an Azure Function endpoint that already expects the function key as a code query-string parameter. They want to register the endpoint directly in the Plug-in Registration Tool.

Which WebHook authentication option should they choose?

- **A.** HttpHeader
- **B.** HttpQueryString
- **C.** WebHookKey ✅
- **D.** SharedAccessSignature

> **Answer:** C. WebHookKey

WebHookKey is the best choice because the Plug-in Registration Tool supports it specifically for endpoints that expect the authentication value in a query string using the key name code. Microsoft’s WebHook registration guidance explicitly notes that this option is useful with Azure Functions because Azure Functions commonly expect that pattern.

This is a better fit than the other WebHook authentication choices because the requirement is already defined by the receiving Azure Function. In the Plug-in Registration Tool, WebHook registrations capture the endpoint URL and one of the supported authentication models, and WebHookKey maps directly to the Azure Function-style ?code=... requirement.

<sub>Set A · Q67</sub>

---

### 4. A developer wants Dataverse to publish the execution context for the Create message on the account table to Azure Service Bus by using the out-of-box Azure-aware capability. They want to use the Plug-in Registration Tool and avoid writing custom plug-in code.

Which two actions are required? (Select TWO.)

- **A.** Register a service endpoint ✅
- **B.** Register a step for the message and table ✅
- **C.** Upload a custom Azure-aware assembly
- **D.** Force synchronous execution
- **E.** Create a pre-image for all steps

> **Answer:** A. Register a service endpoint · B. Register a step for the message and table

The required actions are to register a service endpoint and then register a step that identifies the message and table combination that should trigger publication. Microsoft’s Azure integration guidance states that the out-of-box Azure-aware plug-in is made available by registering a service endpoint in the Plug-in Registration Tool, and that a plug-in step must then be registered to identify the event that triggers the posting notification.

This is also consistent with the general Plug-in Registration Tool model. Microsoft’s registration guidance explains that steps define the runtime conditions for execution, including the message and primary entity. For Azure-aware publication, the step is what binds the Dataverse event to the registered service endpoint.

<sub>Set A · Q69</sub>

---

### 5. A team is configuring a service endpoint in the Plug-in Registration Tool for an Azure Event Hubs solution. They want a registration that aligns with Microsoft’s documented Event Hubs requirements.

Exhibit 1

Which option is correctly configured for Azure Event Hubs?

- **A.** Option A
- **B.** Option B
- **C.** Option C
- **D.** Option D ✅

> **Answer:** D. Option D

Option D is correct because Microsoft states that for an Event Hubs solution, the Plug-in Registration Tool registration must use a contract type of Event Hub. Microsoft also states that only SAS authorization is permitted for this registration type, and that the message body format can be either XML or JSON. Option D is the only row that satisfies all of those conditions.

The exhibit is designed to test both endpoint type and authorization model. Even though XML and JSON are both valid body formats for Event Hubs, the contract type and the use of SAS are the critical requirements, which is why the other rows fail.

<sub>Set A · Q72</sub>

---

### 6. An external order system sends records to Dataverse by using a business identifier that already exists in the source system. The synchronization process must create the row if it doesn’t exist and update it if it does, without first retrieving the row to check.

Which message should the integration use?

- **A.** RetrieveRequest
- **B.** UpsertRequest ✅
- **C.** CreateRequest
- **D.** UpdateRequest

> **Answer:** B. UpsertRequest

UpsertRequest is the best fit because Microsoft documents upsert as the pattern to reduce complexity in data integration scenarios where you might not know whether the record already exists. Instead of retrieving first and then deciding between create or update, the platform handles that decision for you. Microsoft also notes that this is commonly paired with alternate keys in integration scenarios.

This is exactly the synchronization pattern described in the question. The source system already has a business identifier, and the Dataverse side needs a single write path that can create missing rows or update existing ones. That makes UpsertRequest the cleanest message for the design.

<sub>Set A · Q75</sub>

---

### 7. A company wants Dataverse to publish account update events to Azure. Several downstream services must each receive the same published event independently. The team does not want the design limited to a single consumer.

Which contract should they choose when they register the service endpoint in the Plug-in Registration Tool?

- **A.** Queue
- **B.** Topic ✅
- **C.** One-way
- **D.** Two-way

> **Answer:** B. Topic

A Topic contract is the best fit because Microsoft defines a topic as similar to a queue except that one or more listeners can subscribe to receive messages from it. That matches the requirement for multiple downstream services to receive the same Dataverse-published event stream.

This is a better design than a queue when fan-out is required. A queue is suited to message delivery semantics where a listener reads from the queue, but the topic contract is the documented Service Bus pattern that supports multiple subscribers for the same published Dataverse event.

<sub>Set A · Q77</sub>

---

### 8. A .NET synchronization worker must write customer rows to Dataverse by using an external account number. The team also needs to know, for each write, whether Dataverse created a new row or updated an existing one because downstream logging differs for inserts and updates.

Which implementation approach is the best fit?

- **A.** Web API PATCH by key
- **B.** CreateRequest then UpdateRequest
- **C.** UpdateRequest with RowVersion
- **D.** SDK UpsertRequest with RecordCreated ✅

> **Answer:** D. SDK UpsertRequest with RecordCreated

The SDK UpsertRequest with UpsertResponse.RecordCreated is the best fit because Microsoft documents that RecordCreated tells you whether the record was created, and the SDK sample shows using that property to distinguish between new and existing rows. That directly satisfies the logging requirement in the scenario.

This is also a better fit than a generic Web API PATCH when the design explicitly needs a reliable created-versus-updated signal. Microsoft documents that plain Web API upsert returns 204 No Content in either case unless you add the representation-return preference, so the SDK route is the cleaner synchronization design here.

<sub>Set A · Q78</sub>

---

### 9. An ERP system sends product rows to Dataverse by using an external product code that is unique in the source system. The integration must keep Dataverse synchronized without relying on Dataverse GUIDs and must avoid composing the request in a way that can introduce key mismatches.

Which two design decisions should be included? (Select TWO.)

- **A.** Repeat key values in Attributes
- **B.** Alternate key on source code ✅
- **C.** Notes-based row matching
- **D.** Virtual table key mapping
- **E.** UpsertRequest for inbound rows ✅

> **Answer:** B. Alternate key on source code · E. UpsertRequest for inbound rows

An alternate key on the source code is correct because Microsoft documents alternate keys as the way to identify Dataverse rows by business columns instead of only a GUID primary key, especially for external-system integration. UpsertRequest is also correct because Microsoft describes upsert as the message to use when synchronization needs to create or update based on whether a matching row already exists.

Together, these two choices produce a clean synchronization design: the alternate key defines how the external identifier maps to Dataverse identity, and upsert uses that identity to keep the row synchronized without a preliminary existence check. Microsoft also warns against duplicating alternate key data in the saved-attribute portion of the request because it can create mismatch problems.

<sub>Set A · Q79</sub>

---

### 10. A nightly synchronization job uses alternate-key upsert semantics for a custom table. Most rows work, but rows whose external key contains values such as A/102 or EU+44 consistently fail when the integration tries to update or upsert them by key.

What is the most likely cause?

- **A.** Unsupported key characters ✅
- **B.** Missing row sharing
- **C.** Disabled plug-in step
- **D.** Wrong business unit

> **Answer:** A. Unsupported key characters

The most likely cause is unsupported characters in alternate key values. Microsoft documents that if the data in a column used in an alternate key contains characters such as / or +, then retrieve, update, or upsert actions using those keys don’t work. That matches the failure pattern in the scenario exactly.

This is an important design consideration when using UpsertRequest for synchronization. Even if a source-system identifier is unique, it may still be a poor alternate-key choice if its value format includes characters Dataverse doesn’t support for key-based retrieve, update, or upsert operations.

<sub>Set A · Q80</sub>

---

### 11. You are registering a Dataverse webhook that targets an Azure Function endpoint. The function owner says the request must include the function key by using the code query-string parameter, and you should not send custom header pairs instead.

Which authentication option should you choose for the service endpoint?

- **A.** HttpHeader
- **B.** HttpQueryString
- **C.** WebhookKey ✅
- **D.** SAS key

> **Answer:** C. WebhookKey

WebhookKey is the correct choice because Microsoft states that this option includes a query string using code as the key and that it is useful with Azure Functions because the authentication query string is expected to have a key name of code. That is an exact match for the requirement in the scenario.

This is also why HttpHeader is not appropriate here. The endpoint owner is explicitly asking for the Azure Functions-style query-string secret rather than custom header-based authentication, and WebhookKey is the specific Dataverse registration option designed for that pattern.

<sub>Set B · Q23</sub>

---

### 12. A Dataverse integration must push the same event stream to several independent downstream consumers without creating a separate endpoint for each listener.

Which contract should you register?

- **A.** Queue
- **B.** One-way
- **C.** REST
- **D.** Topic ✅

> **Answer:** D. Topic

A Topic contract is the best fit because Microsoft documents that a topic is similar to a queue except that one or more listeners can subscribe to receive messages from it. That directly matches the fan-out requirement in the question.

The other Service Bus contracts have different delivery characteristics. A queue is for queued delivery, a one-way contract requires an active listener, and a REST contract is described as similar to a two-way contract on a REST endpoint. None of those matches the requirement as cleanly as a topic when multiple downstream subscribers are expected.

<sub>Set B · Q72</sub>

---

### 13. A developer is registering a Dataverse service endpoint that will send runtime event data to Azure Event Hubs.

Which two settings are supported for that registration? (Select TWO.)

- **A.** Queue contract with relay listener
- **B.** Event Hub contract ✅
- **C.** OAuth 2.0 authorization mode
- **D.** JSON body format ✅
- **E.** WebhookKey authentication

> **Answer:** B. Event Hub contract · D. JSON body format

Event Hub contract is correct because Microsoft states that when you fill out the Plug-in Registration Tool form for this scenario, you should specify a contract type of Event Hub. That is the contract type specifically associated with Azure Event Hubs solutions.

JSON body format is also correct because Microsoft says the message body format for Event Hub registration can be XML or JSON. The same documentation also notes that only SAS authorization is permitted and that you must provide the connection string for the event hub, which helps eliminate several of the distractors.

<sub>Set B · Q73</sub>

---

### 14. A team wants a webhook registration for contact updates. The external service should be called only when firstname or lastname changes, and failures must be reviewable later without blocking the user’s save operation.

Exhibit 1

Which row best matches the requirement?

- **A.** Row 1 ✅
- **B.** Row 2
- **C.** Row 3
- **D.** Row 4

> **Answer:** A. Row 1

Row 1 is the best fit because Microsoft says that when you register a webhook step, you can specify execution mode and pipeline stage, and if you do not set filtering attributes for a message that supports them, you are prompted to do so as a performance best practice. Using firstname,lastname limits unnecessary webhook calls, and asynchronous execution avoids blocking the save while still capturing failures in System Jobs.

Microsoft also explains that asynchronous webhook failures are recorded in System Jobs, where you can review status and failure details later. That matches the requirement that failures be reviewable without interrupting the user’s save. A synchronous registration would instead surface endpoint problems directly to the user.

<sub>Set B · Q74</sub>

---

### 15. A synchronous webhook step posts successfully to an external API. The API returns HTTP 200 and includes a JSON body telling Dataverse to skip downstream processing. The developer expects Dataverse to parse that body and alter the current operation, but nothing changes in the platform.

What is the most likely cause?

- **A.** HTTP payload truncation behavior
- **B.** Missing step registration
- **C.** Response body ignored ✅
- **D.** Asynchronous execution requirement for webhooks

> **Answer:** C. Response body ignored

The most likely cause is that Dataverse does not parse the response body for webhook registrations. Microsoft states that the system sends the request and evaluates the response, but it cannot parse any data returned in the body and only looks at the response StatusCode value. That means a 200 response can signal success, but the returned JSON body itself will not instruct Dataverse to change platform behavior.

This is why the design assumption is flawed even though the HTTP call succeeds. Webhooks are useful for notifying external services, but they are not a general response-body command channel back into the Dataverse transaction pipeline. If the step is synchronous, the main impact of the response is whether the request is considered successful or failed.

<sub>Set B · Q75</sub>

---

### 16. An architecture review identifies two external listener needs for Dataverse events. One consumer needs high-throughput streaming for analytics, and another needs enterprise publish-subscribe messaging for multiple downstream processors.

Which two options should you recommend? (Select TWO.)

- **A.** Synchronous plug-in step
- **B.** Webhook endpoint
- **C.** Azure Event Hubs ✅
- **D.** Power Automate cloud flow
- **E.** Service Bus topic ✅

> **Answer:** C. Azure Event Hubs · E. Service Bus topic

Azure Event Hubs is the right choice for the analytics-style listener because Microsoft describes it as a big data streaming platform and event ingestion service that can receive and process millions of events per second. Service Bus topics are the right fit for enterprise pub/sub because Azure Service Bus provides brokered messaging with topics, and Microsoft states that a topic is similar to a queue except that one or more listeners can subscribe to receive messages from it.

These two recommendations also match the stated requirement split. One requirement is about streaming large volumes of ordered event data for analytics, while the other is about reliable enterprise-style distribution to multiple downstream consumers. Those are different problem shapes, and Microsoft’s messaging guidance separates Event Hubs and Service Bus accordingly.

<sub>Set C · Q44</sub>

---

### 17. A product owner wants a low-code listener for a Dataverse business event. The response must run asynchronously after the event occurs, and the team does not want to build a custom HTTP listener or .NET event handler.

Exhibit 1

Which option best fits the requirement?

- **A.** Synchronous plug-in step
- **B.** Webhook endpoint
- **C.** Power Automate flow ✅
- **D.** Azure Event Hubs listener

> **Answer:** C. Power Automate flow

Power Automate flow is the best fit because Microsoft states that Dataverse business events provide ways to expose events and compose logic asynchronously, including the Power Automate Dataverse “When an action is performed” trigger. That matches both the low-code requirement and the asynchronous response requirement in the exhibit.

The exhibit also rules out the other choices by design. The team does not want custom code or a custom external endpoint, and the need is not high-throughput streaming analytics. Power Automate is therefore the cleanest recommendation for a low-code asynchronous listener.

<sub>Set C · Q51</sub>

---

### 18. A validation rule must stop a row update before the transaction completes and show the user an error immediately.

Which listener option should you recommend?

- **A.** Webhook endpoint
- **B.** Synchronous plug-in step ✅
- **C.** Azure Event Hubs listener
- **D.** Power Automate cloud flow

> **Answer:** B. Synchronous plug-in step

A synchronous Dataverse plug-in step is the best fit because plug-ins run during Dataverse data processing, and synchronous plug-ins make the data operation wait until the code finishes. Microsoft also documents that plug-ins can cancel the current pipeline operation and optionally display an error to the user, which is exactly what this requirement needs.

The other options are listeners for external or asynchronous handling patterns, but they are not the right choice when the requirement is in-transaction enforcement. For immediate validation that can block the save, the listener must participate directly in the Dataverse event pipeline rather than reacting later outside it.

<sub>Set C · Q74</sub>

---

### 19. A team needs Dataverse to notify a custom external web application whenever a row is updated. The listener must receive an HTTP POST with JSON, and the team wants a simpler endpoint-security model than Azure Service Bus SAS.

Which option should you recommend?

- **A.** Power Automate cloud flow
- **B.** Service Bus topic endpoint
- **C.** Azure Event Hubs consumer
- **D.** Webhook endpoint ✅

> **Answer:** D. Webhook endpoint

A webhook endpoint is the best recommendation because Microsoft documents webhooks as a way to send Dataverse server events to an external web application using POST requests with JSON payloads. The same guidance also notes that webhook endpoint security can use authentication headers or query string keys, and that this approach is simpler than the SAS model used with Azure Service Bus integration.

This option also fits the listener style more closely than the alternatives because it is a direct external callback pattern. Microsoft further distinguishes webhooks from Azure Service Bus by noting that webhooks can be used with synchronous and asynchronous steps, while Azure Service Bus allows only asynchronous steps.

<sub>Set C · Q75</sub>

---

### 20. A Dataverse event is posted to an Azure Service Bus service endpoint that uses a one-way contract. The listener process is often offline, and system jobs keep retrying until they fail. The business requirement is to allow the consumer to read the event later without requiring an always-running listener.

What should you recommend?

- **A.** Start a persistent listener
- **B.** Increase retry frequency
- **C.** Use a queue contract ✅
- **D.** Replace with a webhook endpoint

> **Answer:** C. Use a queue contract

A queue contract is the best recommendation because Microsoft states that a queue contract provides a cloud message queue and that a listener does not have to actively listen on the endpoint. By contrast, Microsoft says a one-way contract requires an active listener, and if none is available the post fails and Dataverse retries until the asynchronous system job is eventually aborted.

This makes the problem a mismatch between listener contract and runtime availability. The requirement is specifically for later consumption without a permanently active listener, which is exactly the behavior queue-based brokered messaging is designed to support.

<sub>Set C · Q76</sub>

---

### 21. A nightly synchronization service was paused for more than a week because of an infrastructure outage. When the team resumes processing and reuses the last stored change-tracking token, Dataverse throws an exception instead of returning incremental changes.

What should you do first?

- **A.** Reinitialize the sync baseline ✅
- **B.** Add $top to the delta request
- **C.** Switch to auditing for deltas
- **D.** Retry the same delta link

> **Answer:** A. Reinitialize the sync baseline

Reinitializing the sync baseline is the right first step because Microsoft states that changes are returned only if the last token is within a default seven-day window, controlled by the ExpireChangeTrackingInDays organization setting. If unprocessed changes are older than the configured value, Dataverse throws an exception rather than continuing from that stale token.

That means the problem is not a transient request-format error. The saved continuation point has aged beyond the retention window, so the integration must re-establish a fresh baseline and obtain a new tracking state instead of trying to force the expired token to continue working.

<sub>Set D · Q38</sub>

---

### 22. A downstream warehouse stores account data from Dataverse. The sync job must avoid full-table comparisons on each run and retrieve only rows that changed since the last successful synchronization.

Which Dataverse capability should the integration use?

- **A.** Audit history
- **B.** Duplicate detection
- **C.** Change tracking ✅
- **D.** Scheduled full export reconcile

> **Answer:** C. Change tracking

Change tracking is the best fit because Microsoft documents it as the Dataverse feature used to keep external systems synchronized efficiently by detecting what changed since the data was first extracted or last synchronized. That is exactly the requirement in the stem: incremental synchronization instead of repeated full comparisons.

It is also the feature the platform exposes specifically for this pattern through table settings and Web API or SDK retrieval mechanisms. Once enabled for a table, the integration can establish a tracking context and then request only the subsequent changes rather than re-reading everything each cycle.

<sub>Set D · Q71</sub>

---

### 23. An integration service already completed its initial export of a custom Dataverse table. The team now wants every later cycle to stay incremental and still remove rows from the external store when records are deleted in Dataverse.

Which TWO actions should the service implement? (Select TWO.)

- **A.** Save the latest delta link ✅
- **B.** Add $orderby to change requests
- **C.** Re-enable Track changes before each run
- **D.** Process deleted-entity entries ✅
- **E.** Add $top to the initial tracking request

> **Answer:** A. Save the latest delta link · D. Process deleted-entity entries

The service should save the latest delta link and process deleted-entity entries. Microsoft documents the @odata.deltaLink as the service-generated link used to retrieve subsequent changes, and the delta response can include deleted-row markers that the client must interpret so downstream stores stay synchronized when records are removed.

Those two behaviors are what make the synchronization loop both incremental and correct over time. If the service fails to persist the newest delta link, it loses its continuation point, and if it ignores deleted entries, the external store will drift because records removed in Dataverse will remain behind in the target system.

<sub>Set D · Q72</sub>

---

### 24. A custom integration wants to start incremental synchronization for the account table by using the Dataverse Web API. The first request must establish the change-tracking context that later requests will reuse.
Which value from the response should the client persist for the next incremental request?

Snippet

GET https://org.crm.dynamics.com/api/data/v9.2/accounts?$select=name,accountnumber
Prefer: odata.track-changes
OData-Version: 4.0

HTTP/1.1 200 OK
Preference-Applied: odata.track-changes

{
  "@odata.context": "https://org.crm.dynamics.com/api/data/v9.2/$metadata#accounts(name,accountnumber)",
  "@odata.deltaLink": "https://org.crm.dynamics.com/api/data/v9.2/accounts?$select=name,accountnumber&$deltatoken=...",
  "value": [
    {
      "accountid": "60c4e274-0d87-e711-80e5-00155db19e6d",
      "name": "Contoso"
    }
  ]
}

- **A.** @odata.context value
- **B.** @odata.deltaLink ✅
- **C.** Preference-Applied header
- **D.** First accountid value

> **Answer:** B. @odata.deltaLink

@odata.deltaLink is the value the client must persist because Microsoft describes the delta link as the opaque, service-generated link used to retrieve subsequent changes for the tracked result set. It represents the continuation point for later incremental synchronization cycles.

The other response elements are useful in their own ways, but they do not serve as the synchronization token. The integration should treat the delta link as the durable tracking artifact and use it on later requests instead of trying to reconstruct its own notion of where the change stream should resume.

<sub>Set D · Q74</sub>

---

### 25. A sync worker is being built for a custom Dataverse table that the team wants to keep aligned with an external data store. The design must follow the supported Web API change-tracking pattern from first-time setup into later incremental cycles.

Steps

Persist the returned delta link after successful processing.

Enable Track changes on the table.

Send the initial request with Prefer: odata.track-changes.

Process the returned rows and any deleted-entity entries.

What is the correct order?

- **A.** 3 → 2 → 4 → 1
- **B.** 2 → 4 → 3 → 1
- **C.** 4 → 2 → 1 → 3
- **D.** 2 → 3 → 4 → 1 ✅

> **Answer:** D. 2 → 3 → 4 → 1

The correct order is 2 → 3 → 4 → 1. First, the table must have Track changes enabled. Next, the integration sends the initial request with Prefer: odata.track-changes to establish tracking and receive a delta link. Then it processes the returned rows, including deleted-entity entries, and finally it stores the newest delta link for the next incremental cycle.

This sequence matches the documented Dataverse protocol rather than a custom polling design. The integration begins with feature enablement, establishes the server-generated tracking context, handles the current change set correctly, and only then persists the continuation point that will drive later delta requests.

• 2 is first because change tracking must be enabled on the table before the sync design can rely on it. Microsoft explicitly says to make sure change tracking is enabled before retrieving changes for a table.

• 3 is second because the initial Web API request with Prefer: odata.track-changes is what establishes the tracking context and returns the first delta link. Without that request, there is no continuation token to drive later incremental synchronization.

• 4 is third because the integration must apply the returned changes, including deleted-row markers, before it advances its continuation state. That keeps the external store consistent with the actual Dataverse change set represented by the response.

• 1 is last because the integration should store the latest delta link after it has successfully processed the current results. Persisting the continuation point too early risks advancing the bookmark before the downstream sync has actually completed.

<sub>Set D · Q75</sub>

---

### 26. A developer writes a custom Azure-aware plug-in and retrieves IServiceEndpointNotificationService from IServiceProvider. During testing, the returned service is always null. The step is currently registered as a synchronous plug-in, and the team also wants the implementation to stay within the supported Azure-aware registration model.

What should the developer change?

- **A.** Synchronous PreOperation sandbox step registration
- **B.** Service endpoint table caching
- **C.** Application user impersonation mode
- **D.** Asynchronous sandbox registration ✅

> **Answer:** D. Asynchronous sandbox registration

The best fix is Asynchronous sandbox registration. Microsoft states that the notification service is only provided for asynchronous registered plug-ins, and the Azure-aware custom plug-in guidance also says the plug-in must be registered to execute in the sandbox. Those two requirements together make asynchronous sandbox registration the supported configuration for this pattern.

This question is testing the registration model rather than the code line itself. Even correct publish code will fail to retrieve the notification service if the step is registered synchronously, and Azure-aware custom plug-ins are specifically constrained to sandbox execution.

<sub>Set E · Q3</sub>

---

### 27. A custom Dataverse plug-in must publish the current execution context to Azure Service Bus when a row is updated. The developer wants to retrieve the correct service from IServiceProvider and use the supported Dataverse mechanism.

Which service should the plug-in request?

- **A.** Organization service factory
- **B.** Service endpoint notification service ✅
- **C.** Tracing service with Service Bus relay
- **D.** Dataverse listener registration context

> **Answer:** B. Service endpoint notification service

The correct choice is Service endpoint notification service because IServiceEndpointNotificationService is the Dataverse interface that posts the plug-in execution context to Azure Service Bus. Microsoft’s API reference states that this interface posts the execution context to the specified cloud service endpoint, and the plug-in execution method documentation lists it as one of the services available through IServiceProvider.

This is the supported integration surface when the goal is to publish the current Dataverse execution context rather than perform normal CRUD or tracing. In practice, the plug-in obtains the execution context and the notification service from IServiceProvider, then calls Execute(EntityReference, IExecutionContext) against a registered service endpoint.

<sub>Set E · Q59</sub>

---

### 28. You need to update an Account row by using the external account number because the source system does not store the Dataverse GUID.

Which SDK for .NET approach should you use?

- **A.** EntityReference("account", id)
- **B.** new Account()
- **C.** Entity("account", KeyAttributeCollection) ✅
- **D.** RetrieveRequest(ColumnSet)

> **Answer:** C. Entity("account", KeyAttributeCollection)

The correct approach is to create an Entity by using the constructor that accepts a KeyAttributeCollection. Microsoft documents that when you update a Dataverse row by alternate key in the SDK for .NET, you must use the Entity(String, KeyAttributeCollection) constructor to identify the row, because the alternate key values belong in KeyAttributes rather than Attributes.

This is the core SDK pattern for alternate-key-based synchronization. Dataverse alternate keys exist specifically to identify rows by business columns instead of only by GUIDs, which is why this constructor is the best fit when the source system knows an external identifier but not the Dataverse primary key.

<sub>Set E · Q65</sub>

---

### 29. An ERP system sends customer updates with accountnumber, but it never stores the Dataverse row ID. The integration must avoid a separate existence check and should create the row when it does not exist or update it when it already exists.

Which approach should you implement?

- **A.** POST then duplicate retry
- **B.** GET by filter then PATCH
- **C.** PATCH by GUID URL
- **D.** PATCH by alternate key URL ✅

> **Answer:** D. PATCH by alternate key URL

PATCH by alternate key URL is the best fit because Microsoft documents that in the Dataverse Web API, the keys in the URL identify the resource, and alternate keys can be used directly in that URL. Microsoft also explains that PATCH to a specified entity-set resource can drive update or upsert behavior, which removes the need for a separate existence check in common synchronization scenarios.

This is exactly why alternate keys are useful for integration code. They let the source system use a business identifier such as accountnumber in place of the GUID, and Upsert reduces the branching logic that would otherwise require a retrieve-first pattern.

<sub>Set E · Q66</sub>

---

### 30. A developer is defining a Dataverse alternate key that will be used by synchronization code. Which two column choices are valid for the key definition? (Select TWO.)

- **A.** Single line text ✅
- **B.** Single line text with field security
- **C.** Multi-line text column
- **D.** File column
- **E.** Lookup column ✅

> **Answer:** A. Single line text · E. Lookup column

Single line text and Lookup column are both valid choices. Microsoft documents that alternate keys can include supported column types such as single line of text, whole number, decimal, date time, lookup, and option set.

This matters in synchronization design because the alternate key is not just any unique-looking column combination. Dataverse validates the key definition against supported types and other constraints, so developers need to choose columns that are both uniquely meaningful and technically eligible for alternate-key operations.

<sub>Set E · Q68</sub>

---

### 31. A developer wants to update an Account row by using the accountnumber alternate key. The following code does not correctly express the alternate-key identity.

Snippet

Account account = new Account();
account["accountnumber"] = "AC-1007";
account.Name = "Contoso North";
service.Update(account);
What is the best fix?

- **A.** Set account.Id after query
- **B.** Create Entity("account", keys) ✅
- **C.** Switch to CreateRequest
- **D.** Add accountnumber to ColumnSet

> **Answer:** B. Create Entity("account", keys)

The best fix is to create an Entity("account", keys) by using a KeyAttributeCollection, and then update that entity or convert it to an early-bound Account if needed. Microsoft states that for SDK update by alternate key, you must use the Entity(String, KeyAttributeCollection) constructor, because the alternate key identifies the row through KeyAttributes rather than through normal attribute assignment.

In the snippet, account["accountnumber"] is being set as regular attribute data, not as the row identity. That means the code is not telling Dataverse to target an existing row by alternate key. The supported pattern is to construct the entity with the key definition first, then set the non-key data you want to change.

<sub>Set E · Q69</sub>

---

### 32. An integration uses this Web API pattern to update rows by external reference:
PATCH /accounts(accountnumber='EU/2026/0042')

The accountnumber column is configured as an alternate key, and uniqueness is enforced in Dataverse. The request still fails during synchronization.

What is the most likely cause?

- **A.** Unsupported key characters ✅
- **B.** Missing duplicate rule
- **C.** Too many key definitions
- **D.** Early-bound type mismatch

> **Answer:** A. Unsupported key characters

The most likely cause is unsupported key characters. Microsoft documents that if an alternate-key value contains any of these characters /, <, >, *, %, &, :, \\, ?, or +, then Web API retrieve, update, and upsert operations using that key do not work. The slash in EU/2026/0042 matches that restriction exactly.

This is an important PL-400 integration nuance because a column can still be unique and still be a poor choice for API-based synchronization. Microsoft explicitly notes that such a key can still serve uniqueness purposes, but if you need to use it in integration operations, you should choose columns whose values do not contain those unsupported characters.

<sub>Set E · Q72</sub>

---

### 33. A team is implementing a custom Azure-aware plug-in that will publish Dataverse event context to Azure Service Bus. Which TWO actions are part of the supported implementation pattern? (Select TWO.)

- **A.** Register the plug-in outside sandbox for direct network access
- **B.** Pass the endpoint ID as unsecure config ✅
- **C.** Expect the notification service on synchronous steps
- **D.** Execute with serviceendpoint reference and context ✅
- **E.** Replace the service endpoint row with a webhook URL

> **Answer:** B. Pass the endpoint ID as unsecure config · D. Execute with serviceendpoint reference and context

The two correct actions are Pass the endpoint ID as unsecure config and Execute with serviceendpoint reference and context. Microsoft’s Azure-aware plug-in example shows the service endpoint ID being passed into the constructor through unsecure configuration when the step is registered, and the sample then calls Execute(new EntityReference("serviceendpoint", serviceEndpointId), context).

These are both implementation details specific to the documented pattern for publishing Dataverse execution context to Azure Service Bus. The plug-in is not calling a webhook URL directly; it is using a registered serviceendpoint row and the current execution context through the notification service.

<sub>Set E · Q73</sub>

---

### 34. A developer is reviewing the publishing logic in a custom Azure-aware plug-in.

Snippet

IPluginExecutionContext context =
    (IPluginExecutionContext)serviceProvider.GetService(typeof(IPluginExecutionContext));

IServiceEndpointNotificationService cloudService =
    (IServiceEndpointNotificationService)serviceProvider.GetService(typeof(IServiceEndpointNotificationService));

string response = cloudService.Execute(
    new EntityReference("account", serviceEndpointId),
    context);
What should the developer change?

- **A.** serviceendpoint logical name ✅
- **B.** organization logical name value
- **C.** tracing service instance
- **D.** sdkmessageprocessingstep entity reference

> **Answer:** A. serviceendpoint logical name

The code should use serviceendpoint logical name. Microsoft’s Azure-aware plug-in sample calls Execute with new EntityReference("serviceendpoint", serviceEndpointId) and the current execution context, which means the entity reference must point to the registered service endpoint record rather than a business table such as account.

The rest of the pattern is correct in principle: retrieve the execution context and notification service from IServiceProvider, then publish using Execute(EntityReference, IExecutionContext). The specific defect is the wrong logical name in the EntityReference.

<sub>Set E · Q74</sub>

---

### 35. A custom Azure-aware plug-in publishes Dataverse event context to Azure Service Bus from an asynchronous step. During a temporary Service Bus outage, downstream systems later receive duplicate side effects after retry. The plug-in not only modifies the execution context before publishing, but also performs extra business logic before returning.

What is the best redesign?

- **A.** One-way endpoint contract
- **B.** Synchronous PostOperation step
- **C.** Publish-only plug-in design ✅
- **D.** Binary XML message format setting

> **Answer:** C. Publish-only plug-in design

The best redesign is Publish-only plug-in design. Microsoft warns that for asynchronous registered plug-ins, if the Azure Service Bus post is retried after a failure, the entire plug-in logic is executed again. Because of that, Microsoft specifically says not to add other logic to the custom Azure-aware plug-in beyond modifying the context and posting to the service bus.

This means the duplication problem is not best solved by changing message format or switching the step to synchronous execution. The supported and safest redesign is to keep the Azure-aware plug-in narrowly focused on publishing, so retry behavior does not replay unrelated business side effects.

<sub>Set E · Q75</sub>

---

### 36. A scheduled integration runs every five minutes between Dataverse and a downstream platform. It must avoid rereading unchanged rows, survive retries without creating duplicates, and recover cleanly when Dataverse returns 429 responses during peak load.

Which sync pattern should you choose?

- **A.** Delta sync with keyed upsert ✅
- **B.** Full-table compare with parallel create and update
- **C.** Audit-log replay with random retry backoff
- **D.** GUID polling with manual duplicate cleanup

> **Answer:** A. Delta sync with keyed upsert

A reliable Dataverse sync pattern should combine delta detection with idempotent matching and controlled retry behavior. Microsoft’s guidance supports using change tracking for incremental synchronization, alternate keys for record identity when GUIDs are not the integration key, and upsert for create-or-update behavior without a separate existence check.

For resilience, Dataverse also documents service protection API limits and explains that 429 responses include retry timing information such as Retry-After. That makes a delta-based keyed upsert pattern the strongest answer here because it minimizes unnecessary reads, avoids duplicate creation on retry, and aligns naturally with controlled backoff when throttling occurs.

<sub>Set F · Q16</sub>

---

### 37. A product team must stream very high volumes of Dataverse event data into multiple downstream analytics consumers. The design prioritizes scalable event ingestion and downstream streaming fan-out over direct request/response handling.

Which listener option is the best fit?

- **A.** Webhook endpoint
- **B.** Service Bus queue listener
- **C.** Cloud flow trigger
- **D.** Event Hub consumer ✅

> **Answer:** D. Event Hub consumer

Event Hub consumer is the best answer because Microsoft documents Azure Event Hubs as a highly scalable publish-subscribe service that can ingest millions of events per second and stream them into multiple applications. That matches the scenario’s emphasis on high-volume ingestion and downstream streaming fan-out.

Webhook and queue-based patterns solve different problems. Microsoft documents webhooks as a direct mechanism for sending Dataverse server events to an external web application, while Service Bus is the stronger fit for decoupled messaging and queueing semantics. The scenario is specifically steering toward streaming-scale analytics distribution, which is where Event Hubs is the strongest option.

<sub>Set F · Q32</sub>

---

### 38. A custom Azure-aware plug-in must publish the current execution context to an integration endpoint.

Snippet

var notificationService =
    (IServiceEndpointNotificationService)serviceProvider.GetService(
        typeof(IServiceEndpointNotificationService));

notificationService.Execute(
    new EntityReference("serviceendpoint", endpointId),
    context);
What platform target is this code publishing to? Select only one answer.

- **A.** Business event catalog
- **B.** Power Automate Dataverse trigger
- **C.** Azure Service Bus ✅
- **D.** Form script handler

> **Answer:** C. Azure Service Bus

Azure Service Bus is the correct answer because Microsoft documents that an Azure-aware plug-in can use IServiceEndpointNotificationService to initiate posting of the current request data context to the service bus. That is the core publish pattern for Dataverse-to-Azure messaging through registered service endpoints.

This is distinct from cataloging a business event or starting a client-side action. The code is server-side integration logic that posts execution context outward through the Dataverse-Azure integration path, not a maker experience feature or a browser event pattern.

<sub>Set F · Q56</sub>

---

### 39. A team is reviewing endpoint-registration notes before using the Plug-in Registration Tool.

Exhibit 1

Which row is correct?

- **A.** Row 1 ✅
- **B.** Row 2
- **C.** Row 3
- **D.** Row 4

> **Answer:** A. Row 1

Row 1 is correct because Microsoft documents webhooks as a way to send Dataverse server events to an external web application. That is the defining registration model for a Dataverse webhook endpoint.

The other rows reverse or misstate endpoint-registration rules. Microsoft documents Event Hub endpoint registration as SAS-based in this integration path, and Azure Service Bus listener behavior differs between relay and queue contracts, where relay listeners must actively listen while queue contracts do not require an active listener.

<sub>Set F · Q57</sub>

---

### 40. A product integration copies Dataverse account rows into an external system every 10 minutes. The integration must process only rows that changed since the last successful run and must avoid expensive full-table comparisons as data volume grows.

Which approach should you use? Select only one answer.

- **A.** Scheduled full-table compare
- **B.** Audit-history polling
- **C.** Change tracking ✅
- **D.** Duplicate detection rules

> **Answer:** C. Change tracking

Change tracking is the best fit because Dataverse provides it specifically to synchronize data efficiently by detecting what changed since the data was first extracted or last synchronized. That matches the requirement to process only deltas instead of repeatedly scanning the entire table.

This is also the strongest integration design choice for scale. Microsoft’s guidance for change tracking and data-integration best practices both point toward delta-based synchronization patterns rather than expensive full refresh logic when the goal is reliable, efficient external sync.

<sub>Set F · Q58</sub>

---

### 41. An ERP system sends customer records to Dataverse and identifies each customer by an immutable external customer number. The integration does not know the Dataverse GUIDs and must match existing rows reliably during repeated loads.

Which design should you choose? Select only one answer.

- **A.** Business-required text column
- **B.** Alternate key ✅
- **C.** Calculated match colum
- **D.** Auto-number primary column

> **Answer:** B. Alternate key

An alternate key is the correct design because Dataverse uses alternate keys in data integration scenarios where you do not know the Dataverse primary key value. Microsoft also notes that alternate keys let you uniquely identify rows by business columns instead of relying only on the GUID primary key.

This is exactly what the scenario needs: a stable external identifier that can be used repeatedly for matching during integration runs. A normal text column might store the value, but it does not become a key-based record identity for integration operations unless it is defined as an alternate key.

<sub>Set F · Q59</sub>

---

### 42. An import process receives supplier rows from an external system and identifies each row by an alternate key. The process must create the Dataverse row if it does not exist and update it if it already exists, without first retrieving the row to decide between create and update.

Snippet

Entity supplier = new Entity("account");
supplier.KeyAttributes["accountnumber"] = "SUP-1042";
supplier["name"] = "Contoso Supplier";
supplier["telephone1"] = "555-0104";

// Which request should be executed here?
Which request should you use?

- **A.** UpdateRequest after pre-retrieve
- **B.** CreateRequest with source GUID
- **C.** ExecuteMultipleRequest batch
- **D.** UpsertRequest ✅

> **Answer:** D. UpsertRequest

UpsertRequest is the best choice because Microsoft documents Upsert as the way to reduce complexity in integration scenarios when you do not know whether the record already exists. The request lets Dataverse use the target record identity, typically from alternate keys, and then create or update as needed.

This also fits the snippet precisely because the entity is identified with KeyAttributes, which Microsoft describes as the usual pattern for record identification in standard-table upsert scenarios. The whole point is to avoid a separate existence check before deciding whether to call create or update.

<sub>Set F · Q60</sub>

---
