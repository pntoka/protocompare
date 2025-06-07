import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Apply Seaborn style
sns.set_theme(style="whitegrid")

# Labels for each axis
labels = ['Speed', 'Reliability', 'Comfort', 'Safety', 'Efficiency']
num_vars = len(labels)

# Data values (normalized 0–1 or in similar range)
values = [0.8, 0.7, 0.6, 0.9, 0.75]
values += values[:1]  # close the circle

# Angle of each axis in the plot (in radians)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]

# Create radar plot
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

# Draw outline and fill
ax.plot(angles, values, color='tab:blue', linewidth=2)
ax.fill(angles, values, color='tab:blue', alpha=0.3)

# Set the labels for each axis
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontsize=12)

# Set radius gridlines and labels
ax.set_rlabel_position(30)
ax.set_yticks([0.2, 0.4, 0.6, 0.8])
ax.set_yticklabels(["20%", "40%", "60%", "80%"], fontsize=10)
ax.set_ylim(0, 1)

# Title
plt.title('Performance Metrics', size=16, weight='bold', pad=20)

plt.tight_layout()
#plt.show()
plt.savefig("webchart.png")

