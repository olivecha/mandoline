# Welcome to the AMReX Kitchen

<img width="450" alt="image" src="https://github.com/olivecha/amrex-kitchen/assets/78630053/f2115bef-887a-4408-8d20-6be15bb0a4a4">

This is a collection of tools to perform post processing and visualization tasks 
on the AMReX plotfile format. For the moment all tools are written in python
and make use of the `multiprocessing` module when advantageous to do so. 

A kitchen themed naming convention is employed as it helps remembering the
command names and conveys a positive sentiment. It also makes sense of the
colloquial phrase *"Let him cook"* and the Breaking Bad reference *"we need to
cook"* which is well suited to the analysis of reacting flows.

## Overview of the tools

- **chef:** Compute (cook) derived thermochemical quantities (recipes) using Cantera
            `SolutionArrays`.

- **colander:** Strains out fileds or levels from a plotfile to make the file-size more manageable.

- **combine:** Combine fields from two plotfile with the same geometric mesh data.

- **mandoline:** Create (fast) slices of 3D plotfiles or covered grids of 2D plotfiles

- **menu:** Print out field information and min/max values by only reading the plotfile headers

- **pestle:** Grind and combine, fast and low memory volume integrals for multi-level plotfiles.

- **taste:** Parse the plotfile data to ensure it is not corrupted and that no files are missing.

- **whip:** Increased volume, 3D uniform grids from adaptive mesh refinement data.
            Smaller data types are supported (`float32`, ...) to reduce memory usage

- **minuterie:** Its all about timing, prints out the time of the plotfile,
                 much faster than amrex/Tools/Plotfile/ftime.cpp. (work in progress)

- **PlotfileCooker:** The base python class used by most tools to process the
                  plotfile data. Also makes available methods which provide
                  iterators over the data in the plotfile by each AMR level.
  
- **marinate:** Save the `PlotfileCooker` instance to binary using the python `pickle` library.
                This allows exploring the adaptive mesh refinement without needing the whole plotfile. 
  

## Installation

The python pakage will eventually be distributed with pip, but in the mean time
it can be installed manually by cloning the repository:

Clone the repository
```
git clone https://github.com/olivecha/amrex-kitchen.git
```
Go into it
```
cd amrex-kitchen
```

(Optional) Activate your python virtual or conda environment.

Install the requirements:
```
pip install -r requirements.txt
```

Then install the amrex-kitchen module:
```
pip install -e .
```
The `-e` flag makes the source files editable so reinstalling after each `git pull` is not necessary.

## Performance

All tools are tested on large (> 1TB) plotfiles with around 40 fields and 5 AMR Levels.
The computationaly intensive tools were optimized to work best on a single node
of a CPU cluster (Niagara) with a large number of CPUs (40), and a large amount of RAM (> 100 GB).

Compared to the tools proposed in the AMReX repository, what is proposed here is arguably a bit slower when a large amount of computing
power is available, as the `multiprocessing` module is limited to a single compute node. However, the tools proposed here work well with 
arbitrarly large plotfiles, and scale linearly with plotfile size (with some exceptions).

# Documentation

## Chef

The **chef** has entered the Amrex kitchen: with this tool you can apply **recipes** to plotfiles.

![image](https://github.com/user-attachments/assets/d0f20c96-a34a-4118-80d8-a75dacd468a5)

There are predefined recipes like Enthalpy and HeatRelease:
```
chef --outdir plthrr --recipe HRR --mech mechanism.yaml --pressure 1 plt00000
```
You can apply recipes on selected species, like the reaction rate of H2 and O2:
```
chef --outdir pltomega_sp --recipe SRi --species H2 O2 --mech mechanism.yaml --pressure 1 plt00000
```
Or selected individual reactions like the net rate of progress:
```
chef --outdir pltnetrxrate --recipe RRi --reactions 0 1 2 3 --mech mechanism.yaml --pressure 1 plt00000
```
But you can also be the chef and define your own recipes in an arbitrary `.py` file and pass it as an argument. 
The function must take two or three arguments. if it takes three they are a dictionnary containing the indexes
of the fields in the plotfile, a box array with shape (nx, ny, nz, nfields) and a Cantera SolutionArray with shape
(nx, ny, nz). In the case of two arguments the SolutionArray is omitted which is faster. The docstring of the 
function is taken as the field name in the plotfile.

For example using the SolutionArray to access the reactions rates and compute the ratio between the production
rates of two species:
```python
# my_recipe.py

def recipe(field_indexes, box_array, sol_array):
    """
    fuel_oxy_omega_ratio
    """
    id_H2 = sol_array.species_index('H2')
    id_O2 = sol_array.species_index('O2')
    omega_H2 = sol_array.net_production_rates[:, :, :, id_H2]
    omega_O2 = sol_array.net_production_rates[:, :, :, id_O2]
    return omega_H2/omega_O2
```
Then using the following command:
```
$ chef --output pltrxratio --recipe my_recipe.py --mech mechanism.yaml --pressure 1 plt00000
```

Or computing the difference between the temperature and an arbitrary value wich is function of 
the progress variable:
```
# my_recipe2.py

T_vs_C = a_user_defined_function...

def recipe(field_indexes, box_array):
    """
    T_minus_T_C
    """
    temp = box_array[:, :, :, field_indexes["temp"]]
    C = box_array[:, :, :, field_indexes["progress_variable"]]
    return temp - T_vs_C(C)
```
Which is computed using a similar command (without needing mechanism or pressure inputs):
```
$ chef --output pltTdiff --recipe my_recipe2.py plt00000
```

## Colander

<img width="300" alt="colander" src="https://github.com/olivecha/amrex-kitchen/assets/78630053/aec452e7-520e-4f2c-bbb2-44c79dd0c6ca">

Strain out variables or levels from plotfiles, see:

```
$ colander --help
```

## mandoline

<img width="350" alt="image" src="https://github.com/olivecha/mandoline/assets/78630053/857636f4-e49d-41d2-b428-6e12b6874157">

Fast slices of (large) AMReX plotfiles. This is equivalent to
`amrex/Tools/Plotfile/fsnapshot.cpp`, and retains the command line arguments names when available, 
but it only loads the data needed for the slice, so large plotfiles can be
visualized rapidly. This tools also supports multiple output formats (`.png`
image, `.npy` array and 2D AMReX plotfiles). Slicing a 2D plotfile will simply
create a uniform grid for the data, and put it in the output format. If the
`plotfile` format is used with a 2D plotfile the binary files will be rewritten
with the requested fields in the output file.


### Usage

```
usage: mandoline [-h] [--normal NORMAL] [--position POSITION] [--variables VARIABLES [VARIABLES ...]] [--max_level MAX_LEVEL]
                 [--serial] [--format FORMAT] [--output OUTPUT] [--colormap COLORMAP] [--minimum MINIMUM] [--maximum MAXIMUM]
                 [--log] [--verbose VERBOSE]
                 plotfile

Fast slices of (large) AMReX plotfiles

positional arguments:
  plotfile              Path of the plotfile to slice

options:
  -h, --help            show this help message and exit

  --normal, -n NORMAL   Index of the coordinate normal to the slice x:0, y:1, z:2

  --position, -p POSITION   position of the slice in mesh coordinates, defaults to domain center.

  --variables, -v VARIABLES [VARIABLES ...]
                        variables names to slice, defaults to "density", "all" slices all the fields in the plotfile, "grid_level"
                        outputs the AMR grid level data.

  --max_level, -L MAX_LEVEL   Maximum AMR level loaded, defaults to finest level.

  --serial, -s          Flag to disable multiprocessing, this is usefull when processing many small plotfiles in a bash loop.

  --format, -f FORMAT   Either "image", "array" or "plotfile". image: creates and saves an image using matplotlib. array: creates
                        a numpy array with a uniform grid at the resolution of --max_level and saves it as a numpy file with
                        separated fields. plotfile: Keep the adaptive mesh refinement information and save the slice and specified
                        fields in a 2D amrex plotfile

  --output, -o OUTPUT   Output file name used to override the default value.

  --verbose, -V VERBOSE   Verbosity level, defaults to 1

 # Image output flags
  --colormap, -c COLORMAP   A named matplotlib colormap, defaults to jet.
  --minimum, -m MINIMUM     Minimum value used in the colormap
  --maximum, -M MAXIMUM.    Maximum value used in the colormap
  --log, -l                 Flag to use log scale in the plotted image
```
### How it works

AMReX blocks intersecting the slicing plane are read from the plotfile. Arrays
with the closests points at either side of the plane are constructed for each
level and a linear interpolation is performed to compute the data in the slice. 

Support for non-orthogonal slicing planes, and downsampling of higher level
data to increase speed and reduce output size is planned.

**Known issue:** when the slice position is between the last point of a higher
level box and the fist point of a lower level box it is possible that the region
will only be covered with lower level data. Moving the slice by the grid
resolution of the highest level is a temporary fix. 






