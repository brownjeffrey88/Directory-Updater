import Connect
import FileManip
import schedule
import time


def main():
    # daily
    FileManip.catalogCheck()
    FileManip.checkExpiredImages()
    schedule.every().hour.do(Connect.checkMessages)
    while True:
        schedule.run_pending()
        time.sleep(1)


main()
