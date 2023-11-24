import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file into a Pandas DataFrame

csv_path_sender = '/home/seaonics/Desktop/scripts_seaonics/genicam/log/events_sender.csv'
csv_path_receiver = '/home/seaonics/Desktop/scripts_seaonics/genicam/log/events_receiver.csv'
df = pd.read_csv(csv_path_sender, names=['frame_id', 'event', 'timestamp'])
df_sender = pd.read_csv(csv_path_sender, names=['frame_id', 'event', 'timestamp'])
df_receiver = pd.read_csv(csv_path_receiver, names=['frame_id', 'event', 'timestamp'])


# Convert the timestamps to numeric values for calculation
df_sender['timestamp'] = pd.to_numeric(df_sender['timestamp']) * 1000
df_receiver['timestamp'] = pd.to_numeric(df_receiver['timestamp']) * 1000

print(df_sender)
print(df_receiver)


# Merge the DataFrames on frame_id
# Merge the DataFrames on frame_id
df_merged = pd.merge(df_sender, df_receiver, on=['frame_id', 'event', 'timestamp'], how='outer')


print(df_merged)

# Pivot the DataFrame
pivot_df = df_merged.pivot(index='frame_id', columns='event')

print(pivot_df)

# Calculate latency for each event
# Example: 'frame_grabbed' to 'frame_received'
pivot_df['grab_to_push_latency'] = pivot_df[('timestamp', 'frame_pushed')] - pivot_df[('timestamp', 'frame_grabbed')]
pivot_df['push_to_receive_latency'] = pivot_df[('timestamp', 'frame_recieved')] - pivot_df[('timestamp', 'frame_pushed')]
pivot_df['receive_to_display_latency'] = pivot_df[('timestamp', 'frame_displayed')] - pivot_df[('timestamp', 'frame_recieved')]
pivot_df['grab_to_display_latency'] = pivot_df[('timestamp', 'frame_displayed')] - pivot_df[('timestamp', 'frame_grabbed')]

# Optionally, save the results to a new CSV file
#pivot_df[['grab_to_push_latency', 'push_to_receive_latency', 'receive_to_display_latency', 'grab_to_display_latency']].to_csv('latency_results.csv')


# Plotting
plt.figure(figsize=(12, 8))

# Plot each latency column
plt.subplot(2, 2, 1)
plt.plot(pivot_df['grab_to_push_latency'], label='Grab to Push Latency')
plt.xlabel('Frame ID')
plt.ylabel('Latency (s)')
plt.title('Grab to Push Latency')
plt.legend()

plt.subplot(2, 2, 2)
plt.plot(pivot_df['push_to_receive_latency'], label='Push to Receive Latency')
plt.xlabel('Frame ID')
plt.ylabel('Latency (s)')
plt.title('Push to Receive Latency')
plt.legend()

plt.subplot(2, 2, 3)
plt.plot(pivot_df['receive_to_display_latency'], label='Receive to Display Latency')
plt.xlabel('Frame ID')
plt.ylabel('Latency (s)')
plt.title('Receive to Display Latency')
plt.legend()

plt.subplot(2, 2, 4)
plt.plot(pivot_df['grab_to_display_latency'], label='Grab to Display Latency')
plt.xlabel('Frame ID')
plt.ylabel('Latency (s)')
plt.title('Grab to Display Latency')
plt.legend()

plt.tight_layout()
plt.show()


