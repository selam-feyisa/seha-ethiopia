from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model
from azure.identity import DefaultAzureCredential

ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id="29f1cd2f-d0e2-413e-b913-1976b6924fa6",
    resource_group_name="ai-intern",
    workspace_name="AIintern"
)

model = Model(
    path="symptom_model.pkl",
    name="seha-symptom-model",
    version="1",
    type="custom_model"
)

registered_model = ml_client.models.create_or_update(model)

print("Model registered:", registered_model.name)
print("Version:", registered_model.version)