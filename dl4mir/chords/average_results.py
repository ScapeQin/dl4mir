from __future__ import print_function
import argparse
import json
import numpy as np
import tabulate

import dl4mir.common.fileutil as futil


def collapse_results(scores):
    stats = scores[0].keys()
    stats.sort()

    metrics = scores[0].values()[0].keys()
    metrics.sort()

    table = np.zeros([len(scores), len(stats), len(metrics)])
    for i, score in enumerate(scores):
        for j, s in enumerate(stats):
            for k, m in enumerate(metrics):
                table[i, j, k] = score[s][m]

    aves = table.mean(axis=0)
    stdevs = table.std(axis=0)

    res = []
    for j, s in enumerate(stats):
        res.append([s])
        for k, m in enumerate(metrics):
            val = "${0:0.3}\pm{1:0.3}$".format(aves[j, k], stdevs[j, k])
            res[-1].append(val)

    return dict(table=res, headers=metrics)


def main(args):
    """{param_file, statistic, metric}"""
    score_files = futil.load_textlist(args.score_textlist)
    scores = [json.load(open(f)).values()[0] for f in score_files]
    data = collapse_results(scores)
    print(tabulate.tabulate(data['table'], headers=data['headers']))

    with open(args.output_file, 'w') as fp:
        json.dump(data, fp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")

    # Inputs
    parser.add_argument("score_textlist",
                        metavar="score_textlist", type=str,
                        help="List of JSON score objects.")
    # Outputs
    parser.add_argument("output_file",
                        metavar="output_file", type=str,
                        help="Path for saving the final output.")
    main(parser.parse_args())
