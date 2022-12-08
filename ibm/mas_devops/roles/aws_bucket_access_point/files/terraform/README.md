# Terraform provides a S3 bucket resource.

## Preresiquites

Install Terraform

Create file called terraform.tfvars in directory and paste the following and update the values:

```terraform
region = "us-east-2"
```

## Deploy

```bash
terraform init
terraform plan
terraform apply -auto-approve
```

Default timeout for create is 60 mins

## Destroy

```bash
terraform plan 
terraform destroy -auto-approve
```
