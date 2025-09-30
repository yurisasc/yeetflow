# Runtime Architecture

This document describes the intended, declarative architecture for the runtime layer.
It is designed around four key concepts:

- Command/Registry for actions
- Executor with middleware for cross-cutting concerns
- Coordinator for pause/resume orchestration
- Flow Engine as the single orchestration entry point

## Components

```mermaid
flowchart LR
  subgraph Controller/API
    C[RunsController / Service]
  end

  subgraph Runtime Core
    RC[RunContext]
    FSM[RunStateMachine]
    Steps[Steps Parser]
    CP[Checkpoint Memento]
  end

  subgraph Engine
    FE[FlowEngine]
    EX[ActionExecutor]
    MW[Middleware Chain]
    MW --> MWEvents[EventMiddleware]
    MW --> MWLog[Logging]
    MW --> MWError[ErrorScreenshot]
    EE[EventEmitter]
  end

  subgraph Adapters
    AF[AgentFactory]
    SP["SessionProvider<br/>(SteelAdapter)"]
    AG[Agent]
  end

  subgraph Services/Infra
    RS[RunService]
    ES[EventService]
    DB[(DB)]
  end

  C -->|"start(run, manifest, input)"| FE
  FE --> SP
  FE --> AF --> AG
  FE --> EE
  FE --> RC
  FE --> FSM
  FE --> Steps
  FE --> EX --> MW
  EX --> AG
  EE --> ES --> DB
  FE --> RS --> DB
```

## Sequence: Start → Checkpoint → Resume → Complete

```mermaid
sequenceDiagram
  participant C as Controller
  participant FE as FlowEngine
  participant SP as SessionProvider
  participant AF as AgentFactory
  participant AG as Agent
  participant EX as ActionExecutor + Middleware
  participant EE as EventEmitter
  participant RS as RunService

  C->>FE: start(runId, manifest, input)
  FE->>SP: attach_to_session(runId)
  FE->>AF: create(runId)
  AF-->>FE: provide Agent
  FE->>AG: start()
  FE->>RS: update_run(status="running")
  FE->>EE: emit_run_started()
  loop each step
    FE->>FE: parse step
    alt action step
      FE->>EX: execute(step, context)
      EX->>EX: middlewares before
      EX->>AG: perform action
      EX->>EX: middlewares after
    else checkpoint step
      FE->>EE: emit_checkpoint_reached(...)
      FE->>RS: update_run(status="awaiting_input")
      FE->>FE: snapshot_context()
      FE-->>C: pause (await resume)
      C->>FE: resume(runId, latest_input)
      FE->>FE: restore_context()
      FE->>FE: merge_inputs()
      FE->>RS: update_run(status="running")
    end
  end
  FE->>RS: update_run(status="completed")
  FE->>EE: emit_run_completed()
  FE->>AG: stop()
  FE->>SP: close_session()
```

## Developer Experience (DX)

- **Add an action**: implement `Action.execute(context, agent, events)` and `registry.register("my_action", factory)` in `app/runtime/actions/`.
- **Start a flow**: Controller calls `FlowEngine.start(run, manifest, input)`.
- **Resume a flow**: Controller calls `FlowEngine.resume(run_id, latest_input)`; engine restores memento and continues.
- **Cross-cutting concerns**: add a middleware to `engine/middleware.py`.
