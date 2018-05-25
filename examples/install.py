from remotepip import RemotePip

rpip = RemotePip(
    host='163.185.33.8',
    username='drillops',
    pkey_file_path='~/.ssh/planckbuilder.id_rsa'
)

rpip.install('saltypie')
