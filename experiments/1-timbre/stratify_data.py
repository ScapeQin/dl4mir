import argparse
import json
import numpy as np
from sklearn.cross_validation import KFold

import dl4mir.common.fileutil as futil


def main(args):
    files = futil.load_textlist(args.textlist_file)
    keys = np.array([futil.filebase(f) for f in files])
    subsets = json.load(open(args.subset_file))

    folds = dict()
    for config_name, key_set in subsets.iteritems():
        filt_keys = np.array([k for k in keys if k.split('_')[0] in key_set])
        splitter = KFold(n=len(filt_keys),
                         n_folds=args.num_folds,
                         shuffle=True)
        folds[config_name] = dict()
        for fold_idx, data_idxs in enumerate(splitter):
            train_keys, test_keys = [filt_keys[idxs] for idxs in data_idxs]
            num_train = len(train_keys)
            train_idx = np.random.permutation(num_train)
            valid_count = int(args.valid_ratio * num_train)
            valid_keys = train_keys[train_idx[:valid_count]]
            train_keys = train_keys[train_idx[valid_count:]]
            folds[config_name][fold_idx] = dict(train=train_keys.tolist(),
                                                valid=valid_keys.tolist(),
                                                test=test_keys.tolist())

    with open(args.output_file, 'w') as fp:
        json.dump(folds, fp, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Collect files in a directory matching a pattern.")
    parser.add_argument("textlist_file",
                        metavar="textlist_file", type=str,
                        help="Path to a textlist file.")
    parser.add_argument("subset_file",
                        metavar="subset_file", type=str,
                        help="Path to JSON object of instrument subsets.")
    parser.add_argument("num_folds",
                        metavar="num_folds", type=int,
                        help="Number of splits for the data.")
    parser.add_argument("valid_ratio",
                        metavar="valid_ratio", type=float,
                        help="Ratio of the training data for validation.")
    parser.add_argument("output_file",
                        metavar="output_file", type=str,
                        help="File to save the output splits as JSON.")
    main(parser.parse_args())
