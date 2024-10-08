from final_pub import run_pub
from final_sub import run_sub
import threading
import multiprocessing
import shutil
import os


if __name__ == "__main__":
    # Delete previous logs
    logs_folder = "logs"
    if os.path.exists(logs_folder) and os.path.isdir(logs_folder):
        try:
            shutil.rmtree(logs_folder)
            print(f"Successfully deleted the '{logs_folder}' folder and its contents.")
        except OSError as e:
            print(f"Error deleting '{logs_folder}' folder: {e}")
    

    process1 = multiprocessing.Process(target=run_pub, args=("5556",))
    process2 = multiprocessing.Process(target=run_sub, args=("5557",))

    process1.start()
    process2.start()

    process1.join()
    process2.join()

    # Using threads
    # thread1 = threading.Thread(target=run_pub, args=("5556",))
    # thread2 = threading.Thread(target=run_sub, args=("5557",))

    # thread1.start()
    # thread2.start()

    # thread1.join()
    # thread2.join()
