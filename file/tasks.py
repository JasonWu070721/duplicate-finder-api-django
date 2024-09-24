from config.celery import app
from utils.file_library import FileInit
import os
from os import walk
from file.models import File

OS_TYPE = "synology"  # synology, windows
IS_CLEAN_FILE_TABLE = True


@app.task(bind=True)
def file_init_task(self, root_path):
    fileInit = FileInit()

    self.update_state(state="PROGRESS", meta={"current": None, "total": None})

    if root_path:
        root_path = str(root_path).strip()
        root_path = root_path.replace("\\", "/")
        root_path = os.path.normpath(root_path)

        root_path = os.path.join("/search_data", root_path)
    else:
        root_path = "/search_data"

    if IS_CLEAN_FILE_TABLE:
        fileInit.delete_all_data()

    for root, _, files in walk(os.path.normpath(root_path)):
        if OS_TYPE == "synology" and "@eaDir" in root:
            continue

        for file in files:
            path = os.path.join(root, file)
            path = os.path.normpath(path)
            fileInit.save_file_status(path)

            fileInit.file_count = fileInit.file_count + 1

            self.update_state(
                state="PROGRESS",
                meta={"current": fileInit.file_count},
            )

    return {
        "current": fileInit.file_count,
        "root_path": root_path,
    }


@app.task(bind=True)
def search_identical_file_task(self):
    fileInit = FileInit()
    md5_group = fileInit.get_same_file_group()

    return {"file_group": md5_group}


@app.task(bind=True)
def select_file_task(self, reserve_path=None):
    if reserve_path:
        reserve_path = reserve_path.replace("\\", "/")
        reserve_path = str(reserve_path).strip()
        reserve_path = os.path.normpath(reserve_path)

        reserve_path = os.path.join("/search_data", reserve_path)
    else:
        reserve_path = "/search_data"

    fileInit = FileInit()

    md5_group = fileInit.get_same_file_group()
    same_file_group_list = fileInit.selete_fils(md5_group, reserve_path)

    fileInit.delete_other_reserve_path_file(same_file_group_list, reserve_path)
