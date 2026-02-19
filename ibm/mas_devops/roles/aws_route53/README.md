aws_route53
=========

This role will create an AWS Route53 public hosted zone in the targeted AWS Account.

For further details on how to create and configure an AWS Route53 instance, refer to [AWS Route53 documentation](https://docs.aws.amazon.com/cli/latest/reference/route53/index.html).

## Prerequisites
To run this role successfully you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).
Also, you need to have AWS user credentials configured via `aws configure` command or simply export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables with your corresponding AWS username credentials prior running this role.

## Role Variables

### route53_hosted_zone_name
The domain name for the Route53 public hosted zone to be created.

- **Required**
- Environment Variable: `ROUTE53_HOSTED_ZONE_NAME`
- Default Value: None

**Purpose**: Defines the DNS domain name that will be managed by the Route53 hosted zone. This zone will contain DNS records for routing traffic to your MAS deployment.

**When to use**: Always required when creating a Route53 hosted zone. The domain name should match your organization's domain or subdomain that you want to use for MAS endpoints.

**Valid values**:
- Any valid domain name format (e.g., `mycompany.com`, `mas.example.org`)
- Can be a root domain or subdomain
- Must be unique within your AWS account
- Should not include protocol (http/https) or trailing slashes

**Impact**:
- Creates a public hosted zone with this domain name in Route53
- Generates NS (nameserver) records that must be configured with your domain registrar
- All DNS records for MAS endpoints will be created under this domain
- Cannot be changed after creation without recreating the hosted zone

**Related variables**:
- [`route53_hosted_zone_region`](#route53_hosted_zone_region) - Specifies the AWS region for the hosted zone

**Notes**:
- After creation, you must update your domain registrar's nameservers to point to the Route53 NS records
- The hosted zone will incur AWS charges based on the number of hosted zones and queries
- Ensure you have ownership/control of the domain before creating the hosted zone
- For production deployments, consider using a subdomain (e.g., `mas.mycompany.com`) to isolate MAS DNS records

### route53_hosted_zone_region
The AWS region where the Route53 hosted zone will be created.

- **Required**
- Environment Variable: `ROUTE53_HOSTED_ZONE_REGION`
- Default Value: Value from `AWS_REGION` environment variable, or `us-east-2` if not set

**Purpose**: Specifies the AWS region for creating the Route53 hosted zone. While Route53 is a global service, the API calls and zone metadata are associated with a specific region.

**When to use**: Should match the region where your primary MAS infrastructure is deployed, or use the default region configured in your AWS CLI.

**Valid values**:
- Any valid AWS region identifier (e.g., `us-east-1`, `us-west-2`, `eu-west-1`, `ap-southeast-1`)
- Must be a region where Route53 service is available (all standard AWS regions)
- Defaults to `us-east-2` if neither this variable nor `AWS_REGION` is set

**Impact**:
- Determines which regional Route53 API endpoint is used for zone creation
- Does not affect DNS query routing (Route53 is globally distributed)
- Should align with your AWS CLI configuration for consistency
- May affect API latency for zone management operations

**Related variables**:
- [`route53_hosted_zone_name`](#route53_hosted_zone_name) - The domain name for the hosted zone
- Inherits from `AWS_REGION` environment variable if not explicitly set

**Notes**:
- Route53 hosted zones are globally accessible regardless of the creation region
- The region setting primarily affects API operations, not DNS resolution
- For multi-region deployments, you only need one hosted zone (not per region)
- Ensure your AWS credentials have Route53 permissions in the specified region

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
