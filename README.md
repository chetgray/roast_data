# Coffee Roasting Data Analysis
### by Chet Gray

*A project for Code Louisville's Python for Data May 2018 course*


## Overview

When roasting a batch of coffee, two of the key points at the beginning of the process are the drop (or charge) and the turn-around. The drop/charge is the beginning of the roast, where the (room temperature) beans enter the roasting chamber, and the turn-around is where the measured temperature of the roast environment bottoms out and begins to rise.

Anecdotally, I have observed that how quickly turn-around occurs after drop varies day to day, and I suspect that there is some correlation with ambient temperature. As consistency in the temperature profile of a particular coffee's roast is desirable, finding such correlation would help me anticipate and adjust for that variation.

My analysis and further explanation of sources and methodology can be found in the `Coffee Roasting Data Analysis.ipynb` Jupyter notebook.

## Requirements

The rendered notebook may be [viewed on GitHub](https://github.com/chetgray/roast_data/blob/master/Coffee%20Roasting%20Data%20Analysis.ipynb), or in a local Jupyter Notebook instance. To re-run the notebook, the Python packages in `requirements.txt` need to be installed for the Jupyter kernel running the notebook.

I use [Pipenv](https://docs.pipenv.org/) for managing virtual environment and Python packages, and I have included my `Pipfile` and `Pipfile.lock` for it. With [Pipenv installed](https://docs.pipenv.org/install/#installing-pipenv), it is straightforward to set up project requirements, and the Jupyter kernel:

```console
$ pipenv install
Installing dependencies from Pipfile.lock (e2d89c)...
[...]
$ pipenv run python -m ipykernel install --user --name=roast_data
Installed kernelspec roast_data in ~/.local/share/jupyter/kernels/roast_data
```

If you have your own set-up for managing Python packages and Jupyter kernels, go for it.
