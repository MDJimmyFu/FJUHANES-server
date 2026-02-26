# **病歷號檢核碼編碼規則 (MRN Check Digit Algorithm)**

## **1\. 目的 (Objective)**

將 9 碼數字的病歷號，透過加權模數演算法 (Weighted Modulo 10)，計算出第 10 碼的英文字母檢核碼。

## **2\. 輸入與輸出 (Input & Output)**

* 輸入 (Input): 9 位數字字串 (例如：003235483)  
* 輸出 (Output): 1 位大寫英文字母 (A \~ J)

## **3\. 演算法步驟 (Algorithm Steps)**

### **Step 1: 加權總和 (Weighted Sum)**

將 9 位數字由左至右，分別對應遞減的權重 \[9, 8, 7, 6, 5, 4, 3, 2, 1\]，對位相乘後加總。

* 定義: 設輸入數字為 D1, D2, D3, D4, D5, D6, D7, D8, D9  
* 公式: Sum \= (D1 \* 9\) \+ (D2 \* 8\) \+ (D3 \* 7\) \+ (D4 \* 6\) \+ (D5 \* 5\) \+ (D6 \* 4\) \+ (D7 \* 3\) \+ (D8 \* 2\) \+ (D9 \* 1\)

### **Step 2: 模數運算 (Modulo Operation)**

將加權總和 (Sum) 除以 10，取得餘數 (Remainder)。

* 公式: Remainder \= Sum % 10

### **Step 3: 字母轉換 (Character Mapping)**

將取得的餘數 (0-9) 直接對應到大寫英文字母 (A-J)。在 ASCII 編碼中，即為餘數加上 65。

* 公式: CheckDigit \= chr(Remainder \+ 65\)

文字對應規則如下：

* 餘數 0 對應 A  
* 餘數 1 對應 B  
* 餘數 2 對應 C  
* 餘數 3 對應 D  
* 餘數 4 對應 E  
* 餘數 5 對應 F  
* 餘數 6 對應 G  
* 餘數 7 對應 H  
* 餘數 8 對應 I  
* 餘數 9 對應 J