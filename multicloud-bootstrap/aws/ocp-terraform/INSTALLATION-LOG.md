### Checking the cp4d service installation status:
* To check the cp4d service installation status, follow these steps:
  1. Click on the openshift console url and login with the `openshift-username` and `openshift-password` that you provided in the `variables.tf` file.
  2. Check operator pod statuses `oc get pods -n ibm-common-services`
  2. heck service pod statuses  `oc get pods -n zen`
  
