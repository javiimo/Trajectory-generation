from final_pub import run_pub
from final_sub import run_sub
import threading

if __name__ == "__main__":
    thread1 = threading.Thread(target=run_pub, args=("5556",))
    thread2 = threading.Thread(target=run_sub, args=("5557",))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
