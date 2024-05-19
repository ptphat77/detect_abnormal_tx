# This script provides examples to convert a data table into images, which can be modelled by CNN models.

import pandas as pd
import os
from sklearn.preprocessing import MinMaxScaler
from IGTD_Functions import min_max_transform, table_to_image, select_features_by_variation



num_row = 30    # Number of pixel rows in image representation
num_col = 30    # Number of pixel columns in image representation
num = num_row * num_col # Number of features to be included for analysis, which is also the total number of pixels in image representation
save_image_size = 3 # Size of pictures (in inches) saved during the execution of IGTD algorithm.
max_step = 30000    # The maximum number of iterations to run the IGTD algorithm, if it does not converge.
val_step = 300  # The number of iterations for determining algorithm convergence. If the error reduction rate
                # is smaller than a pre-set threshold for val_step itertions, the algorithm converges.

# Import the example data and linearly scale each feature so that its minimum and maximum values are 0 and 1, respectively.

cols_to_read = ['hash','from-active_duration','from-avg_gas_price','from-unique_in_degree','from-avg_amount_incoming','from-out_degree','from-avg_amount_outgoing','from-mean_time_interval','to-active_duration','to-avg_gas_price','to-unique_in_degree','to-avg_amount_incoming','to-out_degree','to-avg_amount_outgoing','to-mean_time_interval']
data = pd.read_csv('../Data/balanced_transaction-from-to-prefix.csv', low_memory=False, sep=',', engine='c',
                   na_values=['na', '-', '','null'], header=0, index_col=0, usecols = cols_to_read)

print(data.shape)
# fill nan value
data = data.fillna(0)                   
# print(data.head(3))
data.to_csv('../Data/view_df.csv', index=False)

# Select features with large variations across samples
id = select_features_by_variation(data, variation_measure='var', num=num)
data = data.iloc[:, id]
data.to_csv('../Data/view_dfv2.csv', index=False)
# Perform min-max transformation so that the maximum and minimum values of every feature become 1 and 0, respectively.
#norm_data = min_max_transform(data.values)
scaler = MinMaxScaler()

norm_data = scaler.fit_transform(data)
norm_data = pd.DataFrame(norm_data, columns=data.columns, index=data.index)
print(norm_data.head(3))
norm_data.to_csv('../Data/view_norm.csv', index=False)

# Run the IGTD algorithm using (1) the Euclidean distance for calculating pairwise feature distances and pariwise pixel
# distances and (2) the absolute function for evaluating the difference between the feature distance ranking matrix and
# the pixel distance ranking matrix. Save the result in Test_1 folder.
fea_dist_method = 'Euclidean'
image_dist_method = 'Euclidean'
error = 'abs'
result_dir = '../Resultsv2/Table_To_Image_Conversion/Test_1'
os.makedirs(name=result_dir, exist_ok=True)
table_to_image(norm_data, [num_row, num_col], fea_dist_method, image_dist_method, save_image_size,
               max_step, val_step, result_dir, error)

# Run the IGTD algorithm using (1) the Pearson correlation coefficient for calculating pairwise feature distances,
# (2) the Manhattan distance for calculating pariwise pixel distances, and (3) the square function for evaluating
# the difference between the feature distance ranking matrix and the pixel distance ranking matrix.
# Save the result in Test_2 folder.
fea_dist_method = 'Pearson'
image_dist_method = 'Manhattan'
error = 'squared'
norm_data = norm_data.iloc[:, :800]
result_dir = '../Resultsv2/Table_To_Image_Conversion/Test_2'
os.makedirs(name=result_dir, exist_ok=True)
table_to_image(norm_data, [num_row, num_col], fea_dist_method, image_dist_method, save_image_size,
               max_step, val_step, result_dir, error)
