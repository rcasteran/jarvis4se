"""@defgroup tools
Tooling module
"""

# Libraries
from datetime import datetime
import os


# Modules
from . import Config


class Logger:
    """@ingroup tools
    @anchor Logger
    Jarvis logger
    """

    @classmethod
    def set_debug(cls, module_name, msg):
        """Format DEBUG message

        DEBUG message are displayed with verbosity level greater than or equal to 2
        @param[in] module_name module name responsible for the message
        @param[in] msg message to be formatted
        @return None
        """
        if Config.verbose_level >= 2:
            print("[DEBUG] " + msg)
            if Config.is_log_file:
                cls.write("DEBUG", module_name, msg)

    @classmethod
    def set_info(cls, module_name, msg):
        """Format INFO message

        INFO message are displayed with verbosity level greater than 1
        @param[in] module_name module name responsible for the message
        @param[in] msg message to be formatted
        @return None
        """
        if Config.verbose_level >= 1:
            print(msg)
            if Config.is_log_file:
                cls.write("INFO", module_name, msg)

    @classmethod
    def set_warning(cls, module_name, msg):
        """Format WARNING message

        WARNING message are always displayed (no verbosity level consideration)
        @param[in] module_name module name responsible for the message
        @param[in] msg message to be formatted
        @return None
        """
        print("[WARNING] " + msg)
        if Config.is_log_file:
            cls.write("WARNING", module_name, msg)

    @classmethod
    def set_error(cls, module_name, msg):
        """Format ERROR message

        ERROR message are always displayed (no verbosity level consideration)
        @param[in] module_name module name responsible for the message
        @param[in] msg message to be formatted
        @return None
        """
        print("[ERROR] " + msg)
        if Config.is_log_file:
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
        except EnvironmentError as ex:
            print(f"[ERROR] Unable to write log file in {os.getcwd()}\\log: {ex}")
