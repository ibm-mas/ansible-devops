# Python Docstrings Guidelines
Docstrings are inline documentation for Python modules, classes, and functions. They are:

- Embedded directly in the source code
- Used to generate API documentation automatically
- Essential for code maintainability and usability


## Writing Style

1. **Be Concise**: Use clear, direct language
2. **Be Specific**: Provide concrete details, not vague descriptions
3. **Be Consistent**: Use the same terminology throughout
4. **Be Complete**: Document all parameters, returns, and exceptions
5. **Be Accurate**: Keep documentation in sync with code, and do not make assumptions when generating documentation


## Google Style Docstrings
All Python code MUST use **Google-style docstrings**. This style is:

- Human-readable in source code
- Well-supported by documentation tools (mkdocstrings, Sphinx)
- Clear and consistent
- Easy to parse and validate


## Required Docstring Structure
A complete docstring includes these sections **in order**:

1. **Summary Line**:
   - One line describing what the function does
   - Use imperative mood ("Create" not "Creates")
   - No period at the end

2. **Extended Description**:
   - Provide additional context about behavior
   - Explain complex logic or side effects
   - Can span multiple paragraphs
   - Separate from summary with blank line

3. **Args Section**:
   - Use `Args:` as the section header
   - Format: `param_name (type): Description`
   - For optional parameters: `param_name (type, optional): Description. Defaults to value.`
   - Multi-line descriptions should be indented to align with the first line
   - Include type in parentheses after parameter name
   - Always specify "Defaults to X" for optional parameters

4. **Returns Section**:
   - Format: `type: Description of return value`
   - Be specific about what is returned

5. **Raises Section**:
   - Format: `ExceptionType: When this exception occurs`
   - List all exceptions that may be raised
   - Explain the conditions that trigger each exception

Do **NOT** include these sections: `Note`, `Warning`, or `Example`; any notes or warnings should be part of the extended description.


## Module Docstrings
Every Python module MUST have a module-level docstring.

```python
"""Brief module description in one line.

Extended description providing more context about what this module
provides, its key components, and how it fits into the larger system.
Can span multiple paragraphs if needed.
"""
```


## Class Docstrings
Every class MUST have a docstring describing its purpose.

```python
class ClassName:
    """Brief class description.

    Extended description explaining the class purpose, key responsibilities,
    and important usage patterns.

    Attributes:
        attribute_name: Description of class or instance attribute.
        another_attribute: Description of another attribute.
    """
```


## Function and Method Docstrings
All public functions and methods MUST have docstrings following this exact format.

```python
def create_subscription(
    dynClient: DynamicClient,
    namespace: str,
    packageName: str,
    packageChannel: Optional[str] = None,
    catalogSource: Optional[str] = None,
    catalogSourceNamespace: str = "openshift-marketplace",
    config: Optional[dict] = None,
    installMode: str = "OwnNamespace",
    installPlanApproval: Optional[str] = None,
    startingCSV: Optional[str] = None
) -> Subscription:
    """Create or update an operator subscription in a namespace.

    Automatically detects default channel and catalog source from PackageManifest if not provided.
    Ensures an OperatorGroup exists before creating the subscription.

    When installPlanApproval is set to "Manual" and a startingCSV is specified, this function will
    automatically approve the InstallPlan for the first-time installation to move to that startingCSV.
    Subsequent upgrades will still require manual approval.

    Args:
        dynClient (DynamicClient): OpenShift Dynamic Client
        namespace (str): The namespace to create the subscription in
        packageName (str): Name of the operator package (e.g., "ibm-mas-operator")
        packageChannel (str, optional): Subscription channel. Auto-detected if None. Defaults to None.
        catalogSource (str, optional): Catalog source name. Auto-detected if None. Defaults to None.
        catalogSourceNamespace (str, optional): Namespace of the catalog source. Defaults to "openshift-marketplace".
        config (dict, optional): Additional subscription configuration. Defaults to None.
        installMode (str, optional): Install mode for the OperatorGroup. Defaults to "OwnNamespace".
        installPlanApproval (str, optional): Install plan approval mode ("Automatic" or "Manual"). Defaults to None.
        startingCSV (str, optional): The specific CSV version to install. When combined with Manual approval,
            the first InstallPlan to this CSV will be automatically approved. Required when installPlanApproval is "Manual". Defaults to None.

    Returns:
        Subscription: The created or updated subscription resource

    Raises:
        OLMException: If the package is not available in any catalog, or if installPlanApproval is "Manual" without a startingCSV
        NotFoundError: If resources cannot be created
    """
```
