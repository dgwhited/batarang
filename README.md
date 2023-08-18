# batarang

It goes out and gets stuff and comes back.

## Get set up


Clone and run locally --profile is optional, should also accept creds exported to the local env

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.batarang (nodes | latest | sechub) --profile yourawsprofile 
```

Install from src

```
python3 -m venv .venv
source .venv/bin/activate
pip install -U git+https://code.batcave.internal.cms.gov/batcave-watchtower/batarang.git
batarang (nodes | latest | sechub) --profile yourawsprofile
```

## Running the tool

Options in square brackets are optional.


Print the help file
```
batarang [--help] [--version]
```

Print the nodes in an account and their AMI date
```
batarang nodes  [--order-by order] [--profile PROFILE] [--csvoutputfile CSV_OUT]
```

Print information in JSON format about the latest AMI. Defaults to EKS version 1.22
```
batarang latest [--eksversion eksversion] [--profile PROFILE] [--csvoutputfile CSV_OUT]
```

Print Security Hub information - severity defaults to all, but can be any combination of CRITICAL, HIGH, MEDIUM, LOW, INFORMATIONAL. A single product name can also be specified.
```
batarang sechub [--severity severity] [--profile PROFILE] [--csvoutputfile CSV_OUT] [--productname productname]
```

Print Guardduty information
```
batarang guardduty [--profile PROFILE] [--csvoutputfile CSV_OUT]
```

For currently running images on a Kubernetes cluster, you should have an updated and default context in kubeconfig
```
aws --profile AWSPROFILE eks update-kubeconfig --name CLUSTERNAME --region REGION
batarang k8s [--csvoutputfile CSV_OUT]
```

To list pipeline tools in artifactory
```
batarang artifactory [--csvoutputfile CSV_OUT]
```
It will prompt for your EID and password.


