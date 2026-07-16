# Dependency Graph

## High-Level Graph

```mermaid
graph TD
    run_agent[run_agent.py] --> model_tools[model_tools.py]
    run_agent --> agentpkg[agent/*]
    run_agent --> toolsreg[tools/registry.py]
    model_tools --> toolsreg
    model_tools --> pluginloader[hermes_cli.plugins]
    pluginloader --> plugins[plugins/*]
    gatewayrun[gateway/run.py] --> agentpkg
    gatewayrun --> hermescli[hermes_cli/*]
    gatewayrun --> gatewaypkg[gateway/*]
    cli[cli.py] --> hermescli
    cli --> model_tools
    cli --> run_agent
```

## Core Modules

- `run_agent.py`
- `model_tools.py`
- `tools/registry.py`
- `agent/*`
- `gateway/*`
- `hermes_cli/*`

## Shared Modules

- `utils.py`
- `hermes_constants.py`
- `hermes_bootstrap.py`

## Leaf Modules

Many tool and plugin files are leaf nodes that register behavior into the core registries.

## Coupling Notes

- The tool registry is a central dependency.
- Plugin discovery is a central extension boundary.
- Memory/provider interfaces are intentionally narrow.
