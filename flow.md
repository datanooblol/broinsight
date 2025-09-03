```mermaid
flowchart TD
    BroInsight_Start! -->|default| UserInput
    UserInput -->|default| Organize
    Organize -->|select_metadata| SelectMetadata
    SelectMetadata -->|default| GenerateSQL
    GenerateSQL -->|default| Retrieve
    Retrieve -->|default| Chat
    Chat -->|default| UserInput
    Organize -->|default| Chat
    UserInput -->|exit| End
```