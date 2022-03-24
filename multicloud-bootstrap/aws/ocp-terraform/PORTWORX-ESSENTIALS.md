### Generating the Portworx Spec URL
* Launch the [spec generator](https://central.portworx.com/specGen/wizard)
* Select `Portworx Essentials` and press Next to continue:
![Alt text](images/essential-enterprise.png)
* Check `Use the Portworx Operator` box and select the `Portworx version` as `2.6`. For `ETCD` select `Built-in` option and then press Next:
![Alt text](images/portworx-version.png)
* Select `Cloud` for `Select your environment` option. Click on `AWS` and select `Create Using a Spec` option for `Select type of disk`.
Enter value for `Size(GB)` as `1000` and then press Next. 
![Alt text](images/cloud-platform.png)
* Leave `auto` as the network interfaces and press Next:
![Alt text](images/network-interface.png)
* Select `Openshift 4+` as Openshift version, go to `Advanced Settings`:
![Alt text](images/openshift-version.png)
* In the `Advanced Settings` tab select all three options and press Finish:
![Alt text](images/Advanced_settings.png)
* Copy Spec URL and Paste in a browser:
![Alt text](images/spec-url.png)
* Copy the Name (Cluster ID), the User ID and the OSB endpoint highlighted in red. This will be the value for the `cluster_id`, `user_id` and `osb_endpoint` variables respectively.
![Alt text](images/esse-cluster-id.png)