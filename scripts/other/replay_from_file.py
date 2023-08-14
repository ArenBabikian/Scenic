import carla

# TODO Currently buggy, potentially

filepath = "examplesResearch/replay_logs/yassou2.log"

client = carla.Client("localhost", 2000, worker_threads=1)
client.set_timeout(5.0)

maps = client.get_available_maps()
print(maps)

print(client.show_recorder_file_info(filepath, '', True)) # Buggy
client.replay_file(filepath, 0, 0, 0)
print('yassou')