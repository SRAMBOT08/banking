# Plugin Activation Strategy

## Question 1: Are standalone plugins intentionally disabled by default?

Yes.

The plugin loader treats `standalone` plugins as opt-in. In `hermes_cli/plugins.py`, everything that is not a bundled backend, bundled platform, exclusive provider, or model provider is only loaded when it appears in `plugins.enabled`.

## Question 2: Is `plugins.enabled` the official mechanism for activating optional capabilities?

Yes.

The loader explicitly checks `plugins.enabled` for standalone plugins and skips them when they are not listed. That is the framework’s built-in activation gate for optional capabilities.

## Question 3: Is Teams enabled through the same mechanism, or is it treated as a special case?

Teams is treated with the same opt-in mechanism.

`plugins/teams_pipeline/plugin.yaml` declares `kind: standalone`, and `gateway/run.py` checks `plugins.enabled` for `teams_pipeline` before wiring the runtime. ServiceNow follows the same pattern.

## Question 4: Should ServiceNow be enabled by default for all Hermes installations?

No, not based on the current Hermes architecture.

ServiceNow is a third-party enterprise integration. Hermes already models this class of capability as an optional plugin, not as a universally enabled core feature.

## Question 5: Or should it remain opt-in and be enabled only through configuration?

It should remain opt-in and be enabled through configuration.

That matches the current framework semantics and keeps the core installation free of capability-specific side effects.

## Question 6: If Hermes later supports Salesforce, Databricks, SAP, Jira, etc., what is the recommended activation strategy?

Keep each of those integrations as optional plugins activated through `plugins.enabled`.

That is the current Hermes pattern for optional capability surfaces:

- discover the plugin
- parse `plugin.yaml`
- load it only when explicitly enabled
- wire its runtime only after enablement

## Evidence from the code

### Plugin loader

`hermes_cli/plugins.py` states that standalone plugins are opt-in and only load when present in `plugins.enabled`.

### ServiceNow manifest

`plugins/servicenow_pipeline/plugin.yaml` declares:

- `kind: standalone`

### Gateway startup

`gateway/run.py` checks:

- `_servicenow_pipeline_plugin_enabled()`

which reads:

- `plugins.enabled`

before binding the ServiceNow runtime.

### Teams comparison

`plugins/teams_pipeline/plugin.yaml` also declares `kind: standalone`, and Teams uses the same enablement model.

## Recommendation

**OPTION B: Keep ServiceNow as an optional plugin activated through `plugins.enabled`**

### Justification

- It matches Hermes’ existing plugin semantics for standalone capabilities.
- It matches the Teams pipeline pattern already in the codebase.
- It keeps enterprise integrations opt-in, which is the architecture Hermes already uses for optional surface area.
- It scales cleanly to future integrations like Salesforce, Databricks, SAP, and Jira without changing the framework.

