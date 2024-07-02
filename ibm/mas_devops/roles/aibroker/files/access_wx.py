#!/usr/bin/env python3
# Licensed Materials - Property of IBM
# 5737-M66, 5900-AAA
# (C) Copyright IBM Corp. 2024 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication, or disclosure
# restricted by GSA ADP Schedule Contract with IBM Corp.


from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
import sys

GenParams().get_example_values()

generate_params = {GenParams.MAX_NEW_TOKENS: 25}
try:
    model = Model(
        model_id=ModelTypes.FLAN_UL2,
        params=generate_params,
        credentials={"apikey": sys.argv[1], "url": sys.argv[2]},
        project_id=sys.argv[3],
    )
    print("You enter the valid watsonx.ai credential.")
    sys.exit(0)
except Exception as e:
    print("You enter invalid watsonx.ai credential.")
    print(e)
    sys.exit(1)
