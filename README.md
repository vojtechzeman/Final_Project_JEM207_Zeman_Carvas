# Final_Project_JEM207_Zeman_Carvas
Real Estate Market Analysis

Vision: We will look for undervalued apartments in Prague. The user will be able to independently analyze rental prices and purchase prices. The analysis will be limited to apartments in the Prague area.

The project will have the following parts:
- Data scraping
- Updating the previous scraped dataset (to speed up the second and subsequent processes).
- Selecting only deleted ads (ad is in the previous scraping, but not in the current one), that will mean we found the real market value of the properties (many ads are advertised overpriced)
- Data cleaning
- Modeling (detrending time series data, application of machine learning)
- Finding undervalued properties
- Graphical analysis of the price distribution and some other data summary
- All processes will run only on the parameter selected by the user: rents vs purchase prices (speeding up processes)

Other potential parts:
- (Model verification implementation using existing home value estimator websites)
- (Scraping data from other websites)
