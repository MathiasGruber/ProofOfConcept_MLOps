from mlflow import pyfunc


class MyMlflowModel:
    """A generic wrapper for mlflow models"""
    def __init__(self):
        self.pyfunc_model = None

    def load(self):
        self.pyfunc_model = pyfunc.load_pyfunc("model")

    def predict(self, input_data, features_names=None):
        _ = features_names
        if not self.pyfunc_model:
            self.load()
        return self.pyfunc_model.predict(input_data)