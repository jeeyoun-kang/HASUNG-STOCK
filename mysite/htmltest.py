
import json
import mpld3
import matplotlib.pyplot as plt

f = plt.figure()
plt.plot([1,2,3], [4,5,6])

print(mpld3.fig_to_html(f, figid='THIS_IS_FIGID'))