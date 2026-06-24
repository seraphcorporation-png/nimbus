# CarNimbus Agent Authentication (auth.md)

Welcome to the CarNimbus Agent API. We are an "Agent-Ready" platform allowing partner sub-agents to interface with our digital dealership transaction layer securely.

## Authentication Methods

We support **IDJAG (Identity Assertion JWT Authorization Grant)** for autonomous service-to-service authentication.

### Supported Proofs
- `idjag_jwt`: A signed JWT asserting your agent's identity and capabilities.
- `api_key`: A traditional static bearer token (for human-in-the-loop fallback).

### IDJAG Endpoint Flow
1. Mint an IDJAG JWT via your internal identity issuer.
2. Ensure the JWT contains the `email_verified: true` claim, representing human trust.
3. POST your IDJAG to `https://carnimbus.com/api/auth/idjag` to exchange it for a scoped API Access Token.

### Scopes
When asserting your capabilities, the following scopes are recognized by CarNimbus:
- `inventory.read`: Read real-time vehicle availability.
- `deals.calculate`: Run hypothetical constraints through the Matching Engine.
- `appointments.book`: Schedule a test drive via the Cross-Platform Calendar Sync.

## Rate Limiting
Autonomous agent traffic is strictly segmented from consumer traffic. Agents are limited to `100 requests / minute` per `agent_id`.
