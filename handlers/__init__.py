from aiogram import Dispatcher
from .commands import register_command_handlers
from .admin import register_admin_handlers
from .catalog import register_catalog_handlers
from .profile import register_profile_handlers
from .payment import register_payment_handlers
from .rules import register_rules_handlers

def register_all_handlers(dp: Dispatcher):
    """Register all handlers."""
    register_command_handlers(dp)
    register_admin_handlers(dp)
    register_catalog_handlers(dp)
    register_profile_handlers(dp)
    register_payment_handlers(dp)
    register_rules_handlers(dp)