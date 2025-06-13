# System Diagram

To better explain this app, let us view a Systems Diagram Overview

```mermaid
flowchart TD
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
  end

  sbq -.-> deploy
```

Features:

1. External systems publishing to Azure Service Bus Queue using Python.
2. The Kubernetes Ingress routes user traffic to the Service, which routes to the Deployment (Python Flask app).
3. The Deployment (Python Flask app) both polls the Service Bus Queue and reads logs to the external PostgreSQL database in Aiven.


<!--
https://mermaid.live/edit#pako:eNqdUVtvmzAU_iuW-9JKCeGWG5oqZc2kVesDXSJNGuTBhhNAA-z6kiaN8t9nIGSJpr3syfjw3fydI05YCjjA25K9JzkRCq2XcY2Q1DQThOdo8aEFNBMzo29Re0UrELsiAfRZS_SqQcOmQUCdxvUN-ctegahJ2fFhr7imUT9Eq4NUUH2iYvQYHlTOahRqWhYyB7G5ZqDhEMV4ZeRRyTJUgZQkgxib-eN_hFoUO6g7_ZRG9yGTKhOwen1BS6IIJRIe_sGM8TdNTXZQINFTqU18EeNOqqiNiJTRc3e2r0qpyUs4txT_ZfH386PkLonOWVvU3VnpObw7I1LgJTtEy_aooFZntReWLThHIUs3N6ZdQV_X6xDd-743mtkPfTu75GJ6jRrb9gXTuV07d8jvQNLRD1EoaGqXPZr-jQxZWUq0ZaLfjfyznNsm6RsaWhdPPMCZKFIcKKFhgCsQFWmu-NiAY6xyqMyeA_OZwpboUjVtnwyNk_onY1XPFExnOQ62pJTmpnlKFCwLYrZWXabCpADxxHStcOCMvVYEB0e8x4HnWp7jju3pxJ17c7_5eTAgx7MmU9_1XH_mzh3bmZwG-KO1ta3ZtOnQdm3Xd6b22D_9Bj-VDvA
--->