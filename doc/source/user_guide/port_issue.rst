.. _ref_port_issue:

Port connection issues
======================

Overview
--------

When using Python scripts in Motor-CAD either as standalone applications or as part of an adaptive template,
you may encounter a connection error:

.. code-block:: text

    Failed to connect to Motor-CAD instance: port=<port number>

.. image:: /_static/issue.png
    :width: 400
This issue typically arises due to organizational IT security settings that prevent the RPC (Remote Procedure Call)
client from connecting to the Motor-CAD instance.

Below are several troubleshooting measures you can apply to resolve this issue.


Solution 1: Configure RPC client settings
------------------------------------------

Add the following import statements and configuration at the beginning of your Python script:

.. code:: python

    from ansys.motorcad.core.rpc_client_core import TRY_RESOLVE_LOCALHOST, SERVER_IP

    TRY_RESOLVE_LOCALHOST = False
    SERVER_IP = "http://127.0.0.1"

This disables localhost resolution attempts and explicitly sets the server connection to the local machine,
which can help bypass certain network security restrictions.


Solution 2: Run Motor-CAD as Administrator
--------------------------------------------

Motor-CAD may require elevated privileges to establish the RPC connection:

1. Locate the Motor-CAD executable file
2. Right-click on the executable
3. Select "Run as administrator"
   

This grants Motor-CAD the necessary permissions to communicate with the Python script.


Solution 3: Disable Automatic Proxy Setup
-------------------------------------------

Proxy settings configured at the system level may interfere with the RPC connection:

1. Open **Settings** and navigate to **Network & Internet**
2. Locate **Proxy settings**
3. Turn off **Automatic proxy setup**

This prevents the system from automatically routing the localhost connection through a proxy server.


Solution 4: Test the RPC Connection
------------------------------------

Verify that the RPC connection is working by testing it directly:

1. Open a web browser
2. Navigate to: ``localhost:<port_number>/jsonrpc``

   Where ``<port_number>`` is the port number listed under **Defaults > Automation** in Motor-CAD

.. image:: /_static/automation.png
    :width: 400
3. You should see output similar to the following, indicating the connection is working:

.. image:: /_static/json.png
    :width: 600

If you see this output, the issue is on the Python script side. If not, continue to Solution 5.


Contact Support with Diagnostics
----------------------------------------------

If the issue persists after trying the above solutions:

1. Collect the output from the browser test in Solution 4
2. Locate Motor-CAD log files at:

   .. code-block:: text

       C:\Users\<your_PC_username>\AppData\Roaming\Ansys\v261\MotorCAD\RPCLogs

   Replace ``<your_PC_username>`` with your actual Windows username.

3. Contact Motor-CAD support and provide:
   - The browser test output from Solution 4
   - The log files from the RPCLogs directory
   - A description of the troubleshooting steps you have already attempted

The log files will help the support team identify the root cause of the connection issue.
