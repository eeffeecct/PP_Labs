import pandas as pd
from matplotlib import pyplot as plt
from sklearn.preprocessing import LabelEncoder
from scipy.stats import pearsonr

file_path = 'D:/Programming/StudentPerformanceFactors.csv'
df = pd.read_csv(file_path)

# Обработка пропущ.знач.
if df.isnull().sum().any():  # Проверка на наличие пропусков
    for col in df.columns:
        if df[col].dtype == 'object': # Текст столбцы
            df[col].fillna(df[col].mode()[0], inplace=True) # Вставляем самое частое знач
        else:
            df[col].fillna(df[col].mean(), inplace=True) # Числа (ср.знач)
    print("Пропуски обработаны.")
else:
    print("Пропусков нет.")

# удаление дубликатов
duplicates = df.duplicated().sum()
if duplicates > 0:
    df.drop_duplicates(inplace=True)
    print(f"Удалено {duplicates} дубликатов.")
else:
    print("Дубликатов нет.")

# Преобразование в числа
label_encoder = LabelEncoder()
categorical_cols = df.select_dtypes(include=['object']).columns  # выбор категорий
for col in categorical_cols:
    df[col + '_encoded'] = label_encoder.fit_transform(df[col])  # новые таблицы с кодами

# нормализация
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
for col in numeric_cols:
    if col != 'Exam_Score':  # не нормализуем переменную
        df[col + '_normalized'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())


print(df.head())
print(df.describe())


plt.figure(figsize=(8, 6))
plt.hist(df['Exam_Score'], bins=40, color='blue', edgecolor='black')
plt.title('Распределение оценок на экзамене')
plt.xlabel('Оценка')
plt.ylabel('Количество студентов')
plt.show()

plt.figure(figsize=(8, 6))
plt.scatter(df['Hours_Studied'], df['Exam_Score'], color='green')
plt.title('Часы учебы vs. Оценка на экзамене')
plt.xlabel('Часы учебы')
plt.ylabel('Оценка')
plt.show()

# Проверка гипотезы: Корреляция между часами учебы и оценками
corr_coef, p_value = pearsonr(df['Hours_Studied'], df['Exam_Score'])

# Вывод результатов
print(f"Коэффициент корреляции Пирсона: {corr_coef:.4f}")
print(f"p-value: {p_value:.4e}")
if p_value < 0.05:
    print("Гипотеза подтверждается: Существует значимая положительная корреляция.")
else:
    print("Гипотеза отвергается: Корреляция не значима.")
