import boto3

from botocore.exceptions import ClientError
from libs_aws.aws_generic_helper import AWSGenericHelper

import logging

from pprint import pprint

class ELBHelper():
    '''
    Object used to access the AWS ELB service
    '''

    def __init__(self, aws_config):
        self.__elb_session = self.__create_client_session(aws_config)

    def __create_client_session(self, aws_config):

        # Create an AWS session client
        try:
            session_helper = AWSGenericHelper(aws_config)
            aws_session = session_helper.create_session()
            elb_session = aws_session.client('elb')
            return elb_session
        except ClientError as e:
            # logging.error(e)
            print("  * The AWS client could not be created.")
            print('  * Please, try again.')
            exit(1)

    def describe_resource(self, operation_name, object_key):
        resource = []

        # Create a reusable Paginator
        paginator = self.__elb_session.get_paginator(operation_name)

        # Create a PageIterator from the Paginator
        page_iterator = paginator.paginate()

        for page in page_iterator:
            resource = resource + page[object_key]

        return resource

    def get_num_elb(self):
        elb = self.describe_resource('describe_load_balancers',
                                     'LoadBalancerDescriptions')
        return len(elb)

