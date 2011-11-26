# Scrapy settings for cyespider project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'cyespider'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['cyespider.spiders']
NEWSPIDER_MODULE = 'cyespider.spiders'
DEFAULT_ITEM_CLASS = 'cyespider.items.CyespiderItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)


SCHEDULER = 'cyecore.scheduler.Scheduler'
SCHEDULER_PERSIST = False
