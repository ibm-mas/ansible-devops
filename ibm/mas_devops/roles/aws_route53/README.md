# aws_route53

This role will create an AWS Route53 public hosted zone in the targeted AWS Account.

For further details on how to create and configure an AWS Route53 instance, refer to [AWS Route53 documentation](https://docs.aws.amazon.com/cli/latest/reference/route53/index.html).

## Prerequisites

To run this role successfully you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`route53_hosted_zone_name`](#route53_hosted_zone_name) | Yes | None |
| [`route53_hosted_zone_region`](#route53_hosted_zone_region) | Yes | `AWS_REGION`, or `us-east-2` |

### Hosted Zone

#### route53_hosted_zone_name

The domain name for the Route53 public hosted zone to be created (e.g. `mycompany.com`, `mas.example.org` — a root domain or subdomain, without protocol or trailing slashes; must be unique within your AWS account).

- **Required**
- Environment Variable: `ROUTE53_HOSTED_ZONE_NAME`
- Default: None

After creation you must update your domain registrar's nameservers to point to the Route53 NS records; all DNS records for MAS endpoints will be created under this domain. For production deployments, consider using a subdomain (e.g. `mas.mycompany.com`) to isolate MAS DNS records. Hosted zones incur AWS charges based on the number of hosted zones and queries.

#### route53_hosted_zone_region

The AWS region where the Route53 hosted zone will be created.

- **Required**
- Environment Variable: `ROUTE53_HOSTED_ZONE_REGION`
- Default: Value from the `AWS_REGION` environment variable, or `us-east-2` if not set

Route53 is a globally distributed service, so this primarily determines which regional API endpoint is used for zone management — it does not affect DNS resolution, and for multi-region deployments a single hosted zone is sufficient.

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
