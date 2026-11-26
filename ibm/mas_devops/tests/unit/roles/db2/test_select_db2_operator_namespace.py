"""Unit tests for the db2 role's select-db2-operator-namespace.yml task file.

Regression tests for ibm-mas/cli#1496, where the Db2 upgrade failed when another product
(e.g. Cloud Pak for Data in cpd-operators) owned a second db2u-operator subscription.
"""

from utils import run_task, task_path

_TASK_FILE = task_path("db2", "upgrade", "select-db2-operator-namespace.yml")


def _run(fake_k8s, namespaces, db2_namespace="db2u"):
    return run_task(
        _TASK_FILE,
        fake_k8s,
        {"db2_operator_namespaces": namespaces, "db2_namespace": db2_namespace},
    )


def _output(result):
    return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"


class TestSelectDb2OperatorNamespace:

    def test_single_subscription_in_target_namespace(self, fake_k8s):
        """Test a single subscription in the target namespace is selected.

        GIVEN one db2u-operator subscription in the target db2_namespace
        WHEN the task runs
        THEN it succeeds and selects that namespace.
        """
        result = _run(fake_k8s, ["db2u"])
        assert result.returncode == 0, _output(result)
        assert "Selected Db2 operator namespace: db2u" in result.stdout

    def test_single_subscription_in_other_namespace(self, fake_k8s):
        """Test a single subscription outside the target namespace is still accepted.

        GIVEN one db2u-operator subscription in ibm-common-services and db2_namespace=db2u
        WHEN the task runs
        THEN it succeeds so the subscription can be migrated to db2_namespace.
        """
        result = _run(fake_k8s, ["ibm-common-services"])
        assert result.returncode == 0, _output(result)
        assert "Selected Db2 operator namespace: ibm-common-services" in result.stdout

    def test_multiple_subscriptions_one_in_target_namespace(self, fake_k8s):
        """Test multiple subscriptions are accepted when one is in the target namespace (cli#1496).

        GIVEN db2u-operator subscriptions in cpd-operators and db2u with db2_namespace=db2u
        WHEN the task runs
        THEN it succeeds and selects db2u.
        """
        result = _run(fake_k8s, ["cpd-operators", "db2u"])
        assert result.returncode == 0, _output(result)
        assert "Selected Db2 operator namespace: db2u" in result.stdout

    def test_multiple_subscriptions_none_in_target_namespace(self, fake_k8s):
        """Test multiple subscriptions are rejected when none is in the target namespace.

        GIVEN db2u-operator subscriptions in cpd-operators and ibm-common-services with db2_namespace=db2u
        WHEN the task runs
        THEN it fails with the multiple subscriptions message.
        """
        result = _run(fake_k8s, ["cpd-operators", "ibm-common-services"])
        assert result.returncode != 0
        assert "multiple subscriptions for DB2" in result.stdout

    def test_no_subscriptions(self, fake_k8s):
        """Test the task fails when no db2u-operator subscription exists.

        GIVEN no db2u-operator subscriptions
        WHEN the task runs
        THEN it fails with the operator not found message.
        """
        result = _run(fake_k8s, [])
        assert result.returncode != 0
        assert "DB2 operator was not found" in result.stdout
