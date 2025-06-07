import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split

# Apply Seaborn theme
sns.set_theme(style="whitegrid")

# Create mock dataset
data = pd.DataFrame({
        'Age': [22, 25, 47, 52, 46, 56, 55, 60],
            'Income': [50000, 60000, 80000, 110000, 95000, 120000, 115000, 140000],
                'Student': ['No', 'Yes', 'Yes', 'No', 'No', 'Yes', 'No', 'Yes'],
                    'Buys_Laptop': ['No', 'Yes', 'Yes', 'No', 'Yes', 'Yes', 'No', 'Yes']
})

# Convert categorical variable
data['Student'] = data['Student'].map({'Yes': 1, 'No': 0})
data['Buys_Laptop'] = data['Buys_Laptop'].map({'Yes': 1, 'No': 0})

# Features and target
X = data[['Age', 'Income', 'Student']]
y = data['Buys_Laptop']

# Train/test split (not necessary but good practice)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train decision tree classifier
clf = DecisionTreeClassifier(max_depth=3, random_state=42)
clf.fit(X_train, y_train)

# Plot the decision tree
plt.figure(figsize=(10, 6))
plot_tree(clf,
          feature_names=X.columns,
                    class_names=['No', 'Yes'],
                              filled=True,
                                        rounded=True,
                                                  fontsize=12)
plt.title("Decision Tree - Buys Laptop", fontsize=16)
plt.tight_layout()
#plt.show()
plt.savefig("decision_tree.png")

