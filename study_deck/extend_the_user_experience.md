# Extend the User Experience  

_Exam weight 10–15% · 60 questions across all sets._

---

### 1. A form script calls executionContext.getFormContext() and works in one developer’s test harness, but fails on the actual form with executionContext undefined. The function was added through form event handler properties in the maker experience.

What is the best fix?

- **A.** Pass execution context ✅
- **B.** Use global Xrm.Utility object
- **C.** Move logic to a business rule
- **D.** Convert the form to custom page

> **Answer:** A. Pass execution context

The best fix is to enable passing execution context to the function when the handler is configured. Microsoft explicitly documents that, when defining handlers through the UI, the “Pass execution context as first parameter” option must be selected if the function expects to use executionContext and getFormContext().

This is a direct Client API object model troubleshooting pattern. The code itself may be fine, but if the handler configuration does not pass the execution context, the function never receives the object needed to retrieve formContext. The issue is therefore handler wiring, not the underlying JavaScript API choice.

<sub>Set A · Q6</sub>

---

### 2. A maker changes a value inside a field PCF component. The component must return the updated bound value back to the framework after notifyOutputChanged is raised.

Snippet

private currentValue: string = "";

private onInputChange(value: string): void {
    this.currentValue = value;
    this.notifyOutputChanged();
}

public ______(): IOutputs {
    return {
        sampleProperty: this.currentValue
    };
}
Which lifecycle event completes the snippet correctly?

- **A.** init
- **B.** updateView
- **C.** destroy
- **D.** getOutputs ✅

> **Answer:** D. getOutputs

getOutputs is the correct method because Microsoft documents it as the lifecycle method the framework calls to retrieve values for bound properties. The PCF overview also explains that when a user changes data and the component calls notifyOutputChanged, the platform responds by calling getOutputs, and those outputs are then used to update the framework with the new value.

This snippet is demonstrating the output side of the lifecycle rather than initialization or rerendering. init sets the component up, updateView responds to changed inputs or framework state, and destroy handles teardown. Only getOutputs matches the requirement to return the changed bound value after the component has notified the framework that new outputs are ready.

<sub>Set A · Q8</sub>

---

### 3. A command bar action updates the telephone1 column programmatically. Existing OnChange handlers for telephone1 must still execute after the value is normalized.

Snippet

function normalizePhone(executionContext) {
    var formContext = executionContext.getFormContext();
    var telephone = formContext.getAttribute("telephone1");
    var value = telephone.getValue();

    if (value) {
        telephone.setValue(value.replace(/\s+/g, ""));
    }
}
What should you add inside the if block after setValue?

- **A.** Save the form immediately
- **B.** Re-register the handler
- **C.** telephone.fireOnChange() ✅
- **D.** Read save event arguments

> **Answer:** C. telephone.fireOnChange()

The code already uses setValue, so the missing step is to explicitly raise the OnChange event for the attribute. Microsoft documents that programmatic updates through setValue do not automatically cause OnChange handlers to run, and fireOnChange is the supported way to trigger those handlers.

This is exactly the kind of Client API object model behavior that matters in model-driven app scripting: updating data and invoking event logic are separate actions. Because the requirement is about preserving existing column event behavior after a command changes the value, telephone.fireOnChange() is the correct and most targeted fix.

<sub>Set A · Q23</sub>

---

### 4. A command bar function sets a column value by using JavaScript. Another team already registered OnChange logic for that same column, and that logic must still run after the value is updated.

Which method should the script call after setValue?

- **A.** Re-register OnChange handler
- **B.** fireOnChange ✅
- **C.** Save the form immediately
- **D.** Refresh the command bar

> **Answer:** B. fireOnChange

setValue updates the client-side value, but Microsoft documents that it does not trigger the column OnChange event by itself. If existing OnChange handlers must execute after the script changes the value, the correct follow-up call is fireOnChange.

This is a classic Client API object model distinction: writing a value and raising the related event are separate actions. fireOnChange targets the attribute event pipeline directly, which is why it is the cleanest and most predictable way to keep downstream client scripting behavior aligned with a programmatic column update.

<sub>Set A · Q25</sub>

---

### 5. A reusable JavaScript library must attach the same handler to several columns on form load. Inside that shared handler, the code must determine which column raised the event so it can branch without hard-coded column names.

Which two Client API choices should you use? (Select TWO.)

- **A.** formContext.ui.setFormNotification
- **B.** attribute.addOnChange ✅
- **C.** control.setDisabled
- **D.** Xrm.Page global accessor
- **E.** executionContext.getEventSource ✅

> **Answer:** B. attribute.addOnChange · E. executionContext.getEventSource

attribute.addOnChange is the correct registration mechanism because it adds a function to a column’s OnChange event. Microsoft documents that this is the attribute-level Client API method for wiring a handler to a column, including when you do it from script on load.

executionContext.getEventSource is the correct companion choice because it returns the Xrm object model item that actually triggered the event. In an OnChange scenario, Microsoft documents that this returns the changed column object, which lets a shared handler inspect the source without hard-coding separate entry points per column.

<sub>Set A · Q26</sub>

---

### 6. A development team reviews four planned PCF lifecycle usages. One mapping does not align to the documented purpose of the lifecycle event.

Exhibit 1

Which work item should be revised?

- **A.** Load remote metadata once at startup
- **B.** Re-render when width, visibility, or field value changes
- **C.** Return a changed bound property after notifyOutputChanged
- **D.** Remove global listeners and close WebSockets on unload ✅

> **Answer:** D. Remove global listeners and close WebSockets on unload

The fourth work item should be revised because Microsoft documents cleanup of WebSockets and external event handlers under destroy, not updateView. destroy is called when the component is removed from the DOM tree and is the lifecycle boundary intended for releasing resources and preventing performance problems caused by repeated loading and unloading.

The other three rows match the documented lifecycle purposes. init is for initialization and can start remote calls, updateView is triggered when property-bag values change, and getOutputs returns values for bound outputs after the framework asks for them. The exhibit is testing whether the developer can map each lifecycle event to the correct implementation responsibility.

<sub>Set A · Q35</sub>

---

### 7. A field PCF component is loaded, rendered, edited by a user, and then removed from the page. Assume the component uses the standard lifecycle flow and raises notifyOutputChanged after the user changes the bound value.

Steps

The framework retrieves the changed bound value from the component.

The component instance is initialized.

The component is removed and releases its external resources.

The component reacts to current property-bag values and renders the UI.

What is the correct order?

- **A.** 2 → 4 → 1 → 3 ✅
- **B.** 4 → 2 → 1 → 3
- **C.** 2 → 1 → 4 → 3
- **D.** 4 → 1 → 2 → 3

> **Answer:** A. 2 → 4 → 1 → 3

The correct order is 2 → 4 → 1 → 3. Microsoft documents init as the initialization event, so the component instance is initialized first. updateView is then used when property-bag values are available or change, which makes it the rendering step. After the user changes data and the component raises notifyOutputChanged, the framework calls getOutputs to retrieve the changed bound value. Finally, destroy runs when the component is removed from the DOM and must clean up resources.

This sequence demonstrates the different lifecycle responsibilities rather than just method names. Startup belongs to init, UI refresh belongs to updateView, output return belongs to getOutputs, and teardown belongs to destroy. Understanding that order is important when deciding where to place rendering, startup, data-return, and cleanup logic in a PCF component.

• 2 is first because init is the initialization event for the component instance and is documented as the startup point for initialization actions.

• 4 is second because updateView is the lifecycle event that reacts to property-bag values and is used to render or rerender the UI when those values change.

• 1 is third because after the user changes data and the component signals notifyOutputChanged, the framework retrieves the changed bound value by calling getOutputs.

• 3 is last because destroy is invoked when the component is removed from the DOM and is used to release resources such as listeners and WebSockets.

<sub>Set A · Q36</sub>

---

### 8. A PCF control renders a custom chart and registers a window resize listener and a WebSocket subscription to receive live updates. The component is frequently loaded and unloaded as users move between screens, and the design must avoid memory leaks and duplicate event handling.

Which lifecycle event is the best fit for the cleanup logic?

- **A.** init
- **B.** updateView
- **C.** destroy ✅
- **D.** getOutputs

> **Answer:** C. destroy

destroy is the best fit because Microsoft documents it as the lifecycle event invoked when a component is removed from the DOM tree, and specifically recommends using it for cleanup and memory release. The PCF best-practices guidance explicitly says to close WebSockets and remove event handlers added outside the container element in destroy, which matches the scenario exactly.

This is an important lifecycle design distinction in PCF. init is for starting up the component, updateView is for reacting to property-bag changes, and getOutputs is for returning bound outputs back to the framework. None of those other lifecycle events is the primary cleanup boundary when the component is unloaded.

<sub>Set A · Q52</sub>

---

### 9. A PCF code component must request metadata from a remote service as soon as the component instance starts. The design should avoid waiting until the first visual refresh cycle to begin that network call.

Which lifecycle event should you use?

- **A.** init ✅
- **B.** updateView
- **C.** getOutputs
- **D.** destroy

> **Answer:** A. init

init is the correct lifecycle event for this design because Microsoft documents it as the place used to initialize the component instance and begin remote server calls or other startup actions. Microsoft’s PCF best-practices guidance also says init is first called when the hosting context loads the component and recommends using it to request network resources such as metadata.

updateView is for reacting when values in the property bag change, including field values, dataset values, container dimensions, offline state, and metadata such as visibility or label. That means it is important for rendering and rerendering, but it is not the best primary lifecycle event for starting the initial metadata request described in the scenario.

<sub>Set A · Q55</sub>

---

### 10. A team wants one JavaScript handler to work from both a main form event and an editable grid event. The function must read the current record value and manipulate the current surface without hard-coding assumptions about where it was invoked.

Which object should the function target?

- **A.** Global context
- **B.** Xrm.Utility
- **C.** Deprecated Xrm.Page accessor
- **D.** formContext ✅

> **Answer:** D. formContext

formContext is the correct target because Microsoft positions it as the reference to the current form or form item against which the code is running. The getFormContext method returns that reference from the execution context, which is what enables the same handler to work across supported surfaces such as forms and editable grids.

This is also why Microsoft recommends using formContext instead of relying on the older Xrm.Page pattern for newer code. Xrm.Page remains supported for backward compatibility, but Microsoft explicitly recommends the newer context-aware approach for code targeting version 9.0 or later.

<sub>Set A · Q57</sub>

---

### 11. A shared JavaScript library contains one function that should always run when the main form opens and another function that must filter a lookup right before results are displayed. The team wants to use the most appropriate registration model for each handler instead of forcing both through the same mechanism.

Which two registration approaches should the developer use? (Select TWO.)

- **A.** Register PreSearch in designer
- **B.** Register OnLoad in Events tab ✅
- **C.** Use business rules for JavaScript
- **D.** Pass execution context only for grids
- **E.** Attach PreSearch in code ✅

> **Answer:** B. Register OnLoad in Events tab · E. Attach PreSearch in code

Register OnLoad in Events tab is correct because Microsoft documents standard form events such as On Load and On Save as events that can be associated through the form designer. That makes the Events tab the right registration surface for a normal form-open handler that should be visible in the form configuration.

Attach PreSearch in code is also correct because Microsoft distinguishes events available in the UI from events that are attached using Client API methods. Lookup PreSearch is part of that code-based pattern, and Microsoft’s documented example uses addPreSearch from an OnLoad handler to wire the callback at runtime.

<sub>Set B · Q7</sub>

---

### 12. A team has a stable validation routine that must run every time a main form is saved. Makers want the registration to remain visible in form customization instead of being attached dynamically at runtime.

Which registration approach should you choose?

- **A.** Form Events tab ✅
- **B.** addOnSave at runtime
- **C.** addPreSearch in OnLoad
- **D.** Business rule and column action

> **Answer:** A. Form Events tab

Form Events tab is the best answer because this requirement describes a standard, design-time registration for a main-form event that should stay visible and manageable in form customization. Microsoft documents that form event handlers are configured by associating a JavaScript web resource and function to form events such as On Load and On Save through the form designer.

Code-based registration methods are useful when the handler must be attached dynamically or when the event is not surfaced through the designer, but that is not the case here. For a stable OnSave routine that should be maintained in the form’s event configuration, the form Events tab is the cleanest registration approach.

<sub>Set B · Q16</sub>

---

### 13. A model-driven app contains a customer lookup that must be filtered using the latest values on the form at the moment the user opens the search results. The team wants the filter to apply just before lookup results are shown instead of relying on a static configuration captured earlier in the form session.

Which registration approach should you use?

- **A.** Column OnChange in designer
- **B.** Form OnSave in designer
- **C.** Form OnLoad plus addPreSearch ✅
- **D.** Form OnLoad with static parameters

> **Answer:** C. Form OnLoad plus addPreSearch

Form OnLoad plus addPreSearch is the best answer because Microsoft documents addPreSearch as the event hook used to change lookup behavior just before results are displayed. The documented pattern is to register the callback from a form OnLoad handler and then apply the lookup filter inside the PreSearch callback so the lookup uses current form state at search time.

This is exactly the kind of scenario where runtime registration is appropriate. The form designer can register standard form and column handlers, but lookup filtering through addCustomFilter is documented to work from a PreSearch event handler, and Microsoft’s example shows that registration being added from form OnLoad.

<sub>Set B · Q27</sub>

---

### 14. A developer registered the following function for a column event. Users now see an error because the handler assumes a context object that is not being supplied.

Snippet

function validateAmount(executionContext) {
    var formContext = executionContext.getFormContext();
    var value = formContext.getAttribute("new_amount").getValue();

    if (value !== null && value < 0) {
        formContext.getControl("new_amount").setNotification("Amount cannot be negative.");
    }
}
Which registration change should fix the issue?

- **A.** Add dependent columns to form
- **B.** Move handler to OnSave
- **C.** Replace with Business Rule
- **D.** Pass execution context ✅

> **Answer:** D. Pass execution context

Pass execution context is the correct answer because the function signature expects an executionContext parameter and immediately calls getFormContext on it. Microsoft documents that when event handlers are defined through the UI, the developer must select the option to pass execution context as the first parameter when the handler needs access to formContext through executionContext.

This is a classic registration mismatch rather than a logic bug in the function body. The code pattern itself is aligned with Microsoft’s current guidance to use formContext obtained from the passed execution context instead of relying on the older static Xrm.Page pattern.

<sub>Set B · Q28</sub>

---

### 15. A form OnLoad handler calls addOnChange for the same column every time the form data reloads. After a save and refresh cycle, users notice that the same notification logic fires multiple times for a single edit.

What is the best registration fix?

- **A.** Add another OnLoad handler
- **B.** Conditionally call addOnChange ✅
- **C.** Switch to static parameters
- **D.** Replace it with HTML web resource

> **Answer:** B. Conditionally call addOnChange

Conditionally call addOnChange is the best answer because Microsoft specifically warns that when addOnChange is used from a form OnLoad handler, you should ensure it is called only when necessary. The documentation recommends using getEventArgs to conditionally call addOnChange based on data load state, which directly addresses duplicate registrations caused by repeated loads.

This is a registration-timing problem, not a signal that the handler must move to a different technology. The supported fix is to control when the attachment occurs so the same callback is not repeatedly added to the event pipeline during repeated load cycles.

<sub>Set B · Q30</sub>

---

### 16. A canvas app code component calls a third-party REST endpoint directly from the browser. The team must declare that behavior in the manifest so the component is classified correctly at runtime.

Which manifest element should you add?

- **A.** feature-usage wrapper
- **B.** type-group definition
- **C.** external-service-usage element ✅
- **D.** property-dependencies block

> **Answer:** C. external-service-usage element

external-service-usage is the correct manifest element for a code component that connects directly to an external service. In the PCF manifest schema, that element is used to declare whether the control uses an external service, and when it does, the external domains are listed under it.

That matters here because a control that uses an external service is treated as a premium control. This is a manifest-configuration decision, not an implementation detail in the TypeScript alone, so the declaration belongs in the manifest rather than in feature-usage, type-group, or property dependency metadata.

<sub>Set B · Q31</sub>

---

### 17. You are building a model-driven field component that should let makers provide a configurable placeholder value in the designer. The component must read that value at runtime, but it must not write the value back to the Dataverse column.

Which property usage should you configure in the manifest?

- **A.** bound property usage
- **B.** output property usage
- **C.** data-set property usage
- **D.** input property usage ✅

> **Answer:** D. input property usage

input is the correct usage because the component needs a configurable value that it can read, but not change as a bound Dataverse column value. In the manifest schema, the usage attribute identifies whether a property is bound, input, or output, and input is the read-only configuration pattern for this scenario.

This is different from bound, which represents a column value the component can change, and different again from output, which is used for values emitted by the component. Since the requirement is maker-supplied configuration with no writeback to the target column, input is the clean manifest choice.

<sub>Set B · Q32</sub>

---

### 18. A PCF component already has its main TypeScript resource registered. The team now wants the component to load localized maker-facing strings in the designer and apply custom styling in the rendered control.

Which two resource entries should be added to the manifest? (Select TWO.)

- **A.** property-dependencies
- **B.** css ✅
- **C.** type-group
- **D.** feature-usage
- **E.** resx ✅

> **Answer:** B. css · E. resx

css and resx are the two resource entries that fit this requirement. The resources element can include CSS for the component’s UI styling and RESX files for localized strings. That combination supports both custom presentation and localization without changing the control’s property structure.

This is a manifest-configuration task because these files must be declared under resources for the framework to recognize and load them correctly. property-dependencies, type-group, and feature-usage all serve different purposes and do not register stylesheet files or localized string resources.

<sub>Set B · Q33</sub>

---

### 19. A developer is converting a field control into a dataset-aware component and updates the manifest as shown below.

Snippet

<control namespace="Contoso.Controls"
         constructor="LookupGrid"
         version="1.0.0"
         display-name-key="LookupGrid"
         description-key="LookupGrid description">
  <data-set name="Items"
            display-name-key="Items"
            cds-data-set-options="displayCommandBar:true;displayViewSelector:true;displayQuickFind:true" />
  <property name="primaryLookup"
            display-name-key="PrimaryLookup"
            of-type="Lookup.Simple"
            usage="input" />
  <resources>
    <code path="index.ts" order="1" />
  </resources>
</control>
What is the best fix for this manifest?

- **A.** Nest Lookup.Simple in data-set ✅
- **B.** Add a second code resource
- **C.** Change the property to output
- **D.** Declare WebAPI in feature-usage

> **Answer:** A. Nest Lookup.Simple in data-set

The best fix is to move the Lookup.Simple property into the data-set element. Microsoft’s manifest reference states that if the manifest contains at least one dataset, then properties of type Lookup.Simple should also be wrapped into the data-set element. That is the specific manifest rule being violated by this snippet.

This is a subtle configuration issue because the manifest is otherwise close to valid. The problem is not the existence of the dataset itself, but the placement of the Lookup.Simple property outside the dataset context after a dataset has been introduced into the component definition.

<sub>Set B · Q34</sub>

---

### 20. A developer adds the following block to a canvas app code component manifest so the control can request WebAPI and Utility features:

<feature-usage><uses-feature name="WebAPI" required="true" /></feature-usage>

The component package builds, but the manifest choice is rejected during review because the team says the element is not supported for the intended host.

What is the most likely cause?

- **A.** Missing resx resource
- **B.** Unsupported canvas element ✅
- **C.** Incorrect constructor name
- **D.** Duplicate type-group declaration

> **Answer:** B. Unsupported canvas element

The most likely cause is that feature-usage is not the correct manifest element for this canvas-app host. The manifest reference marks feature-usage as available for model-driven apps, not canvas apps. That makes the reviewer’s objection consistent with the documented host support for the element.

This is an operational troubleshooting issue because the XML can look reasonable and still be wrong for the target host. In PCF manifest work, availability matters at the individual element level, so a valid-looking block can still be rejected when it is configured for an unsupported app type.

<sub>Set B · Q36</sub>

---

### 21. A developer starts converting a DOM-based control into a React PCF control but keeps the original lifecycle shape.

Snippet

export class StatusBadge
implements ComponentFramework.ReactControl<IInputs, IOutputs> {

  public init(
    context: ComponentFramework.Context<IInputs>,
    notifyOutputChanged: () => void,
    state: ComponentFramework.Dictionary,
    container: HTMLDivElement
  ): void {}

  public updateView(
    context: ComponentFramework.Context<IInputs>
  ): void {}
}
Which change aligns the code with the React control interfaces?

- **A.** Add container cleanup call
- **B.** Drop container; return ReactElement ✅
- **C.** Replace IOutputs with component context
- **D.** Mark value as input

> **Answer:** B. Drop container; return ReactElement

ReactControl has a different interface shape from StandardControl. Microsoft documents that ReactControl.init does not have a container parameter because React controls do not render the DOM directly, and that ReactControl.updateView returns a ReactElement. That means the correct fix is to remove the container parameter and change updateView so it returns a React element.

The issue is structural, not cosmetic. The snippet declares ReactControl<IInputs, IOutputs> but still uses a StandardControl-style init signature and a void-returning updateView. A valid React PCF control must follow the React lifecycle contract rather than mixing the two models.

<sub>Set C · Q16</sub>

---

### 22. A command bar script in a model-driven app must invoke an unbound Dataverse custom API and inspect the response payload before deciding whether to refresh the form. The app runs online, and the team wants to use the supported client-side method instead of manually composing raw REST calls.

Which approach should you use?

- **A.** createRecord helper method
- **B.** retrieveRecord helper method
- **C.** form save callback
- **D.** Xrm.WebApi.online.execute ✅

> **Answer:** D. Xrm.WebApi.online.execute

Xrm.WebApi.online.execute is the correct choice because Microsoft documents it as the client API method to execute a single action, function, or CRUD operation, and it is the method used for custom API and action/function execution from model-driven app JavaScript. It is specifically supported for online mode.

The requirement is not to create or retrieve a standard row directly. It is to invoke an unbound Dataverse custom API and inspect the returned response, which fits the execute pattern rather than the simpler CRUD helper methods.

<sub>Set C · Q19</sub>

---

### 23. A model-driven app script must run in mobile offline mode. The sample_tags column is a MultiSelectPicklist.

Snippet

function loadTaggedAccounts(executionContext) {
    var formContext = executionContext.getFormContext();

    Xrm.WebApi.retrieveMultipleRecords(
        "account",
        "?$select=name&$filter=contains(sample_tags,'VIP')"
    ).then(function (result) {
        if (result.entities.length > 0) {
            formContext.ui.setFormNotification(
                "VIP account found",
                "INFO",
                "viptag"
            );
        }
    });
}
What is the best fix?

- **A.** Use FetchXML ✅
- **B.** Add a return representation header
- **C.** Replace the call with updateRecord
- **D.** Wrap the request in executeMultiple

> **Answer:** A. Use FetchXML

The best fix is to use FetchXML. Microsoft documents that in mobile offline mode, certain attribute types are not supported with OData query string options in Xrm.WebApi.retrieveMultipleRecords, and MultiSelectPicklist is explicitly listed among the unsupported types. Microsoft also states that you should use FetchXML if you need to work with those unsupported types.

The issue is not the promise pattern or notification logic. The issue is the query design itself: an OData filter is being used against a column type that is not supported for that query style in mobile offline.

<sub>Set C · Q20</sub>

---

### 24. A form OnLoad handler retrieves parent account data by using Xrm.WebApi.retrieveRecord and then updates the UI based on the result. The team wants the script to remain supportable across form contexts and avoid returning unnecessary columns.

Which two design choices should you include? (Select TWO.)

- **A.** Use Xrm.Page everywhere
- **B.** Return every column by default
- **C.** Pass execution context to handler ✅
- **D.** Reuse one stored formContext across later events
- **E.** Add $select for needed columns ✅

> **Answer:** C. Pass execution context to handler · E. Add $select for needed columns

You should pass the execution context so the handler can call getFormContext() and work with the correct form context in a supported way. Microsoft documents Xrm.Page as deprecated and explicitly states that you should select the option to pass execution context as the first parameter when defining event handlers that use formContext.

You should also include $select so the Web API returns only the columns the script needs. Microsoft documents limiting returned properties with $select as an important performance best practice for both retrieveRecord and retrieveMultipleRecords; otherwise, all properties are returned.

<sub>Set C · Q21</sub>

---

### 25. A command bar script calls Xrm.WebApi.online.execute to invoke a Dataverse operation and then refreshes the form. It works for browser users, but field technicians report that the same command fails when they work in mobile offline mode.

What is the best explanation?

- **A.** Connection references are required
- **B.** online.execute works online only ✅
- **C.** getFormContext is mobile unsupported
- **D.** Form notifications block Web API

> **Answer:** B. online.execute works online only

The best explanation is that Xrm.WebApi.online.execute is documented as supported only for online mode. If the script depends on that method, the design inherently assumes server connectivity and will not behave the same way for users working in mobile offline mode.

This makes the issue architectural rather than a simple syntax defect. The command can still be perfectly valid for connected browser usage, but the chosen client-side Web API method does not satisfy the offline execution requirement.

<sub>Set C · Q22</sub>

---

### 26. A team is building a PCF field component in TypeScript that creates DOM elements directly and appends them to the supplied container during initialization. The component will not return a React tree.

Which interface should the class implement?

- **A.** React control interface
- **B.** Context parameter interface
- **C.** Standard control interface ✅
- **D.** Virtual dataset contract type

> **Answer:** C. Standard control interface

StandardControl is the correct interface for this design. Microsoft’s PCF API reference shows that StandardControl.init includes the container: HTMLDivElement parameter, which is the host surface used when the control renders DOM directly. That matches a DOM-based field component that appends elements during initialization.

ReactControl is a different contract. Microsoft documents that ReactControl.init does not have a container parameter because React controls do not render the DOM directly; instead, ReactControl.updateView returns a ReactElement. That is why a direct-DOM component should implement StandardControl rather than ReactControl.

<sub>Set C · Q28</sub>

---

### 27. A maker adds a PCF field component to a model-driven form and binds it to a Dataverse decimal column. Users can change the value inside the component, and the new value must flow back through the framework by using the supported field-component contract rather than writing directly to Dataverse from the control.

Which implementation approach should you use?

- **A.** Session state persistence pattern
- **B.** Return changed value from updateView
- **C.** Input manifest property
- **D.** Notify and bound output ✅

> **Answer:** D. Notify and bound output

The supported PCF pattern is to call notifyOutputChanged when the user changes the value and then return the changed value through getOutputs. Microsoft’s code component documentation explicitly states that when a user changes data, the component must call notifyOutputChanged, after which the platform calls getOutputs, and getOutputs returns the changed values.

This also depends on the manifest contract. Microsoft documents that the property usage value determines whether the property is bound, input, or output, and identifies bound as the option representing a column the component can change. That is why the correct implementation is a notify-plus-bound-output pattern rather than a direct write or an input-only definition.

<sub>Set C · Q31</sub>

---

### 28. A reviewer is checking whether proposed PCF interface designs are valid before development starts.

Exhibit 1

Which row represents a valid interface design?

- **A.** Row 2 ✅
- **B.** Row 1
- **C.** Row 3
- **D.** Row 4

> **Answer:** A. Row 2

Row 2 is the valid design. Microsoft states that ReactControl does not receive an HTMLDivElement container in init and that ReactControl.updateView returns a ReactElement. Row 2 is the only row that matches both parts of that documented interface contract.

The other rows each break a documented rule. Microsoft says dataset values cannot be initialized in init and should instead be handled in updateView. Microsoft also says trackContainerResize(true) should be called so the framework provides allocatedWidth and allocatedHeight in updateView. Those points eliminate Rows 3 and 4, while Row 1 is invalid because it incorrectly adds a container parameter to ReactControl.

<sub>Set C · Q32</sub>

---

### 29. A PCF field component registers browser event handlers during initialization and works correctly on first load. After users navigate away and back several times in the same session, the form becomes slower and old handlers still fire.

Which interface method should the developer implement more carefully to fix the issue?

- **A.** getOutputs method
- **B.** updateView method
- **C.** setControlState method
- **D.** destroy method ✅

> **Answer:** D. destroy method

The correct answer is destroy. Microsoft’s StandardControl reference says destroy is invoked when the component is removed from the DOM tree and should be used for cleanup and releasing memory. That is the lifecycle method intended for unregistering browser handlers and disposing of resources that should not survive the control instance.

Microsoft’s code component overview also explains that when a user steps away from the page, some methods such as event handlers can remain and continue consuming memory, and specifically says developers should implement destroy to remove cleanup code such as event handlers. That is exactly the problem described in the incident.

<sub>Set C · Q34</sub>

---

### 30. A model-driven app form script must read and update Dataverse rows without building raw authenticated HTTP requests. The script must use the supported client-side API designed for Dataverse data operations.

Which object should the script target?

- **A.** form data entity methods
- **B.** Xrm.Navigation dialog APIs
- **C.** Xrm.WebApi object ✅
- **D.** global context utilities

> **Answer:** C. Xrm.WebApi object

Xrm.WebApi is the client-side object designed for model-driven apps to interact with Dataverse through the Web API. Microsoft documents it as the object that exposes methods to create, retrieve, update, delete, and execute operations from client-side JavaScript in model-driven apps.

The other options are part of the client API surface, but they do different jobs. formContext.data.entity is about the record on the form, Xrm.Navigation is for navigation and dialogs, and global context utilities do not replace the Web API operation layer for Dataverse CRUD and action/function calls.

<sub>Set C · Q42</sub>

---

### 31. A developer wants to package a finished PCF control by using the supported solution-based process. They need an output that can be imported into Dataverse rather than a control that remains local to the source folder.

Snippet

pac solution init --publisher-name Contoso --publisher-prefix cts
pac solution add-reference --path ..\ColorPickerControl
msbuild /t:restore
msbuild
What is this sequence intended to produce?

- **A.** Build a solution zip ✅
- **B.** Push directly to Dataverse
- **C.** Register a plug-in assembly
- **D.** Convert to a reusable web resource package

> **Answer:** A. Build a solution zip

This sequence creates a solution project, adds the PCF project as a reference, restores dependencies, and builds the solution project. Microsoft documents this flow as the packaging path used to bundle the code component into a solution file that can then be imported into Dataverse.

The key step is pac solution add-reference, because that tells the solution project which PCF control to include during build. Without that reference, the build would not package the code component into the deployable solution artifact the downstream environment expects.

<sub>Set D · Q3</sub>

---

### 32. You are configuring a modern command in a model-driven app. The button must be visible only when the current user has permission to edit the selected record.

Which Power Fx approach should you use?

- **A.** SelectedControlSelectedItemIds
- **B.** DataSourceInfo(Accounts, DataSourceInfo.CreatePermission)
- **C.** JavaScript custom rule
- **D.** RecordInfo(Self.Selected.Item, RecordInfo.EditPermission) ✅

> **Answer:** D. RecordInfo(Self.Selected.Item, RecordInfo.EditPermission)

RecordInfo(Self.Selected.Item, RecordInfo.EditPermission) is the best fit because the requirement is record-specific, not table-wide. Microsoft’s commanding guidance maps record-permission visibility to RecordInfo(), while table-permission visibility maps to DataSourceInfo().

This is exactly the kind of condition Power Fx visibility formulas are meant to handle in modern commanding. Microsoft recommends Power Fx for modern visibility logic, and the command designer supports Power Fx for visibility in model-driven app commands.

<sub>Set D · Q8</sub>

---

### 33. A team wants a command button on a model-driven app form that opens a custom page as a dialog and can later trigger a cloud flow from that dialog. A maker tries to build the command action directly with Power Fx in that customization path.

Which approach should the team use?

- **A.** Run formula with Navigate()
- **B.** Classic visibility rule
- **C.** JavaScript command with web resource ✅
- **D.** Table-scoped Power Fx override

> **Answer:** C. JavaScript command with web resource

For the custom-page dialog commanding pattern documented by Microsoft, the supported action is JavaScript. The custom-page command article explicitly states that this customization currently supports only JavaScript and that Power Fx is not supported for that scenario.

That makes a JavaScript command with a web resource the best supported implementation choice. The command designer also supports JavaScript actions in modern commands by attaching a JavaScript library and function name, which fits the requirement cleanly.

<sub>Set D · Q26</sub>

---

### 34. A maker configures the Visible property of a main grid command with the following formula.

Snippet

CountRows(Self.Selected.AllItems) > 0
What does this formula do?

- **A.** Rows selected in grid ✅
- **B.** Unsaved form changes only
- **C.** New form record state
- **D.** Library publish completion

> **Answer:** A. Rows selected in grid

This formula makes the command visible when one or more rows are selected in the grid. Microsoft’s commanding examples show CountRows(Self.Selected.AllItems) > 0 specifically as the visible-property pattern for showing a command when at least one record is selected in a grid view.

The key detail is Self.Selected.AllItems, which represents the selected records from the command host context. The formula is about current selection state, not save state, record mode, or publishing status.

<sub>Set D · Q27</sub>

---

### 35. A maker opens command editing from the Solutions area and can attach JavaScript, but the options to set Run formula and Show on condition from formula are unavailable. The team needs to configure a Power Fx action and Power Fx visibility for the command.

What should the maker do next?

- **A.** Convert the command to global scope
- **B.** Edit from modern app designer ✅
- **C.** Add a second component library
- **D.** Replace it with classic ribbon XML

> **Answer:** B. Edit from modern app designer

The maker should edit the command from within the modern app designer. Microsoft documents that editing commands from the Solutions or Tables areas does not have the capability to set Run formula or Show on condition from formula; those capabilities are available only when editing commands from within the modern app designer.

This is a tooling-entry-point issue, not a command-definition corruption issue. The feature is available, but only through the correct designer surface for modern Power Fx commanding.

<sub>Set D · Q28</sub>

---

### 36. A solution already contains the modern command components for a model-driven app. One command runs a Power Fx formula, and another runs JavaScript.

Which two additional components must also be included in the solution for export and import to work correctly? (Select TWO.)

- **A.** Site map
- **B.** App module setting
- **C.** Dataverse component library ✅
- **D.** JavaScript web resource ✅
- **E.** Security role with table privileges

> **Answer:** C. Dataverse component library · D. JavaScript web resource

When you move modern commands through solutions, the underlying dependencies must travel with them. Microsoft states that Power Fx commands use a Dataverse component library and JavaScript commands use a web resource, so both must be added to the solution if you plan to export them.

This is a common ALM failure point because the command itself can be present while the runtime artifact behind it is missing. The result is a solution that imports but does not fully preserve the intended command behavior in the target environment.

<sub>Set D · Q29</sub>

---

### 37. A developer finishes a PCF control for a model-driven app and the team wants to move it from development to test and production. System customizers in the target environments must be able to configure the control on columns without rebuilding the component project in each environment.

Which deployment approach should you use?

- **A.** pac pcf push to Dev
- **B.** Web resource bundle upload
- **C.** Solution zip import ✅
- **D.** npm package publish

> **Answer:** C. Solution zip import

PCF controls are solution components, so the durable deployment path is to package the component into a solution and import that solution into Dataverse. That is the documented way to make the control available at runtime in another environment rather than treating it like a loose front-end artifact.

That also matches the consumption requirement in the stem. After the solution containing the code component is imported, administrators and customizers can configure supported columns, grids, or other supported surfaces to use the control in the target environment, which is exactly what the team wants.

<sub>Set D · Q31</sub>

---

### 38. A team imports a solution that contains a canvas-compatible PCF control into a new environment. Makers still cannot add the control inside a canvas app even though the solution import succeeded and the component is present in Dataverse.

What should you do next?

- **A.** Rebuild with production mode
- **B.** Enable PCF for canvas apps ✅
- **C.** Re-register the manifest
- **D.** Convert it to dataset type

> **Answer:** B. Enable PCF for canvas apps

For canvas apps, the environment must have the Power Apps component framework feature enabled before makers can add code components inside canvas apps. Microsoft documents that this feature must be turned on in each environment where you want to use code components in canvas apps.

That means a successful solution import is not always enough for canvas consumption. The control may already exist in Dataverse, but the makers still need the environment capability enabled before they can bring the component into a canvas app through the Studio experience.

<sub>Set D · Q32</sub>

---

### 39. A team wants a repeatable process for moving a PCF control from source code to target-environment usage. They want the flow to follow the supported packaging model and end with the control being used in the app layer.

Steps

Import the solution into the target environment.

Add the PCF project reference to the solution project.

Create the solution project.

Configure the control in the app.

What is the correct order?

- **A.** 2 → 3 → 1 → 4
- **B.** 3 → 1 → 2 → 4
- **C.** 2 → 1 → 3 → 4
- **D.** 3 → 2 → 1 → 4 ✅

> **Answer:** D. 3 → 2 → 1 → 4

The supported flow starts by creating the solution project, then adding the PCF project reference so the solution project knows which control to package. After that, the built solution can be imported into the target environment, and only then can makers or customizers configure the control in the app.

This order matters because app consumption happens after deployment, not before it. You cannot configure a control in the target app until the environment has received the packaged solution that contains the component.

• 3 is first because the solution project is the container used to package the PCF control for deployment. Without that project, there is nothing for the build process to package into a deployable Dataverse solution.

• 2 is second because the solution project must reference the PCF project before build. Microsoft documents pac solution add-reference as the mechanism that links the code component into the solution packaging process.

• 1 is third because the packaged solution must be imported into the target environment before the control is available there. Deployment precedes usage.

• 4 is last because consumption is the final stage in this flow. The control is configured on supported app surfaces only after it has been deployed into the environment.

<sub>Set D · Q33</sub>

---

### 40. A team has completed a PCF project and wants a supported flow to move it into another Dataverse environment. They want the component to be deployable and then available for makers or customizers to consume in that target environment.

Which TWO actions belong in that packaging-and-deployment flow? (Select TWO.)

- **A.** Upload bundle as web resource
- **B.** Add PCF project reference ✅
- **C.** Publish package to npm
- **D.** Import solution zip ✅
- **E.** Register plug-in assembly manually

> **Answer:** B. Add PCF project reference · D. Import solution zip

A PCF project must be referenced from a Dataverse solution project before that solution project is built into the deployable package. Microsoft documents the pac solution add-reference step as the way the solution project knows which code component project to include during build.

Once the solution has been built, the deployable result is the solution package that is imported into Dataverse. That import step is what makes the component available in the environment so it can then be configured or added by makers and customizers on supported app surfaces.

<sub>Set D · Q39</sub>

---

### 41. Service agents open an Account form and then launch a guided review experience built as a custom page. The review must open on top of the current form instead of replacing it, and the custom page must receive the current account record context.

Which approach should you use?

- **A.** Entity form dialog with formId
- **B.** HTML web resource with query string
- **C.** Custom page inline target 1
- **D.** Custom page dialog recordId ✅

> **Answer:** D. Custom page dialog recordId

A custom page dialog with recordId is the best fit because the requirement is to keep the current form in place and open the custom page above it while passing record context. Microsoft’s examples show centered-dialog navigation for custom pages by using Xrm.Navigation.navigateTo with target: 2, and the custom-page pageInput supports recordId so the target page can access the record via Param("recordId").

Inline navigation with target: 1 would replace the current page experience, which breaks the stated requirement. The question is really about matching navigation mode to UX intent: full-page for replacement, dialog for overlay, and side-pane APIs for pane-specific experiences. Here, the dialog pattern is the cleanest match.

<sub>Set E · Q27</sub>

---

### 42. A developer wants a custom page to receive both the current table name and the current row ID so that the page can read them by using Param("entityName") and Param("recordId").

Which two properties should be included in the pageInput object? (Select TWO.)

- **A.** navigation target value
- **B.** pageInput.entityName ✅
- **C.** dialog position setting
- **D.** dialog title text
- **E.** pageInput.recordId ✅

> **Answer:** B. pageInput.entityName · E. pageInput.recordId

The two required properties are entityName and recordId. Microsoft documents these as optional properties of the custom-page pageInput object, and specifically states that they are exposed to the custom page through Param("entityName") and Param("recordId").

This is an important distinction in Client API navigation design. The pageInput object carries the destination page definition and page-specific context, while dialog title, position, width, and target belong to navigationOptions and control how the destination opens rather than what context it receives.

<sub>Set E · Q28</sub>

---

### 43. A developer wrote the following form script to open a custom page for the current sales order. The script runs, but it does not navigate to the custom page.

Snippet

function openOrderReview(executionContext) {
    var formContext = executionContext.getFormContext();
    var pageInput = {
        pageType: "entityrecord",
        name: "cr8f_orderreview",
        entityName: "salesorder",
        recordId: formContext.data.entity.getId().replace(/[{}]/g, "")
    };

    Xrm.Navigation.navigateTo(pageInput, { target: 1 });
}
What is the best fix?

- **A.** Change pageType to custom ✅
- **B.** Replace name with the main formId
- **C.** Use Xrm.Navigation.openForm instead
- **D.** Remove recordId from pageInput

> **Answer:** A. Change pageType to custom

The best fix is to change pageType to custom. Microsoft documents that the custom-page object for navigateTo must use pageType: "custom" and name set to the logical name of the custom page. In the snippet, entityrecord tells the API to expect an entity-record navigation object instead of a custom-page navigation object.

The rest of the snippet is broadly aligned with the custom-page pattern. Microsoft’s examples show using executionContext.getFormContext() to obtain the current form context and then using record context in the custom-page navigation object, which means the core defect is the wrong pageType rather than the use of recordId itself.

<sub>Set E · Q29</sub>

---

### 44. A JavaScript handler opens a custom page and passes the current customer number into recordId. The custom page later fails when users reopen the URL directly, and the value is rejected during startup validation.

What is the most likely cause?

- **A.** The page name must match the site map title
- **B.** recordId must be a GUID ✅
- **C.** navigateTo requires dialog target 2
- **D.** custom page navigation must use openForm

> **Answer:** B. recordId must be a GUID

The most likely cause is that recordId must be a GUID. Microsoft’s custom-page navigation example explicitly says the recordId parameter must be a GUID because it is validated when the app starts from the URL. Passing a customer number, alternate identifier, or other business key into recordId breaks that expectation.

This is a common implementation mistake because a custom page can absolutely use business keys, but not by misusing the recordId parameter. If a developer wants to work with non-GUID business identifiers, they need a different parameter strategy inside the custom page logic rather than overloading the documented GUID-specific field.

<sub>Set E · Q30</sub>

---

### 45. A model-driven PCF control on an Opportunity form must let sellers pick an existing Contact by using the platform’s native lookup experience. The team does not want to build a custom dialog and wants to stay within supported PCF APIs instead of calling unsupported client objects directly.

Which approach should you use?

- **A.** Device camera prompt
- **B.** Web API createRecord call
- **C.** Utility lookupObjects dialog ✅
- **D.** Client connectivity inspection

> **Answer:** C. Utility lookupObjects dialog

The best choice is Utility lookupObjects dialog because the Utility API includes lookupObjects, which opens a native lookup dialog for the user to select one or more items. That maps directly to the requirement to reuse the platform’s lookup experience from inside a model-driven PCF component.

This is also the supported framework path. Microsoft’s PCF API reference explicitly warns against using Xrm object methods that are not exposed by the framework, so the clean design is to use the framework’s Utility surface rather than reach outside it for unsupported client calls.

<sub>Set E · Q31</sub>

---

### 46. A team wants one PCF component package to run in both model-driven and canvas apps wherever the selected APIs are supported. Which TWO design rules are correct? (Select TWO.)

- **A.** Call raw Xrm methods directly
- **B.** Check host API availability ✅
- **C.** Assume Utility methods work across all canvas hosts
- **D.** Skip manifest feature declarations
- **E.** Declare device usage in manifest ✅

> **Answer:** B. Check host API availability · E. Declare device usage in manifest

The two correct rules are Check host API availability and Declare device usage in manifest. Microsoft’s PCF API reference explicitly tells developers to check the “Available for” support information for each API, and Microsoft’s best-practices guidance gives context.webAPI as a concrete example of an API that is not available in canvas apps.

Microsoft also documents that Device API methods must be declared in the manifest feature-usage section before they are used. Together, these two rules are the correct design baseline for a reusable component that may be hosted in more than one Power Apps surface.

<sub>Set E · Q32</sub>

---

### 47. A PCF control must create Dataverse records directly from inside its own component logic. The same component package is then added to both a model-driven app and a canvas app, and the canvas host throws at runtime.

Snippet

public init(context: ComponentFramework.Context<IInputs>): void {
    context.webAPI.createRecord("task", {
        subject: "Follow up from PCF"
    });
}
What is the best correction?

- **A.** Restrict to model-driven host ✅
- **B.** Replace with Utility lookupObjects dialog
- **C.** Move the call into updateView
- **D.** Add a device feature declaration

> **Answer:** A. Restrict to model-driven host

The best correction is Restrict to model-driven host because the component is using context.webAPI directly, and Microsoft’s PCF guidance says context.webAPI is not available in canvas apps. The WebAPI reference also identifies the PCF Web API surface as available for model-driven apps and portals, not canvas apps.

Moving the same Web API call to a different lifecycle method would not change host support. The root problem is not timing; it is API availability. If the design requirement is direct Dataverse CRUD from inside the component by using PCF context.webAPI, the supported architectural boundary is a model-driven host.

<sub>Set E · Q33</sub>

---

### 48. A developer is testing a PCF control locally by using npm start and the browser test harness. Calls to context.device.getBarcodeValue() and context.utils.lookupObjects() throw exceptions even though the component package and manifest are valid.

What is the best next step?

- **A.** Add a retry loop in init
- **B.** Deploy and test in Dataverse ✅
- **C.** Call raw Xrm.WebApi methods
- **D.** Disable the feature-usage node

> **Answer:** B. Deploy and test in Dataverse

The best next step is Deploy and test in Dataverse because Microsoft documents important limits in the local browser test harness. The debug guidance says scenarios that use features listed in the feature-usage section can throw exceptions in the harness, and it also says other context APIs such as Navigation and Utility methods are not suitable for full harness testing.

That means a locally failing Device or Utility call is not automatically proof that the component logic is wrong. It can simply reflect a harness limitation. Microsoft’s Device reference still requires proper manifest declaration for device methods, but once that is in place, the supported next validation step is deployment-based testing in Dataverse rather than relying on the local harness alone.

<sub>Set E · Q34</sub>

---

### 49. A warehouse PCF control must populate a field by scanning a package label on a phone or tablet. The component should use native camera-based barcode capture instead of opening a lookup or querying Dataverse first.

Which feature should the component logic use?

- **A.** Utility lookup dialog for records
- **B.** Dataverse Web API retrieval
- **C.** Client form-factor detection
- **D.** Device barcode scan ✅

> **Answer:** D. Device barcode scan

The correct choice is Device barcode scan because the PCF Device API is the framework surface for native device capabilities, and the getBarcodeValue method is specifically documented for scanning barcode information by invoking the device camera. Microsoft lists the Device API as available for model-driven and canvas apps, and the barcode method as available for mobile clients.

This is a better fit than Utility or Web API because the requirement is direct hardware-assisted capture inside the component, not record lookup or Dataverse CRUD. Microsoft also notes that if you use device API methods, you must declare their usage in the manifest’s feature-usage section.

<sub>Set E · Q37</sub>

---

### 50. A form script in a model-driven app must open a custom page as the main page experience.

Which Client API method should you use?

- **A.** Xrm.Navigation.openForm with parameters
- **B.** Xrm.Panels.loadPanel for navigation
- **C.** Xrm.Navigation.navigateTo ✅
- **D.** Xrm.App.sidePanes.createPane then navigate

> **Answer:** C. Xrm.Navigation.navigateTo

Xrm.Navigation.navigateTo is the correct method because Microsoft documents it as the Client API used to navigate to a table list, table record, HTML web resource, or custom page. For custom-page navigation in model-driven apps, the supported pattern is to pass a pageInput object with pageType: "custom" and the custom page logical name into navigateTo.

This is the most direct full-page navigation choice when the goal is to open a custom page from model-driven app scripting. Microsoft’s custom-page navigation examples show navigateTo being used for inline full-page navigation, centered dialogs, and side dialogs, which makes it the core API for this requirement.

<sub>Set E · Q45</sub>

---

### 51. A field component declares a bound input in ControlManifest.Input.xml. The TypeScript class compiles, but the component does not refresh when the framework passes changed values in the property bag.

Snippet

export class StatusBadge implements ComponentFramework.StandardControl<IInputs, IOutputs> {
    public init(
        context: ComponentFramework.Context<IInputs>,
        notifyOutputChanged: () => void,
        state: ComponentFramework.Dictionary,
        container: HTMLDivElement
    ): void {
        // initialization
    }

    public getOutputs(): IOutputs {
        return { };
    }

    public destroy(): void {
        // cleanup
    }
}
Which required interface method must be added?

- **A.** init override
- **B.** updateView method ✅
- **C.** output schema method
- **D.** manifest parser

> **Answer:** B. updateView method

StandardControl requires the core lifecycle methods that let a PCF component initialize, react to changed values, return outputs, and clean up. Microsoft documents updateView as the method called when values in the property bag change, including field values, datasets, dimensions, metadata, and other framework-provided values, so that is the missing required method in this control.

The manifest defines the component shape and the parameters that become available through context.parameters, but reacting to changed inputs is still an interface responsibility in the TypeScript implementation. In practice, that means a bound manifest property and a StandardControl implementation work together: the manifest declares the inputs, and updateView is where the control receives and renders the latest values.

<sub>Set F · Q1</sub>

---

### 52. A model-driven app form must disable the credit limit control when the account is inactive. The script must align with the current Client API object model and work from the event context instead of relying on deprecated global form references.

Snippet

function toggleCreditLimit(executionContext) {
    const formContext = executionContext.getFormContext();
    const stateCode = formContext.getAttribute("statecode").getValue();
    formContext.getControl("creditlimit").setDisabled(stateCode === 1);
}
Which API choice makes this handler align with the current Client API object model? Select only one answer.

- **A.** Xrm.Page reference
- **B.** Process control API
- **C.** executionContext.getFormContext() ✅
- **D.** Global page context helper

> **Answer:** C. executionContext.getFormContext()

executionContext.getFormContext() is the correct choice because Microsoft’s Client API guidance says the execution context defines the event context and is used to obtain the relevant formContext or gridContext. Microsoft also documents that when event handlers are defined by using code, the system automatically passes the execution context as the first parameter.

That makes this pattern the right way to build JavaScript against the current Client API object model in model-driven apps. It keeps the code anchored to the active form context instead of depending on older global references, and it matches Microsoft’s form-event scripting model where handlers are attached through script web resources and react to form events.

<sub>Set F · Q24</sub>

---

### 53. A developer must register one handler at runtime when a column value changes and a different handler just before the form is saved. Which two registration methods should the developer use? (Select TWO.)

- **A.** formContext.ui.addOnLoad
- **B.** formContext.data.addOnLoad
- **C.** addOnSave ✅
- **D.** addOnChange ✅
- **E.** addLoaded

> **Answer:** C. addOnSave · D. addOnChange

addOnChange and addOnSave are the correct pair because Microsoft’s event-registration documentation explicitly lists addOnChange for attribute OnChange events and addOnSave for the form OnSave event when handlers are attached by using code. This is exactly the runtime-registration scenario described in the question.

The distinction matters because different model-driven app events have separate registration methods. Microsoft documents form OnLoad, form data OnLoad, form loaded, OnSave, lookup PreSearch, and attribute OnChange as separate event families, each with their own add/remove methods. Choosing the right registration method is therefore part of correct Client API design, not just syntax recall.

<sub>Set F · Q25</sub>

---

### 54. A developer needs to load the current account record’s name from JavaScript running on a model-driven form. The code should call the Dataverse Web API directly from client scripting and return a single record.

Snippet

function loadAccountName(executionContext) {
    const formContext = executionContext.getFormContext();
    const id = formContext.data.entity.getId().replace(/[{}]/g, "");

    // TODO: replace this line with the correct Dataverse Web API call
}
Which call should replace the TODO line? Select only one answer.

- **A.** updateRecord call
- **B.** retrieveRecord call ✅
- **C.** retrieveMultipleRecords call
- **D.** navigation call instead

> **Answer:** B. retrieveRecord call

retrieveRecord is correct because Microsoft’s Client API reference states that Xrm.WebApi.retrieveRecord(entityLogicalName, id, options) retrieves a table record. The question explicitly asks for a single Dataverse record to be loaded from client scripting, which is the exact purpose of that method.

This also fits the broader Client API design for model-driven apps. Microsoft documents Xrm.WebApi as the client-side surface for creating and managing records and executing Web API actions and functions, and retrieveRecord is the single-record retrieval method within that surface.

<sub>Set F · Q26</sub>

---

### 55. A model-driven app command must appear only when at least one row is selected in the main grid. The maker wants to use a modern command with Power Fx instead of JavaScript.

Snippet

// Visible property
??
Which formula should you use? Select only one answer.

- **A.** IsBlank(Self.Selected.Item)
- **B.** CountRows(Self.Selected.AllItems) = 0
- **C.** CountRows(Self.Selected.AllItems) > 0 ✅
- **D.** CountRows(Self.Selected.AllItems) > 0 And !Self.Selected.Unsaved

> **Answer:** C. CountRows(Self.Selected.AllItems) > 0

CountRows(Self.Selected.AllItems) > 0 is the best answer because Microsoft’s commanding documentation for model-driven apps shows that Self.Selected.AllItems represents all selected records and explicitly uses CountRows(Self.Selected.AllItems) > 0 as the visibility pattern for showing a command when one or more records are selected.

This is a strong Power Fx command-design answer because it directly matches the selection model provided by the command host. Microsoft also documents Self.Selected.Item, Self.Selected.AllItems, and related state information as command-host-provided selection properties, so using the selection table for visibility is the intended pattern rather than inventing a custom condition.

<sub>Set F · Q27</sub>

---

### 56. A model-driven app needs a custom command that opens a custom page dialog and passes control to an existing JavaScript function in a web resource. The team wants to keep the command action in JavaScript rather than rewrite the behavior in Power Fx.

Which command configuration should you use?

- **A.** Flow action
- **B.** Classic ribbon enable rule
- **C.** Inline Power Fx action formula
- **D.** JavaScript library + function ✅

> **Answer:** D. JavaScript library + function

JavaScript library + function is correct because Microsoft’s command documentation shows that a command can call JavaScript from a command by adding the JavaScript library web resource and then specifying the JavaScript function name in the command properties. The official custom-page command example walks through exactly that pattern.

This makes it the best-fit configuration when the requirement is specifically to keep the command behavior in JavaScript. The scenario is not asking for a visibility rule, a Power Fx action, or an external automation trigger. It is asking for a command action bound to an existing client-side function, which is exactly what the documented JavaScript-library configuration supports.

<sub>Set F · Q29</sub>

---

### 57. A developer wants a command to open a custom page by using Xrm.Navigation.navigateTo. The design must pass the current table logical name and record ID so the custom page can read them by using Param("entityName") and Param("recordId").

Exhibit 1

Which row should be used as the pageInput object?

- **A.** Row 1 ✅
- **B.** Row 2
- **C.** Row 3
- **D.** Row 4

> **Answer:** A. Row 1

Row 1 is correct because Microsoft’s navigateTo reference says that when opening a custom page, the pageInput object should use pageType: "custom" and name for the logical name of the custom page. Microsoft also documents entityName and recordId as optional values that are made available to the custom page through Param("entityName") and Param("recordId").

That means Row 1 matches the documented structure exactly. It uses the right page type, the right identifier field, and the correct contextual properties for passing record context into the custom page. This is the strongest Microsoft-exam answer because it aligns directly with the official object shape for custom-page navigation.

<sub>Set F · Q30</sub>

---

### 58. A PCF field control is loaded on a model-driven form, then receives updated context after the user changes data, then returns bound output, and finally is removed from the page. Which sequence best represents that lifecycle?

Steps

Return bound values through getOutputs

Initialize the control in init

Clean up listeners in destroy

Refresh the rendered view in updateView

What is the correct order?

- **A.** 4 → 2 → 1 → 3
- **B.** 2 → 4 → 1 → 3 ✅
- **C.** 2 → 1 → 4 → 3
- **D.** 4 → 1 → 2 → 3

> **Answer:** B. 2 → 4 → 1 → 3

The correct sequence is 2 → 4 → 1 → 3. Microsoft’s PCF documentation says init is used to initialize the component instance, updateView is called when values in the property bag change, getOutputs returns the bound outputs, and destroy is invoked when the component is removed from the DOM tree for cleanup.

That lifecycle makes practical sense for a field control. The control must first initialize its instance and setup state, then render or rerender as the framework sends updated context, then return outputs when the framework needs changed bound values, and finally release handlers and memory when the control is torn down. Microsoft’s StandardControl reference and code-component overview describe exactly these responsibilities.

• 2 is first because init is the component’s initialization stage. Microsoft says this method is used to initialize the component instance and can kick off startup actions. A control cannot sensibly refresh or return outputs before it has been initialized. That makes init the correct first step.

• 4 is second because after the control exists, the framework calls updateView whenever values in the property bag change. Microsoft explicitly lists field values, datasets, global values, and metadata among the things that can trigger it. In the scenario, this is the phase where the control reflects changed context after user interaction. So updateView belongs after initialization and before teardown.

• 1 is third because getOutputs is the stage where the component returns bound values back to the framework. Microsoft documents it as being called by the framework prior to a component receiving new data and as the method that returns output values. In a field-control flow, that is the right place to surface the changed value after interaction. It logically follows initialization and rendering activity.

• 3 is last because destroy is the cleanup step. Microsoft says it is invoked when the component is to be removed from the DOM tree and should be used to release memory and clean up artifacts like event listeners. That makes it the terminal lifecycle stage. Once destroy has run, the active control instance is being removed rather than updated.

<sub>Set F · Q31</sub>

---

### 59. A team is building a PCF control that uses context.device for camera access and context.webAPI to create related Dataverse records. They want to move from implementation to a deployable package that can be imported into Dataverse.

Steps

Create a solution project and add a reference to the PCF project.

Implement the control logic that uses Device, Utility, and Web API features.

Build the PCF project.

Build and import the solution package into Dataverse.

What is the correct order?

- **A.** 1 → 2 → 3 → 4
- **B.** 2 → 1 → 3 → 4
- **C.** 2 → 3 → 1 → 4 ✅
- **D.** 3 → 2 → 1 → 4

> **Answer:** C. 2 → 3 → 1 → 4

The logical flow is to implement the control first, then build the PCF project, then create the solution project that references that component, and finally build and import the solution package into Dataverse. Microsoft documents the PCF development flow as implementing the component artifacts and building the component, and then bundling the code component into a solution file for import into Dataverse.

This question also tests that Device, Utility, and Web API usage belong in the PCF control implementation phase, because those capabilities are surfaced through the framework Context. Packaging and deployment are separate solution lifecycle steps carried out afterward with CLI and solution packaging commands.

• 2 is first because the control logic must exist before there is anything meaningful to build or package. Microsoft’s context reference shows that device, utils, and webAPI are framework capabilities exposed to the control at implementation time.

• 3 is second because after implementing the control, the next step is to build the PCF project. Microsoft’s build guidance explicitly calls out building the component project before bundling it into a solution file.

• 1 is third because the solution project is the packaging container used to bundle the already-created PCF project into a solution zip. Microsoft’s packaging guidance describes using pac solution init and pac solution add-reference for this solution packaging stage.

• 4 is last because the finished solution package is what gets built and imported into Dataverse. Microsoft states that the bundled solution file is what you import to make the code component available at runtime.

<sub>Set F · Q34</sub>

---

### 60. A model-driven form must calculate a recommended follow-up date as soon as the form opens for a new record. The same calculation must run again every time the Estimated Revenue column changes while the user is editing the form.

Which event design should you configure?

- **A.** Form OnSave + data OnLoad handler
- **B.** Form OnLoad + column OnChange ✅
- **C.** Lookup PreSearch + addLoaded
- **D.** Command OnSelect + form Loaded handler

> **Answer:** B. Form OnLoad + column OnChange

Form OnLoad + column OnChange is the best design because the requirement has two separate trigger points: once when the form first opens, and again whenever a specific field value changes. Microsoft’s client scripting documentation describes form events such as load and save, and it separately describes data changes in a column as event triggers that your script can react to.

This is exactly the pattern you use when a calculation needs both initialization behavior and interactive recalculation behavior. The form OnLoad event handles the initial state of the page, while the attribute OnChange event handles user-driven updates after the form is already open. That pairing matches the operational requirement much more precisely than save, lookup, or command-triggered events.

<sub>Set F · Q50</sub>

---
