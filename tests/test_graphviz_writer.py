
import unittest2
import os
import re

from prpl.apis.hl.spec.builder.graph import GraphvizWriter as HLAPIDiagramWriter
from prpl.apis.hl.spec.builder.graph import NodeFactory
from prpl.apis.hl.com import API as HLAPI
from prpl.apis.hl.com import Object as HLAPIObject
from prpl.config import Manager as ConfigManager


class TestGraphvizWriter(unittest2.TestCase):
    """Tests the 'prpl.apis.hl.spec.builder.GraphvizWriter' component."""

    def setUp(self):
        """Test environment setup."""

        # Setup dummy objects.
        dummy_objects = list()

        dummy_objects.append(HLAPIObject(1, 'User.Accounts', 'User Account'))
        dummy_objects.append(HLAPIObject(1, 'User.Accounts.{AccountId}', 'User Account'))
        dummy_objects.append(HLAPIObject(1, 'User.Roles', 'User Role'))
        dummy_objects.append(HLAPIObject(1, 'User.Roles.{RoleId}', 'User Role'))
        dummy_objects.append(HLAPIObject(1, 'User.Roles.{RoleId}.ACL', 'User Role ACL Rule'))
        dummy_objects.append(HLAPIObject(1, 'User.Roles.{RoleId}.ACL.Rules', 'User Role ACL Rule'))
        dummy_objects.append(HLAPIObject(1, 'User.Roles.{RoleId}.ACL.Rules.{RuleId}', 'User Role ACL Rule'))
        dummy_objects.append(HLAPIObject(1, 'Services.Management.CLI', 'Command Line Interface'))

        # Graphviz library path.
        self.libpath = ConfigManager.get_config()['libs']['graphviz']

        # Setup mock api.
        self.api = HLAPI(dummy_objects, [], [])

        # Output file.
        self.dot_filename = 'tests/dummy-diagram.gv'
        self.png_filename = 'tests/dummy-diagram.png'

    def test_node_factory(self):
        """Tests the 'NodeFactory.get_graph' method ability to generate a tree cluster."""

        objects = list(map(lambda x: x.name, self.api.objects))
        graph = NodeFactory.get_graph(objects)

        self.assertEqual(str(graph), '+ User\n'
                                     '  + Accounts\n'
                                     '    - {AccountId}\n'
                                     '  + Roles\n'
                                     '    + {RoleId}\n'
                                     '      + ACL\n'
                                     '        + Rules\n'
                                     '          - {RuleId}\n'
                                     '+ Services\n'
                                     '  + Management\n'
                                     '    - CLI')

    def test_build(self):
        """Tests the 'GraphvizWriter.build' method ability to generate a diagram."""

        # Generate a new diagram.
        writer = HLAPIDiagramWriter(self.api, self.png_filename, self.libpath)
        writer.build()

        # Validate a new file has been created.
        self.assertTrue(os.path.isfile(self.dot_filename))

        # Access internal contents of the diagram.
        with open(self.dot_filename, 'r') as f:
            dot = f.readlines()

            self.assertEqual(dot[0], 'graph G {\n')
            self.assertEqual(dot[1], '  graph [font="Calibri Light" fontsize=11 style=dashed penwidth=0.5]\n')
            self.assertEqual(dot[2], '  node [shape=box font="Calibri Light" fontsize=11 style=dashed penwidth=0.5]\n')
            self.assertEqual(dot[7], '      node [label="{AccountId}"] 2\n')
            self.assertEqual(dot[-1], '}')

            f.close()

        # Validate a new file has been created.
        self.assertTrue(os.path.isfile(self.png_filename))

    def test_version(self):
        """Tests the 'GraphvizWriter.version' method ability to return the library version number."""
        writer = HLAPIDiagramWriter(None, self.png_filename, self.libpath)
        version = writer.version()

        # Validate whether the returned value matches the format of a version.
        self.assertTrue(bool(re.match('^\d+(\.\d+)+$', version)))


    def tearDown(self):
        """Clean-up test-environment."""

        # Delete temporary dummy diagram.
        try:
            os.remove(self.dot_filename)
            os.remove(self.png_filename)
        except:
            pass


if __name__ == '__main__':
    unittest2.main()
