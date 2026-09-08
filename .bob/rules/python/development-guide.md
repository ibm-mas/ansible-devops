# Python Code Development Guide

## Black and Flake8
All changes made to Python code must be validated by running `black` and `flake8` against the changed files:

```bash
black src/mas/toolchain/github/issues.py src/mas/toolchain/github/utils.py && \
flake8 src/mas/toolchain/github/issues.py src/mas/toolchain/github/utils.py
```

**If either of these tools are unavailable you must refuse to continue until the developer makes them available in your environment**


## Variable, Function, and Class Naming
Use `camelCase` for variable and function names, and `PascalCase` for class names.


## Copyright Headers
**Product Code** must carry a copyright header as follows:

```python
# -----------------------------------------------------------
# Licensed Materials - Property of IBM
# <PID1>, <PID2>
# (C) Copyright IBM Corp. <YEAR> All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication, or disclosure
# restricted by GSA ADP Schedule Contract with IBM Corp.
# -----------------------------------------------------------
```

Where `<PID>` is an IBM product ID, and `<YEAR>` is one of the following:
- If the file was created in the current year, use the current year, e.g. `2026`
- If the file was created and updated in different years, record both e.g. `2020, 2026`

**Important:** When updating any source file, update the copyright year if it does not match the current year - otherwise it will result in a build error in the CI/CD pipeline.

Use the `.copyright.yml` configuration file to determine the PID(s) for copyright headers, and guide where copyright headers are required.

```yaml
copyright:
  validate: true
  pid: 5737-M66, 5900-AAA
  ignore:
    - tests/*
```

Note:
- In most cases copyright headers are not required for test files, and will be listed in the `.copyright.yml` file's `ignore` list.
- In non-product code copyright headers are not required, in this case validate will be set to `false` in the `.copyright.yml` file.
- Never modify the `.copyright.yml` file without explicit instruction to do so.
- This file must always exist in the repository root directory. If it is missing, help the developer create it.


## Import Organization
Organize imports in three groups:

```python
# 1. Standard library
import logging
import os
from datetime import datetime
from typing import Optional, Dict, List

# 2. Third-party packages
import requests
from kubernetes import client
from pymongo import MongoClient

# 3. Local imports
from mas.utils import exceptions
from mas.utils import violations
```

**Do not use inline imports**, all imports must be listed at the top of the file.


## Logger Declaration
Declare logger after imports:

```python
import logging

from mas.utils import exceptions

logger = logging.getLogger(__name__)
```


## Type Hints
Always include type hints in function signatures:

```python
# ✅ CORRECT
def process_user(
    user_id: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process user data."""
    pass

# ❌ INCORRECT - Missing type hints
def process_user(user_id, options=None):
    """Process user data."""
    pass
```

## Constants
Use uppercase for constants:

```python
# ✅ CORRECT
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
API_VERSION = "v1"

# ❌ INCORRECT
default_timeout = 30
maxRetries = 3
```


## No Sensitive Data in Logs
```python
# ✅ CORRECT
logger.info(f"User {user_id} authenticated successfully")
logger.debug(f"Processing request for user {user_id}")

# ❌ INCORRECT - Logging sensitive data
logger.info(f"User password: {password}")
logger.debug(f"API key: {api_key}")
```
