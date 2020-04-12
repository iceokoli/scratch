# How to Create an EC2 Instance with Jupyter

logon onto your AWS EC2 instance with the following
``` zsh
ssh -i /path/my-key-pair.pem -L 8000:localhost:8888 ec2-user@ec2-198-51-100-1.compute-1.amazonaws.com
```

Spin up a Jupyter notebook
```zsh
jupyter notebook --no-browser --port 8888
```

Things to note:
- ensure your security group allows access from your current ip address

## User Data

This is to ensure python and jupyter are installed

```zsh
#!/bin/bash
sudo yum install python3 python3-virtualenv python3-pip -y
sudo pip3 install jupyter
```
