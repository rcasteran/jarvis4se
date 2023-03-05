# Libraries
from datetime import datetime
import os


# Modules


class Logger:
    """@ingroup logger
    @anchor Logger
    Jarvis logger
    """

    @classmethod
    def set_debug(cls, module_name, msg):
        """Format DEBUG message
        @param[in] module_name module name responsible for the message
        @param[in] msg message to be formatted
        @return None
        """
        print("[DEBUG] " + msg)
        cls.write("DEBUG", module_name, msg)

    @classmethod
    def set_info(cls, module_name, msg):
        """Format INFO message
        @param[in] module_name module name responsible for the message
        @param[in] msg message to be formatted
        @return None
        """
        print(msg)
        cls.write("INFO", module_name, msg)

    @classmethod
    def set_warning(cls, module_name, msg):
        """Format WARNING message
        @param[in] module_name module name responsible for the message
        @param[in] msg message to be formatted
        @return None
        """
        print("[WARNING] " + msg)
        cls.write("WARNING", module_name, msg)

    @classmethod
    def set_error(cls, module_name, msg):
        """Format ERROR message
        @param[in] module_name module name responsible for the message
        @param[in] msg message to be formatted
        @return None
        """
        print("[ERROR] " + msg)
        cls.write("ERROR", module_name, msg)

    @classmethod
    def write(cls, msg_type, module_name, msg):
        """Write message in the log file
        @param[in] msg_type message type
        @param[in] module_name module name responsible for the message
        @param[in] msg message to be written
        @return None
        """
        try:
            now = datetime.now()
            date = now.strftime("%Y-%m-%d")
            time = now.strftime("%H:%M:%S")

            if not os.path.isdir("log"):
                os.makedirs("log")

            with open("log/log_" + date + ".log", "a+", newline='', encoding='utf-8') as file_writer:
                file_writer.write(date + ";"
                                  + time + ";"
                                  + msg_type + ";"
                                  + module_name + ";"
                                  + msg + "\n")
        except():
            print(f"[ERROR] Unable to write log file in {os.getcwd()}")
