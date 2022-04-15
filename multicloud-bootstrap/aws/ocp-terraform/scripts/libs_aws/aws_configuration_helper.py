import boto3

from botocore.config import Config
from botocore.exceptions import ClientError

import configparser
import os
import os.path

class AWSConfigurationHelper():
    '''
    Object used to gather the AWS configuration
    - credentials
    - region
    '''

    @staticmethod
    def validate_config(aws_config):
        print("Validate AWS configuration")
        print("==========================")
        
        region_name_list = []

        # Validate entered AWS access credentials
        try:
            ec2_client = boto3.client(
                'ec2',
                aws_access_key_id = aws_config['access_key'],
                aws_secret_access_key = aws_config['secret_access_key'],            
            )

            # Retrieves all regions that work with EC2
            response = ec2_client.describe_regions()

        except ClientError as e:
            # print(e)
            # logging.error(e)
            print("  * The credentials you provided were rejected.")
            print("  * Please, try again.\n")
            exit(1)


        # Validate entered AWS region
        for region in response['Regions']:
            region_name_list.append(region['RegionName'])
        
        if aws_config['region'] not in region_name_list:
            print(f"  * Region '{aws_config['region']}' does not exist in AWS.")
            print("  * Please, try again.\n")
            exit(1)

        print("  Validation passed.\n")

    @staticmethod
    def get_aws_credentials(credentials_from_file = False, profile = ''):
        aws_config = {}

        aws_config_path_name = os.environ.get('HOME') + "/.aws"
        aws_credentials_file_name = aws_config_path_name + "/credentials"
        aws_access_key = ''
        aws_secret_access_key = ''

        print("\nAWS access credentials need to be determined")
        print("============================================")
        answer_matched = False
        answer_default = 'file'
        answer = ''

        if credentials_from_file:
            print(f"\n  Credentials taken from file.")
            answer = answer_default
            answer_matched = True

        while not answer_matched:
            print("  AWS credentials to be read from "
                   + "user input or credentials file ?")
            answer = input("  Enter  'user'  or  'file' (default: 'file'): ")

            if not answer:
                answer = answer_default
            if answer in ['user', 'file']:
                answer_matched = True
            else:
                print("  * Wrong input.")
                print("  * Please enter  'user'  or  'file'.\n")

        if answer == 'file':
            if os.path.isfile(aws_credentials_file_name):
                config = configparser.ConfigParser()
                config.read(aws_credentials_file_name)

                profiles = config.sections()
                if profile == '':
                    if len(profiles) == 1:
                        profile = profiles[0]
                    else:
                        print(f"\n  Profiles in AWS credentials file: {profiles}")
                        profile_matched = False

                        while not profile_matched:
                            profile = input("  Which AWS Profile to be used: ")
                            if profile in profiles:
                                profile_matched = True
                            else:
                                print("  * Profile does not exist.")
                                print("  * Please, try again.")
                else:
                    if profile not in profiles:
                        print(f"  * Profile '{profile}' does not exist.")
                        print("  * Please, try again with an existing profile.")
                        exit ()

                aws_access_key = config[profile]['aws_access_key_id']
                aws_secret_access_key = config[profile]['aws_secret_access_key']
        else:
            aws_access_key = input("  Enter the AWS 'Access key ID': ")
            aws_secret_access_key = input("  Enter the AWS 'Secret access key': ")

        aws_config['access_key'] = aws_access_key
        aws_config['secret_access_key'] = aws_secret_access_key

        print("\n")

        return aws_config

    @staticmethod
    def get_aws_config():
        aws_config = {}

        aws_config_path_name = os.environ.get('HOME') + "/.aws"
        aws_config_file_name = aws_config_path_name + "/config"
        aws_region = ''

        print("AWS region needs to be determined")
        print("=================================")
        answer_matched = False
        answer_default = 'file'
        answer = ''
        while not answer_matched:
            print("  AWS config / region to be read from "
                   + "user input or credentials file ?")
            answer = input("  Enter  'user'  or  'file' (default: 'file'): ")
            if not answer:
                answer = answer_default
            if answer in ['user', 'file']:
                answer_matched = True
            else:
                print("  * Wrong input.")
                print("  * Please enter  'user'  or  'file'.")

        if answer == 'file':
            if os.path.isfile(aws_config_file_name):
                config = configparser.ConfigParser()
                config.read(aws_config_file_name)

                profiles = config.sections()
                profile = ''
                if len(profiles) == 1:
                    profile = profiles[0]
                else:
                    print(f"\n  Profiles in AWS config file found: {profiles}")
                    profile_matched = False

                    while not profile_matched:
                        profile = input("  Which AWS config profile to be used: ")
                        if profile in profiles:
                            profile_matched = True
                        else:
                            print("  * Profile does not exist.")
                            print("  * Please, try again.")

                aws_region = config[profile]['region']
        else:
            aws_region = input("  Enter the AWS 'region' (e.g.: eu-west-1): ")
        
        aws_config['region'] = aws_region

        print("\n")

        return aws_config

    @staticmethod
    def get_config(region = None, credentials_from_file = False, profile = ''):    
        aws_config = dict(AWSConfigurationHelper.get_aws_credentials(credentials_from_file, profile) )
        if region:
            aws_config['region'] = region
        else:
            aws_config.update(AWSConfigurationHelper.get_aws_config() )
        AWSConfigurationHelper.validate_config(aws_config)

        return aws_config

    @staticmethod
    def get_ha_config(num_az, region, ha_config = None):

        if not ha_config:
            print("\nCluster High Availability configuration need to be determined")
            print("=============================================================")
            answer_matched = False
            answer_default = 'multi_zone'
            answer = ''
            while not answer_matched:
                print("  Cluster High Availability requires a 'multi_zone' deployment.")
                answer = input("  Enter  'single_zone'  or  'multi_zone'  (default: 'multi_zone'): ")
                if not answer:
                    answer = answer_default
                if answer in ['single_zone', 'multi_zone']:
                    answer_matched = True
                    ha_config = answer
                else:
                    print("  * Wrong input.")
                    print("  * Please enter  'single_zone'  or  'multi_zone'.")
        
        if ha_config == 'multi_zone' and num_az < 3:
            print("\n  HINT:")
            print(f"    In AWS region '{region}' there is / are only '{num_az}' Availability Zone(s) available.")
            print("    A 'multi_zone' cluster configuration can not be depolyed in that region.")
            print("    Resource quotas will be validated for a 'single_zone' cluster configuration.")
            ha_config = 'single_zone'

        return ha_config
