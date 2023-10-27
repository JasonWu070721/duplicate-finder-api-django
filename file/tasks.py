
import time
from config.celery import app


@app.task(bind=True)
def file_init(self, file_path):
    for i in range(0, 100):
        time.sleep(1)
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': 100})

    print('Task completed')
    return {'current': 100, 'total': 100, }
