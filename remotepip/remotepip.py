"""Module to manage pip package on remote hosts via SSH."""

import os
import base64
import time
import logging
import paramiko

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class RemotePip:
    """Manages pip package on remote hosts via SSH"""

    def __init__(self, host, username, port=22, password=None, pkey_file_path=None, b64_key=None):

        """
        Args:
            host (str): Host address
            username (str): Host user name.
            port (int): Port to connect to.
            password (str): User or private key password.
            pkey_file_path (str): Specify the path to a private key file. If key-based authentication is required.
            b64_key (str): Base 64 Private RSA key used as an alternative to the private key file path.
        """

        self.host = host
        self.username = username
        self.port = port
        self.password = password
        self.pkey_file_path = os.path.expanduser(pkey_file_path)
        self.b64_key = b64_key

        self.ssh_client = self._connect()

        self.pip_path = '/usr/local/bin/pip'

    def _connect(self):
        """
        Creates a SSH session with the host.

        Returns:
            paramiko.SSHClient
        """
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if self.pkey_file_path:
            private_key = paramiko.RSAKey.from_private_key_file(self.pkey_file_path, password=self.password)
        elif self.b64_key:
            decoded_key = base64.b64decode(self.b64_key)
            decoded_key = decoded_key.decode("utf-8")
            key_file = StringIO(decoded_key)
            private_key = paramiko.RSAKey.from_private_key(key_file)
            key_file.close()
        else:
            private_key = None

        ssh_client.connect(
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            pkey=private_key
        )

        return ssh_client

    def _run(self, cmd, retries=1, interval=10, sudo='sudo'):
        _in, _out, _err = self.ssh_client.exec_command(cmd)
        if _out.channel.recv_exit_status() > 0:
            err = _err.read().decode()
            print(err)
            if retries > 0:
                print("Remote command failed. Waiting {} seconds before retry...".format(interval))
                time.sleep(interval)
                self._run(cmd, retries=retries-1, interval=interval, sudo=sudo)
            else:
                # TODO raise exception
                exit(1)
        else:
            print(_out.read().decode())


    def install(self, pkg, version=None, args=None, retries=15, interval=10, sudo=True):
        """
        Install a python package on the remote host.

        Args:
            pkg (str): Package name.
            version (str): Package version.
            args (list, optional): Extra arguments to be passed to pip uninstall command.
            retries (int): Number of times to attempt to install the package.
            interval (int): How long to wait between installation retries.
            sudo (bool, optional): Defaults to True. Whether or not to run command as sudo.

        Returns:

        """

        prefix = 'sudo' if sudo else ''
        cmd = "{} {} install {} {}".format(prefix, self.pip_path, ' '.join(args or []), pkg)
        if version:
            cmd += '=={}'.format(version)

        # TODO switch to logging
        print('pip command:', cmd)
        self._run(cmd, retries=retries, interval=interval, sudo=sudo)

    def uninstall(self, pkg, args=None, sudo=True):
        """Uninstall a python packge from the remote host.

        Args:
            pkg (str): The package to be uninstalled.
            args (list, optional): Extra arguments to be passed to pip uninstall command.
            sudo (bool, optional): Defaults to True. Whether or not to run command as sudo.
        """

        prefix = 'sudo' if sudo else ''
        cmd = "{} {} uninstall {} -y {}".format(prefix, self.pip_path, ' '.join(args or []), pkg)
        # TODO switch to logging
        print('pip command:', cmd)
        self._run(cmd, sudo=sudo)

    def close(self):
        """Closes the ssh connection with the remote host."""
        self.ssh_client.close()
