# User Guide

## Purpose
This document provides instructions for operating the Next.js visual dashboard, running simulations, reviewing investigations, executing containment plans, and troubleshooting the Lokii Platform.

## Overview
The Lokii user interface is a Next.js-based single page application that connects to the Gateway API. It provides a visual dashboard for security analysts to triage alerts, execute simulations, review case timelines, and authorize response plans.

---

## Detailed Explanation

### 1. The Dashboard Shell
The visual UI features a sidebar navigation bar with the following modules:
- **Overview**: Displays active investigations, threat level indicators, case counters, and health statuses.
- **Investigations**: Table listing active triage items, detailing confidence, severity, and status.
- **Attack Simulator**: Panel allowing operators to trigger attack scenarios (e.g. `account_takeover`).
- **System Health**: Connection status and latency charts for system dependencies.

### 2. Standard Operations Guide

#### Running an Attack Simulation
1. Navigate to the **Attack Simulator** page in the sidebar.
2. Select a scenario (e.g., `Credential Stuffing` or `Account Takeover`).
3. Click the **Run Scenario** button.
4. Review the **Execution Trace** and the **Pipeline Progress** visualizer as the simulation executes.
5. Once completed, select the generated investigation ID to open the workspace.

#### Reviewing an Investigation Case
1. Go to the **Investigations** page in the sidebar.
2. Select an investigation row to open the workspace.
3. Use the tabs to navigate details:
   - **Timeline**: Chronological log of observed events and service actions.
   - **Evidence**: Lists extracted telemetry facts.
   - **Relationships**: Graph visualization showing connected entities.
   - **AI Reports**: Technical, executive, or compliance summaries.
   - **Response**: Containment actions (e.g. suspend account) awaiting authorization.

---

## Workflow

### Analyst Incident Response Workflow
1. **Alert Ingest**: The simulator publishes an alert candidate.
2. **Review Details**: Analyst opens the **Investigations** tab, reviewing confidence and severity.
3. **Graph Explorer**: Analyst opens the **Relationships** tab to identify the scope of compromised nodes.
4. **AI Report**: Analyst opens the **AI Reports** tab to review generated summaries.
5. **Mitigation**: Analyst reviews pending containment tasks in the **Response** tab, clicks **Approve**, and validates execution.

---

## Design Decisions
- **Unified Gateway Endpoint**: The UI connects exclusively to the API Gateway port (`8000`), protecting downstream microservices.
- **Zustand Store Caching**: Active view changes and investigation details are cached in local browser storage using a Zustand store.

## Best Practices
- **Analyze Blast Radius**: Always evaluate the node network in the **Relationships** explorer before approving containment actions.
- **Check Health Latency**: If the UI behaves unexpectedly, check the **System Health** dashboard for degraded services.

## Future Enhancements
- Support automated UI re-renders using WebSockets for real-time synchronization.
- Implement user role segregation (RBAC) within the UI layout.
