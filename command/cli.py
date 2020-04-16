import os

import click

from stream_parser.parser import parse


class AutoStream:
    def __init__(self, **kwargs):
        self.custom = kwargs.get('custom', None)
        self.file_path = kwargs.get('file_path')
        self.output_dir = kwargs.get('output_directory')

        print(self.custom)

        # self._verify_paths()
        if self.custom:
            self._get_custom_library()

    def _verify_paths(self):
        if not os.path.isfile(self.file_path):
            print("The provided file path does not exist. Exiting...")
            exit(1)
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

    def _get_custom_library(self):
        charts = []
        for root, dir, files in os.walk(self.custom):
            for file in files:
                if os.path.splitext(file)[1] == '.sm':
                    path = os.path.join(root, file)
                    sim_obj = parse(path)
                    charts += sim_obj.charts

        print(len(charts))


@click.command()
@click.argument('file_path')
@click.argument('output_directory')
@click.option('--custom', default=None, help='Directory of a song pack for building a custom pattern library.')
@click.option('--as', default=True, help='This option denotes AutoStream. This is the default for now. More to come')
def parse_args(**kwargs):
    if kwargs.pop('as'):
        AutoStream(**kwargs)


if __name__ == '__main__':
    parse_args()
