import pandas as pd

normal_address_raw_checkpoint_df = pd.read_csv('Normal_address_raw-checkpoint.csv')
normal_address_raw_df = pd.read_csv('Normal_address_raw.csv')
abnormal_addreess_raw_df = pd.read_csv('Abnormal_address_raw.csv')
transaction_raw_df = pd.read_csv('Transaction_raw.csv')
abnormal_transaction_df = pd.read_csv('Transaction_raw.csv')

####### Collect normal address #######
# Tạo Series từ các cột 'address'
addresses_checkpoint = normal_address_raw_checkpoint_df['address']
addresses_raw = normal_address_raw_df['address']

# Lấy các giá trị chỉ tồn tại trong addresses_checkpoint
address_only_in_checkpoint_series = addresses_checkpoint[~addresses_checkpoint.isin(addresses_raw)]

# Tạo dataframe từ series addresses_only_in_checkpoint
address_only_in_checkpoint_df = pd.DataFrame({'address': address_only_in_checkpoint_series})

# Random ra 100 địa chỉ ngẫu nhiên
address_only_in_checkpoint_df = address_only_in_checkpoint_df.sample(n=50, random_state=42)

print('address_only_in_checkpoint_df: ', address_only_in_checkpoint_df.shape)

####### Collect normal transaction #######
# Tạo một series chứa tất cả các địa chỉ trong df_addresses_only_in_checkpoint
addresses_in_checkpoint = address_only_in_checkpoint_df['address']

address_only_in_checkpoint_df.to_csv('used_normal_address.csv')

# Lọc các dòng trong transaction_raw_df có from_address hoặc to_address thuộc addresses_in_checkpoint
transactions_has_normal_address = transaction_raw_df[
    (transaction_raw_df['from_address'].isin(addresses_in_checkpoint)) |
    (transaction_raw_df['to_address'].isin(addresses_in_checkpoint))
]

print('transactions_has_normal_address: ',transactions_has_normal_address.shape)

####### Collect abnormal address #######
# Lấy các địa chỉ có exploit bằng 1
exploited_addresses = pd.concat([
    transactions_has_normal_address.loc[transactions_has_normal_address['from_exploit'] == 1, ['from_address', 'network_name']].rename(columns={'from_address': 'address'}),
    transactions_has_normal_address.loc[transactions_has_normal_address['to_exploit'] == 1, ['to_address', 'network_name']].rename(columns={'to_address': 'address'})
], ignore_index=True)

# Tạo dataframe mới với các trường address, network_name, label
abnormal_addresses_df = exploited_addresses.assign(label=1)

# Loại bỏ các địa chỉ trùng lặp
abnormal_addresses_df.drop_duplicates(subset=['address'], inplace=True)

print('abnormal_addresses_df: ', abnormal_addresses_df.shape)

####### Collect abnormal transaction #######
# Tạo một series chứa tất cả các địa chỉ trong df_addresses_only_in_checkpoint
abnormal_addresses_series = abnormal_addresses_df['address']

# Lọc các dòng trong transaction_raw_df có from_address hoặc to_address thuộc abnormal_addresses_series
transactions_has_abnormal_address = transaction_raw_df[
    (transaction_raw_df['from_address'].isin(abnormal_addresses_series)) |
    (transaction_raw_df['to_address'].isin(abnormal_addresses_series))
]

print('transactions_has_abnormal_address: ',transactions_has_abnormal_address.shape)

####### Merge transaction #######
merged_df = pd.concat([transactions_has_abnormal_address, transactions_has_normal_address], ignore_index=True)

# Loại bỏ các địa chỉ trùng lặp
merged_df.drop_duplicates(subset=['hash'], inplace=True)

print('merged_df: ', merged_df.shape)

merged_df.to_csv('graph_transaction_dataset.csv')