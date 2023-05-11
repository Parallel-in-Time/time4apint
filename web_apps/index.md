## Motivations

Develop a python code based on a generic framework allowing to investigate and analyze the performance of iterative parallel-in-time (PinT) algorithms : [blockops](./blockops/)

Implement a graphical user interface that could be exposed through a [**demonstration website (web api)**](./accuracy).

> Take a look at the [API Demonstration](./demo)

## Base convention

Represent an iterative PinT algorithm with a **block iteration** of the form

$$
u_{n+1}^{k+1} = B_1^0 u_{n+1}^k + B_0^0 u_{n}^k + B_0^1 u_{n}^{k+1} + ...
$$

with $B_i^j$ the **block coefficient**, built using one or a combination of **block operators** (addition, substraction, multiplication, inverse).
For instance, looking at the Parareal algorithm, we have

$$
u_{n+1}^{k+1} = (F - G) u_{n}^k + G u_{n}^{k+1},
$$

with $F$ and $G$ the block operators.
Then we have two block coefficients $B_0^0 = F-G$ and $B_0^1 = G$. Note that the same block operator can be present in several block coefficients.

**Note** : block coefficients indices don't depend on $k$ and $n$, but on the offset.
Hence, $B_1^0$ is the block coefficient for the $u_{n+1}^{k+0}$ term, and the block coefficient for the $u_{n-1}^{k+1}$ term would then be $B_{-1}^{1}$.

Any combination of block operators can be seen as a unique block operator, hence a block coefficient is itself a combination of block operators and also a block operator. This aspect is fully used in the framework implementation.

## Acknowledgements

This repository results from a collaboration between University of Wuppertal ([Jens HAHNE](https://www.hpc.uni-wuppertal.de/de/mitarbeiter/jens-hahne/)) and Hamburg University of Technology ([Thibaut LUNET](https://www.mat.tuhh.de/home/tlunet/?homepage_id=tlunet)), as part of the [Time-X project](https://www.timex-eurohpc.eu/).

This project has received funding from the [European High-Performance Computing Joint Undertaking](https://eurohpc-ju.europa.eu/) (JU) under grant agreement No 955701 ([Time-X](https://www.timex-eurohpc.eu/)). The JU receives support from the European Union’s Horizon 2020 research and innovation programme and Belgium, France, Germany, and Switzerland. This project also received funding from the [German Federal Ministry of Education and Research](https://www.bmbf.de/bmbf/en/home/home_node.html) (BMBF) grant 16HPC048.

<div
    class="uk-child-width-1-3@s uk-text-center"
    uk-grid="masonry: true"
>
    <div>
    <div class="uk-card uk-card-default uk-card-body">
        <img src="/images/logo_BUW_black.png" />
    </div>
    </div>
    <div>
    <div class="uk-card uk-card-default uk-card-body">
        <img src="/images/tuhh-logo.png" />
    </div>
    </div>
    <div>
    <div class="uk-card uk-card-default uk-card-body">
        <img src="/images/LogoTime-X.png" />
    </div>
    </div>
    <div>
    <div class="uk-card uk-card-default uk-card-body">
        <img src="/images/EuroHPC.jpg" />
    </div>
    </div>
    <div>
    <div class="uk-card uk-card-default uk-card-body">
        <img src="/images/logo_eu.png" />
    </div>
    </div>
    <div>
    <div class="uk-card uk-card-default uk-card-body">
        <img src="/images/BMBF_gefoerdert_2017_en.jpg" />
    </div>
    </div>
</div>

```{image} /images/EuroHPC.jpg
:alt: alt Text
:width: 300
```

```{image} /images/logo_BUW_black.png
:alt: alt Text
:width: 300
```

```{image} /images/tuhh-logo.png
:alt: alt Text
:width: 300
```

```{figure} /images/LogoTime-X.png
:alt: alt Text
:width: 300
```

```{figure} /images/logo_eu.png
:alt: alt Text
:width: 300
```

```{figure} /images/BMBF_gefoerdert_2017_en.jpg
:alt: alt Text
:width: 300
```
