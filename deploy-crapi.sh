echo "WARNING! DO NOT DEPLOY THIS APPLICATION ON A PRODUCTION SERVER!"
git clone https://github.com/OWASP/crAPI.git
cd crAPI/deploy/helm
kubectl create namespace crapi
helm install --namespace crapi crapi . --values values.yaml
