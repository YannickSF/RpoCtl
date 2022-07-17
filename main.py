
import os
import shutil
from shutil import Error
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

PATH_TO_TRACK = 'input'
PATH_TO_DROP = 'output'
PATH_TO_ARCHIVES = os.path.join(PATH_TO_DROP, '_archives')


class MyHandler(FileSystemEventHandler):

    @staticmethod
    def file_exist(filename):
        return os.path.isfile(os.path.join(PATH_TO_DROP, filename))

    @staticmethod
    def filter_files(filename):
        if '.py' not in filename and '.json' not in filename:
            return True
        return False

    @staticmethod
    def rename(file, track=PATH_TO_TRACK, out=PATH_TO_DROP):
        # move file
        try:
            os.rename(os.path.join(track, file), os.path.join(out, file))
            print('Ok')
            return True
        except OSError as er:
            print(er.errno)
            return False

    @staticmethod
    def copy(file):
        # copy file
        try:
            shutil.copyfile(os.path.join(PATH_TO_TRACK, file), os.path.join(PATH_TO_DROP, file))
            print('Ok')
            return True
        except Error as er:
            print(er.strerror)
            return False

    def filter(self, file):
        print(self.file_exist(file))
        print(self.filter_files(file))

        if not self.file_exist(file):
            return self.filter_files(file)
        return False

    def on_created(self, event):
        """ Called when a file or directory is created. """
        for file in os.listdir(PATH_TO_TRACK):
            if self.filter(file):
                self.copy(file)

    def on_modified(self, event):
        """ Called when a file or directory is modified. """
        pass

    def on_moved(self, event):
        """ Called when a file or a directory is moved or renamed. """
        # event.key[2]
        print(event)

    def on_deleted(self, event):
        """ Called when a file or directory is deleted. | move to _archives dir """
        filename_deleted = os.path.basename(event.key[1])
        for dirpath, dirnames, filenames in os.walk(PATH_TO_DROP):
            for filename in [f for f in filenames if self.filter_files(f)]:
                if filename == filename_deleted:
                    # move : output.* > _archives
                    self.rename(filename, PATH_TO_DROP, PATH_TO_ARCHIVES)

    def on_closed(self, event):
        """ Called when a file opened for writing is closed. """
        pass


def main():
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, PATH_TO_TRACK, recursive=True)
    observer.start()
    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()


if __name__ == '__main__':
    main()
