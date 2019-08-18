# vertigo
[![Build Status](https://travis-ci.org/JoranHonig/vertigo.svg?branch=master)](https://travis-ci.org/JoranHonig/vertigo)

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
vertigo run --network development --truffle <node_dir>/bin/truffle 
```

There are a few additional parameters available that allow you to tweak the execution of vertigo:
```bash
$ vertigo run --help                                                                                                                                                ⬡ 9.11.2 [±master ●●▴]
Usage: vertigo run [OPTIONS]

  Performs a mutation test campaign

Options:
  --output TEXT            Output mutation test results to file
  --network TEXT           Network names that vertigo can use
  --truffle-location TEXT  Location of truffle cli
  --sample-ratio FLOAT     If this option is set. Vertigo will apply the
                           sample filter with the given ratio
  --exclude TEXT           Vertigo won't mutate files in these directories
  --help                   Show this message and exit.
                                                       
```
### Publications
A paper to introduce Vertigo will be presented CBT'19
