# %%
import os
from io import StringIO
import pandas as pd

# %%
# 改路徑
folder = r"D:\智利實習\reporte_cupos_agenda\reporte_cupos_agenda(1)"

# 找出資料夾（含子資料夾）裡所有 reporte_cupos_agenda01~08.xls
files = sorted(glob.glob(os.path.join(folder, "**", "reporte_cupos_agenda0*.xls"), recursive=True))

# 同名檔案只保留一個，避免重複下載的檔案被算兩次
seen = {}
for f in files:
    name = os.path.basename(f)
    if name in seen:
        print("⚠ 重複檔名，略過：", f)
    else:
        seen[name] = f
files = list(seen.values())

print("找到", len(files), "個檔案：")
for f in files:
    print("  ", f)

# %%
def read_report(path):
    # 讀取 HTML 文字
    html = None
    for enc in ["utf-8", "cp1252", "latin-1"]:
        try:
            with open(path, encoding=enc) as f:
                html = f.read()
            break
        except UnicodeDecodeError:
            continue

    tables = pd.read_html(StringIO(html))

    # 取列數最多的表格（預約明細）
    df = max(tables, key=len)

    # 如果標題沒被認出來，找含有 "Número" 的那一列當標題
    if "Número" not in df.columns:
        header_row = df.index[df.astype(str).eq("Número").any(axis=1)][0]
        df.columns = df.loc[header_row].astype(str).str.strip()
        df = df.loc[header_row + 1:].reset_index(drop=True)

    # 刪掉合計列與全空白列
    df = df[~df.astype(str).apply(lambda r: r.str.startswith("Total Registros").any(), axis=1)]
    df = df.dropna(how="all")

    # 記錄資料來自哪個檔案
    df["archivo"] = os.path.basename(path)

    # 另外存一份單檔 .xlsx
    df.to_excel(os.path.splitext(path)[0] + ".xlsx", index=False)
    return df

# %%
all_dfs = []
for f in files:
    df = read_report(f)
    print(f"{os.path.basename(f)}：{len(df)} 筆")
    all_dfs.append(df)

merged = pd.concat(all_dfs, ignore_index=True)
print("合併後共", len(merged), "筆，", merged.shape[1], "欄")

# %%
out = os.path.join(folder, "reporte_cupos_agenda_合併.xlsx")
merged.to_excel(out, index=False)
print("已存成：", out)


# %%
# 直接指定檔案
path = r"D:\智利實習\reporte_cupos_agenda\reporte_cupos_agenda.xls"

# %%
def read_report(path):
    # 讀取 HTML 文字
    html = None
    for enc in ["utf-8", "cp1252", "latin-1"]:
        try:
            with open(path, encoding=enc) as f:
                html = f.read()
            break
        except UnicodeDecodeError:
            continue

    tables = pd.read_html(StringIO(html))

    # 取列數最多的表格（預約明細）
    df = max(tables, key=len)

    # 如果標題沒被認出來，找含有 "Número" 的那一列當標題
    if "Número" not in df.columns:
        header_row = df.index[df.astype(str).eq("Número").any(axis=1)][0]
        df.columns = df.loc[header_row].astype(str).str.strip()
        df = df.loc[header_row + 1:].reset_index(drop=True)

    # 刪掉合計列與全空白列
    df = df[~df.astype(str).apply(lambda r: r.str.startswith("Total Registros").any(), axis=1)]
    df = df.dropna(how="all")

    # 記錄資料來自哪個檔案
    df["archivo"] = os.path.basename(path)

    # 另外存一份單檔 .xlsx
    df.to_excel(os.path.splitext(path)[0] + ".xlsx", index=False)
    return df

# %%
df = read_report(path)
print(f"{os.path.basename(path)}：{len(df)} 筆，{df.shape[1]} 欄")

# %%
import glob

# %%
# 資料夾路徑（依你實際位置修改）
folder = r"D:\智利實習\reporte_pacientes_inasistentes_centro"

# 抓出所有 reporte_pacientes_inasistentes_centro 開頭的 .xls
files = sorted(glob.glob(os.path.join(folder, "reporte_pacientes_inasistentes_centro*.xls")))
print("共找到", len(files), "個檔案")

# %%
for src in files:
    print("\n處理：", os.path.basename(src))

    # 讀取 HTML 文字（先試 UTF-8，不行再用 cp1252 / latin-1）
    html = None
    for enc in ["utf-8", "cp1252", "latin-1"]:
        try:
            with open(src, encoding=enc) as f:
                html = f.read()
            print("  使用編碼：", enc)
            break
        except UnicodeDecodeError:
            continue

    # 讀出所有表格，失敗就跳過這個檔案繼續下一個
    try:
        tables = pd.read_html(StringIO(html))
    except ValueError as e:
        print("  讀不到表格，跳過：", e)
        continue
    print("  共找到", len(tables), "個表格")

    # 輸出成同名 .xlsx
    out = os.path.splitext(src)[0] + ".xlsx"
    with pd.ExcelWriter(out) as writer:
        for i, df in enumerate(tables):
            df.to_excel(writer, sheet_name=f"表格_{i}", index=False)
            print(f"  表格 {i} 形狀為 {df.shape}")

    print("  已存成：", os.path.basename(out))

print("\n全部完成！")

# %%
