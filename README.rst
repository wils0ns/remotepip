Remote pip package management
=============================

Installation
============

.. code-block:: bash

   pip install remotepip


Usage example
=============

Code:

.. code-block:: python

   from remotepip import RemotePip

   rpip = RemotePip(
       host='10.0.0.0',
       username='myuser',
       pkey_file_path='~/.ssh/myuser.id_rsa'
   )

   rpip.install('saltypie')

