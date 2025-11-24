import pandas as pd


file_path = 'D:/Programming/StudentPerformanceFactors.csv'
df = pd.read_csv(file_path)

print("Размер датасета:", df.shape)
print(df.info())
print(df.describe())
print(df.head(10))  # Таблица с образцами данных
print(df['Parental_Involvement'].unique())