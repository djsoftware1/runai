## DJ Software Code Automation

Run:

```
pip install -r requirements.txt
```

To run:

```
python agent.py
```

Design thoughts on main task types:

## Main Task Types:

1. **Code Generation**
   - Add new code, such as classes, functions, or entire modules.
   - Example: Automatically generate a new Vec3d class in vec3d.h/cpp files.

2. **Code Enhancement**
   - Extend existing files by adding new functionalities, methods, or classes.
   - Implement stubs or abstract methods.
   - Example: Add new methods to an existing class or implement TODOs.

3. **Code Refactoring**
   - Modify existing code to improve structure, performance, readability, or maintainability without changing its external behavior.
   - Example: Refactor specific patterns, optimize algorithms, or update to newer syntax.

4. **Build and Test Automation**
   - Compile code, run build processes, and execute automated tests.
   - Analyze build logs and test reports for errors or warnings.
   - Example: Run unit tests, integration tests, and analyze results.

5. **Code Analysis and Linting**
   - Perform static code analysis for potential issues.
   - Enforce coding standards and style guides.
   - Example: Run linters and format code according to PEP 8 for Python.

6. **Documentation Generation**
   - Auto-generate documentation from code comments and docstrings.
   - Keep documentation in sync with code changes.
   - Example: Generate API documentation using tools like Doxygen or Sphinx.

7. **Dependency Management**
   - Update or manage external libraries and dependencies.
   - Ensure compatibility and security of dependencies.
   - Example: Update packages to the latest versions while ensuring compatibility.

8. **Version Control Operations**
   - Automate commits, merges, branches, and other version control operations.
   - Handle version tagging and release management.
   - Example: Auto-commit changes after successful tests and linting.

9. **Deployment and Release Automation**
   - Automate the deployment of code to production or staging environments.
   - Manage release cycles and deployment schedules.
   - Example: Automatically deploy code to a staging server after passing CI/CD pipelines.
