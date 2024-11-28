import yaml
import os
import datetime

class Logger:
    """Custom logger to log messages to the console and save them to a single log file."""
    
    def __init__(self, log_dir: str = "logs", log_file_name: str = "run"):
        """
        Initializes the logger, setting up the log file path.
        
        Parameters:
        - log_dir: Directory where log files will be saved.
        - log_file_name: Base name for the log file (it will be appended with date).
        """
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        now = datetime.datetime.now()
        today = now.strftime("%Y-%m-%d")
        
        # Define a log file path for the entire run, based on the date
        log_file_name = f"{log_file_name}_{today}.log"
        self.log_file_path = os.path.join(self.log_dir, log_file_name)
    
    def log(self, msg: str, level: str = "INFO", pipeline_name: str = "general"):
        """
        Logs a message to the console and appends it to the log file for the current run.
        
        Parameters:
        - msg: The message to log.
        - level: The log level ('INFO', 'WARNING', 'ERROR').
        - pipeline_name: The name of the pipeline or context (e.g., 'data', 'training', 'evaluation').
        """
        now = datetime.datetime.now()
        time = now.strftime("%H:%M:%S")
        
        log_message = f"[{time}] [{level}] [{pipeline_name}] {msg}"
        
        # Log to console
        print(log_message)
        
        # Write log to the log file
        with open(self.log_file_path, "a+", encoding="utf-8") as log_file:
            log_file.write(log_message + "\n")


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from a YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def update_ticker(config_path, new_ticker):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Update the ticker and dependent columns
    config["data_params"]["ticker"] = new_ticker
    config["data_params"]["columns"] = [
        col if not col.startswith(("SMA_20_", "EMA_20_", "20_day_std_", "Momentum_", "MACD_", "rsi_"))
        else f"{col.split('_')[0]}_{col.split('_')[1]}_{new_ticker}"
        for col in config["data_params"]["columns"]
    ]
    
    # Save the updated config
    with open(config_path, "w") as f:
        yaml.safe_dump(config, f)

if __name__ == '__main__':
    pass