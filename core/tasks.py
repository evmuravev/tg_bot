
from telegram.ext._application import Application
from db.tasks import connect_to_db, close_db_connection
from utils.logger import setup_logger
from handlers.callback_query_handlers import CALLBACK_QUERY_HANDLERS
from handlers.command_handlers import COMMAND_HANDLERS
from handlers.conversation_handlers import CONVERSATION_HANDLERS


async def start_bot(app: Application) -> None:
    setup_logger()
    await connect_to_db(app)

    for handler in [
            *CALLBACK_QUERY_HANDLERS,
            *COMMAND_HANDLERS,
            *CONVERSATION_HANDLERS
    ]:
        app.add_handler(handler)

    app.run_polling()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        await close_db_connection(app)
