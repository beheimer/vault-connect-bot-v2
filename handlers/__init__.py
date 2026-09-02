from .start import register_handlers as register_start
from .admin_panel import register_handlers as register_admin_panel

def register_all_handlers(dp):
    register_start(dp)
    register_admin_panel(dp)
