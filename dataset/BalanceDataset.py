import pandas as pd
import numpy as np

# Đọc dữ liệu từ file CSV hoặc DataFrame của bạn
df = pd.read_csv('graph_transaction_dataset.csv')
print(df.shape)

# Lấy tất cả địa chỉ bất thường (nhãn 1)
abnormal_addresses = df[df['exploit'] == 1]

# Tính số lượng địa chỉ bình thường cần lấy
num_normal_addresses = int(len(abnormal_addresses) / 0.46 * 0.54)

# Lấy ngẫu nhiên các địa chỉ bình thường
normal_addresses = df[df['exploit'] == 0].sample(num_normal_addresses, random_state=42)

# Kết hợp các địa chỉ bất thường và bình thường
balanced_df = pd.concat([abnormal_addresses, normal_addresses])

# Trộn lại tập dữ liệu
balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

# Xuất ra dataset mới
balanced_df.to_csv('balanced_transaction_dataset.csv', index=False)

print(f"Số lượng giao dịch bất thường: {abnormal_addresses.shape[0]}")
print(f"Số lượng giao dịch bình thường: {normal_addresses.shape[0]}")
