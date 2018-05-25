from remotepip import RemotePip

rpip = RemotePip(
    host='10.10.0.10',
    username='myuser',
    pkey_file_path='~/.ssh/mykey.id_rsa'
)

rpip.install('saltypie')
