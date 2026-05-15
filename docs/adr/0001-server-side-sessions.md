# Server-side stateful sessions for Interview State

REST APIs are conventionally stateless, but this backend maintains server-side in-memory sessions keyed by UUID. We chose this because the Interview requires tracking which fields have been collected and which question is currently pending — state that belongs to the Agent, not the Customer. Putting Interview State on the client would mean the frontend must understand and enforce the interview logic, coupling it to business rules it shouldn't own. Sessions are cleaned up on Interview completion or explicit close.

## Considered Options

- **Client sends full message history each request** — backend stays stateless, but Interview State tracking (field completion, pending question) would have to live on the client or be reconstructed from the history on every request.
- **Server-side in-memory sessions (chosen)** — Interview State lives where it belongs, alongside the conversation history, without leaking logic to the frontend.

## Consequences

The backend is stateful. It cannot be horizontally scaled without a shared session store (e.g., Redis). Acceptable for the current scope; revisit if multi-instance deployment becomes a requirement.
