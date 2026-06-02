# users-api

Small Flask user management API with Terraform-provisioned S3 storage.

## Run

```bash
pip install -r requirements.txt
python app.py
pytest
```

## Endpoints

- `GET  /users`         list all users
- `GET  /users/<id>`    get one user
- `POST /users`         create a user (JSON body)

## Infra

`infra/main.tf` provisions the S3 bucket used for user-uploaded avatars.
