# Libraries
import os


# Modules


class Config:
    """@ingroup tools
    @anchor Config
    Jarvis configurator
    """

    is_log_file = False
    is_diagram_file = False

    @classmethod
    def read(cls):
        """ Read the configuration file if any
        @return None
        """
        try:
            if os.path.isdir("config"):
                with open("config/config.cfg", "r", encoding='utf-8') as file_reader:
                    line = file_reader.readline()

                    error = False
                    while (line != '') & (not error):
                        lines = line.split('=')
                        if len(lines) > 1:
                            if lines[0].strip() == 'log':
                                if 'True' == lines[1].strip() or '1' == lines[1].strip():
                                    cls.is_log_file = True
                                    # Logger depends from Config. Thus simple print
                                    print("Log file storage activated")
                            elif lines[0].strip() == 'diagram':
                                if 'True' == lines[1].strip() or '1' == lines[1].strip():
                                    cls.is_diagram_file = True
                                    # Logger depends from Config. Thus simple print
                                    print("Diagram file storage activated")
                            else:
                                error = True
                        else:
                            error = True
                        line = file_reader.readline()

                    if error:
                        # Logger depends from Config. Thus simple print
                        print("[ERROR] Configuration file is not correctly formatted")
            else:
                # Logger depends from Config. Thus simple print
                print(f"No configuration file detected in {os.getcwd()}\\config")
        except EnvironmentError as ex:
            # Logger depends from Config. Thus simple print
            print(f"[ERROR] Unable to read the configuration file in {os.getcwd()}\\config: {ex}")
