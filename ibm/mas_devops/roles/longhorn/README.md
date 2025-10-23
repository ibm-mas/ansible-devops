Longhorn provides a single solution to fulfil both the `ReadWriteMany` and `ReadWriteOnce` storage requirements for Maximo Application Suite.

> Longhorn is a lightweight, reliable and easy-to-use distributed block storage system for Kubernetes.
>
> Longhorn is free, open source software. Originally developed by Rancher Labs, it is now being developed as a incubating project of the Cloud Native Computing Foundation.

The Longhorn UI will be available at `https://longhorn-ui-longhorn-system.{clusterdomain}` (supporting authenciation via OpenShift OAuth).

More information:
- [What is Longhorn?](https://longhorn.io/docs/latest/what-is-longhorn/)
- [Longhorn Helm Chart Settings](https://longhorn.io/docs/latest/references/helm-values/)
- [Longhorn on OpemShift Readme](https://github.com/longhorn/longhorn/blob/master/chart/ocp-readme.md)



```
oc -n longhorn-system get deployments
NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
csi-attacher               3/3     3            3           38m
csi-provisioner            3/3     3            3           38m
csi-resizer                3/3     3            3           38m
csi-snapshotter            3/3     3            3           38m
longhorn-driver-deployer   1/1     1            1           40m
longhorn-ui                2/2     2            2           40m
```

Two storage classes will be set up automatically, Maximo Application Suite uses dynamic provisioning and as such will not use the `longhorn-static` storage class:

```
oc get storageclass | grep longhorn
longhorn (default)          driver.longhorn.io   Delete          Immediate           true                   40m
longhorn-static             driver.longhorn.io   Delete          Immediate           true                   40m
```

Role Variables
-------------------------------------------------------------------------------

### longhorn_namespace
Define the namespace where Longhorn will be installed.

* Optional
* Environment Variable: `LONGHORN_NAMESPACE`
* Default Value: `longhorn-system`

### longhorn_replica_count
The replica count in Longhorn determines the number of copies of a volume's data stored across different nodes in a Kubernetes cluster, which directly impacts data availability and resilience. The default replica count of 3 allows the system to tolerate up to two replica failures while maintaining data integrity, but in development system you may prefer to set this to 1 to sacrifice resiliance in favour of reduced storage requirements.

* Optional
* Environment Variable: `LONGHORN_REPLICA_COUNT`
* Default Value: `3`
