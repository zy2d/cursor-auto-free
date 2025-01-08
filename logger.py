import logging
import os
from datetime import datetime

# Configure logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log"),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def main_task():
    try:
        # Example task
        logging.info("Starting the main task...")
        
        # Simulated error
        if some_condition():  # Replace with actual logic
            raise ValueError("Simulated error occurred.")
        
        logging.info("Main task completed successfully.")
    
    except ValueError as ve:
        logging.error(f"ValueError: {ve}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        logging.info("Task execution finished.")

def some_condition():
    # Simulate an error condition
    return True

if __name__ == "__main__":
    logging.info("Application started.")
    main_task()
    logging.info("Application exited.")
