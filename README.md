
# 40K dice stats computing

This code is a Python toolset for WH40k dice statistical computation. This code works in two parts:
* A stat computing (in python): capability to compute the average enemy dead / HP lost after an attack, depending on strength, AP, ... (see `src/`)
* An interface, coded with `kivy` to enable android app. In this app, you can compute stats and compare results on typical enemy stats (marine, tank, ...)
(see [main.py](main.py))

## Table of Contents
1. [Presentation of the app](#presentation-of-the-app)
2. [Questions](#questions)
   - [How to start](#how-to-start)
   - [How to add more profiles (datasheet) ?](#how-to-add-more-profiles-datasheet)
   - [Useful links](#Useful-links)
   - [Acronyms](#Acronyms)
3. [Elements for developers](#Elements-for-developers)
   - [How to install (developers)](#How-to-install-developers)
   - [Architecture of dirs](#Architecture-of-dirs)

## Presentation of the app

The app permits to compute average dead / wounds given to typical classes of ennemy. It permits to evaluate the strenght of
an unit / weapon on a glimpse. Here are the typical enemy considered (their stats are stored in [data/enemy.csv](data/enemy.csv)):
* space marine
* sorotita default soldier
* astra militarum guard
* terminator
* space marine captain in terminator armor
* monster
* heavy imperial knight


## Questions

### How to start

Just launch `main.py`, on a terminal `python main.py`

### How to add more profiles (datasheet) ?

Update file [data/enemy.csv](data/enemy.csv).
"Compile" file: `python src/build_enemy.py`. This script permits to create a .py file containing content of CSV -> avoid
using heavy python library to manage the CSV (pandas, ...). A priori, it is optimal way to do.

### Useful links

This code were performed thanks to [this medium tutorial](https://towardsdatascience.com/building-android-apps-with-python-part-1-603820bebde8). 

Our model is [this 40k dice stats computer](https://www.rolegenerator.com/en/module/w40k).

### Acronyms

* fnp: feel no pain
* svg: save


## Elements for developers

### How to install [developers]

You can install code on your own laptop to develop and modify the app.

1. Install Python (if you are on Windows, I advise you to install Python via [miniconda](https://docs.conda.io/projects/miniconda/en/latest/))

NB: On Linux distribution, Python is installed by default. 

2. Install tox, the environment manager: `pip install tox`

3. Run tox to init the correct environment and run tests: `tox`.

NB: The name of this environment can be modified in [tox.ini](tox.ini) file (section `[tox]  envlist=`)
NB: To recreate your tox env, just rm the `.tox` dir and re-run command `tox`.

### Architecture of dirs

* [main.py](main.py): The main script, permitting to launch an app (via `kivy` python library)
* [requirements.txt](requirements.txt): all python library to install. Do not pay attention to this script, `tox` will automatically handle it
* [tox.ini](tox.ini): A simple configuration file containing all useful info (libs, python version, ...) when launching command `tox`
* dir [test](test/): contains all test scripts. Permits to test non regression of the evolution of the code.
* dir [data](data/): contains a dataset of typical enemy. 
  * [enemy.csv](data/enemy.csv): contains the stats of typical enemy
* dir `src/` contains all source code
    * [dice](src/dice.py): All useful functions permitting to compute stats on dice launch
    * [workflow](src/workflow.py): Simulate an attack: (1) touch and (2) wounds, then, compute saves, and eventually feel no pain
    * [utils](src/utils.py): set default configuration (essentially for tests and debug), e.g. critical hit on `6`...
    * [build_enemy](src/build_enemy.py): A script to transform `data/enemy.csv` into `src/enemy.py`
    * [enemy](src/enemy.py): A script containing the `enemy.csv` data defined as python dict. Permits to avoid using heavy library (pandas, csv...) and lighten the kivy dependencies.
* File [.github/workflows/build.yml](.github/workflows/buildozer.yml): contains commands to build the app on github 
plateform (launched when new code is push). See github documentation [here](https://github.com/ArtemSBulgakov/buildozer-action)
* File [buildozer.spec](buildozer.spec): File containing command to launch on github servers when code is push
(see details [here](https://github.com/ArtemSBulgakov/buildozer-action/tree/master)
