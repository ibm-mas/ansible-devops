from libs_aws.aws_generic_helper import AWSGenericHelper

import boto3

from botocore.exceptions import ClientError

import configparser
import logging
import os
import os.path

from pprint import pprint

import re


class ServiceQuotasHelper():
    '''
    Object used to access the AWS Service Quota service to retrieve
    service quotas (limits) for the AWS account
    '''

    def __init__(self, aws_config):
        self.__service_quotas_session = self.__create_client_session(
                                                                aws_config)

    def __create_client_session(self, aws_config):

        # Create an AWS session client
        try:
            session_helper = AWSGenericHelper(aws_config)
            aws_session = session_helper.create_session()
            service_quotas_session = aws_session.client('service-quotas')
            return service_quotas_session
        except ClientError as e:
            # logging.error(e)
            print("  * The AWS client could not be created.")
            print('  * Please, try again.')
            exit(1)

    @staticmethod
    def get_aws_service_quota_to_be_validated(service_quota_file_name):
        service_quotas = {}

        if os.path.isfile(service_quota_file_name):
            config = configparser.ConfigParser()
            config.read(service_quota_file_name)

            service_codes = config.sections()

            for service_code in service_codes:
                service_quotas[service_code] = {}
                for quota_code in config[service_code]:
                    quota = {quota_code.upper(): config[service_code][quota_code]}
                    service_quotas[service_code].update(quota)
        else:
            print(f"ERROR: File does not exist: {service_quota_file_name}")
            print("Please make sure the file is in place.")
            exit(1)

        # pprint(service_quotas)

        return service_quotas

    def list_service_quotas(self, service_code):

        service_quotas = []

        # Create a reusable Paginator
        paginator = self.__service_quotas_session.get_paginator(
            'list_service_quotas'
        )

        # Create a PageIterator from the Paginator
        page_iterator = paginator.paginate(ServiceCode=service_code)

        for page in page_iterator:
            service_quotas = service_quotas + page['Quotas']

        return service_quotas

    def list_aws_default_service_quotas(self, service_code):

        aws_default_service_quotas = []

        # Create a reusable Paginator
        paginator = self.__service_quotas_session.get_paginator(
            'list_aws_default_service_quotas'
        )

        # Create a PageIterator from the Paginator
        page_iterator = paginator.paginate(ServiceCode=service_code)

        for page in page_iterator:
            aws_default_service_quotas = ( aws_default_service_quotas +
                                           page['Quotas'] )

        return aws_default_service_quotas

    def _retrieve_quota(self, quota_code, service_quotas,
                        num_az = None):
        quota = {}

        for svc_quota in service_quotas:
            svc_quota_code = svc_quota['QuotaCode']
            if svc_quota_code == quota_code:
                quota[svc_quota_code] = {}
                quota[svc_quota_code]['Validation'] = "PASSED"
                quota[svc_quota_code]['QuotaSource'] = 'service quotas'
                quota[svc_quota_code]['QuotaCode'] = svc_quota['QuotaCode']
                quota[svc_quota_code]['QuotaName'] = svc_quota['QuotaName']
                quota[svc_quota_code]['ServiceCode'] = svc_quota['ServiceCode']
                quota[svc_quota_code]['Value'] = svc_quota['Value']

                # Service Quota 'RegionValue'
                # multiply values for QuotaCodes that are tied to Availability Zone by
                # the number of Availability Zones in that Region
                # here: "L-FE5A380F" - "NAT gateways per Availability Zone"
                if svc_quota['QuotaCode'] == 'L-FE5A380F':
                    quota[svc_quota_code]['RegionValue'] = svc_quota['Value'] * num_az
                else:
                    quota[svc_quota_code]['RegionValue'] = svc_quota['Value']

                # Service Quota 'Unit'
                if re.search(r'Running On-Demand .* instances',
                                svc_quota['QuotaName']):
                    quota[svc_quota_code]['Unit'] = 'vCPUs'
                elif svc_quota['Unit'] == 'None':
                    quota[svc_quota_code]['Unit'] = 'Count'
                else:
                    quota[svc_quota_code]['Unit'] = svc_quota['Unit']

        return quota

    def validate_aws_service_quotas(self, service_quotas_to_be_validated,
                                    num_az = None):

        service_quotas_retrieved = {}
        quota_is_missing = False

        for service_code in service_quotas_to_be_validated:
            service_quotas_retrieved[service_code] = {}

            # Get applied quota values
            service_quotas = self.list_service_quotas(service_code)

            # Get AWS default quota values
            aws_default_service_quotas = self.list_aws_default_service_quotas(
                                                                    service_code)

            # list of quota_codes to be validated
            quota_codes = service_quotas_to_be_validated[service_code].keys()

            # list of quota_codes retrieved from applied quota values
            service_quotas_quota_codes = [ svc_quota['QuotaCode'] for svc_quota in service_quotas ]

            # list of quota_codes retrieved from default quota values
            dflt_service_quotas_quota_codes = [ svc_quota['QuotaCode'] for svc_quota in aws_default_service_quotas ]

            for quota_code in quota_codes:
                if quota_code in service_quotas_quota_codes:
                    quota = self._retrieve_quota(quota_code,
                                                 service_quotas,
                                                 num_az = num_az)
                    service_quotas_retrieved[service_code].update(quota)
                elif quota_code in dflt_service_quotas_quota_codes:
                    quota = self._retrieve_quota(quota_code,
                                                 aws_default_service_quotas,
                                                 num_az = num_az)
                    service_quotas_retrieved[service_code].update(quota)
                else:
                    quota_is_missing = True
                    quota = {}
                    quota[quota_code] = {}
                    quota[quota_code]['QuotaCode'] = quota_code
                    quota[quota_code]['QuotaName'] = service_quotas_to_be_validated[service_code][quota_code]
                    quota[quota_code]['Validation'] = "FAILED"
                    service_quotas_retrieved[service_code].update(quota)

        if quota_is_missing:
            ServiceQuotasHelper.print_out_service_quotas(service_quotas_retrieved)
            exit(1)

        return service_quotas_retrieved

    @staticmethod
    def print_out_service_quotas(service_quotas):

        section_name = "Validate AWS service quota in selected AWS region"
        print(f"\n{section_name}")
        print("="*len(section_name))
        print("")

        # Table column width
        width_column_1 = 22
        width_column_2 = 11
        width_column_3 = 65
        width_column_4 = 12

        # Tabel header format
        table_header_format = (
            "  {col_1:<{col_1_width}}|" +
            " {col_2:<{col_2_width}} |" +
            " {col_3:<{col_3_width}} |" +
            " {col_4:<{col_4_width}}"
        )

        # Tabel header separator format
        table_row_separator_format = (
            "  {col_1:{col_1_width}}|" +
            "{col_2:{col_2_width}}|" +
            "{col_3:{col_3_width}}|" +
            "{col_4:{col_4_width}}"
        )

        # Table row format
        table_row_format = (
            "   {col_1:<{col_1_width}}|" +
            "  {col_2:<{col_2_width}}|" +
            "  {col_3:<{col_3_width}}|" +
            "  {col_4:{col_4_width}}"
        )

        # Table header
        table_header = (table_header_format.format(
            col_1="Service code", col_1_width=width_column_1,
            col_2="Quota code", col_2_width=width_column_2,
            col_3="Quota Name", col_3_width=width_column_3,
            col_4="Validation", col_4_width=width_column_4)
        )

        # Table header separator
        table_row_separator = (table_row_separator_format.format(
            col_1="-"*width_column_1, col_1_width=width_column_1,
            col_2="-"*(width_column_2 + 2), col_2_width=width_column_2 + 2,
            col_3="-"*(width_column_3 + 2), col_3_width=width_column_3 + 2,
            col_4="-"*width_column_4, col_4_width=width_column_4)
        )

        # Table - print out
        print(table_header)
        # print(table_header_separator)

        print_validation_check_failed_comment = False
        for service_code in service_quotas:
            print(table_row_separator)
            for quota_code in service_quotas[service_code]:
                q_code = service_quotas[service_code][quota_code]['QuotaCode']
                q_name = service_quotas[service_code][quota_code]['QuotaName']
                validation = service_quotas[service_code][quota_code]['Validation']
                print(table_row_format.format(
                    col_1=service_code, col_1_width=width_column_1 - 1,
                    col_2=q_code, col_2_width=width_column_2,
                    col_3=q_name, col_3_width=width_column_3,
                    col_4=validation, col_4_width=width_column_4)
                )

        print("\n")
        print("Comments")
        print("--------")
        print("  * Validation = 'FAILED'")
        print("    There are some AWS service quotas not available/supported in that region.")
        print("")
        print("    Recommendation:")
        print("      - Check your AWS service quotas for that region.")
        print("      - Specify a different region.")
        print("")

