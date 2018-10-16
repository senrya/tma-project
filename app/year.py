import matplotlib.pyplot as plot
import numpy as np
 
# Year data for the semilog plot 
years       = [1900, 1910, 1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2017]
 
# index data - taken at end of every decade - for the semilog plot 
indexValues = [68, 81, 71, 244, 151, 200, 615, 809, 824, 2633, 10787, 11577, 20656]
 
# Display grid
plot.grid(True, which="both")
 
# Linear X axis, Logarithmic Y axis 
plot.semilogy(years, indexValues )
#plot.ylim([10,21000])
#plot.xlim([1900,2020])
 
# Provide the title for the semilog plot 
plot.title('Y axis in Semilog using Python Matplotlib')
 
# Give x axis label for the semilog plot
plot.xlabel('Year')
 
# Give y axis label for the semilog plot
plot.ylabel('Stock market index')
 
# Display the semilog plot
plot.show()