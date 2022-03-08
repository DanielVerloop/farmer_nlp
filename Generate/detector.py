import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from generate import generate_for_project


class ReGenerate(FileSystemEventHandler):
    # if change detected, generate tests for project path - not used in experiment
    def on_modified(self, event):
        print(f'event type: {event.event_type}  path : {event.src_path}')
        generate_for_project(event.src_path)


# detect changes in project path
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = ReGenerate()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
