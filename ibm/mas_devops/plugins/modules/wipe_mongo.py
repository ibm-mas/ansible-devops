# coding: utf-8 -*-
# # (C) Copyright IBM Corp. 2020 All Rights Reserved.
# Eclipse Public License 2.0 (see https://spdx.org/licenses/EPL-2.0.html)

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: wipe_mongo

short_description: Wipe all MAS databases in MongoDb instance

version_added: "1.0.0"

description: Removes all databases associated with the specified MAS instance ID from the chosen MongoDb instance.

options:
    instance_id:
        description: MAS instance ID.
        required: true
        type: str
    mongo_uri:
        description: Mongo URI.
        required: true
        type: str
    config:
        description: true
        required: true
        type: complex
    certificates:
        description: true
        required: true
        type: complex

author:
    - Tom Klapiscak (@tomklapiscak)
    - David Parker (@durera)
'''

from ansible.module_utils.basic import AnsibleModule

import pymongo
import tempfile
import os

def main():
    fields = dict(
        instance_id = dict(
            type = "str",
            required = True,
        ),

        mongo_uri = dict(
            type = "str",
            no_log = True,
        ),

        config = dict(
            type = "dict",
            required_if = [
                ('authMechanism', 'DEFAULT', ('configDb', ))
            ],
            options = dict(
                hosts = dict(
                    type = "list",
                    elements = "dict",
                    options = dict(
                        host = dict(
                            type = "str",
                            required = True
                        ),
                        port = dict(
                            type = "int",
                            required = True
                        )
                    ),
                    required = True
                ),
                username = dict(
                    type = "str",
                    required = True,
                    no_log = True,
                ),
                password = dict(
                    type = "str",
                    required = True,
                    no_log = True,
                ),
                configDb = dict(
                    type = "str",
                    no_log = True,
                ),
                authMechanism = dict(
                    type = "str",
                    choices = ['DEFAULT', 'PLAIN'],
                    required = False,
                    default = "DEFAULT",
                ),
            )
        ),

        certificates = dict(
            type = "list",
            elements = "dict",
            options = dict(
                crt = dict(
                    type="str",
                    required = True
                ),
                alias = dict(
                    type = "str",
                    required = False
                )
            ),
            required = False
        )
    )
    module = AnsibleModule(
        argument_spec=fields,
        supports_check_mode = True,
        required_one_of = [
            ('mongo_uri', 'config')
        ],
        mutually_exclusive = [
            ('mongo_uri', 'config')
        ],
    )

    # Construct Mongo URI
    params_config = module.params.get('config')
    if params_config is not None:

        mongo_uri = 'mongodb://'

        # Add creds
        mongo_uri += f"{params_config['username']}:{params_config['password']}@"

        # Add hosts
        nodes = []
        for host in params_config['hosts']:
            nodes.append(f"{host['host']}:{host['port']}")
        mongo_uri += ','.join(nodes)

        # Add options
        mongo_uri += "/?"

        # LDAP
        if params_config['authMechanism'] == 'PLAIN':
            mongo_uri += f"authSource=$external&authMechanism=PLAIN"
        # Regular
        else:
            auth_source = params_config['configDb']
            mongo_uri += f"authSource={auth_source}"
    else:
        mongo_uri = module.params['mongo_uri']


    ca_file = None
    mongo_client = None
    try:
        # Write certificates out to a (temporary) file so we can pass them into pymongo
        if module.params['certificates'] is not None:
            with tempfile.NamedTemporaryFile(delete=False) as ca_file:
                for certificate in module.params['certificates']:
                    ca_file.write(bytes(certificate['crt'], 'utf-8'))
                    ca_file.write(b'\n')

        try:
            mongo_client = pymongo.MongoClient(
                mongo_uri,
                tls = True,
                tlsCAFile = ca_file.name if ca_file is not None else None,
                tlsAllowInvalidCertificates = False
            )
        except Exception as ex:
            module.fail_json(msg = f"Unable to initialize mongo client: {str(ex)}")


        try:
            inst_id = module.params['instance_id']

            # Drop databases as defined in https://github.ibm.com/maximoappsuite/coreapi/blob/bbd6607a42f0cb4d645ce59dfd4ec75d6567832c/image/coreapi/src/wipeData.py#L133
            db_names = mongo_client.list_database_names()

            dbs_to_drop = [
                f'mas_{inst_id}_core',
                f'mas_{inst_id}_catalog',
                f'mas_{inst_id}_adoptionusage'
            ]

            # Map to a list of (db_name, exists?) tuples so we can return information
            # about what was *actually* dropped in the results
            db_statuses = list(
                map(
                    lambda db_name :
                        dict(
                            name = db_name,
                            exists = db_name in db_names
                        ),
                    dbs_to_drop
                )
            )

            # discover any iot databases for this instance
            # (these implicitly exist since they were derived from the actual list of db names)
            for db_name in db_names:
                if db_name.startswith(f"iot_{inst_id}_"):
                    db_statuses.append(
                        dict(
                            name =  db_name,
                            exists = True
                        )
                    )

            if module.check_mode:
                for db_status in db_statuses:
                    # In check mode, we'll assume if the database exists then the drop will work
                    db_status['dropped'] = db_status['exists']
            else:
                for db_status in db_statuses:
                    if db_status['exists']:
                        try:
                            mongo_client.drop_database(db_status['name'])
                            db_status['dropped'] = True
                        except Exception as ex:
                            db_status['dropped'] = True
                            db_status['error'] = f"Failed to drop database: {str(ex)}"
                    else:
                        db_status['dropped'] = False


            # report failure iff at least one database failed to drop
            failed = False
            for db_status in db_statuses:
                if db_status.get('error') is not None:
                    failed = True
                    break


            if failed:
                module.fail_json(
                    msg = f"Failed to drop at least one database. See db_statuses for details.",
                    mongo_uri=mongo_uri,
                    db_statuses=db_statuses,
                )
            else:
                # changed is true iff at least one database was dropped
                changed = False
                for db_status in db_statuses:
                    if db_status['dropped']:
                        changed = True
                        break

                module.exit_json(
                    changed = changed,
                    mongo_uri=mongo_uri,
                    db_statuses=db_statuses,
                )

        except Exception as ex:
            module.fail_json(msg = f"Unexpected error: {str(ex)}")
    finally:
        if mongo_client is not None:
            mongo_client.close()

        if ca_file is not None:
            os.remove( ca_file.name )


if __name__ == '__main__':
    main()
