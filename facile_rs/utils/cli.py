import argparse
import inspect
import os.path
from warnings import warn

from facile_rs import (
    create_bag,
    create_bagpack,
    create_cff,
    create_datacite,
    create_radar,
    create_release,
    create_zenodo,
    prepare_radar,
    prepare_release,
    prepare_zenodo,
    run_bibtex_pipeline,
    run_docstring_pipeline,
    run_markdown_pipeline,
)


# create the top-level parser
def create_parser():
    """
    Create parsers for the facile-rs command line interface.
    The main parser has one subparser per platform (Zenodo, RADAR, ...) or metadata type (CFF, DataCite,...).
    Each of this subparser has a subparser per FACILE-RS script.

    :return: The parser object.
    """
    # Main parser
    parser = argparse.ArgumentParser(prog='facile-rs',
        description="FACILE-RS command-line tool, to perform metadata conversion and software publication" \
            "based on CodeMeta metadata.",
        epilog="Get help on a subcommand by running 'facile-rs <subcommand> -h'.")

    # Parsers for the subcommands
    subparsers = parser.add_subparsers(help='Select the target platform or metadata type.',
                                       dest='subcommand')

    # Parser for the 'release' subcommand
    parser_release = subparsers.add_parser('release', help='Perform operations on CodeMeta metadata')
    release_subparsers = parser_release.add_subparsers()
    parser_release_prepare = release_subparsers.add_parser('prepare',
                                                           help='Update CodeMeta file with the given version and date',
                                                           parents=[prepare_release.create_parser(add_help=False)],
                                                           add_help=True)
    parser_release_prepare.set_defaults(func=prepare_release.main)

    # Parser for the 'gitlab' subcommand
    parser_gitlab = subparsers.add_parser('gitlab', help='Perform operations for GitLab releases')
    gitlab_subparsers = parser_gitlab.add_subparsers()
    parser_gitlab_publish = gitlab_subparsers.add_parser('publish',
                                                        parents=[create_release.create_parser(add_help=False)],
                                                        help="Create a release on GitLab",
                                                        add_help=True)
    parser_gitlab_publish.set_defaults(func=create_release.main)

    # Parser for the 'radar' subcommand
    parser_radar = subparsers.add_parser('radar', help='Perform operations for RADAR releases')
    radar_subparsers = parser_radar.add_subparsers()
    parser_radar_prepare = radar_subparsers.add_parser('prepare',
                                                       help='Prepare a release on RADAR',
                                                       parents=[prepare_radar.create_parser(add_help=False)],
                                                       add_help=True)
    parser_radar_prepare.set_defaults(func=prepare_radar.main)
    parser_radar_upload = radar_subparsers.add_parser('upload',
                                                      help='Create a release on RADAR',
                                                      parents=[create_radar.create_parser(add_help=False)],
                                                      add_help=True)
    parser_radar_upload.set_defaults(func=create_radar.main)

    # Parser for the 'zenodo' subcommand
    parser_zenodo = subparsers.add_parser('zenodo', help='Perform operations for Zenodo releases')
    zenodo_subparsers = parser_zenodo.add_subparsers()
    parser_zenodo_prepare = zenodo_subparsers.add_parser('prepare',
                                                        help='Prepare a release on Zenodo',
                                                        parents=[prepare_zenodo.create_parser(add_help=False)],
                                                        add_help=True)
    parser_zenodo_prepare.set_defaults(func=prepare_zenodo.main)
    parser_zenodo_upload = zenodo_subparsers.add_parser('upload',
                                                        help='Create a release on Zenodo',
                                                        parents=[create_zenodo.create_parser(add_help=False)],
                                                        add_help=True)
    parser_zenodo_upload.set_defaults(func=create_zenodo.main)

    # Parser for the 'cff' subcommand
    parser_cff = subparsers.add_parser('cff', help='Generate and manage CFF metadata')
    cff_subparsers = parser_cff.add_subparsers()
    parser_cff_create = cff_subparsers.add_parser('create',
                                                  help='Create a CFF metadata file',
                                                  parents=[create_cff.create_parser(add_help=False)],
                                                  add_help=True)
    parser_cff_create.set_defaults(func=create_cff.main)

    # Parser for the 'datacite' subcommand
    parser_datacite = subparsers.add_parser('datacite', help='Generate and manage DataCite metadata')
    datacite_subparsers = parser_datacite.add_subparsers()
    parser_datacite_create = datacite_subparsers.add_parser('create',
                                                            help='Create a DataCite metadata file',
                                                            parents=[create_datacite.create_parser(add_help=False)],
                                                            add_help=True)
    parser_datacite_create.set_defaults(func=create_datacite.main)

    # Parser for the 'bag' subcommand
    parser_bag = subparsers.add_parser('bag', help='Generate and manage BagIt bags')
    bag_subparsers = parser_bag.add_subparsers()
    parser_bag_create = bag_subparsers.add_parser('create',
                                                  help='Create a BagIt bag',
                                                  parents=[create_bag.create_parser(add_help=False)],
                                                  add_help=True)
    parser_bag_create.set_defaults(func=create_bag.main)

    # Parser for the 'bagpack' subcommand
    parser_bagpack = subparsers.add_parser('bagpack',
                                           help='Generate and manage BagPack bags (BagIt with DataCite metadata)')
    bagpack_subparsers = parser_bagpack.add_subparsers()
    parser_bagpack_create = bagpack_subparsers.add_parser('create',
                                                          help='Create a BagIt bag with DataCite metadata',
                                                          parents=[create_bagpack.create_parser(add_help=False)],
                                                          add_help=True)
    parser_bagpack_create.set_defaults(func=create_bagpack.main)

    # Parser for the 'grav' subcommand
    parser_grav = subparsers.add_parser('grav', help='Perform operations for Grav CMS')
    grav_subparsers = parser_grav.add_subparsers()
    parser_grav_bibtex = grav_subparsers.add_parser('bibtex',
                                                    help='Run the BibTex conversion pipeline',
                                                    parents=[run_bibtex_pipeline.create_parser(add_help=False)],
                                                    add_help=True)
    parser_grav_bibtex.set_defaults(func=run_bibtex_pipeline.main)

    parser_grav_docstring = grav_subparsers.add_parser('docstring',
                                                         help='Run the docstring conversion pipeline',
                                                         parents=[run_docstring_pipeline.create_parser(add_help=False)],
                                                         add_help=True)
    parser_grav_docstring.set_defaults(func=run_docstring_pipeline.main)

    parser_grav_markdown = grav_subparsers.add_parser('markdown',
                                                        help='Run the Markdown conversion pipeline',
                                                        parents=[run_markdown_pipeline.create_parser(add_help=False)],
                                                        add_help=True)
    parser_grav_markdown.set_defaults(func=run_markdown_pipeline.main)
    return parser


def cli_call_deprecated(func):
    """
    Display a deprecation warning when a script is called from the command line directly,
    without using the 'facile-rs' entry point.

    :param func: The main function to call in the script.
    """
    script_name = os.path.basename(inspect.getfile(func)).removesuffix('.py')
    warn(f"Calling {script_name} directly is deprecated. Use the entry point 'facile-rs' instead.",
         stacklevel=2)
    func()
