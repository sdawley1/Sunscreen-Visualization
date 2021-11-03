%matplotlib notebook
import os, csv
import matplotlib.pyplot as plt
import numpy as np

# Get current working directory
cwd = os.getcwd()

# Attain list of csv files
files = os.listdir(cwd + '/Sunscreen-2019/')
csvs = [f for f in files if f.endswith('.csv')]
csvs.sort()

# Create subplots
m = int(np.floor(np.sqrt(np.size(csvs)))) # temporary variable
fig, ax = plt.subplots(m+1, m+1, sharex=True)
fig.suptitle('All Absorbance Spectra: Absorbance vs. Wavelength')

# Turning off axis to make it look pretty
for i in range(len(ax)):
    for j in range(len(ax)):
        ax[i][j].axis('off')

# Dictionary for font parameters in plot
fontdict = {'fontsize':6}

# Dictionary of data
# 0 index = wavelengths
# 1 index = relative absorbances
data = {}

# Inputting and plotting data
for i,name in enumerate(csvs):
    with open(cwd + '/Sunscreen-2019/{}'.format(name), 'r') as f:
        dat = csv.reader(f, delimiter=',', quotechar='|')
        wavelength = []; absorption = []
        for row in dat:
            wavelength.append(float(row[0])); absorption.append(float(row[1])) 
        data[name] = wavelength, absorption
            
    # Choosing axes to plot the data
    # Coloring beneath the curve to more clearly show the area under the curve
    ax[int(np.floor(i/(m+1)))][int(i%(m+1))].plot(wavelength, absorption, c='k', lw=0.75)
    ax[int(np.floor(i/(m+1)))][int(i%(m+1))].fill_between(wavelength,absorption, color='b', alpha=0.5)
    ax[int(np.floor(i/(m+1)))][int(i%(m+1))].set_title('id: {}'.format(i), fontdict=fontdict, pad=0)

# Here's the list of samples I think I should probably remove at some point
# The list will always be the same (thankfully) because I sorted the 
# list of csv files after importing
ids2remove = [19, 28, 29, 31, 44, 50, 54, 60, 74, 152, 154, 156, 157, 161]


# This is where I'll store the list with the outliers removed
csvs = [m for m in csvs if csvs.index(m) not in ids2remove]
# I printed the length of the csv list before and after to make sure the filter was actually applied


def find_SPF(filename):
    '''
    This is a function which determines the SPF associated with a sample.
    Only pass .csv files please :)
    
    Parameters
    ----------
    filename (str) = name of csv file. Should have SPF information in the first part of the filename 
    
    Returns
    -------
    SPF of sunscreen sample (float)
    '''
    # Get the first part of the filename - This contains the things we're interested in
    interesting = filename.split('-')[0]
    ints = []
    
    # Here we iterate through the beginning of the filename to find the integers
    # If the element is in fact an integer, append it to the list of candidates
    for i in interesting:
        try:
            ints.append(int(i))
        except:
            continue
    
    # The filenames in the sample are written in multiple ways, but one way to capture the SPF
    # without fail every time is to drop the final integer in the name IF there are more than 2 integers
    # in the file name
    if len(ints) > 2:
        ints.pop(-1)
        
    # Here I reverse the list for ease of creating the SPF from the list of integers and
    # set the SPF to zero
    # I add to the SPF value by utilizing the base 10 system of numbering
    ints.reverse(); spf = 0
    for ii,n in enumerate(ints):
        spf += n*10**(ii)
    return float(spf)

#print(find_SPF(csvs[94]))

def num_SPFs(filelist):
    '''
    This is a function which determines the number of different SPF values we measured.
    Only pass .csv files please :)
    
    Parameters
    ----------
    filelist (list) = list of csv files. Should have SPF information in the first part of the filename 

    Returns
    -------
    (Sorted) List of different SPF values in the collected data
    '''
    # Initialize a list of SPF values
    spfs = []
    
    # Iterate through each name in the list of files and determine the SPF measured in the file
    # We can use the function `find_SPF` we made earlier! 
    for filename in filelist:
        spf = find_SPF(filename)
        
        # Append to list only if we haven't already added it
        # We're interested in the SPF, not the number of times we measured the SPF, after all
        if spf not in spfs:
            spfs.append(spf)
            
    # Sort the list
    spfs.sort()
        
    return spfs

def avg_absorption(filename, lambda_range):
    '''
    This is a function which determines the average absorbance of a sample over a specified wavelength range
    Only pass .csv files please :)
    
    Parameters
    ----------
    filename (str) = name of csv file. Should have SPF information in the first part of the filename 
    lambda_range (tuple) = tuple of (min, max) wavelength values to average absorbances 
    
    Returns
    -------
    Average absorbance across given range of wavelengths (float)
    
    '''
    # Finding lower/upper bound for wavelength range
    lb, ub = lambda_range
    Sam_Dawley = True
    
    # Determining indices of this wavelength range in data set for sample
    # If the absorption at the desired wavelength wasn't recorded, continually
    # add +1 to the lower bound on the wavelength until we find the largest possible
    # wavelength which is closest to the desired wavelength
    # 'NA1003-film-206.csv' doesn't have 280 as a wavelength, so that's why 
    # I had to make this more complicated than it needed to be
    while Sam_Dawley == True:
        try:
            id_lb, id_ub = (data[filename][0]).index(lb), (data[filename][0]).index(ub)
            Sam_Dawley = False
        except:
            if lb not in data[filename][0]:
                lb += 1

    # Averaging the absorptions on the specified wavelength range of the sample data
    return float(np.average([v for v in data[filename][1][id_lb:id_ub]]))

def avg_SPF_absorption(filelist, lambda_range, SPF):
    '''
    This is a function which computes the average absorbance for all samples with a 
    particluar SPF over a specified range of wavelengths. Only pass .csv files please :)
    
    Parameters
    ----------
    filelist (list) = list of csv files. Should have SPF information in the first part of each filename 
    lambda_range (tuple) = tuple of (min, max) wavelength values to average absorbances 
    SPF (int) = particular SPF we want to average on
    
    Returns
    -------
    Average absorbance for a particular SPF across given range of wavelengths (float)
    
    '''
    # Cumulative list of averages to do statistics on later
    cumlist = []
    
    # Iterate through each data set in the list of files
    # Use the function `avg_absorption` we defined above!
    for name in filelist:
        if find_SPF(name) == SPF:
            cumlist.append(avg_absorption(name, lambda_range))
        
    # Averaging the absorptions on the specified wavelength range of the sample data
    return np.average(cumlist), np.std(cumlist)

for f in range(len(csvs)):
    try:
        avg_absorption(csvs[f], (280, 315))
        avg_absorption(csvs[f], (315, 400))
        avg_SPF_absorption(csvs, (280, 315), 100)
        avg_SPF_absorption(csvs, (315, 400), 100)
    except:
        print('{} didn\'t work for some reason'.format(csvs[f]))

# Creating new visualization for absorbance on nm=[280, 315]
fig = plt.figure()

# Wavelength range
m = 280; n = 315

# Iterating through list of data sets and plotting
for f in csvs:
    try:
        x = find_SPF(f)
        y = avg_absorption(f, (m, n))
        plt.plot([x], [y], marker='o', c='b', markersize=7.5, alpha=0.08)
    except:
        print(f)

# Plotting the mean and error bars
for SPF in num_SPFs(csvs):
    x2 = SPF
    y2 = avg_SPF_absorption(csvs, (m,n), SPF)[0]
    plt.plot(x2, y2, marker='o', c='b', markersize=3)
    plt.errorbar(x2, y2, yerr=avg_SPF_absorption(csvs, (m,n), SPF)[1],
                 capsize=5, c='b', elinewidth=2, capthick=2)

# Making the plot informative
plt.title('Average Absorbance on Interval [{0}, {1}] nm'.format(m, n))
plt.xlabel('SPF')
plt.ylabel('Average Relative Absorbance')

# Creating new visualization for absorbance on nm=[315, 400]
fig = plt.figure()

# Wavelength range
m2 = 315; n2 = 400

# Iterating through list of data sets and plotting
for f in csvs:
    try:
        x = find_SPF(f)
        y = avg_absorption(f, (m2, n2))
        plt.plot([x], [y], marker='o', c='r', markersize=7.5, alpha=0.08)
    except:
        print(f)
        
for SPF in num_SPFs(csvs):
    x3 = SPF
    y3 = avg_SPF_absorption(csvs, (m2,n2), SPF)[0]
    plt.plot(x3, y3, marker='o', c='r', markersize=3)
    plt.errorbar(x3, y3, yerr=avg_SPF_absorption(csvs, (m2,n2), SPF)[1], 
                 capsize=5, c='r', elinewidth=2, capthick=2)
    
# Making the plot informative
plt.title('Average Absorbance on Interval [{0}, {1}] nm'.format(m2, n2))
plt.xlabel('SPF')
plt.ylabel('Average Relative Absorbance')


from scipy.stats import linregress

fig = plt.figure()

# Wavelength range(s)
m = 280; m2 = 315
n = 315; n2 = 400

# Lists to run linear regression on 
UVA = []
UVB = []
       
# Plotting the data for comparison
for SPF in num_SPFs(csvs):
    # x and y values
    xn = SPF-0.5; xns = SPF+0.5
    yn = avg_SPF_absorption(csvs, (m,n), SPF)[0]; yn2 = avg_SPF_absorption(csvs, (m2,n2), SPF)[0]
    UVA.append(yn); UVB.append(yn2) 
    
    # Means of each data set and associated error bars
    plt.plot(xn, yn, marker='o', c='b', markersize=3, alpha=0.5)
    plt.plot(xns, yn2, marker='o', c='r', markersize=3, alpha=0.5)
    plt.errorbar(xn, yn, yerr=avg_SPF_absorption(csvs, (m,n), SPF)[1], capsize=5, c='b', alpha=0.5)
    plt.errorbar(xns, yn2, yerr=avg_SPF_absorption(csvs, (m2,n2), SPF)[1], capsize=5, c='r', alpha=0.5)

# Linear regression
blue_curve = linregress(num_SPFs(csvs), UVA)
temp = [blue_curve[0]*h+blue_curve[1] for h in num_SPFs(csvs)]
red_curve = linregress(num_SPFs(csvs), UVB)
temp2 = [red_curve[0]*h+red_curve[1] for h in num_SPFs(csvs)]

# Plotting the linear regression so our work isn't in vein
plt.plot(num_SPFs(csvs), temp, c='b', label='UVA Absorption')
plt.plot(num_SPFs(csvs), temp2, c='r', label='UVB Absorption')

# Making the plot informative
plt.title('Comparing Average Absorbances')
plt.xlabel('SPF')
plt.ylabel('Average Relative Absorbance')
plt.legend()

print('Coefficient of Determination for UVA Absorption: {:0.3f}'.format(blue_curve[2]**2))
print('Coefficient of Determination for UVA Absorption: {:0.3f}'.format(red_curve[2]**2))




    
