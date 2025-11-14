# Sample Allure Report Data

Đặt các file Allure Report JSON của bạn vào đây:

## Cấu trúc:

```
sample-data/
├── project1/
│   ├── result1.json
│   ├── result2.json
│   └── ...
└── project2/
    ├── result1.json
    └── ...
```

## Format file:

Mỗi file `*-result.json` có cấu trúc:

```json
{
  "uuid": "unique-id",
  "name": "test_login",
  "fullName": "tests.auth.test_login",
  "status": "passed",
  "statusDetails": {
    "message": "Test passed successfully",
    "trace": ""
  },
  "start": 1699900000000,
  "stop": 1699900005000,
  "labels": [
    {"name": "suite", "value": "Authentication"},
    {"name": "severity", "value": "critical"}
  ],
  "parameters": [],
  "attachments": [],
  "steps": []
}
```

## Sử dụng:

1. Copy các file Allure JSON vào thư mục này
2. Update đường dẫn trong code để load data

