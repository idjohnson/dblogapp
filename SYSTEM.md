# System Diagram

To better explain this app, let us view a Systems Diagram Overview

```mermaid
flowchart TD
  subgraph Google
    idp[Google Federated IdP]
  end

  subgraph Azure
    sbq[Azure Service Bus Queue]
  end

  subgraph External
    extpub[External System<br/>Python Publisher]
    extpub -- "Send log message" --> sbq[Azure Service Bus Queue]
  end

  subgraph Aiven
    db[(PostgreSQL Database)]
  end

  subgraph "Kubernetes Cluster"
    ingress[Ingress<br/>dblogapp.tpk.pw]
    svc[Service<br/>#ClusterIP#]
    deploy[Deployment<br/>dbLogApp Pod]
    ingress -- "HTTP (443/80)" --> svc
    svc -- "HTTP (5000)" --> deploy
    deploy -- "Read/Write logs" --> db
    deploy -- "Polls for messages" --> sbq
    deploy -- "Federated Oauth" --> idp
  end

  sbq -.-> deploy
  idp -.-> deploy
```

Features:

1. External systems publishing to Azure Service Bus Queue using Python.
2. The Kubernetes Ingress routes user traffic to the Service, which routes to the Deployment (Python Flask app).
3. The Deployment (Python Flask app) both polls the Service Bus Queue and reads logs to the external PostgreSQL database in Aiven.

