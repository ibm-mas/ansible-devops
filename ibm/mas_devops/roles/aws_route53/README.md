aws_route53
=========

This role will create an AWS Route53 public hosted zone in the targeted AWS Account.

For further details on how to create and configure an AWS Route53 instance, refer to [AWS Route53 documentation](https://docs.aws.amazon.com/cli/latest/reference/route53/index.html).

## Prerequisites
To run this role successfully you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

## Role Variables

### route53_hosted_zone_name
AWS Route53 Hosted Zone name.

- Required.
- Environment Variable: `ROUTE53_HOSTED_ZONE_NAME`
- Default Value: None

### route53_hosted_zone_region
AWS Route53 Hosted Zone region. 

- Required.
- Environment Variable: `ROUTE53_HOSTED_ZONE_REGION`
- Default Value: Same value as defined in `AWS_REGION`, or if none defined, then `us-east-2` is the defaulted region.

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    route53_hosted_zone_name: "{{ lookup('env', 'ROUTE53_HOSTED_ZONE_NAME') }}" # mycompany.com
    route53_hosted_zone_region: "{{ lookup('env', 'ROUTE53_HOSTED_ZONE_REGION') }}" # us-east-2
  roles:
    - ibm.mas_devops.aws_route53
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export ROUTE53_HOSTED_ZONE_NAME=mycompany.com
export ROUTE53_HOSTED_ZONE_REGION=us-east-2
ROLE_NAME=aws_route53 ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0
