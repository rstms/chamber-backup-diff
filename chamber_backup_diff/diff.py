#!/usr/bin/env python3

import json
import tarfile
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory


class ChamberDiff:
    def __init__(self):
        self.channels = {}

    def files_in(self, path):
        path = Path(path)
        return [node for node in path.iterdir() if node.is_file()]

    def dirs_in(self, path):
        path = Path(path)
        return [node for node in path.iterdir() if node.is_dir()]

    def rewrite(self, filename):
        data = json.loads(filename.read_text())
        filename.write_text(json.dumps(data, indent=2))

    def add_channels(self, name, prefix, path):
        files = self.files_in(path)
        for filename in files:
            self.rewrite(filename)
            channel = filename.stem
            if prefix is None:
                prefix, _, _ = channel.partition(".")
            if channel.startswith(prefix):
                profile = channel[len(prefix) + 1 :]  # noqa: E203
                self.channels.setdefault(profile, {})
                self.channels[profile][name] = str(filename)

    def compare(
        self,
        old_name,
        old_prefix,
        old_tarball,
        new_name,
        new_prefix,
        new_tarball,
    ):
        with TemporaryDirectory() as tempdir:
            with tarfile.open(old_tarball, "r:gz") as old, tarfile.open(
                new_tarball, "r:gz"
            ) as new:
                pre = self.dirs_in(tempdir)
                old.extractall(tempdir)
                post = self.dirs_in(tempdir)
                old_path = str(set(post).difference(set(pre)).pop())
                self.add_channels(old_name, old_prefix, old_path)
                pre = self.dirs_in(tempdir)
                new.extractall(tempdir)
                post = self.dirs_in(tempdir)
                new_path = str(set(post).difference(set(pre)).pop())
                self.add_channels(new_name, new_prefix, new_path)
                self.report(old_name, new_name)

    def print_line(self):
        print("-" * 70)

    def channel_path(self, path):
        if path != "NONE":
            path = Path(path)
            path = str(path.relative_to(path.parent.parent))
        return path

    def report(self, old_name, new_name):
        print()
        footer = False
        for channel, config in self.channels.items():
            if len(config.keys()) == 1:
                self.print_line()
                footer = True
                print(
                    f"{self.channel_path(config.get(old_name, 'NONE'))} != {self.channel_path(config.get(new_name, 'NONE'))}"
                )
                key = list(config.keys())[0]
                print(f"only in {key}:")
                print(f"{channel=}")
                print(Path(config[key]).read_text())
            elif len(config.keys()) == 2:
                cmd = ["diff", config[old_name], config[new_name]]
                proc = run(cmd, capture_output=True, text=True)
                if proc.returncode != 0:
                    self.print_line()
                    footer = True
                    print(
                        f"{self.channel_path(config[old_name])} != {self.channel_path(config[new_name])}"
                    )
                    print(proc.stdout)
            else:
                print("error: unexpected {config=}")
        if footer:
            self.print_line()
