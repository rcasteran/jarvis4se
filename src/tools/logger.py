# Libraries


# Modules


class Logger:
    """@ingroup logger
    @anchor Logger
    Jarvis logger
    """
    @classmethod
    def setDebug(self, module_name, msg):
        """Format DEBUG message
        @param[in] module_name module name responsible for the message
        @param[in] msg message to be formatted
        @return None
        """
        print("[DEBUG] " + module_name + ": " + msg)

    @classmethod
    def setInfo(self, module_name, msg):
        """Format INFO message
        @param[in] module_name module name responsible for the message
        @param[in] msg message to be formatted
        @return None
        """
        print("[INFO] " + module_name + ": " + msg)

    @classmethod
    def setWarning(self, module_name, msg):
        """Format WARNING message
        @param[in] module_name module name responsible for the message
        @param[in] msg message to be formatted
        @return None
        """
        print("[WARNING] " + module_name + ": " + msg)

    @classmethod
    def setError(self, module_name, msg):
        """Format ERROR message
        @param[in] module_name module name responsible for the message
        @param[in] msg message to be formatted
        @return None
        """
        print("[ERROR] " + module_name + ": " + msg)
