import multiprocessing
import os
import sys
from multiprocessing import freeze_support

STRICTDOC_ROOT_PATH = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(STRICTDOC_ROOT_PATH)

from strictdoc.helpers.parallelizer import Parallelizer
from strictdoc.cli.cli_arg_parser import cli_args_parser
from strictdoc.core.actions.export_action import ExportAction
from strictdoc.core.actions.passthrough_action import PassthroughAction


def _main(parallelizer):
    parser = cli_args_parser()
    args = parser.parse_args()

    if args.command == "passthrough":
        input_file = args.input_file
        if not os.path.isfile(input_file):
            sys.stdout.flush()
            message = "error: passthrough command's input file does not exist"
            print("{}: {}".format(message, input_file))
            sys.exit(1)

        output_file = args.output_file
        if output_file:
            output_dir = os.path.dirname(output_file)
            if not os.path.isdir(output_dir):
                print("not a directory: {}".format(output_file))
                sys.exit(1)

        passthrough_action = PassthroughAction()
        passthrough_action.passthrough(input_file, output_file)

    elif args.command == "export":
        parallelization_value = (
            "Enabled" if parallelizer.parallelization_enabled else "Disabled"
        )
        print("Parallelization: {}".format(parallelization_value), flush=True)
        export_controller = ExportAction(STRICTDOC_ROOT_PATH, parallelizer)
        export_controller.export(
            args.input_paths, args.output_dir, args.formats, args.fields
        )

    else:
        raise NotImplementedError


def main():
    enable_parallelization = "--no-parallelization" not in sys.argv
    parallelizer = Parallelizer.create(enable_parallelization)
    try:
        _main(parallelizer)
    except Exception as e:
        raise e
    finally:
        parallelizer.shutdown()


if __name__ == "__main__":
    main()
