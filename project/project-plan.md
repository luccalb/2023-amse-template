# Project Plan

## Summary

<!-- Describe your data science project in max. 5 sentences. -->
This projects analyzes if there is a correlation between the gross domestic product (GDP) per person and the ~~CO2 mass emitted by~~ share of electric vehicles of newly registered cars in Germany.

## Rationale

<!-- Outline the impact of the analysis, e.g. which pains it solves. -->
The analysis helps interested citizens and researchers to test ~~the claim that per capita CO2 emissions rise with income~~ if the relatively high cost of electric vehicles favors a more rapid transition towards EVs in wealthier german states. It is limited to the domain of privately owned vehicles ~~and their emissions~~.

## Datasources

<!-- Describe each datasources you plan to use in a section. Use the prefic "DatasourceX" where X is the id of the datasource. -->

### Newly registered vehicles: Kraftfahrtbundesamt (KBA)
* Metadata URL: https://mobilithek.info/offers/573358127875792896
* Data URL: https://www.kba.de/SharedDocs/Downloads/DE/Statistik/Fahrzeuge/FZ11/fz11_2022_01.xlsx?__blob=publicationFile&v=8
* Data Type: XLSX

Lists the newly registered vehicles in germany by manufacturer, model, type, state, CO2 emissions and more.

### Gross domestic product per capita and state: Statistikportal
* Metadata URL: https://www.statistikportal.de/de/veroeffentlichungen/bruttoinlandsprodukt-bruttowertschoepfung
* Data URL: https://www.statistikportal.de/sites/default/files/2023-03/vgrdl_r1b1_bs2022_1.xlsx
* Data Type: XLSX

Lists the gross domestic product per capita per state in germany.

## Work Packages

<!-- List of work packages ordered sequentially, each pointing to an issue with more details. -->

1. Sight the data [#1][i1]
2. Clean the data and populate the SQLite database [#2][i2]
3. Define target dimensions for data analysis [#3][i3]
4. Perform data analysis [#4][i4]
5. Visualize analysis results [#5][i5]

[i1]: https://github.com/luccalb/2023-amse-template/issues/1
[i2]: https://github.com/luccalb/2023-amse-template/issues/2
[i3]: https://github.com/luccalb/2023-amse-template/issues/3
[i4]: https://github.com/luccalb/2023-amse-template/issues/4
[i5]: https://github.com/luccalb/2023-amse-template/issues/5

