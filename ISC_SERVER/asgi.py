import os
import channels.asgi

os.environ.setdefault("DJANGOs_SETTINGS_MODULE", "ISC_SERVER.settings")
channel_layer = channels.asgi.get_channel_layer()