#!/bin/bash

# 1 Generate self signed root CA cert
openssl req -config openssl.cnf -days 3650 -nodes -x509 -newkey rsa:2048 -subj "/C=US/ST=NY/L=New York/O=Example, LLC/CN=Mongo CA" -extensions v3_ca -keyout ca.key -out ca.pem

# 2 Generate server cert to be signed
openssl req -config openssl.cnf -nodes -newkey rsa:2048 -keyout server.key -out server.csr

# 3 Sign the server cert
openssl x509 -req -in server.csr -days 3650 -CA ca.pem -CAkey ca.key -CAcreateserial -extensions v3_req -extfile openssl.cnf -out server.crt

# 4 Create server PEM file
cat server.key server.crt > mongodb.pem

# 5 Generate client cert to be signed
openssl req -config openssl.cnf -subj "/C=US/ST=NY/L=New York/O=Example, LLC/CN=Mongo Client" -nodes -newkey rsa:2048 -keyout client.key -out client.csr

# 6 Sign the client cert
openssl x509 -req -in client.csr -days 3650 -CA ca.pem -CAkey ca.key -CAserial ca.srl -extensions v3_clnt -extfile openssl.cnf -out client.crt

# 7 Create client PEM file
cat client.key client.crt > client.pem
