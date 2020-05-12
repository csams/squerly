Overview
========
Make digging around in nests of python dicts and lists less tedious.

Motivation
----------
Say you have a pile of yaml docs like this (some data snipped for brevity):

Scheduler:
```yaml
apiVersion: operator.openshift.io/v1
kind: KubeScheduler
metadata:
  annotations:
    release.openshift.io/create-only: 'true'
  creationTimestamp: 2019-09-09 06:16:52+00:00
  generation: 1
  name: cluster
  resourceVersion: '20599'
  selfLink: /apis/operator.openshift.io/v1/kubeschedulers/cluster
  uid: 6a531a9d-d2c9-11e9-b8a1-005056be2a3b
spec:
  managementState: Managed
status:
  conditions:
  - lastTransitionTime: 2019-09-09 06:41:57+00:00
    status: 'False'
    type: MonitoringResourceControllerDegraded
  latestAvailableRevision: 6
  latestAvailableRevisionReason: ''
  nodeStatuses:
  - currentRevision: 6
    nodeName: control-plane-0
  - currentRevision: 6
    nodeName: control-plane-2
  - currentRevision: 5
    nodeName: control-plane-1
    targetRevision: 6
  readyReplicas: 0
```

ControllerManager
```yaml
apiVersion: operator.openshift.io/v1
kind: KubeControllerManager
metadata:
  annotations:
    release.openshift.io/create-only: 'true'
  creationTimestamp: 2019-09-09 06:16:52+00:00
  generation: 3
  name: cluster
  resourceVersion: '17773'
  selfLink: /apis/operator.openshift.io/v1/kubecontrollermanagers/cluster
  uid: 6a4badba-d2c9-11e9-b8a1-005056be2a3b
spec:
  logLevel: ''
  managementState: Managed
  observedConfig:
    extendedArguments:
      cloud-config:
      - /etc/kubernetes/static-pod-resources/configmaps/cloud-config/config
      cloud-provider:
      - some_cloud
      cluster-cidr:
      - 10.128.0.0/14
      cluster-name:
      - some-test-fgt78
      feature-gates:
      - ExperimentalCriticalPodAnnotation=true
      - RotateKubeletServerCertificate=true
      - SupportPodPidsLimit=true
      - LocalStorageCapacityIsolation=false
      service-cluster-ip-range:
      - 172.30.0.0/16
    serviceServingCert:
      certFile: /etc/kubernetes/static-pod-resources/configmaps/service-ca/ca-bundle.crt
  operatorLogLevel: ''
status:
  - lastTransitionTime: 2019-09-09 06:41:57+00:00
    status: 'False'
    type: MonitoringResourceControllerDegraded
  latestAvailableRevision: 6
  latestAvailableRevisionReason: ''
  nodeStatuses:
  - currentRevision: 6
    nodeName: control-plane-2
  - currentRevision: 6
    nodeName: control-plane-1
  - currentRevision: 6
    nodeName: control-plane-0
  readyReplicas: 0
  ```

APIServer
```yaml
apiVersion: operator.openshift.io/v1
kind: KubeAPIServer
metadata:
  annotations:
    release.openshift.io/create-only: 'true'
  creationTimestamp: 2019-09-09 06:16:52+00:00
  generation: 4
  name: cluster
  resourceVersion: '20635'
  selfLink: /apis/operator.openshift.io/v1/kubeapiservers/cluster
  uid: 6a5ecbb4-d2c9-11e9-b8a1-005056be2a3b
spec:
  logLevel: ''
  managementState: Managed
  observedConfig:
    admission:
      pluginConfig:
        network.openshift.io/ExternalIPRanger:
          configuration:
            allowIngressIP: false
            apiVersion: network.openshift.io/v1
            kind: ExternalIPRangerAdmissionConfig
        network.openshift.io/RestrictedEndpointsAdmission:
          configuration:
            apiVersion: network.openshift.io/v1
            kind: RestrictedEndpointsAdmissionConfig
            restrictedCIDRs:
            - 10.128.0.0/14
            - 172.30.0.0/16
    apiServerArguments:
      cloud-config:
      - /etc/kubernetes/static-pod-resources/configmaps/cloud-config/config
      cloud-provider:
      - some_cloud
      feature-gates:
      - ExperimentalCriticalPodAnnotation=true
      - RotateKubeletServerCertificate=true
      - SupportPodPidsLimit=true
      - LocalStorageCapacityIsolation=false
    authConfig:
      oauthMetadataFile: /etc/kubernetes/static-pod-resources/configmaps/oauth-metadata/oauthMetadata
    corsAllowedOrigins:
    - //127\.0\.0\.1(:|$)
    - //localhost(:|$)
    imagePolicyConfig:
      internalRegistryHostname: image-registry.openshift-image-registry.svc:5000
    servicesSubnet: 172.30.0.0/16
    servingInfo:
      namedCertificates:
      - certFile: /etc/kubernetes/static-pod-certs/secrets/localhost-serving-cert-certkey/tls.crt
        keyFile: /etc/kubernetes/static-pod-certs/secrets/localhost-serving-cert-certkey/tls.key
      - certFile: /etc/kubernetes/static-pod-certs/secrets/service-network-serving-certkey/tls.crt
        keyFile: /etc/kubernetes/static-pod-certs/secrets/service-network-serving-certkey/tls.key
      - certFile: /etc/kubernetes/static-pod-certs/secrets/external-loadbalancer-serving-certkey/tls.crt
        keyFile: /etc/kubernetes/static-pod-certs/secrets/external-loadbalancer-serving-certkey/tls.key
      - certFile: /etc/kubernetes/static-pod-certs/secrets/internal-loadbalancer-serving-certkey/tls.crt
        keyFile: /etc/kubernetes/static-pod-certs/secrets/internal-loadbalancer-serving-certkey/tls.key
    storageConfig:
      urls:
      - https://etcd-0.example.com:2379
      - https://etcd-1.example.com:2379
      - https://etcd-2.example.com:2379
  operatorLogLevel: ''
  unsupportedConfigOverrides: null
status:
  conditions:
  - lastTransitionTime: 2019-09-09 06:34:21+00:00
    message: 3 nodes are active; 1 nodes are at revision 2; 2 nodes are at revision 5
    status: 'True'
    type: Available
  - lastTransitionTime: 2019-09-09 06:21:53+00:00
    message: 1 nodes are at revision 2; 2 nodes are at revision 5
    status: 'True'
    type: Progressing
  latestAvailableRevision: 5
  latestAvailableRevisionReason: ''
  nodeStatuses:
  - currentRevision: 2
    nodeName: control-plane-1
    targetRevision: 5
  - currentRevision: 5
    nodeName: control-plane-0
  - currentRevision: 5
    nodeName: control-plane-2
  readyReplicas: 0
  ```

And you want to know which ones mention node statuses not at the latest
revision.

You could do it like this:
```python
import yaml

_Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def load(path):
    with open(path) as f:
        return yaml.load(f, Loader=_Loader)


def get_stale(resources):
    results = []
    for doc in resources:
        for status in doc.get("status", {}).get("nodeStatuses", []):
            if "targetRevision" in status and status["targetRevision"] != status["currentRevision"]:
                results.append(doc)
    return results


scheduler = load("scheduler.yaml")
cm = load("controller_manager.yaml")
api = load("api_server.yaml")

stale = get_stale([scheduler, cm, api])
```

Or you could do it like this:
```python
import yaml
from querylous import List, convert, Queryable

_Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def load(path):
    with open(path) as f:
        return yaml.load(f, Loader=_Loader)


scheduler = convert(load("scheduler.yaml"))
cm = convert(load("controller_manager.yaml"))
api = load("api_server.yaml")
docs = Queryable(List([scheduler, cm, api]))

stale = docs.status.nodeStatuses.where(lambda s: s.currentRevision != s.targetRevision).roots
```

Or better yet, run `./analyze.py must-gather.local.12345/` and get access to
_every_ collected resource in the archive:
```python
In [1]: stale = conf.status.nodeStatuses.where(lambda s: s.currentRevision != s.targetRevision).roots

In [2]: stale.kind

Out[2]: 
- KubeScheduler
- KubeAPIServer

In [3]: conf.find(("message", matches("Perm")))

Out[3]:
- 'rm: cannot remove ''/etc/cni/net.d/80-openshift-network.conf'': Permission denied

  '
- 'rm: cannot remove ''/etc/cni/net.d/80-openshift-network.conf'': Permission denied

  '
- '+ source /run/etcd/environment

  /bin/sh: line 3: /run/etcd/environment: Permission denied

  '

In [8]: conf.find(("message", matches("Perm"))).upto("items").metadata.name

Out[8]: 
- sdn-7llq6
- etcd-member-control-plane-0
```
