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
| Docs | Settings | Plots |

Each column contain components that are eventually displayed incrementally.
At first, the `Settings` columns contains a component 
allowing to setup the first main parameters for the application,
with some eventual associated documentation component located in the `Docs` column.
Then, setting values for the `Settings` component will eventually add more `Settings` component afterward, additional `Docs` components, and ultimately display some `Plots` components. 
Specific plot settings are displayed on the top of the `Plots` column.

**Summary :**

1. Accuracy and stability on the complex plane :<br>
TODO : [documentation ...](./web-applications/1_accuracy.md)
2. Convergence of local and global truncation error :<br>
TODO : [documentation ...](./web-applications/2_convergence.md)
3. Error of an approximate / coarse block operator :<br>
TODO : [documentation ...](./web-applications/3_error.md)
4. Task graph and schedule of a PinT algorithm :<br>
TODO : [documentation ...](./web-applications/4_tasks.md)
5. PinT performance analysis on the complex plane :<br>
Display the estimated speedup and efficiency of a PinT iterative algorithm in the complex plane, provided that iteration are done until the PinT error is lower
than the fine discretization error. See [more details here ...](./web-applications/5_speedup.md)