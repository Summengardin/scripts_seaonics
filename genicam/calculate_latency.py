import pandas as pd

# Load the CSV file into a Pandas DataFrame

csv_path_sender = '/home/seaonics/Desktop/scripts_seaonics/genicam/log/events_sender.csv'
csv_path_receiver = '/home/seaonics/Desktop/scripts_seaonics/genicam/log/events_receiver.csv'
df = pd.read_csv(csv_path_sender, names=['frame_id', 'event', 'timestamp'])
df_sender = pd.read_csv(csv_path_sender, names=['frame_id', 'event', 'timestamp_sender'])
df_receiver = pd.read_csv(csv_path_receiver, names=['frame_id', 'event', 'timestamp_receiver'])


# Convert the timestamps to numeric values for calculation
df_sender['timestamp_sender'] = pd.to_numeric(df_sender['timestamp_sender'])
df_receiver['timestamp_receiver'] = pd.to_numeric(df_receiver['timestamp_receiver'])

# Merge the DataFrames on frame_id
df_merged = pd.merge(df_sender, df_receiver, on=['frame_id', 'event'])


# Pivot the DataFrame
pivot_df = df_merged.pivot(index='frame_id', columns='event', values=['timestamp_sender', 'timestamp_receiver'])

# Calculate latency for each event
# Example: 'frame_grabbed' to 'frame_received'
pivot_df['grab_to_push_latency'] = pivot_df[('timestamp_sender', 'frame_pushed')] - pivot_df[('timestamp_sender', 'frame_grabbed')]
pivot_df['push_to_receive_latency'] = pivot_df[('timestamp_receiver', 'frame_received')] - pivot_df[('timestamp_sender', 'frame_pushed')]
pivot_df['receive_to_display_latency'] = pivot_df[('timestamp_receiver', 'frame_displayed')] - pivot_df[('timestamp_receiver', 'frame_received')]
pivot_df['grab_to_display_latency'] = pivot_df[('timestamp_receiver', 'frame_displayed')] - pivot_df[('timestamp_sender', 'frame_grabbed')]

# Display the results
print(pivot_df[['grab_to_push_latency', 'push_to_receive_latency', 'receive_to_display_latency', 'grab_to_display_latency']])

# Optionally, save the results to a new CSV file
# pivot_df[['grab_to_receive_latency', 'send_to_display_latency']].to_csv('latency_results.csv')
