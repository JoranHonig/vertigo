# vertigo-rs

## Introduction
This is an actively maintained fork of Joran Honig's [vertigo](https://github.com/JoranHonig/vertigo) with support for foundry added.

This tool will mutate files in `src/` and run `forge test` to see if the mutant survives. Files that end with `.t.sol` or have `test` in their name (including the path) are ignored. Files in lib (or any directory that isn't src/) will not be mutated.

You do not need to specify that you are in a foundry project, the presence of a `foundry.toml` file will signify to this tool that you are in a foundry repo. If you have configuration files for truffle or hardhat in your project, this tool will get confused. You can temporarily change their names.

```bash
git clone https://github.com/RareSkills/vertigo-rs
python setup.py develop

cd <your foundry repo>

python <path-to-this-project>/vertigo-rs/vertigo.py run --output results.txt
```

## Maintainers
Jeffrey Scholz [RareSkills](https://www.rareskills.io)

## Publications and Articles
[Practical Mutation Testing for Smart Contracts](https://link.springer.com/chapter/10.1007/978-3-030-31500-9_19) - Joran J. Honig, Maarten H. Everts, Marieke Huisman

[Introduction into Mutation Testing](https://medium.com/swlh/introduction-into-mutation-testing-d6512dc702b0?source=friends_link&sk=2878e0c08b6301a125198a264e43edb4) - Joran Honig

[Mutation Testing for Smart Contracts - A step by step guide](https://medium.com/@joran.honig/mutation-testing-for-smart-contracts-a-step-by-step-guide-68c838ca2094) - Joran Honig

If you want to cite vertigo, please use the following:
```
@InProceedings{10.1007/978-3-030-31500-9_19,
author="Honig, Joran J.
and Everts, Maarten H.
and Huisman, Marieke",
title="Practical Mutation Testing for Smart Contracts",
booktitle="Data Privacy Management, Cryptocurrencies and Blockchain Technology",
year="2019",
publisher="Springer International Publishing",
pages="289--303"
}
```
