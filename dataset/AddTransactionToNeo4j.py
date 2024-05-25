import pandas as pd
from neo4j import GraphDatabase

####### Add to neo4j database #######
merged_df = pd.read_csv("graph_transaction_dataset.csv")

transaction_execution_commands = []

count = 0
for _, transaction in merged_df.iterrows():
    neo4j_create_statemenet = f"""
            MERGE (from:Address {{address: "{transaction.from_address}", network_name: "{transaction.network_name}"}})
            ON CREATE SET from.label = {transaction.from_exploit}
            MERGE (to:Address {{address: "{transaction.to_address}", network_name: "{transaction.network_name}"}})
            ON CREATE SET to.label = {transaction.to_exploit}
            MERGE (from)-[r:TRANSACTION {{hash: "{transaction.hash}", network_name: "{transaction.network_name}"}}]->(to)
            ON CREATE SET r += {{
                from_address: "{transaction.from_address}",
                to_address: "{transaction.to_address}",
                value: toFloat({transaction.value}.0),
                block_timestamp: toFloat({transaction.block_timestamp}.0),
                gas_price: toFloat({transaction.gas_price}.0)
            }}
        """
    transaction_execution_commands.append(neo4j_create_statemenet)


def execute_transactions(transaction_execution_commands):
    print("Adding transaction...")
    data_base_connection = GraphDatabase.driver(
        uri="bolt://localhost:7687", auth=("neo4j", "12345678")
    )
    session = data_base_connection.session()
    for i in transaction_execution_commands:
        count += 1
        if count % 100 == 0:
            print('session ', i)
        session.run(i)

print(len(transaction_execution_commands))
execute_transactions(transaction_execution_commands)

