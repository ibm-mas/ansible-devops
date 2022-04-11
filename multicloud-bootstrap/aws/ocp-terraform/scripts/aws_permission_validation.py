'''
Resource quota validation for AWS accounts
'''

from libs_aws.aws_configuration_helper import AWSConfigurationHelper
from libs_aws.aws_generic_helper import AWSGenericHelper
from libs_aws.iam_helper import IAMHelper

import os
import boto3
import argparse

from pprint import pprint

import sys

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', required=True, help='Name of the file containing the permissions to be tested.')
    parser.add_argument('--credentials_from_file', '-c', required=False, action='store_true', help='If set, the credentials will be taken from file.')
    parser.add_argument('--profile', '-p', required=False, default='', help='Profile to be used from the AWS credentials file.')
    return parser.parse_args()

def get_terraform_configuration():
    print("\nCluster configuration")
    print("=====================")

    tf_var_file = os.path.dirname(os.path.abspath(__file__)) + '/../variables.tf'
    print("  The cluster configuration will be derived from terraform " +
          f"configuration: '{tf_var_file}'\n")

    tf_config = {}

    tf_config_json = AWSGenericHelper.get_terraform_config_json(tf_var_file)

    tf_config['region'] = tf_config_json['variable']['region']['default']
    pprint(tf_config)

    return tf_config


def main():
    args = _parse_args()
    actions_file = args.file
    cred = args.credentials_from_file
    profile = args.profile

    # Get resource related values from terraform config variables file
    tf_config = get_terraform_configuration()

    # Get the AWS configuration (credentials, region)
    aws_config = AWSConfigurationHelper.get_config(tf_config['region'], cred, profile)

    iam_helper = IAMHelper(aws_config)

    # Show user data
    user_name = iam_helper.get_user_name()
    print("Going to check the permissions for user: " + user_name)

    groups = iam_helper.get_groups_from_username(user_name)
    print("The user " + user_name + " is member of the groups:")
    print(groups)
    
    policies = iam_helper.get_user_and_group_policies(user_name, groups)
    print("The following policies are applied to the user " + user_name + ":")
    print(policies)

    # Test the permissions
    resource_actions = []
    try:
        with open(actions_file) as f:
            resource_actions = f.read().splitlines()
    except IOError as e:
        print(e)
        print("Check specified actions file path name and try again.")
        sys.exit(1)

    resource_actions = list(filter(None, resource_actions))
    resource_actions = list(filter(lambda name : name.strip(), resource_actions))
    resource_actions = list(filter(lambda x : "#" not in x, resource_actions))
    print("Going to verify the permissions for the following resource actions:")
    print(*resource_actions, sep='\n')
    print("")

    blocked_actions = iam_helper.blocked(user_name, actions=resource_actions)

    if blocked_actions != []:
        print(" * The user " + user_name + " has unsufficient permissions to exexute the following actions:")
        print(*blocked_actions, sep='\n')
        sys.exit(1)
    print("")

if __name__ == '__main__':
    sys.exit(main())
