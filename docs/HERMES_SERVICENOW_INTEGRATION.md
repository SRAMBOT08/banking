# Hermes ServiceNow Integration

## 1. Hermes Plugin Lifecycle

Hermes discovers plugins by scanning plugin manifests and importing each plugin
package's `register(ctx)` entrypoint.

For the ServiceNow capability:

- `plugin.yaml` declares the capability metadata
- `plugins/servicenow_pipeline/__init__.py` exposes the CLI registration entrypoint
- the runtime composition module is available for gateway startup binding

## 2. Runtime Lifecycle

The ServiceNow runtime mirrors the Teams runtime composition pattern:

```text
gateway config
  ↓
runtime config reader
  ↓
ServiceNowClient
  ↓
TableExecutor
  ↓
PayloadBuilder
  ↓
IncidentService
  ↓
ExecutionVerifier
  ↓
ServiceNowPipeline
```

The runtime layer only wires dependencies together.

## 3. Dependency Graph

```text
ServiceNowClient
  ↓
TableExecutor
  ↓
IncidentService
  ├── PayloadBuilder
  └── TableExecutor
  ↓
ExecutionVerifier
  ↓
ServiceNowPipeline
```

## 4. Initialization Sequence

1. Hermes discovers the plugin through `plugin.yaml`.
2. Hermes imports the plugin package and calls `register(ctx)`.
3. The runtime layer reads configuration from gateway state.
4. The runtime constructs the client, executor, service, verifier, and pipeline.
5. The composed pipeline is stored on the gateway runtime binding slot when the
   gateway invokes the bind function.

## 5. Startup Sequence

The Teams capability binds itself during gateway startup through Hermes core
gateway wiring. The ServiceNow capability follows the same runtime pattern, but
the actual startup invocation point remains a Hermes core concern.

## 6. Shutdown Sequence

The ServiceNow runtime layer itself is passive during shutdown.

Resource cleanup is expected to happen through:

- client lifecycle closure
- gateway shutdown cleanup
- future orchestration-level teardown if introduced later

## 7. Integration Differences from Teams

| Area | Teams | ServiceNow |
|---|---|---|
| Runtime wiring target | Microsoft Graph webhook ingress | Generic ServiceNow capability slot |
| Business layer | Meetings / transcript workflow | Incident orchestration |
| Verification | Teams summary delivery outcome | ServiceNow creation verification |
| Transport | Teams-specific adapter and writer | Generic ServiceNow client and table executor |
| Current activation path | Bound in gateway runtime | Composition layer ready; Hermes core binding hook is the remaining core integration point |

## 8. Remaining Work Before MVP Completion

- connect the ServiceNow runtime binding to Hermes gateway startup in the same
  place Teams is wired today
- expose a ServiceNow gateway trigger or adapter entrypoint if the capability is
  intended to run automatically from inbound events
- add any ServiceNow-specific configuration keys once the activation path is
  finalized

## Design Note

The ServiceNow integration is intentionally non-invasive:

- no Hermes runtime redesign
- no Teams capability changes
- no business logic inside runtime wiring
- no HTTP or payload logic in the runtime layer

