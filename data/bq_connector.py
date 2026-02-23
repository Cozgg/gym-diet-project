import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import os


class BigQueryConnector:
    def __init__(self, key_path, project_id=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(base_dir)

        if not os.path.isabs(key_path):
            key_path = os.path.join(project_root, key_path)

        if not os.path.exists(key_path):
            raise FileNotFoundError(f"Không tìm thấy tệp khóa tại: {key_path}")

        self.credentials = service_account.Credentials.from_service_account_file(key_path)
        self.project_id = project_id if project_id else self.credentials.project_id
        self.client = bigquery.Client(credentials=self.credentials, project=self.project_id)

    def query_to_df(self, sql_query):
        """Đọc dữ liệu từ BigQuery về Pandas DataFrame"""
        try:
            query_job = self.client.query(sql_query)
            return query_job.to_dataframe()
        except Exception as e:
            print(f"Lỗi khi truy vấn BigQuery: {e}")
            return None

    def write_df_to_table(self, df, table_id, if_exists='append'):
        """Ghi dữ liệu từ DataFrame lên BigQuery table"""
        full_table_id = f"{self.project_id}.{table_id}"
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE" if if_exists == 'replace' else "WRITE_APPEND",
        )
        try:
            job = self.client.load_table_from_dataframe(df, full_table_id, job_config=job_config)
            job.result()
            print(f"Đã ghi thành công {len(df)} dòng vào bảng {full_table_id}")
        except Exception as e:
            print(f"Lỗi khi ghi dữ liệu lên BigQuery: {e}")


# test
if __name__ == "__main__":
    KEY_FILE = "gym-diet-ai-project-4a8a9252bb4d.json"

    try:
        connector = BigQueryConnector(key_path=KEY_FILE)
        print("Kết nối BigQuery thành công!")

        sql = """
                SELECT table_id, row_count, size_bytes 
                FROM `gym-diet-ai-project.warehouse_zone.__TABLES__`
            """

        data = connector.query_to_df(sql)
        if data is not None and not data.empty:
            print("\nDanh sách các bảng:")
            print(data)

            first_table = data.iloc[0]['table_id']
            print(f"\nThử truy vấn 5 dòng từ bảng: {first_table}")
            sample_sql = f"SELECT * FROM `gym-diet-ai-project.warehouse_zone.{first_table}` LIMIT 5"
            sample_data = connector.query_to_df(sample_sql)
            print(sample_data)
        else:
            print("\nchưa có bảng nào")

    except Exception as e:
        print(e)