# FVT With Openshift Pipelines Operator

This is and work in progress experimental project. The code in this folder is not meant to be reused in for other fvt repos yet. At the moment its prepared to support fvt release. In order to make it reusable to any fvt repo or any other kind of environment, we need to solve the following issues.

- [ ] Need to find a better home for settings secret, this secret was created to fulfill information to Tasks that use ibm-mas.devops or mas-fvt ansible collections. APIKeys and Entitlement Key are wellcomed in this secret

- [ ] Need to remove configurations from settings secrets and place it in an Config Map and make it available as workspace for the Tasks that needs it. MAS config files are wellcomed here, such as BASCfg and Workspace 

- [ ] ibm-mas.devops collection needs a few minor changes to support this, would be nice to review playbooks and see if we can reduce some dependencies.

- [ ] Find a better home for pipeline runs in the image.

- [ ] Remove custom playbooks from image

- [ ] Update base image with latest ibm-mas.devops

- [ ] Decide about which image use for fvt Taks, considering it should contain mas-fvt ansible collection, does not make sense add it to the public image