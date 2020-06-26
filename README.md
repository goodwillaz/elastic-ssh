## AWS EC2 SSH Utility

This is a command line utility to assist in connecting to EC2 via SSH using IAM and [EC2 Instance Connect](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Connect-using-EC2-Instance-Connect.html).  It also allows connecting to private instances via a Bastion Host if you have one configured in your VPC. This currently only works on *nix command lines with the OpenSSH client installed at /usr/bin/ssh.

### AWS Setup

Follow Amazon's [documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-connect-set-up.html) on setting up Instance Connect.

### Installation

Install via you're favorite method for installing Python-based CLI tools: [pip](https://pip.pypa.io/en/stable/), [pipenv](https://pypi.org/project/pipenv/), [easy_install](https://setuptools.readthedocs.io/en/latest/easy_install.html), etc.  I recommend using `pipenv`, creating an environment just for this tool and then creating a symlink from the virtualenv bin directory to a directory on your PATH.

```bash
$ pipenv install -e git+https://github.com/goodwillaz/elastic-ssh\#egg=elastic-ssh
$ sudo ln -s `pipenv --venv`/bin/aws-ec2 /usr/local/bin/aws-ec2
```

Once you've installed the utility, you'll need to configure it.  It uses AWS's Boto library which means it will look in the standard places for AWS Credentials.  To configure the utility with an optional profile name (default is `default`):

```bash
$ aws-ec2 [--profile <profile>] configure
```

Note that the private key you are prompted for does not need to be the key-pair you used to create your EC2 instance.  You can use any RSA based key-pair. The public key must sit in the same folder as the private key and have a `.pub` suffix to it.

### Usage

Simply type `aws-ec2 ssh` on the command line; you'll be provided with a list of instances (and their names) for easy selection.  Select the instance you'd like to connect to and you'll instantly be connected!

For help, simply run `aws-ec2 --help` or `aws-ec2 <command> --help`

### Environment Variable Support

All of the command line flags can be specified as environment variables (if you need to):

* AWS_EC2_DEBUG
* AWS_EC2_PROFILE
* AWS_EC2_SSH_USER
* AWS_EC2_SSH_PORT
* AWS_EC2_SSH_KEY
* AWS_EC2_SSH_COMMAND

### License

See the [LICENSE](LICENSE.md) file for license rights and limitations (BSD 3-clause).
