
import os
import subprocess
import re
import logging

from prpl.apis.hl.spec.builder.graph import NodeFactory


class GraphvizWriter:
    """Graphviz open source graph visualization software writer for prpl HL-API.

    It generates a visual representation of the specification using.

    Example:
        # Setup an API.
        from prpl.apis.hl.com import API as HLAPI

        # Create list of objects.
        api_objects = []

        # Create list of response codes.
        api_response_codes = []

        # Create list of version.
        api_versions = []

        # Create API.
        api = HLAPI(api_objects, api_response_codes, api_versions)

        # Import module.
        from prpl.apis.hl.spec.builder import GraphvizWriter as HLAPIDiagramWriter

        # Load API.
        writer = HLAPIDiagramWriter(api, 'specs/prpl HL-API ({}).dot'.format(self.api.get_version()))

        # Generate report.
        writer.build()

    """

    def __init__(self, api, filename, libpath):
        """Initializes the specification writer.

        Args:
            api (prpl.apis.hl.com.api): API to be parsed.
            file (str): Target filename for the diagram.

        """

        self.api = api

        # Define raw dot filename.
        self.dot_filename = '{}.gv'.format(os.path.splitext(filename)[0])

        # Define img filename.
        self.img_filename = filename

        # Add graphviz binary to system path
        os.environ['PATH'] += ';{}'.format(libpath)

        # Retrieve logger.
        self.logger = logging.getLogger('WordWriter')

    def build(self):
        """Generates a dot file diagram to be used with the Graphviz library."""

        # Retrieve the names of the objects.
        objects = list(map(lambda x: x.name, self.api.objects))

        self.logger.debug('Dot - Started writing.')

        # Build graph.
        graph = NodeFactory.get_graph(objects)

        # Generate dot file.
        with open(self.dot_filename, 'w') as f:
            f.write(graph.dot())
            f.close()

        self.logger.debug('Dot - Finished ({}).\n'.format(self.dot_filename))

        # Generate png file.
        self.logger.debug('PNG - Started writing.')
        self._run_command([self.dot_filename, '-Tpng', '-o', self.img_filename])
        self.logger.debug('PNG - Finished ({}).\n'.format(self.img_filename))

    def version(self):
        """Returns the Graphviz fdp engine version.

        Returns:
            str: Graphviz fdp engine version number.

        """

        # Run shell command with '-V' flag.
        output = self._run_command(['-V'])

        # Retrieve version number.
        version = re.search('\d+(\.\d+)+', output)

        # Raise error if binary is not available.
        if version is None:
            raise Exception('Could not run "fdp -V" command. Please validate whether graphviz bin folder is '
                            'part of the system PATH environment or the "config.json" file has been properly setup.')

        return version.group()

    def _run_command(self, options):
        """Executes a Graphviz fdp engine shell command and returns the output.

        Args:
            options (list<str>): List of options/flags to be included in the command separated by blank spaces.

        Returns:
            str: The combined stdout and stderr output.
        """

        # Add flags to command.
        cmd = ['fdp'] + options

        # Execute shell command.
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Parse both stdout and stderr streams.
        stdout, stderr = proc.communicate()
        output = ''.join([stdout.decode(), stderr.decode()])

        return output
