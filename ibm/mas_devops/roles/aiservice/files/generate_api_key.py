#!/usr/bin/env python3
# Licensed Materials - Property of IBM
# 5737-M66, 5900-AAA
# (C) Copyright IBM Corp. 2024 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication, or disclosure
# restricted by GSA ADP Schedule Contract with IBM Corp.

import secrets
import string
import random


def generate_api_key():
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for i in range(32))


if __name__ == "__main__":
    print(generate_api_key())
