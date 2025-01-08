# RESTfulAPIs Specification

## Users Management
### Registration (POST)
- **http://localhost:8080/users/add**
#### Request
- body
```json
{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password",
    "disease_codes": ["D001", "D002"],
    "medicine_codes": ["M001", "M002"]
}
```

#### Response

### Login (POST)
#### Request
- body
```json
{
    "email": "test@example.com",
    "password": "password"
}
```

#### Response

### Update (PUT)
#### Request
- header
```json
{
    "Authorization": "Bearer <JWT Token>"
}
```

- body
```json
{
    "email": "test@example.com",
    "username": "updated_user",
    "password": "new_password",
    "disease_codes": ["D001"],
    "medicine_codes": ["M001"]
}
```

#### Response

### Delete (DELETE)
- header
```json
{
    "Authorization": "Bearer <JWT Token>"
}
```

- body
```json
{
    "email": "test@example.com"
}
```