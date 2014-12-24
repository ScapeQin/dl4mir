import argparse
import marl.fileutils as futils
import shutil


def main(args):
    param_files = futils.load_textlist(args.param_textlist)
    param_files.sort()
    shutil.copyfile(param_files[-1], args.param_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")

    # Inputs
    parser.add_argument("param_textlist",
                        metavar="param_textlist", type=str,
                        help="Path to save the training results.")
    # Outputs
    parser.add_argument("param_file",
                        metavar="param_file", type=str,
                        help="Path for renaming best parameters.")
    main(parser.parse_args())
