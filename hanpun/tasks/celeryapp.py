from celery import Celery

from hanpun import config

app = Celery('tasks', backend=config.CELERY_BROKER_URI, broker=config.CELERY_BROKER_URI)
app.conf.update(
    task_serializer='json',
    enable_utc=True,
    result_expires=3600,
)
app.conf.timezone = 'UTC'


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kw):
    from hanpun.tasks import command
    from hanpun.tasks import fetch_ticker
    # sender.add_periodic_task(crontab(minute=20), video.update_all_video.s(), name='every 10 sec product')
    sender.add_periodic_task(1, fetch_ticker.tick_bithumb.s())
    sender.add_periodic_task(2, fetch_ticker.tick_bitfinex.s())


if __name__ == '__main__':
    app.start()
