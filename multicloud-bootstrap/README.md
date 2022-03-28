# MultiCloud Bootstrap Process

This folder contains the automation required for the bootstrap process.
The scripts in this folder are not meant to be called manually unless needed for troubleshooting. These scripts are called in a specific order during the bootstrap process. The bootstrap process is called from the virtual server (aka the `bootnode`) automatically when the bootnode is created. The bootnode is a virtual server (_EC2 instance_ in AWS and _virtual machine_ in Azure and Google Cloud) that gets created in the buyer's account during the MAS instance deployment.

For example,
- In AWS, the Marketplace product has associated CloudFormation template, and the template creates the EC2 instance. The _UserData_ section in the EC2 instance has the commands to start the bootstrap process.
- In Azure, the Marketplace product has associated ARM template, and the template creates the virtual machine. The virtual machine has the _CustomScript extension_ defined that has the commands to start the bootstrap process.

Below are the steps that are invoked by Cloud provider automatically upon the creation of the bootnode.

#### From the template associated with the Marketplace product
1. Clone the GitHub repo having bootstrap code
2. Make the required scripts executable
3. Execute `init.sh` script, which is the starting point of the bootstrap process.
#### From the `init.sh`:
4. Call `pre-validate.sh` to perform pre-validation checks before starting the deployment.
5. Call `deploy.sh` to perform the OpenShift cluster creation and application deployment.
   1. Run Terraform automation to create OpenShift cluster
   2. Run Terraform automation to create bastion host.
   3. Upload the deployment context to storage.
   4. Call Ansible playbooks to deploy Mas and prerequisites in correct order.
6. Call Cloud specific `notify.sh` to send the email notifications.
7. Send stack create completion signal to CloudFormation (specific to AWS).
8. Upload the log file to storage.

The bootstrap code is organized in such a way that there is some generic code which will be common to any Cloud (with conditional handling of the Cloud type within the code), and some code that is specific to the Cloud.
The below table defines all the files/folders with those details.

File/Directory | Generic/Cloud-Specific | Cloud type | Details
-- | -- | -- | -- |
`init.sh` (file)	| Generic	| | The entrypoint of the bootstrap process. It will have all the common code to read the parameters passed by the Cloud init process and initiate the bootstrap flow. It has a parameter as Cloud type that can be used to perform any Cloud specific processing within the script. |
`helper.sh` (file) | Generic | | Helper functions used by various other scripts. It has functions for logging, retrieving details from OCP cluster, processing user inputs etc. It can also have Cloud specific functions defined and can be called from other scripts as needed. |
`pre-validate.sh` (file) | Generic | | Perform the pre-validation before starting the cluster deployment. If any of the pre-deployment checks fail, the bootstrap flow fails. __Note:__ It can also have Cloud specific checks by making use of Cloud type global variable. |
`jdbc-prevalidate.py` (file) | Generic | AWS |Python code to check if provided database details are valid by making a connection check to it. |
`ansible` (directory)	| Generic	| |	Ansible automation for Mas and prerequisite component deployments. There is a separate documentation for Ansible playbooks and roles. |
`aws` (directory)	| Cloud-Specific | AWS | This folder contains the code specific to AWS implementation.
`aws/bootnode-ami` (directory) | Cloud-Specific	| AWS | Contains the code to create/manage Bootnode AMI. |
`aws/bootnode-ami/prepare-bootnode-ami.sh` (file)	| Cloud-Specific | AWS | This script is used to install required packages in the EC2 instance to create the image (AMI) from it. Please check the developer documentation here for the detailed steps on creating Bootnode AMI. Normally the AMI should be created in us-east-1 region. |
`aws/bootnode-ami/copy-ami-to-region.sh` (file)	| Cloud-Specific | AWS | Helper script that can be executed manually to copy the AMI from us-east-1 to all supported regions. This will be useful in the development stage where once the AMI is created in us-east-1 region, we want to copy it to other regions to perform the testing in those regions. Make sure to update the CloudFromation template for the AMI IDs for those regions. For the actual Marketplace product, AWS takes care of copying the AMI to all supported regions and updating the CloudFormation template. |
`aws/iam` (directory) | Cloud-Specific | AWS | Files specific IAM configuration required for the deployment. |
`aws/iam/policy.json` (file) | Cloud-Specific | AWS | A policy definition file used to create the policy using AWS CLI. |
`aws/master-cft/cft-mas-core-dev.json` (file) | Cloud-Specific | AWS | The CloudFormation template file used to deploy during the development testing. This template pulls the code from dev branch of the repo where bootstrap code resides. |
`aws/master-cft/cft-mas-core.json` (file) |  Cloud-Specific | AWS | The CloudFormation template file that we share with AWS. This template pulls the code from main/master branch of the repo where bootstrap code resides. Please note that, the CloudFormation template used for the deployments by buyers is taken from the S3 bucket that is already pre-populated by AWS. None of the templates kept in the GitHub repo are used in the actual product deployments done by the buyers. |
`aws/notification/message-details.json` (file) | 	Cloud-Specific | AWS | Email template containing the environment details to be used by SES raw email notification. |
`aws/notification/message-creds.json` (file) | 	Cloud-Specific | AWS | Email template containing the credentials to be used by SES raw email notification. |
`aws/ocp-terraform` (directory) | Cloud-Specific | AWS | Terraform automation code used to deploy OpenShift cluster, configure OCS storage etc. |
`aws/ocp-bastion-host` (directory) | Cloud-Specific | AWS | Terraform automation code used to create the bastion host. |
`create-bastion-host.sh` (file) | Cloud-Specific | AWS | Script that creates the bastion host using the Terraform code at aws/ocp-bastion-host. |
`deploy.sh` (file) | Cloud-Specific | AWS | Script containing the actual deployment code that calls the underlying automation. |
`notify.sh` (file) | Cloud-Specific | AWS | Send the email notifications using Amazon SES service. |
`cleanup-mas-deployment.sh` (file) | Cloud-Specific | AWS | Uninstall the product. It basically deletes all the AWS resources for a particular MAS instance.
