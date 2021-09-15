import datetime as dt
import pandas as pd
import seaborn as sns
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df_ = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()
df.head()


#Verinin betimsel istatistikleri

df.describe().T

#Veri setinde eksik gözlem var mı? Varsa hangi değişkende kaç tane eksik gözlem vardır?

df.isnull().sum()

#Eksik gözlemleri veri setinden çıkartma

df.dropna(inplace=True)

#Eşsiz ürün sayısı kaçtır?

df["Description"].nunique()

#Hangi üründen kaçar tane vardır?

df["Description"].value_counts().head()

#En çok sipariş edilen 5 ürün

df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()

#Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir. İptal edilen işlemleri veri setinden çıkartma

df = df[~df["Invoice"].str.contains("C", na=False)]

#Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturma

df["TotalPrice"] = df["Quantity"] * df["Price"]
df.head()

#RFM Metriklerinin Hazırlanması

df["InvoiceDate"].max()
today_date = dt.datetime(2011, 12, 11)

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
rfm.head()
rfm.columns = ['recency', 'frequency', 'monetary']
rfm = rfm[(rfm['monetary'] > 0)]

rfm.head()

#RFM Skorlarının Oluşturulması ve Tek Bir Değişkene Çevrilmesi

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

rfm.head()

#RFM Skorlarının Segment Olarak Tanımlanması

seg_map = {
    r'[1-2][1-2]': 'Hibernating',
    r'[1-2][3-4]': 'At_Risk',
    r'[1-2]5': 'Cant_Loose',
    r'3[1-2]': 'About_to_Sleep',
    r'33': 'Need_Attention',
    r'[3-4][4-5]': 'Loyal_Customers',
    r'41': 'Promising',
    r'51': 'New_Customers',
    r'[4-5][2-3]': 'Potential_Loyalists',
    r'5[4-5]': 'Champions'
}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

rfm.head()

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

t = rfm["segment"].value_counts()
t = [i/t.sum()*100 for i in t]
t

z = rfm["segment"].value_counts()
z

"""İlgili veri setiyle alakalı segmentasyon yapıldığında sayıca en fazla olan segmentin
Hibernating" olduğu gözlemlenmiştir. Recency ve Frequency skorlarında en düşük skora sahip bu 
grup için öncelikli aksiyon alınması düşünülse de uzun vadede daha fazla verim alınabilecek segmentler göze çarpmaktadır.
Total kümenin %24.7'lik bir kısmını oluşturan "At Risk" ve "Potential Loyalist" segmentleri bu konuda ilk etapta aksiyon alınması gereken segmentler olabilir. 
Potential Loyalist segmentinin sık sık alışveriş yaptığı ancak bu alışveriş frekanslarının görece yüksek olmadığını görüyoruz. 
Bu kategoride müşteri için alınacak ilk aksiyon "Cross-sell" ya da "Upper-sell" methodları olacaktır. 
Müşteriye hitap eden ürünle beraber tamamlayıcı bir ürün ya da daha fazla verim alacağı bir üst ürün satışı gerçekleştirmek için pazarlama çalışmaları yapılmalıdır.
Bu çalışmalar için ise ilgili ürün satışından sonra e-mail, sms ya da bildirim yoluyla cross/upper sell kategorisinde yer alan ürünler göz önünde tutulmalıdır.
Bu %24.7'lik dilimin içerisinde yer alan bir diğer segment "At_Risk" segmentine bakıldığında 
hem sık sık alışveriş yapmadığı ancak yapılan alışverin yüksek frekanslı olduğunu gözlemliyoruz. Bu tarz bir segment için öncelikli olarak müşteriyi 
daha kısa periyotlarla alışverişe teşvik edebilecek aksiyonlar alınması önerilebilir.
Bu aksiyonlara Potential Loyalist'lere uygulanan cross/upper sell methotları dahil olabileceği gibi, müşteriyle birebir iletişim ve indirim gibi 
daha çekici pazarlama teknikleri düşünülebilir.
At Risk grubunun tabiri caizse bir üst modeli olan Cant Loose grubunun da getiri bakımından sıralamada 3.sırada yer aldığını gözlemliyoruz. 
Uzun aralıklarla ancak frekansı yüksek ve getirisi fazla alışverişleriyle dikkat çeken bu grup için de alışveriş aralıklarını kısaltacak aksiyonlar devreye sokulmalıdır. 
Birebir iletişim yoluyla, ya da pazarlama yapısı uygunsa üyelik avantajlarıyla bu müşteri tipinin dikkati bir şekilde alışveriş kanallarına çekilmelidir.
"""

