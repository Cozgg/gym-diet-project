import os
import sys
import pandas as pd

# Thêm thư mục gốc vào path để import được BigQueryConnector
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from data.bq_connector import BigQueryConnector


class DataFetcher:
    def __init__(self, key_path="gym-diet-ai-project-4a8a9252bb4d.json"):
        """
        Khởi tạo kết nối tới BigQuery.
        """
        self.connector = BigQueryConnector(key_path=key_path)
        self.project_id = "gym-diet-ai-project"
        self.dataset_id = "warehouse_zone"

    def fetch_training_data(self):
        """
        Task 1 & 2: Trích xuất dữ liệu từ các bảng đã gộp và làm sạch.
        Dữ liệu trên DW đã là float nên không cần clean_format.
        """
        print("--- Đang bắt đầu trích xuất dữ liệu từ Data Warehouse ---")

        # 1. Trích xuất bảng Gym Members (Đầu vào cho Encoder)
        sql_gym = f"SELECT * FROM `{self.project_id}.{self.dataset_id}.gym_members_nutrition_cleaned`"
        df_gym = self.connector.query_to_df(sql_gym)
        print(f"✅ Đã tải bảng Gym Members: {df_gym.shape if df_gym is not None else 'Thất bại'}")

        # 2. Trích xuất bảng Master Food List (Đã gộp Món ăn & Thực phẩm)
        sql_food = f"SELECT * FROM `{self.project_id}.{self.dataset_id}.master_food_list`"
        df_food = self.connector.query_to_df(sql_food)
        print(f"✅ Đã tải bảng Master Food List: {df_food.shape if df_food is not None else 'Thất bại'}")

        # 3. Trích xuất bảng Diet Recommendations (Ràng buộc y tế)
        sql_diet = f"SELECT * FROM `{self.project_id}.{self.dataset_id}.diet_recommendations_dataset_cleaned`"
        df_diet = self.connector.query_to_df(sql_diet)
        print(f"✅ Đã tải bảng Diet Recommendations: {df_diet.shape if df_diet is not None else 'Thất bại'}")

        return df_gym, df_food, df_diet

    def prepare_combined_dataset(self, df_gym, df_diet):
        """
        Gộp dữ liệu gym và diet để chuẩn bị cho Loader.
        """
        if df_gym is None or df_diet is None:
            return None

        combined_df = pd.concat([df_gym, df_diet], axis=1)
        combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]
        return combined_df


def create_food_mapping(df_food):
    # Tạo từ điển ánh xạ dish_id -> integer index
    dish_to_idx = {dish_id: i for i, dish_id in enumerate(df_food['dish_id'])}
    idx_to_dish = {i: dish_id for dish_id, i in dish_to_idx.items()}

    # Trích xuất các chỉ số dinh dưỡng dưới dạng tensor/matrix để tra cứu nhanh
    food_nutrition_matrix = df_food[['kcal', 'protein', 'fat', 'carb', 'sodium']].values

    return dish_to_idx, idx_to_dish, food_nutrition_matrix

if __name__ == "__main__":
    fetcher = DataFetcher()
    # Chạy thử nghiệm trích xuất
    df_gym, df_food, df_diet = fetcher.fetch_training_data()

    if df_gym is not None and df_food is not None:
        print(f"\n--- Kết nối thành công ---")
        print(f"Số lượng món ăn trong Master List: {len(df_food)}")
        print(f"Cấu trúc bảng thực phẩm: {df_food.columns.tolist()}")