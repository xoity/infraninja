'''

this file is used to define the hosts variable as a list of tuples

NOTE: THE HOST CONFIGURATIONS ARE DEFINED IN THIS FILE, AND MUST BE IN TUPLES, AND GIVEN DATA IN A DICTIONARY STLE, (if youre using ssh users and keys for example.)

'''

# defined the hosts variable as a list of tuples
hosts = [
    ("10.1.10.134", {"ssh_user": "vagrant", "ssh_key": "~/.ssh/id_rsa"}), # ubuntu key
]
