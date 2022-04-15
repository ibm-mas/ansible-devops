import re
import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import ParamValidationError
import logging
from pprint import pprint


class IAMHelper():
    '''
    Object used to access the AWS IAM service
    '''

    def __init__(self, aws_config):
        self.__iam_session = self.__create_client_session(aws_config)
        self.__iam_resource = self.__create_resource_session(aws_config)

    def __create_session(self, aws_config):

        # Create an AWS session client
        try:
            aws_session = boto3.session.Session(
                aws_access_key_id = aws_config['access_key'],
                aws_secret_access_key = aws_config['secret_access_key'],
                region_name = aws_config['region']
            )
            return aws_session
        except ClientError as e:
            # logging.error(e)
            print("  * The AWS client could not be created.")
            print('  * Please, try again.')
            exit(1)

    def __create_client_session(self, aws_config):

        # Create an AWS session client
        try:
            aws_session = self.__create_session(aws_config)
    
            iam_session = aws_session.client('iam')
            return iam_session
        except ClientError as e:
            # logging.error(e)
            print("  * The AWS client could not be created.")
            print('  * Please, try again.')
            exit(1)

    def __create_resource_session(self, aws_config):

        # Create an AWS session client
        try:
            aws_session = self.__create_session(aws_config)
            iam_resource = aws_session.resource('iam')
            return iam_resource
        except ClientError as e:
            # logging.error(e)
            print("  * The AWS resource could not be created.")
            print('  * Please, try again.')
            exit(1)


    # helpers
    def get_groups_from_username(self, username):
        group_names = []
        client = self.__iam_session 

        try:
            groups_json = client.list_groups_for_user(UserName=username)['Groups']
            for group in groups_json:
                group_names.append(group['GroupName'])
        except ClientError as e:
            # logging.error(e)
            print('  * No permissions to read the groups for users.')
        return group_names

    def get_user_policies(self, username):
        policy_names = []
        client = self.__iam_session 

        try:
            attached_user_policies = (client.list_attached_user_policies(UserName=username)['AttachedPolicies'])
            for policy in attached_user_policies:
                policy_names.append(policy['PolicyName'])
            user_policies = (client.list_user_policies(UserName=username)['PolicyNames'])
            for policy in user_policies:
                policy_names.append(policy)
        except ClientError as e:
            # logging.error(e)
            print('  * No permissions to read policies attached to the user.')
        return policy_names

    def get_group_policies(self, user_groups):
        policy_names = []
        client = self.__iam_session 

        try:
            for group in user_groups:
                attached_group_policies = (client.list_attached_group_policies(GroupName=group)['AttachedPolicies'])
                for policy in attached_group_policies:
                    policy_names.append(policy['PolicyName'])
                group_policies = (client.list_group_policies(GroupName=group)['PolicyNames'])
                for policy in group_policies:
                    policy_names.append(policy)
        except ClientError as e:
            # logging.error(e)
            print('  * No permissions to read group policies.')
        return policy_names

    def get_user_and_group_policies(self, username, user_groups):
        policy_names = []
        client = self.__iam_session 

        try:
            policy_names = self.get_group_policies(user_groups)
            policy_names+= self.get_user_policies(username)
            return policy_names
        except ClientError as e:
            # logging.error(e)
            print("  * AccessDenied")
            print('  * You need to change the users permissions and try again.')
            print(e)
            exit(1)

    def get_user_name(self):
        resource = []

        try:
            targetArn = self.__iam_resource.CurrentUser().arn
            targetUser = targetArn.split('/')[-1]
            return targetUser
        except ClientError as e:
            # logging.error(e)
            print("  * AccessDenied")
            print("  * To run this check the user needs the >iam:GetUser< permissiom.")
            print(e)
            exit(1)

    from typing import List

    def blocked(self, user, actions: List[str]) -> List[str]:
        try:
            if not actions:
                return []
            actions = list(set(actions))
            results = self.__iam_session.simulate_principal_policy(
                PolicySourceArn=self.__iam_resource.CurrentUser().arn,
                ActionNames=actions
            )['EvaluationResults']
            return sorted([result['EvalActionName'] for result in results
                if result['EvalDecision'] != "allowed"])
        except ClientError as e:
            # logging.error(e)
            print("  * AccessDenied")
            print("  * To run this check the user needs the >iam:SimulatePrincipalPolicy< permissiom.")
            print(e)
            exit(1)
        except ParamValidationError as e:
            # logging.error(e)
            print("  * Permission validation aborted.")
            print("  * Check your permision_actions.txt file.")
            print(e)
            exit(1)
