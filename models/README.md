# Trusted local models

Only model bundles created by `scripts/train_model.py` belong here. Each `.joblib` bundle has a
SHA-256 sidecar and is loaded only from this trusted directory. Joblib files can execute code when
loaded; never place an untrusted download or user upload in this directory.

