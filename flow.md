```mermaid
flowchart TB
    ROUTER -.-> CHAT
    ROUTER -.-> SQL
    ROUTER -.-> GUIDE
    CHAT --> COMPLETE
    SQL --> CHAT
    GUIDE --> COMPLETE
```