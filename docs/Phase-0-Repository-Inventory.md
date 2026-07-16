# Phase 0 Repository Inventory

## 1. Repository Overview

### Purpose of Hermes

Hermes is a self-improving AI agent platform that runs across a CLI, a messaging gateway, a terminal UI, and a desktop application. It combines long-lived conversation handling, tool execution, memory, skills, cron scheduling, platform adapters, and plugin-based extensibility.

### Primary Architecture Style

Hermes uses a layered, modular, plugin-oriented architecture:

- A core Python runtime provides agent orchestration, tool execution, persistence, and configuration.
- Platform-specific runtime surfaces connect the core to messaging channels, desktop, and TUI entry points.
- Optional capabilities are pushed into plugins, optional skill packs, and service-gated dependencies.
- Frontend surfaces are split into separate React/TypeScript applications that communicate with Python backends over JSON-RPC or stdio.

### Main Execution Model

- The main agent loop is Python-based and synchronous at the orchestration layer.
- Runtime entry points include the CLI, gateway process, scheduler, ACP adapter, and TUI backend.
- Tool calls are dispatched through a registry and executed by environment-aware tool backends.
- Messaging platforms and UI surfaces are attached through adapters, not embedded directly into the core agent loop.

### Technology Stack

- Python for the agent core, runtime services, gateway, tools, plugins, and automation.
- TypeScript/React for the desktop app, shared client helpers, and TUI/dashboard frontends.
- FastAPI/Uvicorn for HTTP and gateway-facing server surfaces.
- SQLite and file-based persistence for session, state, and caches in the Python core.
- Node.js/Vite for the UI build pipeline.
- YAML, JSON, Markdown, and shell scripts for configuration, manifests, docs, and operations.

---

## 2. High-Level Folder Structure

| Top-Level Folder | Purpose | Architectural Role |
|---|---|---|
| `agent/` | Core agent runtime, provider adapters, memory, prompting, context, and tool orchestration helpers | Runtime Component / Business Logic / Framework Component |
| `apps/` | Desktop app and shared TypeScript helpers | Runtime Component / Platform UI |
| `assets/` | Static repository assets such as branding images | Utility / Configuration asset |
| `cron/` | Scheduled job engine and cron-related logic | Runtime Component / Infrastructure |
| `datagen-config-examples/` | Sample configurations for data generation workflows | Configuration / Utility |
| `docker/` | Container entrypoints, init hooks, and runtime container support | Infrastructure |
| `docs/` | Project documentation and architecture notes | Documentation / Configuration |
| `gateway/` | Messaging gateway runtime and platform adapters | Runtime Component / Platform Integration / Infrastructure |
| `hermes_cli/` | CLI application, subcommands, setup, config, and service orchestration | Runtime Component / Framework Component |
| `infographic/` | Visual design and reference artifacts | Utility / Documentation asset |
| `locales/` | Translation catalogs | Configuration |
| `nix/` | Nix packaging and environment definitions | Infrastructure / Configuration |
| `optional-mcps/` | Example or optional MCP server manifests | Plugin ecosystem / Integration metadata |
| `optional-skills/` | Non-default skill packs and skill descriptions | Plugin ecosystem / Configuration |
| `packaging/` | Distribution and package manager packaging assets | Infrastructure |
| `plugins/` | Plugin bundles for memory, platforms, models, observability, and more | Plugin Component |
| `providers/` | Provider abstraction layer for model/runtime backends | Framework Component |
| `scripts/` | Operational scripts, build helpers, checks, and release tooling | Infrastructure / Utility |
| `skills/` | Built-in skills shipped with Hermes | Business Logic / Plugin-like capability layer |
| `tests/` | Automated test suites for core, runtime, adapters, and plugins | Testing |
| `tools/` | Tool implementations, registries, environment backends, and tool safety layers | Framework Component / Runtime Component |
| `tui_gateway/` | Python backend for the terminal UI | Runtime Component / Platform Integration |
| `ui-tui/` | Ink/React terminal UI application | Runtime Component / Platform UI |
| `web/` | Browser dashboard frontend | Runtime Component / Platform UI |
| `website/` | Docusaurus documentation site | Documentation / Platform UI |

---

## 3. Repository Inventory

### Core Repository Areas

| Folder | Purpose | Child Modules | Dependencies | Architectural Layer |
|---|---|---|---|---|
| `agent/` | Central agent engine and cross-cutting runtime logic | Adapters, context management, memory, prompting, tool dispatch, transport adapters, learning graph, rate limiting, compression | `providers`, `tools`, `skills`, `hermes_state`, `gateway`, external model SDKs | Runtime Component / Business Logic |
| `hermes_cli/` | CLI surface, setup flows, config commands, subcommands, auth, dashboards, and operational commands | `subcommands/`, `dashboard_auth/`, `proxy/` | `agent`, `gateway`, `tools`, `plugins`, config and packaging helpers | Runtime Component / Framework Component |
| `gateway/` | Multi-platform messaging gateway and delivery pipeline | `platforms/`, `relay/`, `builtin_hooks/` | `agent`, `tools`, platform SDKs, auth, session state, delivery filters | Runtime Component / Platform Integration / Infrastructure |
| `tools/` | Tool registry and concrete tools for terminal, browser, files, delegation, memory, MCP, voice, and safety controls | `environments/`, `computer_use/` | `agent`, providers, network/file/process libraries, plugin-specific integrations | Framework Component / Runtime Component |
| `plugins/` | Optional capability bundles packaged separately from core runtime | `browser/`, `cron_providers/`, `dashboard_auth/`, `disk-cleanup/`, `google_meet/`, `image_gen/`, `kanban/`, `memory/`, `model-providers/`, `observability/`, `platforms/`, `security-guidance/`, `spotify/`, `teams_pipeline/` | Core plugin loader, platform SDKs, model/provider SDKs, external services | Plugin Component |
| `apps/` | TypeScript applications and shared client utilities | `desktop/`, `shared/`, `bootstrap-installer/` | React, Vite, Node, shared JSON-RPC helpers, Python backends | Runtime Component / Platform UI |
| `ui-tui/` | Terminal UI frontend for the interactive CLI | `src/`, `scripts/` | Ink, React, Node, JSON-RPC gateway | Runtime Component / Platform UI |
| `tui_gateway/` | Python backend that powers the TUI process boundary | server and session management modules | `agent`, `tools`, model providers, session store | Runtime Component / Infrastructure |
| `cron/` | Scheduler and job classification for timed execution | scheduler, jobs, catalogs, guards, suggestions | `gateway`, `agent`, platform delivery paths | Runtime Component / Infrastructure |
| `providers/` | Provider abstraction layer and shared provider base types | `base.py`, package init, provider docs | model and runtime provider implementations | Framework Component |
| `acp_adapter/` | Agent Client Protocol adapter and server entrypoint | auth, permissions, session, provenance, tools, events | `agent`, session/protocol layers, ACP registry | Platform Integration / Infrastructure |
| `acp_registry/` | ACP registry artifacts | registry manifest and icon assets | ACP adapter / packaging tooling | Configuration / Infrastructure |
| `skills/` | Built-in skills bundled with the repo | Skill directories and metadata | `agent`, `hermes_cli`, tool and prompt integrations | Business Logic / Plugin-like capability layer |
| `optional-skills/` | Optional skill packs grouped by theme | descriptive documents and pack metadata | skills loader and documentation tooling | Plugin Component / Configuration |
| `optional-mcps/` | Optional MCP manifests for external services | manifests for linear, n8n, unreal-engine | MCP tooling and runtime catalog integration | Plugin Component / Integration Metadata |
| `website/` | Public docs website | docs, scripts, sidebar config, Docusaurus config | React/MDX/TypeScript docs stack | Documentation |
| `web/` | Dashboard frontend | React app entrypoint, static assets | Vite, React, browser build tooling | Runtime Component / Platform UI |
| `docs/` | Architecture and operational documentation | architecture notes, security docs, session lifecycle docs | Markdown docs ecosystem | Documentation / Configuration |
| `scripts/` | Maintenance and release utilities | install scripts, tests, CI helpers, diagnostics | shell, Python, Node, repo tooling | Infrastructure / Utility |

### Supporting Repository Areas

| Folder | Purpose | Child Modules | Dependencies | Architectural Layer |
|---|---|---|---|---|
| `docker/` | Container runtime support and init hooks | entrypoint scripts, cont-init hooks, wrapper scripts | Docker image runtime, shell, profile reconciliation | Infrastructure |
| `packaging/` | Package manager and distribution packaging | Homebrew formula resources | packaging toolchain | Infrastructure |
| `nix/` | Nix flakes and packaging configuration | Nix expressions and locks | Nix ecosystem | Infrastructure / Configuration |
| `locales/` | Translation resources | language YAML files | UI/runtime localization loaders | Configuration |
| `assets/` | Static branding and media | banner image and other art assets | docs/site consumers | Utility / Configuration asset |
| `infographic/` | Reference visuals and diagrams | static assets | docs/communication assets | Utility / Documentation asset |
| `datagen-config-examples/` | Example configs for generated datasets/workflows | sample config files | data generation tooling | Configuration |
| `.github/` | Repository automation | workflows, issue templates, bot configs | GitHub Actions and repo automation | Infrastructure |
| `.plans/` | Planning artifacts for internal workstreams | plan documents | project workflow tooling | Documentation / Utility |

---

## 4. Framework Components

Reusable framework components are the pieces that define interfaces, shared behavior, and abstraction boundaries rather than a single product surface.

| Component | Path | Purpose | Major Dependencies |
|---|---|---|---|
| Provider abstraction | `providers/` | Shared base classes and provider documentation for backend integrations | Runtime provider implementations, model/provider plugins |
| Tool registry | `tools/registry.py` and `tools/` | Central tool registration and discovery layer | Tool implementations, environment backends |
| Environment abstraction | `tools/environments/` | Terminal/environment execution backends | Local, Docker, SSH, Modal, Daytona, Singularity backends |
| Plugin utilities | `plugins/plugin_utils.py` | Shared helpers for plugin packaging and registration | Plugin manifests and loaders |
| Slash command framework | `hermes_cli/commands.py` and command consumers | Central command registry used by CLI, gateway, and platform menus | CLI, gateway, autocomplete, help generators |
| Localization framework | `locales/`, `apps/desktop/src/i18n/`, `ui-tui/src/` | Shared internationalization resources and loaders | UI surfaces and runtime text catalogs |
| Transport abstraction | `agent/transports/`, `gateway/relay/` | Standardized agent and gateway transport layers | Model backends, JSON-RPC/stdio, platform relays |
| Session and persistence contracts | `hermes_state.py`, `hermes_cli/session_*`, `gateway/session.py`, `tui_gateway/` | Shared session lifecycle and storage boundaries | SQLite, runtime session controllers |
| Configuration framework | `hermes_cli/config.py`, `gateway/config.py`, `hermes_constants.py` | Cross-cutting config loading and profile-aware paths | YAML files, env bridges, setup flows |

---

## 5. Runtime Components

Runtime components are the parts that actively run Hermes conversations, delivery loops, UI backends, or scheduled work.

| Component | Path | Purpose | Responsibilities |
|---|---|---|---|
| Agent runtime | `run_agent.py`, `agent/` | Main conversation engine | Prompt assembly, tool dispatch, provider routing, memory, compression, learning, turn management |
| CLI runtime | `cli.py`, `hermes_cli/main.py`, `hermes_cli/subcommands/` | Interactive terminal application and operational command entry points | User interaction, setup, auth, config, session control, gateway bootstrap |
| Gateway runtime | `gateway/run.py` and related modules | Messaging hub for external platforms | Platform polling/webhooks, delivery, status, restart guards, stream routing |
| TUI backend runtime | `tui_gateway/` | Python process backing the terminal UI | Session management, JSON-RPC, agent interaction, command dispatch |
| TUI frontend runtime | `ui-tui/src/` | Ink-based terminal interface | Rendering, chat interaction, slash commands, live activity |
| Desktop runtime | `apps/desktop/` | Electron/React app | Desktop chat, state management, backend connection, session and UI orchestration |
| Web dashboard runtime | `web/` | Browser-based dashboard | Browser UI, build/runtime shell, static front-end delivery |
| Scheduler runtime | `cron/` | Timed execution and job dispatch | Cron jobs, suggestions, lifecycle guards, delivery |
| ACP runtime | `acp_adapter/` | Agent Client Protocol server and adapter | Protocol handling, session bridging, permissions, event emission |
| Container runtime | `docker/` | Container launch and lifecycle support | Entrypoints, init scripts, profile reconciliation |
| Scripted operations | `scripts/` | Build, install, diagnostics, test automation | Installer flows, validation, release, profiling, maintenance |

---

## 6. Platform Components

Platform components are the implementations that attach Hermes to a specific user-facing surface or external service.

### Messaging Platforms

| Platform | Path | Purpose | Architectural Type |
|---|---|---|---|
| Telegram | `gateway/platforms/telegram.py` and `plugins/platforms/telegram/` | Telegram messaging integration | Platform Integration |
| Slack | `gateway/platforms/` and `plugins/platforms/slack/` | Slack messaging integration | Platform Integration |
| Discord | `plugins/platforms/discord/` | Discord adapter and voice helpers | Platform Integration |
| WhatsApp | `gateway/platforms/whatsapp*`, `plugins/platforms/whatsapp/` | WhatsApp delivery and cloud integration | Platform Integration |
| Signal | `gateway/platforms/signal.py` | Signal adapter and rate limiting | Platform Integration |
| Matrix | `gateway/platforms/` and `plugins/platforms/matrix/` | Matrix delivery support | Platform Integration |
| Email | `plugins/platforms/email/` | Email gateway integration | Platform Integration |
| Teams | `plugins/platforms/teams/` and `plugins/teams_pipeline/` | Microsoft Teams adapter and pipeline support | Platform Integration |
| Feishu | `gateway/platforms/`, `plugins/platforms/feishu/` | Feishu platform integration | Platform Integration |
| WeCom / Weixin | `gateway/platforms/weixin.py`, `plugins/platforms/wecom/` | Tencent enterprise chat integrations | Platform Integration |
| Google Chat | `plugins/platforms/google_chat/` | Google Chat adapter | Platform Integration |
| Home Assistant | `gateway/platforms/`, `plugins/platforms/homeassistant/` | Home Assistant messaging / callback integration | Platform Integration |
| SMS / NTFY / IRC / Line / Mattermost / Raft / SimpleX / Photon / Dingtalk | `plugins/platforms/*` | Additional channel-specific adapters | Platform Integration |

### UI Platforms

| Platform | Path | Purpose | Architectural Type |
|---|---|---|---|
| CLI | `cli.py`, `hermes_cli/` | Primary terminal interaction surface | Runtime Component |
| TUI | `ui-tui/`, `tui_gateway/` | Full-screen terminal interface | Runtime Component |
| Desktop | `apps/desktop/` | Electron desktop client | Runtime Component |
| Web dashboard | `web/`, `hermes_cli/web_server.py` | Browser-based interface and PTY-backed terminal view | Runtime Component |

### External Service Platforms

| Service Area | Path | Purpose | Architectural Type |
|---|---|---|---|
| Model providers | `plugins/model-providers/`, `agent/`, `providers/` | Provider backends and model routing | Platform Integration / Framework Component |
| Memory providers | `plugins/memory/`, `agent/memory_*` | Persistent memory backends | Platform Integration / Business Logic |
| Image generation providers | `plugins/image_gen/`, `agent/image_gen_*`, `tools/image_generation_tool.py` | Image generation backends | Platform Integration |
| Browser backends | `plugins/browser/`, `tools/browser_*` | External browser automation and retrieval | Platform Integration |
| Observability backends | `plugins/observability/` | Telemetry and tracing adapters | Platform Integration |
| MCP servers | `optional-mcps/`, `tools/mcp_*`, `hermes_cli/mcp_*` | External structured tool servers | Infrastructure / Integration |

---

## 7. Plugin Components

Hermes uses plugins to keep niche, provider-specific, or third-party capabilities out of the core runtime.

### Plugin Architecture

- Plugins are packaged as self-contained directories under `plugins/`.
- Most plugin bundles include a `plugin.yaml` manifest and an `__init__.py` entrypoint.
- Plugins may expose runtime adapters, dashboard hooks, skills, or provider integrations.
- The plugin system is organized by domain, such as memory, platforms, model providers, browser tooling, observability, and specialized workflows.
- Some plugin families include documentation, tests, dashboards, or helper modules beside the plugin manifest.

### Plugin Families

| Family | Path | Primary Purpose |
|---|---|---|
| Memory plugins | `plugins/memory/` | Optional persistent memory providers and user memory backends |
| Model provider plugins | `plugins/model-providers/` | Optional inference backends and provider-specific routing |
| Platform plugins | `plugins/platforms/` | Channel adapters for messaging and enterprise platforms |
| Browser plugins | `plugins/browser/` | Browser automation and external browser services |
| Image generation plugins | `plugins/image_gen/` | Pluggable image generation backends |
| Observability plugins | `plugins/observability/` | External tracing/logging/metrics integrations |
| Dashboard auth plugins | `plugins/dashboard_auth/` | Authentication policies for dashboard deployments |
| Cron providers | `plugins/cron_providers/` | Alternative scheduler providers |
| Specialized plugins | `plugins/google_meet/`, `plugins/teams_pipeline/`, `plugins/spotify/`, `plugins/security-guidance/`, `plugins/disk-cleanup/` | Focused, domain-specific capabilities |

### Optional Capability Packs

| Folder | Role |
|---|---|
| `optional-skills/` | Theme-based skill bundles that can be surfaced selectively |
| `optional-mcps/` | Optional MCP server manifests for external tooling |

---

## 8. Infrastructure Components

Infrastructure components provide the operational substrate that Hermes runs on.

| Component | Path | Purpose | Major Dependencies |
|---|---|---|---|
| Persistence | `hermes_state.py`, `cron/*`, `gateway/session.py`, `gateway/rich_sent_store.py`, `plugins/*/store.py` | Session storage, state tracking, caches, and delivery state | SQLite, filesystem, runtime state models |
| Configuration | `hermes_cli/config.py`, `gateway/config.py`, `hermes_constants.py`, `cli-config.yaml.example` | Profile-aware settings and runtime configuration | YAML, environment variables, setup flows |
| Logging | `hermes_logging.py`, `gateway/*`, `scripts/*` | Application and gateway logging support | Python logging, file rotation, platform-specific handlers |
| Gateway relay | `gateway/relay/` | Transport layer for gateway communications | WebSocket/stdio adapters, auth, descriptors |
| Tool execution | `tools/tool_executor.py`, `tools/managed_tool_gateway.py`, `tools/tool_backend_helpers.py` | Tool dispatch and backend mediation | Tool registry, environment backends, approvals |
| Environment execution | `tools/environments/` | Run-time shell/session backends | Local shell, Docker, SSH, Modal, Daytona, Singularity |
| Packaging and distribution | `setup.py`, `pyproject.toml`, `packaging/`, `uv.lock`, `package-lock.json` | Build and distribution controls | Python packaging, Node workspaces, lockfiles |
| Container and service support | `docker/`, `scripts/install.*`, `scripts/run_tests.sh` | Deployment and installer lifecycle | Shell, system services, container init |
| Static assets | `assets/`, `gateway/assets/`, `plugins/**/dashboard/` | UI and branding resources | Frontend and docs consumers |

---

## 9. Configuration Components

### Configuration Sources

Hermes configuration is spread across a few controlled sources:

- `~/.hermes/config.yaml` for behavioral and runtime settings.
- `~/.hermes/.env` for secrets and credentials.
- Repository examples such as `cli-config.yaml.example`.
- Plugin manifests such as `plugin.yaml` for package-local configuration.
- Localization and UI configuration files for platform-specific presentation.

### Loading and Management

| Area | Path | Role |
|---|---|---|
| Core configuration loading | `hermes_cli/config.py`, `gateway/config.py` | Reads and resolves runtime settings |
| Environment bridging | `hermes_cli/env_loader.py`, `agent/credential_sources.py`, `agent/secret_sources/` | Loads environment and secret sources |
| Profile-aware paths | `hermes_constants.py`, `hermes_cli/profiles.py`, `hermes_cli/profile_distribution.py` | Resolves where config and state live per profile |
| CLI setup and migration | `hermes_cli/setup.py`, `hermes_cli/migrate.py`, `hermes_cli/cli_agent_setup_mixin.py` | Initializes and migrates configuration |
| Platform setup flows | `hermes_cli/setup_whatsapp_cloud.py`, `hermes_cli/memory_setup.py`, `hermes_cli/model_setup_flows.py` | Handles domain-specific configuration workflows |
| Tool and provider setup | `hermes_cli/tools_config.py`, `hermes_cli/provider_catalog.py`, `hermes_cli/model_catalog.py` | Maps config to available capabilities |

### Configuration Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Example CLI config | `cli-config.yaml.example` | Baseline user configuration template |
| Locale catalogs | `locales/*.yaml` | Translation and UI text resources |
| Plugin manifests | `plugins/**/plugin.yaml` | Declarative plugin metadata |
| Optional MCP manifests | `optional-mcps/*/manifest.yaml` | Optional external tool server definitions |

---

## 10. Dependency Overview

### Primary Dependency Flow

```text
Entry Points
  ├─ CLI / TUI / Desktop / Web / Gateway / ACP / Cron
  ↓
Runtime Orchestration
  ├─ agent/
  ├─ hermes_cli/
  ├─ gateway/
  ├─ tui_gateway/
  ├─ cron/
  └─ acp_adapter/
  ↓
Framework Layer
  ├─ providers/
  ├─ tools/
  ├─ transports/
  ├─ session/state/config helpers
  └─ plugin loader and command registries
  ↓
Capability Layer
  ├─ skills/
  ├─ plugins/
  ├─ optional-skills/
  └─ optional-mcps/
  ↓
Business Logic and Integrations
  ├─ model routing
  ├─ memory
  ├─ browser
  ├─ messaging platforms
  ├─ cron jobs
  └─ external services
  ↓
Persistence / Infrastructure
  ├─ SQLite / session stores
  ├─ filesystem state
  ├─ logs
  ├─ container hooks
  └─ packaging / deployment scripts
```

### Simplified Layer Flow

```text
Gateway / UI / CLI
↓
Runtime Orchestration
↓
Tools / Providers / Transports
↓
Plugins / Skills / Optional Packs
↓
Persistence / Logging / Deployment
```

---

## 11. Initial Architectural Observations

### Good Design Decisions

- The repository separates core agent logic from platform adapters and optional capabilities.
- The plugin model keeps niche or third-party integrations out of the core waist.
- The same agent runtime can be reached through multiple surfaces without duplicating the business logic.
- Tooling is centralized behind registries and manifests, which makes discovery and composition consistent.
- UI surfaces are split cleanly between Python backends and TypeScript frontends.

### Tight Coupling Areas

- CLI, gateway, and tool registries share central command and tool metadata, so changes there affect multiple runtime surfaces.
- Session, config, and profile handling is reused broadly across CLI, gateway, and UI backends.
- Platform adapters depend on a common delivery and event pipeline, which concentrates integration behavior in shared gateway modules.

### Generic Components

- Provider abstractions
- Tool registries and execution layers
- Session and configuration helpers
- Environment backends
- Shared JSON-RPC helpers between TypeScript applications

### Platform-Specific Components

- Messaging adapters in `gateway/platforms/` and `plugins/platforms/`
- Desktop application in `apps/desktop/`
- Terminal UI in `ui-tui/`
- Web dashboard in `web/`
- ACP adapter in `acp_adapter/`

### Possible Extension Points

- New platform adapters through the gateway and plugin platform folders
- New model or memory providers through plugin packages
- New tools through the shared tool registry and environment abstractions
- New UI capabilities through the separate TypeScript applications
- New scheduled behaviors through cron catalogs and scheduler modules

---

## Major Files Worth Noting

| File | Purpose | Layer |
|---|---|---|
| `run_agent.py` | Main agent conversation entrypoint and orchestration core | Runtime Component |
| `cli.py` | Primary CLI application | Runtime Component |
| `gateway/run.py` | Gateway process entrypoint | Runtime Component |
| `model_tools.py` | Tool discovery and function-call handling | Framework Component |
| `toolsets.py` | Toolset definition catalog | Framework Component |
| `hermes_state.py` | Session store and persistence | Infrastructure |
| `hermes_constants.py` | Shared path and home-directory resolution | Configuration |
| `hermes_logging.py` | Log setup and profile-aware logging paths | Infrastructure |
| `batch_runner.py` | Batch execution and trajectory generation | Runtime Component |
| `mcp_serve.py` | MCP server launcher surface | Infrastructure / Integration |
| `hermes_bootstrap.py` | Bootstrap and environment initialization | Infrastructure |
| `trajectory_compressor.py` | Trajectory compaction and dataset preparation | Business Logic / Utility |
| `setup.py` | Python packaging entrypoint | Infrastructure |
| `pyproject.toml` | Build metadata and dependency specification | Configuration |
| `package.json` | Node workspace metadata and scripts | Configuration |

---

## Folder Classification Summary

| Folder | Classification |
|---|---|
| `agent/` | Runtime Component, Framework Component, Business Logic |
| `apps/` | Runtime Component, Platform UI |
| `assets/` | Utility, Configuration asset |
| `cron/` | Runtime Component, Infrastructure |
| `datagen-config-examples/` | Configuration |
| `docker/` | Infrastructure |
| `docs/` | Documentation |
| `gateway/` | Runtime Component, Platform Integration, Infrastructure |
| `hermes_cli/` | Runtime Component, Framework Component |
| `infographic/` | Documentation asset |
| `locales/` | Configuration |
| `nix/` | Infrastructure, Configuration |
| `optional-mcps/` | Plugin Component, Integration Metadata |
| `optional-skills/` | Plugin Component |
| `packaging/` | Infrastructure |
| `plugins/` | Plugin Component |
| `providers/` | Framework Component |
| `scripts/` | Infrastructure, Utility |
| `skills/` | Business Logic, Capability layer |
| `tests/` | Testing |
| `tools/` | Framework Component, Runtime Component |
| `tui_gateway/` | Runtime Component, Infrastructure |
| `ui-tui/` | Runtime Component, Platform UI |
| `web/` | Runtime Component, Platform UI |
| `website/` | Documentation |

