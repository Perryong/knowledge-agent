# MCP Protocol — Primary Source Dump
Fetched: 2026-06-13
Source: modelcontextprotocol.io (direct fetch — high confidence)

## Key Facts

### Current Spec Version
- Spec version tag: 2025-11-25 (last published spec)
- Protocol version string in examples: "2025-06-18" (likely upcoming or latest negotiated version)
- Roadmap last updated: 2026-03-05

### Governance
- MCP is now governed under Linux Foundation (LF Projects, LLC)
- Apache 2.0 license for code/spec; CC-BY 4.0 for documentation
- Not Anthropic-controlled: membership/roles are individual, not company-reserved
- Lead Maintainers (BDFL): David Soria Parra, Den Delimarsky
- Core Maintainers: Peter Alexander, Caitie McCaffrey, Kurtis Van Gent, Clare Liguori, Paul Carleton, Nick Cooper, Nick Aldridge
- Core Maintainer group meets bi-weekly

### Ecosystem Adoption
- Supported clients: Claude (web), Claude Desktop, VS Code GitHub Copilot, Cursor, ChatGPT, Goose (Block), Postman, MCPJam, Archestra.AI
- Registry backed by: Anthropic, GitHub, PulseMCP, Microsoft
- Registry is in preview (as of fetch date)
- SDKs exist for multiple languages with a tiering system (SEP-1730)

### SEP Activity (41 Final SEPs as of 2026-06-13)
Most recent Finals:
- SEP-2663: Tasks Extension (2026-04-27) — async/durable tool execution
- SEP-2596: Feature Lifecycle and Deprecation Policy (2026-04-17)
- SEP-2577: Deprecate Roots, Sampling, and Logging (2026-04-14)
- SEP-2575: Make MCP Stateless (drafted 2025-06-18, finalized later)
- SEP-2567: Sessionless MCP via Explicit State Handles (2026-03-11)
- SEP-2322: Multi Round-Trip Requests (2026-02-03)
- SEP-1865: MCP Apps — Interactive UI for MCP (2025-11-21)
- SEP-1686: Tasks (2025-10-20)
- SEP-1577: Sampling With Tools (2025-09-30)
- SEP-414: OpenTelemetry Trace Context Propagation (2025-04-25)

### Transport Mechanisms
1. Stdio transport: for local process communication (no network overhead) — primary for local agents
2. Streamable HTTP: HTTP POST + optional SSE for remote servers; supports OAuth bearer tokens

### Core Primitives
Server exposes: Tools, Resources, Prompts
Client exposes: Sampling, Elicitation, Logging
Experimental: Tasks (async durable operations)

### Tasks Extension (SEP-2663, Final 2026-04-27)
- Returns durable task handle instead of blocking
- States: working → input_required → completed/failed/cancelled
- Supports crash resilience (task ID persists across reconnects)
- Mid-flight user input via tasks/update
- Server-push via notifications/tasks (no polling needed if server supports it)
- Use cases: CI pipelines, batch processing, human-in-loop workflows, external job systems

### Roadmap Priority Areas (as of 2026-03-05)
1. Transport Evolution and Scalability (stateless horizontal scaling, MCP Server Cards via .well-known)
2. Agent Communication (retry semantics, expiry policies for Tasks)
3. Governance Maturation (Contributor Ladder, delegation model, charter templates)
4. Enterprise Readiness (audit trails, enterprise-managed auth, gateway/proxy patterns, config portability)

### On the Horizon (not yet prioritized)
- Triggers and Event-Driven Updates (webhooks/server push)
- Result Type Improvements (streaming results, reference-based large payloads)
- Security & Authorization (DPoP SEP-1932, Workload Identity Federation SEP-1933)
- Extensions Ecosystem (Skills primitive for composed capabilities)

### Tool Calling in MCP
- Model-controlled (LLM decides which tools to invoke based on context)
- Tools defined with JSON Schema inputSchema and outputSchema
- outputSchema enables structured tool results for type-safe agent pipelines
- Tool execution errors returned as isError:true (actionable for LLM self-correction)
- taskSupport per-tool: "forbidden" | "optional" | "required"

### Extensions System
Official extensions: MCP Apps (UI), OAuth Client Credentials, Enterprise-Managed Authorization
Experimental extensions: incubated in experimental-ext- repos, require WG association
Extension negotiation: capability handshake at init time, always opt-in
