
wipe_mongo
============

This role removes all databases associated with the specified MAS instance ID from the chosen MongoDB instance.

Role Variables
--------------

### instance_id
The specified MAS instance ID

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mongo_username
Mongo Username

- Environment Variable: `MONGO_USERNAME`
- Default Value: None

### mongo_password
Mongo password

- Environment Variable: `MONGO_PASSWORD`
- Default Value: None

### mongo_uri
Mongo URI

- Environment Variable: `MONGO_URI`
- Default Value: None

### config
Mongo Config, please refer to the below example playbook section for details

- **Required**
- Environment Variable: `CONFIG`
- Default Value: None

### certificates
Mongo Certificates, please refer to the below example playbook section for details

- **Required**
- Environment Variable: `CERTIFICATES`
- Default Value: None


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    instance_id: masinst1
    mongo_username: pqradmin
    mongo_password: xyzabc
    config:
      configDb: admin
      authMechanism: DEFAULT
      retryWrites: false
      hosts:
        - host: abc-0.pqr.databases.appdomain.cloud
          port: 32250
        - host: abc-1.pqr.databases.appdomain.cloud
          port: 32250
        - host: abc-2.pqr.databases.appdomain.cloud
          port: 32250
    certificates:
      - alias: ca
        crt: |
          -----BEGIN CERTIFICATE-----
          MIIDDzCCAfegAwIBAgIJANEH58y2/kzHMA0GCSqGSIb3DQEBCwUAMB4xHDAaBgNV
          BAMME0lCTSBDbG91ZCBEYXRhYmFzZXMwHhcNMTgwNjI1MTQyOTAwWhcNMjgwNjIy
          MTQyOTAwWjAeMRwwGgYDVQQDDBNJQk0gQ2xvdWQgRGF0YWJhc2VzMIIBIjANBgkq
          1eKI2FLzYKpoKBe5rcnrM7nHgNc/nCdEs5JecHb1dHv1QfPm6pzIxwIDAQABo1Aw
          TjAdBgNVHQ4EFgQUK3+XZo1wyKs+DEoYXbHruwSpXjgwHwYDVR0jBBgwFoAUK3+X
          Zo1wyKs+DEoYXbHruwSpXjgwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOC
          doqqgGIZ2nxCkp5/FXxF/TMb55vteTQwfgBy60jVVkbF7eVOWCv0KaNHPF5hrqbN
          i+3XjJ7/peF3xMvTMoy35DcT3E2ZeSVjouZs15O90kI3k2daS2OHJABW0vSj4nLz
          +PQzp/B9cQmOO8dCe049Q3oaUA==
          -----END CERTIFICATE-----
  roles:
    - ibm.mas_devops.wipe_mongo

```

License
-------

EPL-2.0
