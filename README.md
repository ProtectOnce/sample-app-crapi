# sample-app-crapi
This repository serves as a starting point to deploy crAPI, an intentionally vulnerable application along with scripts to generate automated traffic for demonstration purposes.

**WARNING: Please ensure that this application is not deployed on a production server as it is affected by multiple security vulnerabilities and is meant for demonstration purposes only .** 

### Setup

1. Install [Helm](https://helm.sh/docs/intro/install/#through-package-managers).
2. Install Python.
    ```bash
    sudo apt-get install python3.10
    ```
2. Install pip.
    ```bash
    python3 -m pip install --user --upgrade pip
    ```
3. Clone the repository.
    ```bash
    git clone https://github.com/ProtectOnce/sample-app-crapi
    ```
4. Install the required packages.
    ```bash
    cd sample-app-crapi && pip install -r requirements.txt
    ```

### crAPI Deployment

To setup crAPI, simply run `deploy-crapi.sh`, which will deploy the application in the connected k8s cluster.

For **EKS deployments**, the following additional commands will have to be run, providing the cluster names and regions wherever applicable.

`eksctl utils associate-iam-oidc-provider --region=<REGION-HERE> --cluster=<CLUSTER-NAME-HERE> --approve`

```
eksctl create iamserviceaccount \
  --name ebs-csi-controller-sa \
  --namespace kube-system \
  --cluster <CLUSTER-NAME-HERE> \
  --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
  --approve \
  --role-only \
  --role-name AmazonEKS_EBS_CSI_DriverRole
```

`eksctl create addon --name aws-ebs-csi-driver --cluster <CLUSTER-NAME-HERE> --service-account-role-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/AmazonEKS_EBS_CSI_DriverRole --force`


### Traffic Generation

To generate automated traffic this script uses [locust](https://locust.io/). Run `crapi-traff-gen.sh`, and provide the URLs for crAPI and Mailhog along with the number of users to be created.

```bash
./crapi.sh http://crapi-example.com/ http://mailhog-example.com:8025/ 5
```

The passwords for all test accounts is `Test@123`.
For further configuration, you can modify the arguments passed in `crapi-traff-gen.sh` . By default traffic will be generated for 1 minute.

    -r The number of users spawned every second
    -u The number of users that will simulate browsing the application
    -t amount of time in seconds (30s) or minutes (1m) the script will run
    -H public url of the crAPI server