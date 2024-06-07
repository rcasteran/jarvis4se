"""@defgroup plantuml_adapter
Plantuml adapter module
"""
# Libraries
import os
import re
import pathlib
import subprocess
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from plantuml import PlantUML

# Modules
from tools import Logger


class PlantUmlPicoServer:
    """@ingroup plantuml_adapter
    @anchor PlantUmlPicoServer
    Class that looks for .jar file in root, check version and handle local PlantUml PicoWeb
    Server (https://plantuml.com/en/picoweb)

    If . jar, get it, check if PicoWeb is running, if not start new process else default url
    to online PlantUml server
    """
    def __init__(self):
        """
        @var plantuml_jar_path
        Filepath to the PlantUml jar

        @var url
        URL for the local PlantUml PicoWeb Server

        @var version_cmd
        JAVA command to retrieve the PlantUml jar file version
        """

        self.plantuml_jar_path = None

        jar_file = self.get_jar()
        if not jar_file:
            self.url = 'http://www.plantuml.com/plantuml/svg/'
        else:
            self.plantuml_jar_path = str(pathlib.Path(f'./{jar_file}'))
            self.version_cmd = ['java', '-jar', self.plantuml_jar_path, '-version']
            pico_cmd = ['java', '-DPLANTUML_LIMIT_SIZE=20000', '-jar', self.plantuml_jar_path,
                        '-picoweb']

            self.check_version()
            # Default localhost pico server
            self.url = "http://127.0.0.1:8080/plantuml/svg/"
            # Check if pico is running
            check_pico = False
            try:
                with urlopen(f"{self.url}"):
                    pass
            except HTTPError:
                pass
            except URLError:
                pass
            else:
                check_pico = True

            if not check_pico:
                self.process = subprocess.Popen(pico_cmd)

    @classmethod
    def get_jar(cls):
        """Return first jar filepath with 'plantuml' in filename

        @return jar filepath
        """

        end_message = ", large diagrams will not be displayed.\n" \
                      "See: " \
                      "https://github.com/rcasteran/jarvis4se/blob/main/docs/installation.md"

        list_dir = os.listdir('.')
        if not any('.jar' in f for f in list_dir):
            Logger.set_warning(__name__,
                              f"Not any .jar found for plantuml in root{end_message}")
            return None

        jar_list = [f.string for f in [re.search("plantuml.*jar", i) for i in list_dir] if f]
        if not jar_list:
            Logger.set_warning(__name__,
                              f"Not any .jar found with 'plantuml' in its name{end_message}")
            return None

        # Return first filename with plantuml in it
        return jar_list.pop(0)

    def check_version(self):
        """ Get .jar version and check with latest release

        @return None
        """

        jar_version = subprocess.run(
            self.version_cmd, capture_output=True, encoding="utf-8").stdout[17:26].strip()
        github_url = "https://github.com/plantuml/plantuml/releases/latest"

        try:
            with urlopen(f"{github_url}") as rep:
                release_ver = str(rep.geturl())[51:]

            if int(release_ver[0]) > int(jar_version[0]) or \
                    int(release_ver[2:6]) > int(jar_version[2:6]) or \
                    int(release_ver[7:len(release_ver)]) > int(jar_version[7:len(jar_version)]):
                Logger.set_info(__name__,
                           f"plantUml.jar is not up-to-date, see latest release {github_url}")
        except:
            Logger.set_info(__name__,
                           "Not able to check plantuml.jar version.")


class PlantUmlConnector(PlantUmlPicoServer):
    """@ingroup plantuml_adapter
    @anchor PlantUmlConnector
    Class to encode PlantUml text and get server url as .svg
    """
    def __init__(self):
        """
        @var server
        PlantUml server
        """

        # Init PicoWeb server from PlantUMLPicoServer
        # If .jar found or default online PlantUml, send it to PlantUml for encoding and HTTP handling
        super().__init__()
        # PlantUml has encoding and handling errors
        self.server = PlantUML(url=self.url,
                               basic_auth={},
                               form_auth={}, http_opts={}, request_opts={})

    def get_diagram_url(self, string, from_diagram_cell=False):
        """ Generate .svg from PlantUml text using PlantUml default server or PlantUml .jar PicoWeb
        @param[in] string PlantUml text
        @param[in] from_diagram_cell indicates if PlantUml text is coming from a notebook diagram cell
        (TRUE) or not (FALSE)
        @return diagram url
        """
        if not from_diagram_cell:
            full_string = "@startuml\nskin rose\nskinparam NoteBackgroundColor PapayaWhip\n" \
                          + string + "@enduml"
        else:
            full_string = string

        if len(string) > 15000 and self.plantuml_jar_path is None:
            Logger.set_warning(__name__,
                              f"Diagram is too large to be display with PlantUml Online Server, "
                              f"please consider download .jar at https://plantuml.com/fr/download")
            return None

        return self.server.get_url(full_string)
