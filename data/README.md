**Khởi tạo kết nối**:
```commandline
from bq_connector import BigQueryConnector

KEY_FILE = "gym-diet-ai-project-4a8a9252bb4d.json"
connector = BigQueryConnector(key_path=KEY_FILE)
```


**Tên các bảng có trong data warehouse**:


gym-diet-ai-project.warehouse_zone.gym_members_nutrition_cleaned\
gym-diet-ai-project.warehouse_zone.diet_recommendations_dataset_cleaned