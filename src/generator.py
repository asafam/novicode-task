from typing import Optional
import argparse
import random
import re
import pandas as pd
import numpy as np
from synthetics.sampler import Sampler
from main_representations import (
    generate_text_representation,
    generate_code_representation,
)
from utils.utils import (
    printProgressBar,
    print_sample_to_console,
    print_sample_to_file,
)


def main(
    k: Optional[int] = None,
    lang_representations: bool = False,
    code_representations: bool = False,
    input_file: Optional[str] = None,
    output_file: Optional[str] = None,
    print_console: bool = True,
    seed: int = 42,
    force: bool = False,
):
    if seed:
        random.seed(seed)

    samples = []

    # load the data and generate samples for missing fields
    if input_file and not force:  # check if file exists
        # load the data
        data = pd.read_csv(input_file)
        data = data.replace(np.nan, "", regex=True)

        for i, row in data.iterrows():
            text = row["text"]
            code = row["code"]

            if text:
                if lang_representations:
                    _, lr = generate_text_representation(text, rules_enabled=True)
                    lang_rep = str(lr if lr is not None else "")
                else:
                    lang_rep = row["lang_rep"]
                row["lang_rep"] = re.sub(
                    rf"\s+", " ", lang_rep
                ).strip()  # replace multiple spaces, \n and \t with a space
            else:
                row["lang_rep"] = None

            if code:
                if code_representations:
                    _, cr = generate_code_representation(code, rules_enabled=True)
                    code_rep = str(cr if cr is not None else "")

                else:
                    code_rep = row["code_rep"] if "code_rep" in row else ""
                row["code_rep"] = re.sub(
                    rf"\s+", " ", code_rep
                ).strip()  # replace multiple spaces, \n and \t with a space
            else:
                row["code_rep"] = None

            samples.append(row.to_dict())
            printProgressBar(
                i + 1, data.shape[0], prefix="Progress:", suffix="Updated", length=50
            )
    else:
        # printProgressBar(0, k, prefix = 'Progress:', suffix = 'Complete', length = 50)
        sampler = Sampler(seed=seed)
        for i in range(k):
            s = sampler.sample(seed=seed)
            text = s.to_text()
            code = s.to_code()

            lang_rep = (
                str(generate_text_representation(text, rules_enabled=True)[1])
                if lang_representations
                else (None, None)
            )
            code_rep = (
                str(generate_code_representation(code, rules_enabled=True)[1])
                if code_representations
                else (None, None)
            )
            item = {
                "text": text,
                "code": code,
                "lang_rep": lang_rep,
                "code_rep": code_rep,
            }
            samples.append(item)
            printProgressBar(
                i + 1, k, prefix="Progress:", suffix=f"Complete ({i+1}/{k})", length=50
            )

    if print_console:
        print_sample_to_console(samples)

    if output_file:
        print_sample_to_file(samples, output_file)


def update(data_file: str, columns: list[str] = []):
    # load the data
    compression = "gzip" if data_file.endswith(".gz") else None
    df = pd.read_csv(data_file, compression=compression)

    # update the data
    for column in columns:
        if column == "ast":
            df["code_rep"] = df.apply(
                lambda x: (generate_code_representation(x["code"], rules_enabled=True))[
                    0
                ]
            )

    df.to_csv(
        data_file,
        mode="w",
        header=True,
        index=False,
        compression=compression,
    )
    print(f"Succesfully saved samples to {data_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generates pairs of scenario and intents"
    )
    parser.add_argument("--k", type=int, help="number of examples to generate")
    parser.add_argument("--lang_representations", default=False, action="store_true")
    parser.add_argument("--code_representations", default=False, action="store_true")
    parser.add_argument(
        "--force",
        default=False,
        action="store_true",
        help="force flag to regenerate data",
    )
    parser.add_argument("--seed", type=int, default=42, help="random seed")
    parser.add_argument("--print_console", default=False, action="store_true")
    parser.add_argument("--input_file", type=str, help="input file name")
    parser.add_argument("--output_file", type=str, help="output file name")

    args = parser.parse_args()

    main(
        k=args.k,
        lang_representations=args.lang_representations,
        code_representations=args.code_representations,
        print_console=args.print_console,
        input_file=args.input_file,
        output_file=args.output_file,
        seed=args.seed,
        force=args.force,
    )
