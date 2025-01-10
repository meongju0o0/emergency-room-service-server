# RESTfulAPIs Specification

## Users Management
### Registration (POST)
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
- body
    ```json
    {
        "message": "User created succesfully"
    }
    ```

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
- body
    ```json
    {
        "message": "Login successful",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidXNlcm5hbWUiOiJ0ZXN0dXNlciIsImlhdCI6MTczNjUzMDk0OSwiZXhwIjoxNzM2NTM0NTQ5fQ.NaH66O7kb-GGCww2KBLKXFAVw6jyIK7PVt3AFc8XndA"
    }
    ```

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
- body
    ```json
    {
        "message": "User updated successfully"
    }
    ```

### Delete (DELETE)
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
        "email": "test@example.com"
    }
    ```

#### Response
- body
    ```json
    {
        "message": "User deleted successfully"
    }
    ```