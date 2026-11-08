import unittest
from pathlib import Path

from gisel_study.commands import (
    build_gisel_command,
    build_hip_compile_command,
    build_sdag_command,
)


class CommandsTest(unittest.TestCase):
    def test_builds_hip_device_bitcode_command(self):
        command = build_hip_compile_command(
            clang=Path("/toolchain/clang++"),
            source=Path("/corpus/saxpy.hip"),
            output=Path("/out/saxpy.bc"),
            gpu="gfx1030",
            opt="O2",
            include_dirs=(Path("/corpus/Common"),),
        )

        self.assertEqual(command[0], "/toolchain/clang++")
        self.assertIn("--offload-device-only", command)
        self.assertIn("--offload-arch=gfx1030", command)
        self.assertIn("--rocm-path=/opt/rocm", command)
        self.assertIn("--target=x86_64-unknown-linux-gnu", command)
        self.assertIn("-I/corpus/Common", command)
        self.assertIn("-O2", command)
        self.assertEqual(command[-2:], ["-o", "/out/saxpy.bc"])

    def test_builds_sdag_gate_command(self):
        command = build_sdag_command(
            llc=Path("/toolchain/llc"),
            source=Path("/corpus/input.ll"),
            gpu="gfx900",
            opt="O2",
        )

        self.assertIn("-global-isel=0", command)
        self.assertIn("-mtriple=amdgcn-amd-amdhsa", command)
        self.assertIn("-mcpu=gfx900", command)
        self.assertIn("-verify-machineinstrs", command)
        self.assertEqual(command[-1], "/corpus/input.ll")

    def test_builds_gisel_diagnostic_command(self):
        command = build_gisel_command(
            llc=Path("/toolchain/llc"),
            source=Path("/corpus/input.bc"),
            remarks=Path("/out/remarks.yaml"),
            gpu="gfx1100",
            opt="O0",
        )

        self.assertIn("-global-isel=1", command)
        self.assertIn("-global-isel-abort=2", command)
        self.assertIn("-pass-remarks-missed=gisel.*", command)
        self.assertIn("-pass-remarks-output=/out/remarks.yaml", command)
        self.assertIn("-pass-remarks-format=yaml", command)
        self.assertIn("-filetype=null", command)


if __name__ == "__main__":
    unittest.main()
