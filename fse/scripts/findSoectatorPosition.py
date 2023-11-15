import carla
client = carla.Client("172.30.208.1", 2000)
client.set_timeout(5.0)
world = client.get_world()

spectator = world.get_spectator()
print(spectator.get_transform())