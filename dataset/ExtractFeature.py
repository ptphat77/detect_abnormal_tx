import pandas as pd

# Tải dataset addresses từ file CSV
addresses_df = pd.read_csv("extract_feature_address.csv")

# merge network_name
addresses_df["address"] = addresses_df["address"] + "-" + addresses_df["network_name"]

# Xóa dấu "
addresses_df["address"] = addresses_df["address"].replace('"', "", regex=True)
# addresses_df['label'] = addresses_df['label'].replace('"', '', regex=True)

# Tải dataset transactions từ file CSV
transactions_df = pd.read_csv("balanced_transaction_dataset.csv")

# Thay NaN thành 0
# addresses_df = addresses_df.fillna(0)
# transactions_df = transactions_df.fillna(0)

# print(transactions_df.head(3))

# for col in addresses_df.columns:
#     if col in ['avg_amount_outgoing', 'avg_amount_incoming', 'mean_time_interval', 'out_degree', 'unique_in_degree', 'active_duration', 'avg_gas_price']:
#         addresses_df[col] = pd.to_numeric(addresses_df[col], errors='coerce')

# Tạo dataset mới với các cột có tiền tố "from-" và "to-"
new_columns = list()
new_columns.append("hash")
new_columns.append("from_address")
new_columns.append("to_address")
new_columns.extend(
    [
        "from-" + col
        for col in [
            "active_duration",
            "avg_gas_price",
            "unique_in_degree",
            "avg_amount_incoming",
            "out_degree",
            "avg_amount_outgoing",
            "mean_time_interval",
        ]
    ]
)
new_columns.extend(
    [
        "to-" + col
        for col in [
            "active_duration",
            "avg_gas_price",
            "unique_in_degree",
            "avg_amount_incoming",
            "out_degree",
            "avg_amount_outgoing",
            "mean_time_interval",
        ]
    ]
)
new_columns.append("label")

new_df = pd.DataFrame(columns=new_columns)

# Khởi tạo biến đếm
loop_counter = 1

for _, row in transactions_df.iterrows():
    from_address = row["from_address"]
    to_address = row["to_address"]
    hash = row["hash"]
    print("hash: ", hash)

    from_addr_info = addresses_df.loc[addresses_df["address"] == from_address]
    to_addr_info = addresses_df.loc[addresses_df["address"] == to_address]

    label_value = int(
        from_addr_info["label"].values[0] or to_addr_info["label"].values[0]
    )

    avg_values = list()
    avg_values.append(hash)
    avg_values.append(from_address)
    avg_values.append(to_address)
    avg_values.extend(
        list(
            from_addr_info[
                [
                    "active_duration",
                    "avg_gas_price",
                    "unique_in_degree",
                    "avg_amount_incoming",
                    "out_degree",
                    "avg_amount_outgoing",
                    "mean_time_interval",
                ]
            ].values[0]
        )
    )
    avg_values.extend(
        list(
            to_addr_info[
                [
                    "active_duration",
                    "avg_gas_price",
                    "unique_in_degree",
                    "avg_amount_incoming",
                    "out_degree",
                    "avg_amount_outgoing",
                    "mean_time_interval",
                ]
            ].values[0]
        )
    )
    avg_values.append(label_value)

    new_df.loc[len(new_df)] = avg_values

    # In ra lần chạy thứ n của vòng lặp
    print(f"Lần chạy thứ {loop_counter}")
    loop_counter += 1

new_df.to_csv("balanced_transaction-from-to-prefix.csv", index=False)
