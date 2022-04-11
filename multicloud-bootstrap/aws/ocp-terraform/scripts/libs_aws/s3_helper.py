import boto3

from botocore.exceptions import ClientError
from libs_aws.aws_generic_helper import AWSGenericHelper

import logging

from pprint import pprint

class S3Helper():
    '''
    Object used to access the AWS S3 service
    '''

    def __init__(self, aws_config):
        self.__s3_session = self.__create_client_session(aws_config)

    def __create_client_session(self, aws_config):

        # Create an AWS session client
        try:
            session_helper = AWSGenericHelper(aws_config)
            aws_session = session_helper.create_session()
            s3_session = aws_session.client('s3')
            return s3_session
        except ClientError as e:
            # logging.error(e)
            print("  * The AWS client could not be created.")
            print('  * Please, try again.')
            exit(1)

    def list_buckets(self):
        buckets = self.__s3_session.list_buckets()
        return buckets['Buckets']

    def get_num_buckets(self):
        buckets = self.list_buckets()
        buckets_in_use = len(buckets)
        return buckets_in_use
