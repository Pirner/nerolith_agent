import os
# !! precaution - this is under heavy development - for now this only working on a "local system" -> so only for me :P

class OneDriveManager:
    def __init__(self, local_path: str):
        """
        create an OneDrive Manager
        :param local_path: path to the local onedrive where to store items to
        """
        self.local_path = local_path

    def store_markdown(self, relative_path: str, markdown: str, title: str):
        """
        store the markdown as a file into the given relative path with a given text and title.
        :param relative_path: the relative path - in which directory to store the file for sync
        :param markdown: the markdown itself which is written
        :param title: title of the file
        :return:
        """
        file_title = title
        if not file_title.endswith('.md'):
            file_title += '.md'

        with open(os.path.join(self.local_path, relative_path, file_title), 'w', encoding="utf-8") as f:
            f.write(markdown)
