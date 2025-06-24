# import os
# import csv
# import io
# from datetime import datetime
# from azure.storage.blob import BlobServiceClient
# from azure.core.exceptions import ResourceExistsError

# # --- CONFIGURATION ---
# connection_string = ""
# container_name = "qadata01"
# blob_name = f"qa_data/{datetime.now().strftime('%Y-%m-%d')}.csv"

# # --- INIT STORAGE CLIENTS ---
# # --- INIT STORAGE CLIENTS ---
# blob_service_client = BlobServiceClient.from_connection_string(connection_string)
# container_client = blob_service_client.get_container_client(container_name)

# # Ensure container exists (this will create it if it doesn't)
# try:
#     container_client.create_container()
# except Exception:
#     pass  # Ignore if container already exists

# # Create blob client for the specified blob (this is always the same blob)
# blob_client = container_client.get_blob_client(blob_name)

# # --- APPEND FUNCTION ---
# # def initialize_blob():
# #     """
# #     Initialize the blob with a header row if it doesn't already exist.
# #     """
# #     try:
# #         # Try to create the append blob. This will only work if the blob does not already exist.
# #         blob_client.create_append_blob()
# #         # Write CSV header once (only if the blob was just created)
# #         header = io.StringIO()
# #         writer = csv.writer(header)
# #         writer.writerow(["question", "answer"])
# #         blob_client.append_block(header.getvalue())
# #     except ResourceExistsError:
# #         # Blob already exists, don't create it again
# #         pass

# # # Call initialize_blob() just once, before the first append
# # initialize_blob()

# # --- APPEND NEW DATA FUNCTION ---
# def append_csv_row(question, answer):
#     """
#     Appends a new row to the CSV file in Azure Append Blob.
#     Ensures that existing data is never overwritten.
#     """
#     # Prepare the row data
#     csv_row = io.StringIO()
#     writer = csv.writer(csv_row)
#     writer.writerow([question, answer])

#     # Append the new row to the blob
#     blob_client.append_block(csv_row.getvalue())
#     print(f"✅ Appended row to {blob_name}")

# # --- Example Usage ---
# if __name__ == "__main__":
#     # Call this whenever you want to append data
#     append_csv_row("What is the capital of France?", "Paris")
#     append_csv_row("What is the capital of Germany?", "Berlin")
#     append_csv_row("What is the capital of Italy?", "Rome")