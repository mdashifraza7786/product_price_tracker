import schedule
import time

def job():
    print("Job is running!")

# Schedule the job to run every minute
schedule.every().minute.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)  # Wait a short time before checking again
