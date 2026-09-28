# %%
import pandas as pd

ruta = r"D:\智利實習\reporte_cupos_agenda\cupos_tucapel.xlsx"
df_raw = pd.read_excel(ruta)

print(f"原始筆數：{len(df_raw)}") #172685
print(f"完全重複：{df_raw.duplicated().sum()} 筆") #3
print(f"排除 Número 後重複：{df_raw.duplicated(subset=df_raw.columns.drop('Número')).sum()} 筆")

df = df_raw.drop_duplicates().copy()
# %%
df.head(10)
# %%
df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')

print(f"日期無法轉換：{df['Fecha'].isna().sum()} 筆")
print(f"日期範圍：{df['Fecha'].min().date()} ～ {df['Fecha'].max().date()}")

pd.crosstab(df['Fecha'].dt.to_period('M'), df['Estado'])

# %%
fecha_corte = pd.Timestamp('2026-09-01')

antes = len(df)
df = df[df['Fecha'] < fecha_corte].copy()
print(f"刪除 9 月之後：{antes - len(df)} 筆，剩下 {len(df)} 筆") # 163937
print(f"日期範圍：{df['Fecha'].min().date()} ～ {df['Fecha'].max().date()}")

# %%
tabla = df['Estado'].value_counts(dropna=False).to_frame('筆數')
tabla['比例'] = (tabla['筆數'] / len(df) * 100).round(1).astype(str) + '%'
tabla.loc['合計'] = [len(df), '100.0%']
tabla

# %%
clave = ['Documento', 'Fecha', 'Hora']
multi = df[df.duplicated(subset=clave, keep=False)].sort_values(clave)

print(f"同一病患同一天同一時間有多筆：{len(multi)} 筆")
print(multi.groupby(clave)['Estado'].apply(lambda s: ' + '.join(s.fillna('空白'))).value_counts().head(10))

# %%
g = multi.groupby(clave).agg(n_prof=('Profesional', 'nunique'),
                             n_prest=('Prestación', 'nunique'))
print(f"總組數：{len(g)}")
pd.crosstab(g['n_prof'] > 1, g['n_prest'] > 1,
            rownames=['不同專業人員'], colnames=['不同服務項目'])

# %%
prioridad = {'VISITADO': 1, 'EN CONSULTA': 2, 'EN ESPERA': 3,
             'NO PRESENTADO': 4, 'NO ATENDIDO': 5, 'CITADO': 6}
df['_prio'] = df['Estado'].map(prioridad).fillna(7)

clave2 = ['Documento', 'Fecha', 'Hora', 'Profesional', 'Prestación']
antes = len(df)
df = (df.sort_values('_prio')
        .drop_duplicates(subset=clave2, keep='first')
        .drop(columns='_prio')
        .sort_index())
print(f"刪除重複登記：{antes - len(df)} 筆，剩下 {len(df)} 筆")
# %%
antes = len(df)
df = df[df['Estado'].notna() & ~df['Estado'].isin(['CITADO', 'NO ATENDIDO'])].copy()
print(f"刪除空白、已預約、未看診：{antes - len(df)} 筆，剩下 {len(df)} 筆")

df['缺席'] = (df['Estado'] == 'NO PRESENTADO').astype(int)

print(df['Estado'].value_counts())
print(f"分母（出席 + 未到診）：{len(df)}")
print(f"分子（未到診）：{df['缺席'].sum()}")
print(f"缺席率：{df['缺席'].mean():.1%}")

######################
########進一步拆解
######################
# %% [0] 共用設定
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
 
# 讓圖表可以顯示中文（Windows）
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False
 
resultados = {}   # 所有結果表先存在這裡，最後再一次輸出
 
# %%  
def tasa(data, col, min_n=100, ordenar=True):
    """依某欄分組計算缺席率；預約數少於 min_n 的組別不顯示"""
    t = data.groupby(col, observed=True)['缺席'].agg(預約數='size', 缺席數='sum', 缺席率='mean')
    t['缺席率'] = (t['缺席率'] * 100).round(1)
    t = t[t['預約數'] >= min_n]
    return t.sort_values('缺席率', ascending=False) if ordenar else t
 
 
def grafico_barras(t, titulo):
    ax = t['缺席率'].plot(kind='bar', figsize=(8, 4), color='steelblue')
    ax.set_title(titulo)
    ax.set_ylabel('缺席率（%）')
    ax.set_xlabel('')
    for i, v in enumerate(t['缺席率']):
        ax.text(i, v + 0.2, f'{v}%', ha='center', fontsize=9)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()
 
 
print(f"分析筆數：{len(df)}，整體缺席率：{df['缺席'].mean():.1%}")
 
 
# %% [1] 預約前置天數
df['Fecha Emisión'] = pd.to_datetime(df['Fecha Emisión'], dayfirst=True, errors='coerce')
df['前置天數'] = (df['Fecha'].dt.normalize() - df['Fecha Emisión'].dt.normalize()).dt.days
 
print(f"Fecha Emisión 無法轉換：{df['Fecha Emisión'].isna().sum()} 筆")
print(f"前置天數為負數（建立日晚於預約日）：{(df['前置天數'] < 0).sum()} 筆 → 不列入此分析")
print(df['前置天數'].describe().round(1))
 
df['前置分組'] = pd.cut(df['前置天數'], bins=[-0.5, 0.5, 7, 30, 60, np.inf],
                    labels=['當天', '1–7 天', '8–30 天', '31–60 天', '60 天以上'])
 
t = tasa(df, '前置分組', min_n=0, ordenar=False)
resultados['1_前置天數'] = t
display(t)
grafico_barras(t, '依預約前置天數的缺席率')
 
sin_mismo_dia = df[df['前置天數'] > 0]
print(f"排除當天預約後的缺席率：{sin_mismo_dia['缺席'].mean():.1%}")
 
 
# %% [2a] 星期 × 時段
hora = pd.to_datetime(df['Hora'].astype(str), format='mixed', errors='coerce')
df['小時'] = hora.dt.hour
print(f"Hora 無法轉換：{df['小時'].isna().sum()} 筆")
 
df['時段'] = pd.cut(df['小時'], bins=[-1, 11, 13, 23],
                  labels=['早上（12點前）', '中午（12–14點）', '下午（14點後）'])
 
dias = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
df['星期'] = pd.Categorical(df['Fecha'].dt.dayofweek.map(lambda d: dias[d]),
                          categories=dias, ordered=True)
 
resultados['2_星期'] = tasa(df, '星期', min_n=0, ordenar=False)
resultados['2_時段'] = tasa(df, '時段', min_n=0, ordenar=False)
resultados['2_小時'] = tasa(df, '小時', min_n=50, ordenar=False)
display(resultados['2_星期'], resultados['2_時段'], resultados['2_小時'])
 
# 熱圖
tasa_mapa = df.pivot_table(index='星期', columns='時段', values='缺席',
                           aggfunc='mean', observed=True) * 100
n_mapa = df.pivot_table(index='星期', columns='時段', values='缺席',
                        aggfunc='size', observed=True)
resultados['2_星期x時段'] = tasa_mapa.round(1)
 
fig, ax = plt.subplots(figsize=(7, 4))
im = ax.imshow(tasa_mapa.values, cmap='Reds', aspect='auto')
ax.set_xticks(range(len(tasa_mapa.columns)), tasa_mapa.columns)
ax.set_yticks(range(len(tasa_mapa.index)), tasa_mapa.index)
for i in range(tasa_mapa.shape[0]):
    for j in range(tasa_mapa.shape[1]):
        v, n = tasa_mapa.iat[i, j], n_mapa.iat[i, j]
        if pd.notna(v):
            ax.text(j, i, f'{v:.1f}%\n(n={n:,})', ha='center', va='center', fontsize=8)
ax.set_title('星期 × 時段 缺席率')
plt.colorbar(im, label='缺席率（%）')
plt.tight_layout()
plt.show()
 
 
# %% [2b] 月份
df['月份'] = df['Fecha'].dt.to_period('M')
t = tasa(df, '月份', min_n=0, ordenar=False)
resultados['2_月份'] = t
display(t)
 
ax = t['缺席率'].plot(marker='o', figsize=(8, 4))
ax.set_title('每月缺席率')
ax.set_ylabel('缺席率（%）')
ax.set_xlabel('')
plt.tight_layout()
plt.show()
 
 
# %% [3] 服務與人員
for col in ['Categoría', 'Sector', 'Prestación', 'Profesional']:
    t = tasa(df, col)
    resultados[f'3_{col}'] = t
    print(f"\n===== {col}（共 {len(t)} 組，只列預約數 ≥ 100 的組別）=====")
    display(t if len(t) <= 20 else pd.concat([t.head(10), t.tail(10)]))
 
 
# %% [4a] 年齡層
print("Edad 原始格式範例（請確認數字是「歲」）：")
print(df['Edad'].astype(str).sample(10, random_state=1).tolist())
 
df['Edad_num'] = pd.to_numeric(df['Edad'].astype(str).str.extract(r'(\d+)')[0], errors='coerce')
print(f"Edad 無法轉換：{df['Edad_num'].isna().sum()} 筆")
 
df['年齡層'] = pd.cut(df['Edad_num'], bins=[-1, 4, 14, 24, 44, 64, 200],
                   labels=['0–4', '5–14', '15–24', '25–44', '45–64', '65+'])
t = tasa(df, '年齡層', min_n=0, ordenar=False)
resultados['4_年齡層'] = t
display(t)
grafico_barras(t, '依年齡層的缺席率')
 
 
# %% [4b] 證件類型（外籍病患的替代指標）
print(df['Tipo Doc.'].value_counts(dropna=False))
t = tasa(df, 'Tipo Doc.', min_n=30)
resultados['4_證件類型'] = t
display(t)
 
 
# %% [5a] 缺席集中度（病患層級）
pac = df.groupby('Documento')['缺席'].agg(預約數='size', 缺席數='sum')
n_pac = len(pac)
total_aus = pac['缺席數'].sum()
 
print(f"病患人數：{n_pac:,}")
print(f"至少缺席一次的病患：{(pac['缺席數'] > 0).sum():,}（{(pac['缺席數'] > 0).mean():.1%}）")
 
orden = pac['缺席數'].sort_values(ascending=False).values
acum = np.cumsum(orden) / total_aus
top10 = acum[int(n_pac * 0.10) - 1]
n_mitad = np.searchsorted(acum, 0.5) + 1
print(f"缺席最多的 10% 病患，貢獻了 {top10:.1%} 的缺席")
print(f"一半的缺席來自 {n_mitad:,} 位病患（佔全部病患 {n_mitad / n_pac:.1%}）")
 
dist = pac['缺席數'].clip(upper=5).value_counts().sort_index().rename(index={5: '5+'})
resultados['5_每人缺席次數分布'] = dist.to_frame('病患數')
display(resultados['5_每人缺席次數分布'])
 
# 集中度曲線
x = np.arange(1, n_pac + 1) / n_pac * 100
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(x, acum * 100)
ax.axvline(10, color='gray', ls='--', lw=0.8)
ax.set_xlabel('病患累積比例（%，依缺席次數由多到少）')
ax.set_ylabel('缺席累積比例（%）')
ax.set_title('缺席集中度')
plt.tight_layout()
plt.show()
 
 
# %% [5b] 過去缺席是否預測下次缺席
# 以「病患 + 日期」為一次就診：當天所有預約都未到診才算缺席
visitas = (df.groupby(['Documento', df['Fecha'].dt.normalize()])['缺席']
             .min().reset_index().sort_values(['Documento', 'Fecha']))
 
visitas['上次結果'] = (visitas.groupby('Documento')['缺席'].shift()
                        .map({0: '上次出席', 1: '上次缺席'}).fillna('期間內第一次'))
previas = visitas.groupby('Documento')['缺席'].cumsum() - visitas['缺席']
visitas['之前缺席次數'] = previas.clip(upper=3).map({0: '0 次', 1: '1 次', 2: '2 次', 3: '3 次以上'})
 
print(f"就診次數（病患 + 日期）：{len(visitas):,}")
resultados['5_上次結果'] = tasa(visitas, '上次結果', min_n=0, ordenar=False)
resultados['5_之前缺席次數'] = tasa(visitas, '之前缺席次數', min_n=0, ordenar=False)
display(resultados['5_上次結果'], resultados['5_之前缺席次數'])

# %% [7a] 以病人為單位：各科室病人的缺席情形
per = (df.groupby(['Categoría', 'Documento'])['缺席']
         .agg(預約數='size', 缺席數='sum')
         .reset_index())
per['個人缺席率'] = per['缺席數'] / per['預約數']
per['曾缺席'] = (per['缺席數'] > 0).astype(int)

pac = (per.groupby('Categoría')
          .agg(病人數=('Documento', 'size'),
               平均每人預約數=('預約數', 'mean'),
               曾缺席至少一次比例=('曾缺席', 'mean'),
               平均個人缺席率=('個人缺席率', 'mean'))
          .query('病人數 >= 30')
          .sort_values('平均個人缺席率', ascending=False)
          .round(3))

resultados['7_科室病人'] = pac
display(pac)

# %% [7b] 是病人本身容易缺席，還是這個科室容易被缺席？
rows = []
for cat in per['Categoría'].unique():
    pts = per.loc[per['Categoría'] == cat, 'Documento']
    sub = df[df['Documento'].isin(pts)]
    en_este = sub[sub['Categoría'] == cat]['缺席']
    en_otros = sub[sub['Categoría'] != cat]['缺席']
    rows.append({'科室': cat,
                 '病人數': len(pts),
                 '在本科室缺席率': en_este.mean(),
                 '同批病人在其他科室缺席率': en_otros.mean(),
                 '其他科室預約數': len(en_otros)})

cmp_ = (pd.DataFrame(rows)
          .query('病人數 >= 30 and 其他科室預約數 >= 30')
          .sort_values('在本科室缺席率', ascending=False)
          .round(3))

resultados['7_科室vs病人'] = cmp_
display(cmp_)
 
# %% [完成] 查看已產生的結果表
print("已產生的結果：")
for k, v in resultados.items():
    print(f"  {k}：{len(v)} 列")
# %%
out = r"D:\智利實習\缺席分析結果.xlsx"
with pd.ExcelWriter(out) as writer:
    for k, v in resultados.items():
        v.to_excel(writer, sheet_name=str(k)[:31])   # 工作表名稱最多 31 字
print("已存成：", out)
# %%
