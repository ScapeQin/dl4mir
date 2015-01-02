import argparse
import os
import time

import biggie
import marl.fileutils as futils
import optimus
import pyjams

import dl4mir.chords.lexicon as lex
import dl4mir.chords.decode as D
from dl4mir.chords import PENALTY_VALUES
from dl4mir.common.transform_stash import convolve


NUM_CPUS = None


def predict_stash(stash, transform, penalty_values, vocab):
    """Predict JAMS annotations for all entities in a stash.

    Note: predict = transform + decode

    Parameters
    ----------
    stash : biggie.Stash
        Collection of entities with {cqt, time_points}.
    transform : optimus.Graph
        Callable optimus graph.
    penalty_values : array_like
        Self-transition penalties.
    vocab : dl4mir.chords.lexicon.Vocab
        Map from posterior indices to string labels.

    Returns
    -------
    annots : dict of keyed list of pyjams.RangeAnnotations
        Resulting chord annotations.
    """
    annots = dict()
    for idx, key in enumerate(stash.keys()):
        entity = convolve(stash.get(key), transform, 'cqt')
        annots[key] = D.decode_posterior_parallel(
            entity, penalty_values, vocab, NUM_CPUS)
        print "[{0}] {1:6} / {2:6}: {3}".format(
            time.asctime(), idx, len(stash), key)
    return annots


def main(args):

    param_files = futils.load_textlist(args.param_textlist)
    param_files.sort()
    param_files = param_files[args.start_index::args.stride]

    vocab = lex.Strict(157)
    transform = optimus.load(args.transform_file)

    stash = biggie.Stash(args.validation_file, cache=True)
    jams = {k: pyjams.JAMS() for k in stash.keys()}

    output_dir = futils.create_directory(args.output_dir)
    for fidx, param_file in enumerate(param_files):
        transform.load_param_values(param_file)
        print "Sweeping parameters: {0}".format(param_file)
        results = predict_stash(stash, transform, PENALTY_VALUES, vocab)
        for key, annots in results.iteritems():
            for a in annots:
                a.sandbox.param_file = param_file
            jams[key].chord += annots

            if args.checkpoint or (fidx + 1) == len(param_files):
                output_file = os.path.join(output_dir, "{0}.jams".format(key))
                pyjams.save(jams[key], output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")

    # Inputs
    parser.add_argument("validation_file",
                        metavar="validation_file", type=str,
                        help="Path to a Stash file for validation.")
    parser.add_argument("transform_file",
                        metavar="transform_file", type=str,
                        help="Validator graph definition.")
    parser.add_argument("param_textlist",
                        metavar="param_textlist", type=str,
                        help="Path to save the training results.")
    # Outputs
    parser.add_argument("output_dir",
                        metavar="output_dir", type=str,
                        help="Path for saving JAMS annotations.")
    parser.add_argument("--start_index",
                        metavar="--start_index", type=int, default=0,
                        help="Starting parameter index.")
    parser.add_argument("--stride",
                        metavar="--stride", type=int, default=1,
                        help="Parameter stride.")
    main(parser.parse_args())