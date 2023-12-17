import logging
import inspect
import os

log_folder = 'log'
log_file = 'output.log'

# Create the 'log' folder if it doesn't exist
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
log_path = os.path.join(log_folder, log_file)

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def print_to_log(*args, **kwargs):
    frame_info = inspect.stack()[1]
    calling_file = os.path.basename(frame_info.filename)
    message = ' '.join(map(str, args))
    logging.info(f"{calling_file}: {message}")
    
print = print_to_log
