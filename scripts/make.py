import argparse
import os
import sys

import yaml

sys.path.append(os.getcwd())

from scripts.utils.custom_help_formatter import CustomHelpFormatter

CONFIG_FILE = "config.yml"


def flatten(items):
    if isinstance(items, str):
        yield items
    else:
        for item in items:
            if isinstance(item, dict):
                yield from flatten(item.values())
            else:
                yield from flatten(item)


class Flatten(yaml.YAMLObject):
    yaml_tag = "!flatten"

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f"{list(flatten(self.data))}"

    def __iter__(self):
        return flatten(self.data)

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(loader.construct_sequence(node, deep=True))

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_sequence("tag:yaml.org,2002:seq", data)


yaml.SafeLoader.add_constructor("!flatten", Flatten.from_yaml)
yaml.SafeDumper.add_multi_representer(Flatten, Flatten.to_yaml)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""general script whose purpose is to accomplish 4 tasks:
        1. calculate the gas consumption of mint and verify operations as the number of NFT increases in a collection and along with the gas limit related to the MMR height
        2. calculate the gas consumption of mint and verify operations in relation to several NFT collections given a CSV file containing its NFT transfers
        3. plot the gas consumption of mint and verify along with the gas limit
        4. plot the gas consumption of the provided NFT collections""",
        formatter_class=CustomHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--all",
        action="store_true",
        help="executes all the steps",
        default=True,
    )
    group.add_argument(
        "--calculate-gas",
        action="store_true",
        help="only executes the 1st step",
    )
    group.add_argument(
        "--calculate-collection-gas",
        action="store_true",
        help="only executes the 2nd step",
    )
    group.add_argument(
        "--plot-gas",
        action="store_true",
        help="only executes the 3rd step",
    )
    group.add_argument(
        "--plot-collections",
        action="store_true",
        help="only executes the 4th step",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="increase verbosity",
        default=False,
    )
    args = parser.parse_args()

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    collections = config["collections"]

    if args.all or args.calculate_gas:
        from scripts.gas.merge_gas import merge_gas_mint_verify
        from scripts.gas.max_gas import derive_max_gas_mint, derive_max_gas_verify
        from scripts.gas.extend_gas import extend_gas

        merge_gas_mint_verify(
            config["data"]["gas"]["raw"]["mint"],
            config["data"]["gas"]["raw"]["verify"],
            config["data"]["gas"]["derived"]["merged"],
        )

        num_tokens = derive_max_gas_mint(
            config["data"]["gas"]["derived"]["merged"],
            config["data"]["gas"]["derived"]["max_mint"],
        )
        derive_max_gas_verify(
            config["data"]["gas"]["raw"]["max_verify"],
            config["data"]["gas"]["derived"]["max_verify"],
            num_tokens=num_tokens,
        )

        extend_gas(
            config["data"]["gas"]["derived"]["merged"],
            config["data"]["gas"]["derived"]["max_verify"],
            config["data"]["gas"]["derived"]["complete"],
        )

    if args.all or args.calculate_collection_gas:
        from scripts.collection.collection_gas import derive_collection_gas, timedelta_type

        for collection in collections:
            derive_collection_gas(
                config["data"]["gas"]["derived"]["complete"],
                config["data"]["collections"]["transfers"][collection["id"]],
                config["data"]["collections"]["gas"][collection["id"]],
                period=timedelta_type(collection["aggregation_period"]),
            )
