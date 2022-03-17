# This script allows you to record the results of the pipeline in a MongoDb database.
# To enable this capability you must set additional environment variables as follows:
#
# - DEVOPS_MONGO_URI="mongodb://user:password@host1:port1,host2:port2/admin?ssl=true&ssl_cert_reqs=CERT_NONE"
#
import os
import xml.etree.ElementTree as ET
import sys
from datetime import datetime
from pymongo import MongoClient
from xmljson import Yahoo
import glob

if __name__ == "__main__":
    # Initialize the properties we need
    instanceId = os.getenv("MAS_INSTANCE_ID")
    productId = "ibm-mas-devops"
    build = os.getenv("TRAVIS_BUILD_NUMBER")
    suite = os.getenv("JUNIT_SUITE_NAME", "")
    junitOutputDir = os.getenv("JUNIT_OUTPUT_DIR", "/tmp")

    channelId = "n/a"
    version = "unknown"

    if suite == "":
        print ("Results not recorded because JUNIT_SUITE_NAME is not defined")
        exit(0)

    if instanceId is None:
        print("Results not recorded because MAS_INSTANCE_ID env var is not set")
        exit(0)
    if build is None:
        print("Results not recorded because TRAVIS_BUILD_NUMBER env var is not set")
        exit(0)

    runId = f"{instanceId}:{build}"
    resultId = f"{instanceId}:{build}:{productId}:{suite}"

    resultFiles = glob.glob(f'{junitOutputDir}/*.xml')
    for resultfile in resultFiles:
        try:
            tree = ET.parse(resultfile)
        except (IOError, ET.ParseError) as e:
            print(f"Functional Test result file was not generated for {suite} in build {build}")
            sys.exit(0)

        root = tree.getroot()

        if "DEVOPS_MONGO_URI" in os.environ and os.environ['DEVOPS_MONGO_URI'] != "":
            # Convert junit xml to json
            bf = Yahoo(dict_type=dict)
            resultDoc = bf.data(root)

            for testcase in resultDoc["testsuites"]["testsuite"]["testcase"]:
                testcase["name"] = testcase["name"].replace("[localhost] localhost: ", "")
                testcase["classname"] = testcase["classname"].split("ibm/mas_devops/")[1]
            # Enrich document
            resultDoc["_id"] = resultId
            resultDoc["build"] = build
            resultDoc["suite"] = suite
            resultDoc["timestamp"] = datetime.utcnow()
            resultDoc["target"] = {
                "instanceId": instanceId,
                "build": build,
                "productId": productId,
                "channelId": channelId,
                "version": version
            }

            # Look for existing summary document
            suiteSummary = {
                "tests" : int(resultDoc["testsuites"]["testsuite"]["tests"]),
                "errors" : int(resultDoc["testsuites"]["testsuite"]["errors"]),
                "name" : suite,
                "skipped" : int(resultDoc["testsuites"]["testsuite"]["skipped"]),
                "time" : float(resultDoc["testsuites"]["testsuite"]["time"]),
                "failures" : int(resultDoc["testsuites"]["testsuite"]["failures"])
            }

            # Connect to mongoDb
            client = MongoClient(os.getenv("DEVOPS_MONGO_URI"))
            db = client.masfvt

            # Update or create summary doc
            result1 = db.runsv2.find_one_and_update(
                {"_id": runId},
                {
                    '$setOnInsert': {
                        "_id": runId,
                        "timestamp": datetime.utcnow(),
                        "target": {
                            "instanceId": instanceId,
                            "buildId": build
                        }
                    },
                    '$set': {
                        f"products.ibm-mas-devops.productId": productId,
                        f"products.ibm-mas-devops.channelId": channelId,
                        f"products.ibm-mas-devops.version": version,
                        f"products.ibm-mas-devops.results.{suite}": suiteSummary
                    }
                },
                upsert=True
            )

            # Replace or create result doc
            result2 = db.resultsv2.replace_one(
                {"_id": resultId},
                resultDoc,
                upsert=True
            )
            print ("Pipeline results saved to MongoDb (v2 data model)")
        else:
            print("Pipeline results not recorded as DEVOPS_MONGO_URI is not defined")
