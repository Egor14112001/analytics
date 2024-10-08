import pandas as pd

# считываем листы с excel файла
df_24_12 = pd.read_excel("Задание аналитик Тест_подведение итогов акции дек23.xlsx", sheet_name='24.12')
df_17_12 = pd.read_excel("Задание аналитик Тест_подведение итогов акции дек23.xlsx", sheet_name='17.12')
df_spr = pd.read_excel("Задание аналитик Тест_подведение итогов акции дек23.xlsx", sheet_name='Справка')
# Для удобства переименовываем название столбца
df_spr = df_spr.rename(columns={"Тип магазина ":"type_shop"})
# Отбираем только те магизны, которые находятся в ТЦ
df_spr = df_spr.query('type_shop == "ТЦ"')
# Объединяем магазины по Id и Названию Магазина 
df_17_12_merge = df_17_12.merge(df_spr, how = 'inner', on=['Id','Магазин'])
df_24_12_merge = df_24_12.merge(df_spr, how = 'inner', on=['Id','Магазин'])
# Убираем строки с пустыми ячейками
df_24_12_merge = df_24_12_merge.dropna()
df_17_12_merge = df_17_12_merge.dropna()
# Меняем тип данных столбцов, Кол-во чеков,Кол-во посетителей которые изначально были float
df_24_12_merge[['Кол-во чеков','Кол-во посетителей']] = df_24_12_merge[['Кол-во чеков','Кол-во посетителей']].astype('int32')
df_17_12_merge[['Кол-во чеков','Кол-во посетителей']] = df_17_12_merge[['Кол-во чеков','Кол-во посетителей']].astype('int32')
# Подвести итоги акции, оценивая показатели выручки, кол-ва чеков, трафика, среднего чека и конверсии. Сформулировать выводы об эффективности акции.
# Считаем итоге для листа 24_12 и 17_12 
# --- Выручка
revenue_24_12 = df_24_12_merge['Выручка'].sum()
revenue_17_12 = df_17_12_merge['Выручка'].sum()
# --- Чеки
check_17_12 = df_17_12_merge['Кол-во чеков'].sum()
check_24_12 = df_24_12_merge['Кол-во чеков'].sum()
# --- Трафик
visitors_17_12 = df_17_12_merge['Кол-во посетителей'].sum()
visitors_24_12 = df_24_12_merge['Кол-во посетителей'].sum()
# --- Средний чек
avg_check_17_12 = (df_17_12_merge['Выручка'].sum()/ df_17_12_merge['Кол-во чеков'].sum())
avg_check_24_12 = (df_24_12_merge['Выручка'].sum()/ df_24_12_merge['Кол-во чеков'].sum())
# ---  Конверсия
conversion_17_12 = (df_17_12_merge['Кол-во чеков'].sum()/df_17_12_merge['Кол-во посетителей'].sum())*100
conversion_24_12 = (df_24_12_merge['Кол-во чеков'].sum()/df_24_12_merge['Кол-во посетителей'].sum())*100

# Вывод метрик
print('revenue_24_12', revenue_24_12)
print('revenue_17_12', revenue_17_12)
print('check_17_12', check_17_12)
print('check_24_12', check_24_12)
print('avg_check_17_12', avg_check_17_12)
print('avg_check_24_12', avg_check_24_12)
print('visitors_17_12', visitors_17_12)
print('visitors_24_12', visitors_24_12)
print('conversion_17_12', conversion_17_12)
print('conversion_24_12', conversion_24_12)

# Подвести итоги и выполнить оценку эффективности по регионам. 
# группируем по регионам, делим показатели за 24_12 на 17_12 
df_results = df_24_12_merge.groupby('Область').aggregate({'Выручка':'sum','Кол-во чеков':'sum','Кол-во посетителей':'sum'})/df_17_12_merge.groupby('Область').aggregate({'Кол-во чеков':'sum','Выручка':'sum','Кол-во посетителей':'sum'})
# Считаем процент изменения показателей
df_results = df_results.sort_values(['Выручка'], ascending = False)*100-100
# формируем excel файл с показателями по регионам 
df_results.to_excel('result.xlsx')
# Подготовить отчет для руководителя в разрезе магазинов. 
# Цель отчета - выявление магазинов с наименьшим и наибольшим 
# падением показателей для дальнейшей корректирующей работы с магазинами.

# объединяем 2 датафрэйма - 24_12 и 17_12 для дальнейшего выявление магазинов с наименьшим и наибольшим паденимем показателей 
df_shop_fault = df_24_12_merge.merge(df_17_12_merge, how = 'inner', on=['Id','Магазин'])[['Id','Магазин','Выручка_x',  'Кол-во чеков_x',  'Кол-во посетителей_x','Выручка_y',  'Кол-во чеков_y',  'Кол-во посетителей_y']]
df_shop_fault.set_index(['Id','Магазин'], inplace=True)
df_shop_fault['Выручка'] = df_shop_fault['Выручка_x']/df_shop_fault['Выручка_y']
df_shop_fault['Кол-во чеков'] = df_shop_fault['Кол-во чеков_x']/df_shop_fault['Кол-во чеков_y']
df_shop_fault['Кол-во посетителей'] = df_shop_fault['Кол-во посетителей_x']/df_shop_fault['Кол-во посетителей_y']
df_shop_fault = df_shop_fault[['Выручка',  'Кол-во чеков',  'Кол-во посетителей']]*100 -100
df_shop_fault = df_shop_fault.reset_index()
# формируем excel файл с 3-мя листами
df_shop_fault_revenue = df_shop_fault.sort_values(['Выручка'])[df_shop_fault['Выручка'] < 0][['Id', 'Магазин', 'Выручка']]
df_shop_fault_check = df_shop_fault.sort_values(['Кол-во чеков'])[df_shop_fault['Кол-во чеков'] < 0][['Id', 'Магазин', 'Кол-во чеков']]
df_shop_fault_visitors = df_shop_fault.sort_values(['Кол-во посетителей'])[df_shop_fault['Кол-во посетителей'] < 0][['Id', 'Магазин', 'Кол-во посетителей']]
with pd.ExcelWriter('shop_fault.xlsx') as writer:
    df_shop_fault_revenue.to_excel(writer, sheet_name='Выручка', index=False)
    df_shop_fault_check.to_excel(writer, sheet_name='Кол-во чеков', index=False)
    df_shop_fault_visitors.to_excel(writer, sheet_name='Кол-во посетителей', index=False)
