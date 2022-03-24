'''
Resource quota validation for AWS accounts
'''

from libs_aws.aws_configuration_helper import AWSConfigurationHelper
from libs_aws.aws_generic_helper import AWSGenericHelper
from libs_aws.ec2_helper import EC2Helper
from libs_aws.elb_helper import ELBHelper
from libs_aws.elb_v2_helper import ELBv2Helper
from libs_aws.s3_helper import S3Helper
from libs_aws.service_quotas_helper import ServiceQuotasHelper

import os

from pprint import pprint

import re
import sys


def get_terraform_configuration(tf_var_file):

    print("\nCluster configuration")
    print("=====================")

    print("  The cluster configuration will be derived from the terraform configuration:\n" +
          f"  {tf_var_file}\n")

    tf_config = {}
    tf_config['replica_count'] = {}
    tf_config['instance_type'] = {}
    instance_type_count = {}
    tf_config_json = AWSGenericHelper.get_terraform_config_json(tf_var_file)

    tf_config['region'] = tf_config_json['variable']['region']['default']
    tf_config['deploy_type'] = tf_config_json['variable']['az']['default']
    tf_config['storage_type'] = 'ocs' if tf_config_json['variable']['ocs']['default']['enable'] else 'portworx'
    tf_config['replica_count']['master'] = tf_config_json['variable']['master_replica_count']['default']
    tf_config['replica_count']['worker'] = tf_config_json['variable']['worker_replica_count']['default']
    tf_config['instance_type']['master'] = tf_config_json['variable']['master_instance_type']['default']
    tf_config['instance_type']['worker'] = tf_config_json['variable']['worker_instance_type']['default']
    if tf_config['storage_type'] == 'ocs':
        tf_config['instance_type']['ocs'] = tf_config_json['variable']['ocs']['default']['dedicated_node_instance_type']
        tf_config['replica_count']['ocs'] = 3

    # storage-type dependend adaptions
    ## storage-type == 'ocs' --> 3 additional OCS worker nodes are deployed
    # if tf_config['storage_type'] == 'ocs':
    #     tf_config['replica_count']['worker'] = tf_config['replica_count']['worker'] + 3
    ## storage-type == 'portworx' --> 1 additional worker node added by cluster auto-scaler 
    # <Femi: Commenting this out since autoscaler is disabled>
    # if tf_config['storage_type'] == 'portworx':
    #     tf_config['replica_count']['worker'] = tf_config['replica_count']['worker'] + 1

    # Summing up the number of required number of instance types
    for node_type in tf_config['instance_type']:
        instance_type = tf_config['instance_type'][node_type]
        if instance_type not in instance_type_count:
            instance_type_count[instance_type] = tf_config['replica_count'][node_type]
        else:
            instance_type_count[instance_type] += tf_config['replica_count'][node_type]

    tf_config['instances'] = instance_type_count

    # pprint(tf_config)

    return tf_config

def resource_validation_check(service_quotas, service_code, quota_code,
                              resources_used, resources_required):

    quota_value = 0.0
    # --> S3 Service Quoata: "L-DC2B2D3D" - "Buckets"
    #     since Buckets are tied to the Account
    if service_code == 's3' and quota_code == 'L-DC2B2D3D':
        quota_value = service_quotas[service_code][quota_code]['Value']
    else:
        quota_value = service_quotas[service_code][quota_code]['RegionValue']
    resources_available = quota_value - resources_used
    service_quotas[service_code][quota_code]['ResourcesAvailable'] = resources_available
    service_quotas[service_code][quota_code]['ResourcesRequired'] = resources_required
    service_quotas[service_code][quota_code]['ValidationCheck'] = 'PASSED'
    if resources_available < resources_required:
        service_quotas[service_code][quota_code]['ValidationCheck'] = 'FAILED'

def get_quota_code_by_name_pattern(service_code, quota_name_pattern,
                                   service_quota_to_be_validated):
    qc = ''
    for quota_code in service_quota_to_be_validated[service_code]:
        if re.search(quota_name_pattern,
                     service_quota_to_be_validated[service_code][quota_code]):
            qc = quota_code
    return qc

def main():
    
    # Get resource related values from terraform config variables file
    tf_var_file = os.path.dirname(os.path.abspath(__file__)) + '/../variables.tf'
    tf_config = get_terraform_configuration(tf_var_file)

    # Get the AWS configuration (credentials, region)
    aws_config = AWSConfigurationHelper.get_config(tf_config['region'])

    # Initialize AWS service client objects
    service_quota_helper = ServiceQuotasHelper(aws_config)
    ec2_helper = EC2Helper(aws_config)
    elb_helper = ELBHelper(aws_config)
    elb_v2_helper = ELBv2Helper(aws_config)
    s3_helper = S3Helper(aws_config)


    # Get / validate the Cluster High Availability config (single_zone / multi_zone)
    num_az = ec2_helper.get_num_availability_zones()
    ha_config = AWSConfigurationHelper.get_ha_config(num_az,
                                                     aws_config['region'],
                                                     ha_config = tf_config['deploy_type'])

    # Validate selected AWS instance types in selected AWS region
    ec2_helper.validate_aws_instance_types(tf_var_file)

    # Get / Validate AWS service quotas
    service_quota_file = os.path.dirname(os.path.abspath(__file__)) + '/aws_resource_quota'
    service_quotas_to_be_validated = ServiceQuotasHelper.get_aws_service_quota_to_be_validated(
                                                                                service_quota_file)
    # Service Quota dictionary used to hold all collected data
    sq = service_quota_helper.validate_aws_service_quotas(service_quotas_to_be_validated,
                                                          num_az = num_az)

    # enrich VPC service quotas
    vpc_quota_code_nat_gateways = get_quota_code_by_name_pattern(
                                            'vpc',
                                            'NAT gateways',
                                            service_quotas_to_be_validated)
    vpc_quota_code_security_groups = get_quota_code_by_name_pattern(
                                            'vpc',
                                            'VPC security groups',
                                            service_quotas_to_be_validated)
    vpc_quota_code_network_interfaces = get_quota_code_by_name_pattern(
                                            'vpc',
                                            'Network interfaces',
                                            service_quotas_to_be_validated)
    vpc_quota_code_vpcs = get_quota_code_by_name_pattern(
                                            'vpc',
                                            'VPCs per Region',
                                            service_quotas_to_be_validated)
    sq['vpc'][vpc_quota_code_nat_gateways]['Scope'] = 'Availability Zone'
    sq['vpc'][vpc_quota_code_security_groups]['Scope'] = 'Region'
    sq['vpc'][vpc_quota_code_network_interfaces]['Scope'] = 'Region'
    sq['vpc'][vpc_quota_code_vpcs]['Scope'] = 'Region'
    for quota_code in sq['vpc']:
        sq['vpc'][quota_code]['DisplayServiceCode'] = 'VPC'


    # enrich EC2 service quotas
    for quota_code in sq['ec2']:
        sq['ec2'][quota_code]['Scope'] = 'Region'
        sq['ec2'][quota_code]['DisplayServiceCode'] = 'EC2'

    # enrich Elastic Load Balancing service quotas
    for quota_code in sq['elasticloadbalancing']:
        sq['elasticloadbalancing'][quota_code]['Scope'] = 'Region'
        sq['elasticloadbalancing'][quota_code]['DisplayServiceCode'] = 'ELB'

    # enrich S3 service quotas
    s3_quota_code_buckets = get_quota_code_by_name_pattern(
                                            's3',
                                            'Buckets',
                                            service_quotas_to_be_validated)
    sq['s3'][s3_quota_code_buckets]['Scope'] = 'Account'
    # Since Buckets are tied to the Account - need to unset 'RegionValue'
    sq['s3'][s3_quota_code_buckets]['RegionValue'] = ''
    for quota_code in  sq['s3']:
        sq['s3'][quota_code]['DisplayServiceCode'] = 'S3'

    # VPC Gateway - service quotas
    ## To be done

    ##############################
    #
    # Get resource usage counts  +
    # Add required resource counts
    #
    ##############################

    # OCP required resources
    ocp = AWSGenericHelper.get_opc_required_resources(tf_config['storage_type'],
                                                      ha_config)

    # Calculate the additionally needed number of workers
    # for CP4D services to be installed
    worker_instance_type = tf_config['instance_type']['worker']
    num_service_worker_nodes = ec2_helper.calculate_num_service_worker_nodes(
                                                        worker_instance_type,
                                                        tf_var_file)

    # Add number of required worker nodes for CP4D services
    # to number of OCP worker nodes
    tf_config['instances'][worker_instance_type] = (tf_config['instances'][worker_instance_type] +
                                                    num_service_worker_nodes)

    # Add number of required Network Interfaces according
    # to the number of service worker nodes
    ocp['network-interfaces'] = ocp['network-interfaces'] + num_service_worker_nodes

    # EC2 resources
    ## VPCs
    vpc_used = ec2_helper.get_num_vpc()
    vpc_required = ocp['vpcs']
    resource_validation_check(sq, 'vpc', vpc_quota_code_vpcs,
                              vpc_used, vpc_required)

    ### Elastic IPs
    eip_used = ec2_helper.get_num_elastic_ips()
    eip_required = ocp['elastic-ips']
    ec2_quota_code_elastic_ips = get_quota_code_by_name_pattern(
                                            'ec2',
                                            'Elastic IPs',
                                            service_quotas_to_be_validated)
    resource_validation_check(sq, 'ec2', ec2_quota_code_elastic_ips,
                              eip_used, eip_required)

    ### NatGateways
    nat_gw_used = ec2_helper.get_num_nat_gw()
    nat_gw_required = ocp['nat-gateways']
    resource_validation_check(sq, 'vpc', vpc_quota_code_nat_gateways,
                              nat_gw_used, nat_gw_required)

    ### SecurityGroups
    sg_used = ec2_helper.get_num_security_groups()
    sg_required = ocp['security-groups']
    resource_validation_check(sq, 'vpc', vpc_quota_code_security_groups,
                              sg_used, sg_required)


    ### Elastic Network Interfaces (ENIs)
    eni_used = ec2_helper.get_num_network_interfaces()
    eni_required = ocp['network-interfaces']
    resource_validation_check(sq, 'vpc', vpc_quota_code_network_interfaces,
                              eni_used, eni_required)

    ### Instances
    instances_vcpus_used = ec2_helper.get_instances_num_vcpus_used()
    instances_vcpus_required = ec2_helper.get_instances_num_vcpus(tf_config['instances'])
    ec2_quota_code_instances_f = get_quota_code_by_name_pattern(
                                            'ec2',
                                            'Running On-Demand F',
                                            service_quotas_to_be_validated)
    ec2_quota_code_instances_g = get_quota_code_by_name_pattern(
                                            'ec2',
                                            'Running On-Demand G',
                                            service_quotas_to_be_validated)
    ec2_quota_code_instances_inf = get_quota_code_by_name_pattern(
                                            'ec2',
                                            'Running On-Demand Inf',
                                            service_quotas_to_be_validated)
    ec2_quota_code_instances_p = get_quota_code_by_name_pattern(
                                            'ec2',
                                            'Running On-Demand P',
                                            service_quotas_to_be_validated)
    ec2_quota_code_instances_standard = get_quota_code_by_name_pattern(
                                            'ec2',
                                            'Running On-Demand Standard',
                                            service_quotas_to_be_validated)
    ec2_quota_code_instances_x = get_quota_code_by_name_pattern(
                                            'ec2',
                                            'Running On-Demand X',
                                            service_quotas_to_be_validated)
    resource_validation_check(sq, 'ec2', ec2_quota_code_instances_f,
                              instances_vcpus_used['f'],
                              instances_vcpus_required['f'])
    resource_validation_check(sq, 'ec2', ec2_quota_code_instances_g,
                              instances_vcpus_used['g'],
                              instances_vcpus_required['g'])
    resource_validation_check(sq, 'ec2', ec2_quota_code_instances_inf,
                              instances_vcpus_used['inf'],
                              instances_vcpus_required['inf'])
    resource_validation_check(sq, 'ec2', ec2_quota_code_instances_p,
                              instances_vcpus_used['p'],
                              instances_vcpus_required['p'])
    resource_validation_check(sq, 'ec2', ec2_quota_code_instances_standard,
                              instances_vcpus_used['standard'],
                              instances_vcpus_required['standard'])
    resource_validation_check(sq, 'ec2', ec2_quota_code_instances_x,
                              instances_vcpus_used['x'],
                              instances_vcpus_required['x'])

    ## ELB v2 (network) resouces usage counts
    ### Elastic Load Balancers v2 (ELB/NLB) - type: network
    elb_v2_used = elb_v2_helper.get_num_elb_v2()
    elb_v2_required = ocp['application-load-ballancer']
    elb_v2_quota_code_application_load_balancers = get_quota_code_by_name_pattern(
                                            'elasticloadbalancing',
                                            'Application Load Balancers',
                                            service_quotas_to_be_validated)
    resource_validation_check(sq, 'elasticloadbalancing',
                              elb_v2_quota_code_application_load_balancers,
                              elb_v2_used, elb_v2_required)

    ## ELB (classic) resouces usage counts
    ### Elastic Load Balancers (ELB/NLB) - type: classic
    elb_used = elb_helper.get_num_elb()
    elb_required = ocp['classic-load-ballancer']
    elb_quota_code_classic_load_balancers = get_quota_code_by_name_pattern(
                                            'elasticloadbalancing',
                                            'Classic Load Balancers',
                                            service_quotas_to_be_validated)
    resource_validation_check(sq, 'elasticloadbalancing',
                              elb_quota_code_classic_load_balancers,
                              elb_used, elb_required)

    ## S3 resouces usage counts
    ### S3 buckets
    s3_buckets_used = s3_helper.get_num_buckets()
    s3_required = ocp['s3-buckets']
    resource_validation_check(sq, 's3', s3_quota_code_buckets,
                              s3_buckets_used, s3_required)

    print('\nService quotas + currently used resources:')
    print('==========================================\n')

    print(f"  AWS Region                                  : {aws_config['region']}")
    print(f"  Number of Availability Zones in that region : {num_az}")
    print(f"  Desired HA config                           : {ha_config}\n")

    # pprint(sq)

    # Table column width
    width_column_1 = 8
    width_column_2 = 65
    width_column_3 = 18
    width_column_4 = 6
    width_column_5 = 15
    width_column_6 = 20
    width_column_7 = 19
    width_column_8 = 11

    # Tabel header format
    table_header_format = (
        "  {col_1:<{col_1_width}}|" +
        " {col_2:<{col_2_width}} |" +
        " {col_3:<{col_3_width}} |" +
        " {col_4:<{col_4_width}} |" +
        " {col_5:<{col_5_width}} |" +
        " {col_6:<{col_6_width}} |" +
        " {col_7:<{col_7_width}} |" +
        " {col_8:<{col_8_width}}"
    )

    # Tabel row separator format
    table_row_separator_format = (
        "  {col_1:{col_1_width}}|" +
        "{col_2:{col_2_width}}|" +
        "{col_3:{col_3_width}}|" +
        "{col_4:{col_4_width}}|" +
        "{col_5:{col_5_width}}|" +
        "{col_6:{col_6_width}}|" +
        "{col_7:{col_7_width}}|" +
        "{col_8:{col_8_width}}"
    )

    # Table row format
    table_row_format = (
        "   {col_1:<{col_1_width}}|" +
        "  {col_2:<{col_2_width}}|" +
        "  {col_3:<{col_3_width}}|" +
        "  {col_4:<{col_4_width}}|" +
        "  {col_5:>{col_5_width}} |" +
        "  {col_6:>{col_6_width}} |" +
        "  {col_7:>{col_7_width}} |" +
        "  {col_8:{col_8_width}}"
    )

    # Table header
    table_header = (table_header_format.format(
        col_1="Service", col_1_width=width_column_1,
        col_2="Service Quota Name", col_2_width=width_column_2,
        col_3="Scope", col_3_width=width_column_3,
        col_4="Unit", col_4_width=width_column_4,
        col_5="Service Quotas", col_5_width=width_column_5,
        col_6="Resources available", col_6_width=width_column_6,
        col_7="Resources required", col_7_width=width_column_7,
        col_8="Validation", col_8_width=width_column_8)
    )

    # Table row separator
    table_row_separator = (table_row_separator_format.format(
        col_1="-"*width_column_1, col_1_width=width_column_1,
        col_2="-"*(width_column_2 + 2), col_2_width=width_column_2 + 2,
        col_3="-"*(width_column_3 + 2), col_3_width=width_column_3 + 2,
        col_4="-"*(width_column_4 + 2), col_4_width=width_column_4 + 2,
        col_5="-"*(width_column_5 + 2), col_5_width=width_column_5 + 2,
        col_6="-"*(width_column_6 + 2), col_6_width=width_column_6 + 2,
        col_7="-"*(width_column_7 + 2), col_7_width=width_column_7 + 2,
        col_8="-"*width_column_8, col_8_width=width_column_8)
    )

    # Table - print out
    print(table_header)

    print_validation_check_failed_comment = False
    for key in sq:
        print(table_row_separator)
        for item in sq[key]:
            if sq[key][item]['ValidationCheck'] == 'FAILED':
                print_validation_check_failed_comment = True
            print(table_row_format.format(
                col_1=sq[key][item]['DisplayServiceCode'], col_1_width=width_column_1 - 1,
                col_2=sq[key][item]['QuotaName'], col_2_width=width_column_2,
                col_3=sq[key][item]['Scope'], col_3_width=width_column_3,
                col_4=sq[key][item]['Unit'], col_4_width=width_column_4,
                col_5=sq[key][item]['Value'], col_5_width=width_column_5 - 1,
                col_6=sq[key][item]['ResourcesAvailable'], col_6_width=width_column_6 - 1,
                col_7=sq[key][item]['ResourcesRequired'], col_7_width=width_column_7 - 1,
                col_8=sq[key][item]['ValidationCheck'], col_8_width=width_column_8)
            )

    print("\n")
    print("Comments")
    print("--------")
    if print_validation_check_failed_comment:
        print("  * Validation = 'FAILED'")
        print("    There are not enough resources available to create the desired infrastructure in that region.")
        print("    Recommendation:")
        print("      - Cleanup resources in that region.")
        print("      - Specify a different region.")
        sys.exit(1)
    else:
        print("\n  * Validation = 'PASSED'")
        print("    Cluster can be created in that region.")
    print("")

if __name__ == '__main__':
    sys.exit(main())
