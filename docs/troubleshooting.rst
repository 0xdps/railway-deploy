Troubleshooting
===============

No RAILWAY_TOKEN found
----------------------

Symptom:

- CLI exits with token error.

Fix:

.. code-block:: bash

   export RAILWAY_TOKEN=<your_token>

Or ensure Railway CLI has a valid token in ``~/.railway/config.json``.

Environment not found
---------------------

Symptom:

- Error that the provided ``--env`` name does not exist.

Fix:

- Verify the environment name exactly matches Railway (case-sensitive).
- Confirm project ID is correct.

Service missing ``repo`` in config
----------------------------------

Symptom:

- Service deploy fails before creation.

Fix:

- Add ``repo: owner/repo`` under that service in config.

Variables not applied as expected
---------------------------------

Checklist:

- Confirm env file path using ``--env-file``.
- Ensure variable keys are present under ``vars.common``.
- Validate references use ``service.VARIABLE`` format.

Build triggered twice
---------------------

Symptom:

- One run appears to start duplicate builds.

Cause:

- Railway auto-deploy from GitHub + manual deploy trigger.

Fix:

- Use ``--no-deploy`` when only syncing config/variables.

Pylance import issues in local script mode
------------------------------------------

Symptom:

- ``Import railway_deploy... could not be resolved`` in editor.

Fix:

- Ensure ``.vscode/settings.json`` includes:

.. code-block:: json

   {
     "python.analysis.extraPaths": ["./src"]
   }

- Restart Python language server.
