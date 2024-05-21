ocp_simulate_disconnected_network
===============================================================================

Our goal is to modify the hosts file on each node (worker and master) to add a bogus entry that breaks DNS resolution for all the registries that we are going to mirror.  This will simulate the cluster running in an air gap configuration, although network access will be possible elsewhere, the cluster will be unable to access the docker registries

!!! important
    The host file (on Fyre) will look something like this, this role is (for now anyway) mainly focused on simulating an air gap cluster in Fyre, it may work on other cluster providers but that can not be guaranteed and may require modifications depending on the specific way OpenShift is set up.

```bash
oc get nodes
oc debug node/node1
sh-4.4# more /host/etc/hosts
127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4
::1         localhost localhost.localdomain localhost6 localhost6.localdomain6
172.30.55.8 image-registry.openshift-image-registry.svc image-registry.openshift-image-registry.svc.cluster.local # openshift-generated-node-resolver
```


The default exclusions are:
- quay.io
- registry.redhat.io
- registry.connect.redhat.com
- gcr.io
- nvcr.io
- icr.io
- cp.icr.io
- docker-na-public.artifactory.swg-devops.com
- docker-na-proxy-svl.artifactory.swg-devops.com
- docker-na-proxy-rtp.artifactory.swg-devops.com

These can be changed by setting `airgap_network_exclusions` explicitly.
