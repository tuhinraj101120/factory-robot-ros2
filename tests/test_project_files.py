"""Offline sanity checks; ROS/Gazebo integration tests require a ROS environment."""
import ast
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ProjectFilesTest(unittest.TestCase):
    def test_python_sources_parse(self):
        for path in (ROOT / "factory_robot").glob("*.py"):
            with self.subTest(path=path.name):
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_package_manifest_is_valid_xml(self):
        root = ET.parse(ROOT / "package.xml").getroot()
        self.assertEqual(root.findtext("name"), "factory_robot")
        self.assertEqual(root.findtext("export/build_type"), "ament_python")

    def test_xacro_is_well_formed_xml(self):
        root = ET.parse(ROOT / "urdf/factory_robot.urdf.xacro").getroot()
        self.assertEqual(root.tag, "robot")

    def test_factory_world_is_well_formed_xml(self):
        root = ET.parse(ROOT / "worlds/factory.sdf").getroot()
        self.assertEqual(root.tag, "sdf")
        self.assertIsNotNone(root.find("world"))

    def test_required_package_files_exist(self):
        for rel in ["setup.py", "setup.cfg", "package.xml", "resource/factory_robot",
                    "launch/factory.launch.py", "config/nav2_params.yaml"]:
            with self.subTest(path=rel):
                self.assertTrue((ROOT / rel).is_file())

if __name__ == "__main__":
    unittest.main()
