import pandas as pd

#讀取檔案
df = pd.read_csv('問卷.csv', encoding='utf-8-sig')

def swap():
    global df
    #欄位互換 
    key1 = '分配%'
    key2 = 'CD分配'
    df[[key1, key2]] = df[[key2, key1]] 
    df = df.rename(columns={key1: key2, key2: key1}) 
    
    key1 = 'AB考量'
    key2 = 'CD分配'
    df[[key1, key2]] = df[[key2, key1]] 
    df = df.rename(columns={key1: key2, key2: key1}) 

#名字
def change_name():
    global df
    clean_list = []
    for i, e in df.iterrows():
        e_text = str(e['班級座號姓名']).replace(" ", "")
        
        #我們檢查長度大於5，且前5個字元都是數字
        if len(e_text) >= 5 and e_text[:5].isdigit():
            #前5碼 + "-" + 第5碼之後的所有字
            new_value = f"{e_text[:5]}-{e_text[5:]}"
        else:
            new_value = e_text # 如果不符合格式，就不動它
            
        clean_list.append(new_value)
    df['班級座號姓名'] = clean_list

#AB CD
def clean_money_text(text):
    text = str(text).strip()
    
    #「都」或「平分」
    if '都' in text or '平分' in text: 
        return "25000:25000"
        
    #「全部」
    if '全部' in text:
        if '對方' in text or 'B' in text.upper() or 'D' in text.upper(): 
            return "0:50000"
        else: 
            return "50000:0"

    text = text.replace('/', ':').replace('-', ':').replace('比', ':').replace('：', ':').replace(',', ':').replace('，', ':')

    # 中英文全丟
    clean_str = ""
    for char in text:
        if char.isdigit() or char == ':':
            clean_str += char
            
    if clean_str.isdigit():  #純數字
        x = int(clean_str)
        if x == 25000: return "25000:25000"
        elif x > 25000: return f"{x}:{50000-x}"
        else: return f"{50000-x}:{x}"

    elif ':' in clean_str: # 如果裡面有冒號
        parts = clean_str.split(':') 
        
        #抓數字
        nums = []
        for p in parts:
            if p.isdigit():
                nums.append(int(p))
                
        #兩個數字
        if len(nums) >= 2:
            val1 = nums[0]
            val2 = nums[1]
            
            #3:2
            if val1 < 10 and val2 < 10:
                val1 *= 10000
                val2 *= 10000
                
            return f"{val1}:{val2}"

    return "錯誤"

#AB分配
def AB():
    global df
    final_results = []
    for i, e in df.iterrows():
        result = clean_money_text(e['AB分配'])
        final_results.append(result)
    df['AB分配'] = final_results

#CD分配
def CD():
    global df
    final_results = []
    for i, e in df.iterrows():
        result = clean_money_text(e['CD分配'])
        final_results.append(result)
    df['CD分配'] = final_results

#算出獲勝者
def winner():
    global df
    winner_dict = {104: [], 105: [], 106: [], 107: []}
    current_class = 106
    
    for i, e in df.iterrows():
        class_str = e['班級座號姓名'][0:3]
        if class_str.isdigit():
            current_class = int(class_str)
            
        a = 0
        b = 0
        if '錯誤' not in e['AB分配']:
            a = int(e['AB分配'].split(':')[0])
        if '錯誤' not in e['CD分配']:
            b = int(e['CD分配'].split(':')[0])
        
        if a < 49999:
            money = a + b
            if current_class in winner_dict:
                winner_dict[current_class].append((money, e['班級座號姓名']))
            
    # 輸出檔案
    with open('每班得獎者.txt', 'w', encoding='utf-8') as f:
        for key, winners in winner_dict.items():
            # 依照分數從大到小排序
            winners.sort(reverse=True)
            f.write(f"\n班級:{key}的前五名是:\n")
            
            # 取前5名
            top5 = winners[:5]
            for e in top5:
                f.write(f"分數:{e[0]}，{e[1]}\n")

# 執行所有步驟
swap()
change_name()
AB()
CD()
winner()

df.to_csv('問卷處理結果.csv', index=False, encoding='utf-8-sig')
print("均完成")