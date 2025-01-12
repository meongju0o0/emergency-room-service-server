# Users Management
## Registration (POST)
### Request
- body
    ```json
    {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password",
        "disease_codes": [],
        "medicine_codes": []
    }
    ```
### Response
- body
    ```json
    {
        "message": "User created succesfully"
    }
    ```

## Login (POST)
### Request
- body
    ```json
    {
        "email": "test@example.com",
        "password": "password"
    }
    ```
### Response
- body
    ```json
    {
        "message": "Login successful",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidXNlcm5hbWUiOiJ0ZXN0dXNlciIsImlhdCI6MTczNjUzMDk0OSwiZXhwIjoxNzM2NTM0NTQ5fQ.NaH66O7kb-GGCww2KBLKXFAVw6jyIK7PVt3AFc8XndA"
    }
    ```

## Update (PUT)
### Request
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
        "username": "testuser",
        "password": "password",
        "disease_codes": ["I10", "I49", "K760"],
        "medicine_codes": ["198100119", "198401396"]
    }
    ```
### Response
- body
    ```json
    {
        "message": "User updated successfully"
    }
    ```

## Delete (DELETE)
### Request
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
### Response
- body
    ```json
    {
        "message": "User deleted successfully"
    }
    ```

## get (GET)
### Request
- header
    ```json
    {
        "Authorization": "Bearer <JWT Token>"
    }
    ```
- body
    ```json
    {
        "email": "example.com"
    }
    ```
### Response
- body
    ```json
    {
        "id": 2,
        "email": "test@example.com",
        "username": "",
        "disease_codes": [
            "I10",
            "I49",
            "I109",
            "K64"
        ],
        "medicine_codes": [
            "198100119"
        ]
    }
    ```

# Medical Information Query
## /medical/disease_query
### Request
- body
    ```json
    {
        "disease_name": "지방간"
    }
    ```
### Response
- body
    ```json
    {
        "disease_code": [
            "K700",
            "K758",
            "K760"
        ],
        "disease_name": [
            "알코올성 지방간",
            "비알코올성 지방간염",
            "비알코올성 지방간질환"
        ]
    }
    ```

## /medical/drug_query
### Request
- body
    ```json
    {
        "drug_name": "우루사"
    }
    ```
### Response
- body
    ```json
    {
        "drug_code": [
            "197000040",
            "198100119",
            "198600312",
            "200000801",
            "200901231"
        ],
        "drug_name": [
            "대웅우루사연질캡슐",
            "우루사정100밀리그램(우르소데옥시콜산)",
            "우루사100밀리그램연질캡슐(우르소데옥시콜산)",
            "복합우루사연질캡슐",
            "알파우루사연질캡슐"
        ]
    }
    ```

## /medical/hosp_query
### Request
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
        "course": ["내과"]
    }
    ```
### Response
- body
    ```json
    {
        "hpid_list": [
            "경희대학교병원",
            …
        ],
        "course_list": [
            "가정의학과,내과,마취통증의학과,방사선종양학과,병리과,보건(의료원)소,비뇨기과,산부인과,성형외과,소아청소년과,신경과,신경외과,안과,영상의학과,외과,응급의학과,이비인후과,재활의학과,정신건강의학과,정형외과,조산원,진단검사의학과,피부과,핵의학과,흉부외과",
            …
        ],
        "addr_list": [
            "서울특별시 동대문구 경희대로 23 (회기동)",
            …
        ],
        "map_list": [
            "",
            …
        ],
        "tel_list": [
            "02-958-8114",
            …
        ],
        "x_pos_list": [
            127.05183223390303,
            …
        ],
        "y_pos_list": [
            37.5938765502235,
            …
        ]
    }
    ```
## /medical/nl_query
### Request
- body
    ```json
    {
        "email": "test@example.com",
        "query": "심한 복통, 노란빛 황달, 파란 입술"
    }
    ```
### Response
- body
    ```json
    {
        "result": "환자의 호소 증상(심한 복통, 노란빛 황달, 파란 입술)과 기존 병력(본태성 고혈압, 동맥성 고혈압 등), 복용 중인 약물 정보를 종합하여  **내과 진료**가 적당합니다.\n\n**추후 추가적으로, 다음의 부분을 조사해야 할 것입니다:**\n\n* **황달 심한지 원천은 언제부터 심해졌는지:** 수의 사정변이와 변명 혹은 주사 능동 치사\n* **신진대사 지표:** 활력도와 복통의 진단과 함께 더욱 정확하고 심도 있는 평가\n\n본인은 의료 전문가가 아닙니다. 위 정보는 참고 자료로만 사용하시고 전반적으로, 현 상태와 원한 증상의 진실한 동의 여부를 파악하기 위해 규모 있는 상담과 조치를 추천합니다.\n\n\n"
    }
    ```