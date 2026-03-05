import os
import sys
import pandas as pd

# Thêm thư mục gốc vào path để import được BigQueryConnector từ /data
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from data.bq_connector import BigQueryConnector


class DataFetcher:
    def __init__(self, key_path="gym-diet-ai-project-4a8a9252bb4d.json"):
        """
        Khởi tạo kết nối tới BigQuery dựa trên hạ tầng có sẵn.
        """
        self.connector = BigQueryConnector(key_path=key_path)
        self.project_id = "gym-diet-ai-project"
        self.dataset_id = "warehouse_zone"

    def fetch_training_data(self):
        """
        Lấy dữ liệu từ các bảng đã cleaned để huấn luyện VAE.
        """
        print("--- Đang tải dữ liệu từ Data Warehouse ---")

        # 1. Lấy dữ liệu người dùng (Gym Members)
        # Bảng này chứa các đặc trưng đầu vào: Age, Weight, Height, BMI, TDEE...
        sql_gym = f"SELECT * FROM `{self.project_id}.{self.dataset_id}.gym_members_nutrition_cleaned`"
        df_gym = self.connector.query_to_df(sql_gym)

        # 2. Lấy dữ liệu gợi ý (Diet Recommendations)
        # Bảng này chứa thông tin về các bữa ăn (meal_1 đến meal_6) để làm nhãn (labels)
        sql_diet = f"SELECT * FROM `{self.project_id}.{self.dataset_id}.diet_recommendations_dataset_cleaned`"
        df_diet = self.connector.query_to_df(sql_diet)

        # 3. Dự phòng cho 2 bảng sắp hoàn thiện (Thực phẩm & Món ăn)
        # Bạn có thể gọi hàm này sau khi 2 bảng kia đã sẵn sàng
        df_food = None
        try:
            sql_food = f"SELECT * FROM `{self.project_id}.{self.dataset_id}.monan`"
            df_food = self.connector.query_to_df(sql_food)
        except Exception:
            print("Lưu ý: Bảng monan chưa sẵn sàng hoặc chưa có dữ liệu.")

        return df_gym, df_diet, df_food

    def prepare_for_loader(self, df_gym, df_diet):
        """
        Gộp dữ liệu gym và diet để khớp với Schema của MealPlanningDataset.
        """
        # Giả sử hai bảng khớp nhau qua cột 'index' hoặc thứ tự dòng
        # Trong nghiên cứu máy học, việc join chính xác nhãn và đặc trưng là bắt buộc.
        combined_df = pd.concat([df_gym, df_diet], axis=1)

        # Loại bỏ các cột trùng lặp nếu có sau khi concat
        combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]

        return combined_df


if __name__ == "__main__":
    fetcher = DataFetcher()
    df_gym, df_diet, df_food = fetcher.fetch_training_data()

    if df_gym is not None and df_diet is not None:
        final_df = fetcher.prepare_for_loader(df_gym, df_diet)
        print(f"Dữ liệu đã sẵn sàng: {final_df.shape[0]} mẫu huấn luyện.")
        print(f"Các cột hiện có: {final_df.columns.tolist()}")