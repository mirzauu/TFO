import matplotlib.pyplot as plt
import pandas as pd

# Data
data = {
    'Trends': ['AI Integration', 'Financial Performance', 'Growth Potential', 'Technological Advancements'],
    'Scores': [4, 5, 3, 4]
}

df = pd.DataFrame(data)

# Plotting
plt.figure(figsize=(8, 6))
plt.bar(df['Trends'], df['Scores'], color='skyblue')
plt.xlabel('Trends')
plt.ylabel('Scores')
plt.title('Apple Inc. Market Trends Analysis')
plt.savefig('visualization.png', dpi=300, bbox_inches='tight')

plt.show()