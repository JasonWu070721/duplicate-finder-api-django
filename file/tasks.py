
from config.celery import app
from utils.file_library import FileInit
import os


@app.task(bind=True)
def file_init_task(self, root_path):

    fileInit = FileInit()

    self.update_state(state='PROGRESS',
                      meta={'current': fileInit.file_count, 'total': fileInit.file_total})

    root_path = str(root_path).strip()

    file_list = fileInit.get_file_list(root_path)
    fileInit.file_total = len(file_list)

    for file_path in file_list:
        fileInit.file_count = fileInit.file_count + 1
        self.update_state(state='PROGRESS',
                          meta={'current': fileInit.file_count, 'total': fileInit.file_total})

        fileInit.save_file_status(file_path)

    return {'current': fileInit.file_count, 'total': fileInit.file_total, 'root_path': root_path}


@app.task(bind=True)
def search_identical_file_task(self):

    fileInit = FileInit()

    md5_group = fileInit.get_same_file_group()
    return {'file_group': md5_group}


@app.task(bind=True)
def select_file_task(self, reserve_path):

    reserve_path = str(reserve_path).strip()
    reserve_path = os.path.normpath(
        os.path.join("/app/data", reserve_path))

    fileInit = FileInit()

    md5_group = fileInit.get_same_file_group()
    same_file_group_list = fileInit.selete_fils(md5_group, reserve_path)

    fileInit.delete_other_reserve_path_file(
        same_file_group_list, reserve_path)
