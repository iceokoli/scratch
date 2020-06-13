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

## Get data onto the instance
```zsh
scp -i /path/my-key-pair.pem /path/SampleFile.txt ec2-user@ec2-198-51-100-1.compute-1.amazonaws.com:~
```
## Get data From S3 bucket
- Set up the aws cli on your EC2 instance
```zsh
[ec2-user ~]$ aws s3 sync s3://remote_S3_bucket local_directory
```

## User Data

This is to ensure python and jupyter are installed, if using an ubuntu AMI.

```zsh
#!/bin/bash
sudo apt update
sudo apt install python3-pip -Y
pip3 install jupyter --user
```
