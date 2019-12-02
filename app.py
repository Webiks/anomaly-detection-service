from app import app
from app.config import Config

cfg = Config.get_instance().cfg

app.run(host=cfg.server.host, port=cfg.server.port, debug=cfg.server.debug)
