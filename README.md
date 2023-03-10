# vertigo
[![Build Status](https://travis-ci.org/JoranHonig/vertigo.svg?branch=master)](https://travis-ci.org/JoranHonig/vertigo)
[![Gitter](https://badges.gitter.im/eth-vertigo/community.svg)](https://gitter.im/eth-vertigo/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

Vertigo is a mutation testing framework designed to work specifically for smart contracts.
This mutation testing framework implements a range of mutation operators that are either selected from previous works or tailored to solidity.

### Quick Start Guide

To install vertigo, execute the following command:
```bash
pip3 install --user eth-vertigo
```

You can now run vertigo on a truffle project with the following command (assuming you have a `development` network configured in your`truffle-config.js`):

```bash
vertigo run --network development
```
Depending on your environment it might be required to specify the location of the truffle executable:
```bash
vertigo run --network development --truffle-location <node_dir>/bin/truffle 
```

Or, if you're using Hardhat, just use dynamic networks:
```bash
vertigo run --hardhat-parallel 8
```

There are a few additional parameters available that allow you to tweak the execution of vertigo:
```bash
$ vertigo run --help                                                                                                                                                                  
Usage: vertigo run [OPTIONS]

  Performs a core test campaign

Options:
  --output TEXT                   Output core test results to file
  --network TEXT                  Network names that vertigo can use
  --ganache-path TEXT             Path to ganache binary
  --ganache-network <TEXT INTEGER>...
                                  Dynamic networks that vertigo can use eg.
                                  (develop, 8485)

  --ganache-network-options TEXT  Options to pass to dynamic ganache networks
  --hardhat-parallel INTEGER      Amount of networks that hardhat should be
                                  using in parallel

  --rules TEXT                    Universal Mutator style rules to use in
                                  mutation testing

  --truffle-location TEXT         Location of truffle cli
  --sample-ratio FLOAT            If this option is set. Vertigo will apply
                                  the sample filter with the given ratio

  --exclude TEXT                  Vertigo won't mutate files in these
                                  directories

  --incremental TEXT              File where incremental mutation state is
                                  stored

  --help                          Show this message and exit.
                                                                                                                                     
```

### Known Issues

**Ganache** is generally used only for a single run of the entire test suite. 
For the general use case, it does not matter if Ganache creates a few thousand files.
Unfortunately, once you start executing the entire test suite hundreds of times, you can end up with millions of files, and your machine could run out of free inode's.
You can check whether this happens to you by running:

```
df -i
```

This issue ([#1](https://github.com/JoranHonig/vertigo/issues/1)) is known, and we're working on a fix.
 
In the meanwhile. If your test suite is large enough to munch all your inodes, then there are two options:
 - You can use the command line option `--sample-ratio` to select a random subsample of the mutations (reducing the number of times that the test suite is run)
 - You can create a partition that has a sufficient amount of inodes available

### Errors you could run into
After installing Vertigo like this: `> pip3 install eth-vertigo`
Running `vertigo` could throw an error like this:

```bash
> vertigo
zsh: command not found: vertigo
```

When you install vertigo with pip3 it tells you the path where it gets installed for example:
`/some/path/.local/lib/python3.9/site-packages/`
Look in the output, on the command line, from the installation.

Then, the vertigo binary file (which we thought would execute natively) is located here:
`/some/path/.local/bin/vertigo`
So, to make this work, please add the bin/ path to your PATH variable like this:
`> export PATH="${PATH}:/some/path/.local/bin/"`

#### Using Hardhat
- `Could not find supported project directory in`
- Fix => Rename your hardhat.config.ts to .js
- `Encountered an error while running the framework's test command: Encountered error during test output analysis`
- Fix => Comment out or remove Hardhat plugins that are outputting something on the stdout, for example `require("hardhat-gas-reporter");`

### Publications and Articles
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
