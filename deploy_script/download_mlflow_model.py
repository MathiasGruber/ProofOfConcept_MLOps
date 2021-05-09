import argparse
import os

import mlflow
from mlflow.store.artifact.models_artifact_repo import ModelsArtifactRepository

# Command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--model_name", nargs='?')
parser.add_argument("--model_stage", nargs='?', default='Production')


if __name__ == '__main__':

    # Get arguments
    args = parser.parse_args()

    # Point to databricks managed mlflow server
    mlflow.set_tracking_uri("databricks")

    # Crete model dir & download mlflow model
    os.makedirs("model", exist_ok=True)
    local_path = ModelsArtifactRepository(f'models:/{args.model_name}/{args.model_stage}').download_artifacts(
        "", dst_path="model"
    )
    print(f'{args.model_stage} Model {args.model_name} is downloaded at {local_path}')
