import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import os

class BigQueryConnector:
    def __init__(self, key_path, project_id=None):
        """
        Khởi tạo kết nối tới BigQuery.
        :param key_path: Đường dẫn tới tệp JSON xác thực.
        :param project_id: ID dự án Google Cloud (nếu không cung cấp sẽ lấy từ tệp JSON).
        """
        if not os.path.isabs(key_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(base_dir)
            key_path = os.path.join(project_root, key_path)

        if not os.path.exists(key_path):
            raise FileNotFoundError(f"Không tìm thấy tệp khóa tại: {key_path}")

        self.credentials = service_account.Credentials.from_service_account_file(key_path)
        self.project_id = project_id if project_id else self.credentials.project_id
        self.client = bigquery.Client(credentials=self.credentials, project=self.project_id)

    def query_to_df(self, sql_query):
        """Đọc dữ liệu từ kết quả truy vấn SQL về Pandas DataFrame."""
        try:
            query_job = self.client.query(sql_query)
            return query_job.to_dataframe()
        except Exception as e:
            print(f"Lỗi khi truy vấn BigQuery: {e}")
            return None

    def get_table_df(self, dataset_id, table_id):
        """Truy xuất nhanh toàn bộ dữ liệu của một bảng cụ thể."""
        sql = f"SELECT * FROM `{self.project_id}.{dataset_id}.{table_id}`"
        return self.query_to_df(sql)

    def write_df_to_table(self, df, dataset_id, table_id, if_exists='append'):
        """Ghi dữ liệu từ DataFrame lên một bảng BigQuery."""
        full_table_id = f"{self.project_id}.{dataset_id}.{table_id}"
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE" if if_exists == 'replace' else "WRITE_APPEND",
            # Tự động phát hiện schema để đơn giản hóa việc đẩy dữ liệu thật (CSV/JSON)
            autodetect=True
        )
        try:
            job = self.client.load_table_from_dataframe(df, full_table_id, job_config=job_config)
            job.result()
            print(f"Đã ghi thành công {len(df)} dòng vào bảng {full_table_id}")
        except Exception as e:
            print(f"Lỗi khi ghi dữ liệu lên BigQuery: {e}")

    def list_datasets(self):
        """Liệt kê toàn bộ các Dataset có trong Project."""
        datasets = list(self.client.list_datasets())
        if datasets:
            print(f"Danh sách Dataset trong dự án {self.project_id}:")
            for ds in datasets:
                print(f"- {ds.dataset_id}")
            return [ds.dataset_id for ds in datasets]
        else:
            print("Dự án không có dataset nào.")
            return []

    def list_tables(self, dataset_id):
        """Liệt kê toàn bộ các bảng trong một Dataset cụ thể."""
        try:
            dataset_ref = self.client.dataset(dataset_id)
            tables = list(self.client.list_tables(dataset_ref))
            print(f"Danh sách các bảng trong dataset '{dataset_id}':")
            for table in tables:
                print(f"- {table.table_id}")
            return [table.table_id for table in tables]
        except Exception as e:
            print(f"Lỗi khi liệt kê bảng trong dataset {dataset_id}: {e}")
            return []

if __name__ == "__main__":
    KEY_FILE = "gym-diet-ai-project-4a8a9252bb4d.json"
    DATASET = "warehouse_zone"

    try:
        connector = BigQueryConnector(key_path=KEY_FILE)
        print("Kết nối BigQuery thành công!\n")

        connector.list_tables(DATASET)

        # gym_df = connector.get_table_df(DATASET, "gym_members")
        # if gym_df is not None:
        #     print(gym_df.head())

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")