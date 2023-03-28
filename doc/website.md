# Base website model

##  Home page

- Title
- Quick abstract, link to more complete description (and eventual publications)
- List of application pages (with popup showing application abstract)
- Logos and funding acknowledgements (see [README.md](../README.md#acknowledgements))

## Application pages

Those are pages allowing to use the `blockops` library for one specific thematic application. It can be for instance an error analysis of a given time-stepping scheme, a scheduling representation of a time-parallel algorithm, a speedup modeling of a time-parallel strategy, etc ...
Each application page is organized as follow 

| Column 1 | Column 2 | Column 3 |
| :------: | :------: | :------: |
| Description | Settings | Plots |

Each column contain components that are eventually displayed incrementally.
At first, the `Settings` columns contains a component 
allowing to setup the first main parameters for the application,
with some eventual associated documentation component located in the `Description` column.
Then, setting values for the `Settings` component will eventually add more `Settings` component afterward, additional `Description` components, and ultimately display some plots in the `Plots` column. 
Specific plot settings are displayed on the top of the `Plots` column.

**Summary :**

1. Accuracy and stability of time-integration scheme on the complex plane :<br>
TODO : documentation ...
2. Local and global truncation error of time-integration scheme :<br>
TODO : documentation
3. PinT analysis on complex plane :<br>
see [parameter description](./web-applications/1_params.md) for parameter description and [output components description](./web-applications/2_outputs.md)