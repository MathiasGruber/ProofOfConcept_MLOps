# Proof Of Concept MLOps

Example setting up MLOps using databricks-managed mlFlow and Seldon-Core on Azure.

# How to setup

## Setting up Infrastructure

To provision the infrastructure on Azure use terraform:

```bash
cd terraform
az login
terraform init
terraform apply
```

## Installing seldon-core on kubernetes cluster

Use the following to install seldon-core

```bash
# Get kubernetes credentials
az aks get-credentials --resource-group MLOpsDemo --name kubernetes-demo

# Install Ambassador
sudo curl -fL https://metriton.datawire.io/downloads/linux/edgectl -o /usr/local/bin/edgectl && sudo chmod a+x /usr/local/bin/edgectl
edgectl install

# Create namespaces
kubectl create namespace seldon-system
kubectl create namespace mlflowmodels-namespace

# Install seldon-core on kubernetes cluster
helm install seldon-core seldon-core-operator \
    --repo https://storage.googleapis.com/seldon-charts \
    --set usageMetrics.enabled=true \
    --set ambassador.enabled=true \
    --namespace seldon-system
```

# Testing out with Iris model

```bash
kubectl apply -f iris-seldon.yaml

curl -X POST https://naughty-albattani-574.edgestack.me/seldon/seldon/iris-model/api/v1.0/predictions \
    -H 'Content-Type: application/json' \
    -d '{"data": {"ndarray":[[1.0, 2.0, 5.0, 6.0]]}}'
```

# Testing with wines mlflow model from seldon

```bash
kubectl apply -f mlflow-seldon.yaml

curl -X POST https://naughty-albattani-574.edgestack.me/seldon/seldon/mlflow-wine/api/v1.0/predictions \
    -H 'Content-Type: application/json' \
    -d '{"data": {"ndarray":[[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1]]}}'
```

# Transfer model from mlflow to seldon-core

```bash

# Login to azure & get kubernetes setup
az login
az aks get-credentials --resource-group MLOpsDemo --name kubernetes-demo
az extension add --name storage-preview

# Connect to the databricks workspace
export DATABRICKS_AAD_TOKEN=$(jq .accessToken -r <<< "$(az account get-access-token --resource 2ff814a6-3304-4ab8-85cb-cd0e6f879c1d)")
databricks configure --aad-token

# Fetch mnist keras mlflow model from databricks (trained as described in medium post)
cd deploy_script
python download_mlflow_model.py --model_name "Digit Classifier" --model_stage Production

# S2I image expects conda yaml to be in 'environment.yml' file
# We append 'seldon-core' package in the yaml as a dependency (github issue 1125)
sed -e "/  - mlflow/a\\  - seldon-core" < model/conda.yaml | tee environment.yml

# Put model into docker image
s2i build \
  -e MODEL_NAME=MyMlflowModel \
  -e API_TYPE=REST \
  -e SERVICE_TYPE=MODEL \
  -e PERSISTENCE=0 \
  -e CONDA_ENV_NAME=microservice \
  . seldonio/seldon-core-s2i-python3:1.8.0-dev nanomathias/mlflow_model:0.1

# Push docker image to repository
docker push nanomathias/mlflow_model:0.1

# Test locally by running the docker image & sending a request
docker run --rm --name mlflowmodel -p 5000:5000 nanomathias/mlflow_model:0.1
seldon-core-microservice-tester contract.json 0.0.0.0 5000 -p --grpc

# Deploy to cluster
kubectl apply -f mlflow-custom.yaml
```

For testing deployment we can go to the following:
https://naughty-albattani-574.edgestack.me/seldon/seldon/mlflow-wine/api/v1.0/doc/

## Prometheus & Grafana for Monitoring

```bash
helm install seldon-core-analytics seldon-core-analytics \
  --set grafana_prom_admin_password=password \
   --repo https://storage.googleapis.com/seldon-charts \
   --namespace seldon-system
```

kubectl port-forward svc/seldon-core-analytics-grafana 3000:80 -n seldon-system
