import sys
from . import bot
import logging

if __name__ == "__main__":
    args = sys.argv
    bot.init()
    logger = logging.getLogger('backup-bot')
    if len(args) == 2:
        if args[1] == '--stats':
            bot.get_channels()
        elif args[1] == '--backup':
            bot.start_backup()
        else:
            logger.warning('Invalid argument. Use either --stats or --backup')
    else:
        logger.warning('No arguments. Add either --stats or --backup')
