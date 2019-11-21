from app import app

from app.config import Config
cfg = Config.getInstance().cfg
print(__name__, cfg)

app.run(host='0.0.0.0', port=cfg.server.port, debug=cfg.server.debug)
