import pandas as pd

from .bq_connector import BigQueryConnector
import time


def expand_meal_database(bq_key, project_id, dataset_table_origin, dataset_table_target):
    bq = BigQueryConnector(bq_key, project_id)

    # 1. Lấy danh sách món ăn hiện có (ví dụ: Protein NAP database [cite: 323, 330])
    df_origin = bq.query_to_df(f"SELECT * FROM `{project_id}.{dataset_table_origin}`")

    vietnamese_meals = []

    for index, row in df_origin.iterrows():
        # Tạo Prompt theo chiến lược "FoodAI" của bài báo [cite: 315, 344]
        prompt = f"""You are FoodAI. Create a Vietnamese equivalent for this meal:
        Original Name: {row['Meal_name']}
        Target Calories: {row['Calories']} kcal
        Target Macros: Protein {row['Protein']}g, Carbs {row['Carbohydrates']}g, Fat {row['Fat']}g.
        Return ONLY a CSV row with headers: Meal_name, Calories, Protein, Carbohydrates, Fat, Type
        """

        # Gọi API LLM (Gemini/GPT) - Giả định hàm call_llm đã định nghĩa
        # new_meal_data = call_llm(prompt)
        # vietnamese_meals.append(new_meal_data)

        time.sleep(1)

        # 2. Chuyển kết quả thành DataFrame và đẩy ngược lên BigQuery
    if vietnamese_meals:
        df_new = pd.DataFrame(vietnamese_meals)
        bq.write_df_to_table(df_new, dataset_table_target, if_exists='append')
        print("Đã mở rộng dữ liệu thành công trên BigQuery.")