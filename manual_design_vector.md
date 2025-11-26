### Noktasal Kolon (Node Column)


```
İlgili düğümde noktasal kolon varlığı
colTopo = [0 , 1 , 0 , ...]

Değer Aralığı : 0 veya 1
Eleman Sayısı : len(nodes)
```


```
İlgili düğümdeki noktasal kolon kesiti
colSize = [6 , 1 , 4 , ...]

Değer Aralığı : 0 ile len(colSec)-1 arasındaki tam sayılar
Eleman Sayısı : len(nodes)
```


```
Noktasal kolonun uzun kenarının hangi aks yönünde olduğu bilgisi
Elbette dairesel kolon kesiti seçilmesi durumunda bir anlama gelmiyor.
colDirec = [3 , 1 , 0 , ...]

Değer Aralığı : 0 ile max(len(nodAx[i])) arasındaki tam sayılar
Eleman Sayısı : len(nodes)

Yorumlanırken mod(len(nodAx[i])) alınacaktır; her düğümden farklı sayıda aks geçebilir.
```


```
Noktasal kolonun uzun kenarı doğrultusunda (L yönü) kaçıklık oranı
colEccL = [0 , -0.25 , ...]

Değer Aralığı : -0.5 ve 0.5 arasında 2*intCol aralığı ile oluşturulmuş sayılar.
                intCol = 0 ise, 0
                intCol = 1 ise, -0.5, 0, 0.5
                intCol = 2 ise, -0.5, -0.25, 0, 0.25, 0.5
Eleman Sayısı : len(nodes)
```


```
Noktasal kolonun uzun kenarına dik yönde (L yönüne dik) kaçıklık oranı
colEccS = [0.5 , 0.25 , ...]

Değer Aralığı : -0.5 ve 0.5 arasında 2*intCol aralığı ile oluşturulmuş sayılar.
                intCol = 0 ise, 0
                intCol = 1 ise, -0.5, 0, 0.5
                intCol = 2 ise, -0.5, -0.25, 0, 0.25, 0.5
Eleman Sayısı : len(nodes)
```


### Çizgisel Kolon (Span Column)


```
İlgili açıklıkta çizgisel kolon varlığı
colSpanTopo = [0 , 1 , 0 , ...]

Değer Aralığı : 0 veya 1
Eleman Sayısı : len(spans)
```


```
İlgili açıklıktaki çizgisel kolon kesiti (genişliği)
colSpanSize = [3 , 7 , 2 , ...]

Değer Aralığı : 0 ile len(colSpanSec)-1 arasındaki tam sayılar
Eleman Sayısı : len(spans)
```


```
Çizgisel kolonun eksenden kaçıklığı (genişlik doğrultusunda)
colSpanEcc = [0.25 , -0.5 , 0 , ...]

Değer Aralığı : -0.5 ve 0.5 arasında 2*intColSpan aralığı ile oluşturulmuş sayılar.
                intColSpan = 0 ise, 0
                intColSpan = 1 ise, -0.5, 0, 0.5
                intColSpan = 2 ise, -0.5, -0.25, 0, 0.25, 0.5
Eleman Sayısı : len(spans)
```


### Kiriş (Beam)


```
İlgili açıklıkta kiriş varlığı
beamTopo = [0 , 0 , 1 , ...]

Değer Aralığı : 0 veya 1
Eleman Sayısı : len(spans)
```


```
İlgili açıklıktaki kiriş kesiti
beamSize = [2 , 5 , 0 , ...]

Değer Aralığı : 0 ile len(beamSec)-1 arasındaki tam sayılar
Eleman Sayısı : len(spans)
```


```
Kirişin eksenden kaçıklığı (genişlik doğrultusunda)
beamEcc = [0.5 , -0.5 , 0 , ...]

Değer Aralığı : -0.5 ve 0.5 arasında 2*intBeam aralığı ile oluşturulmuş sayılar.
                intBeam = 0 ise, 0
                intBeam = 1 ise, -0.5, 0, 0.5
                intBeam = 2 ise, -0.5, -0.25, 0, 0.25, 0.5
Eleman Sayısı : len(spans)
```


### Sürekli Kiriş (Continuous Beam)


```
İlgili sürekli kirişin varlığı
contBeamTopo = [0 , 1 , 0 , ...]

Değer Aralığı : -1, 0 veya 1
    -1 : ilgili sürekli kiriş hattı üzerinde bulunan elemanlar ile ilgili bir tercih yoktur.
    0  : ilgili sürekli kiriş hattındaki kirişler ve çizgisel kolonlar yoktur.
    1  : ilgili sürekli kiriş hattındaki kirişler ve çizgisel kolonlar vardır.
Eleman Sayısı : len(contBeams)
                Bu sayı len(axNod) + len(all_path_details) olarak düşünülmelidir.

Optimizasyon sürecinin temelini bu vektör ile yürütmeyi planlıyorum.
```


### Döşeme (Slab)


```
Hangi alan sınıfına sahip alanlarda döşeme olduğu zaten XLS dosyasında verilir.
Bu sebeple döşemeler için topoloji vektörü bulunmamaktadır.
```


```
Döşemenin kesiti (derinliği)
Döşemeler için kesit belirleme işlemi çoğunlukla iteratif değildir.
Yine de döşeme kesitleri için de bir vektör belirlenmiştir.
`slabSize = [1 , 1 , ...]`

Değer Aralığı : 0 ile len(slabSec)-1 arasındaki tam sayılar
Eleman Sayısı : len(areas)
```


***


### Tasarım Vektörü (Design Vector)


```
Tasarım vektörü aşağıdaki gibi bir numpy dizileri listesidir.
Vektör Uzunluğu = 5*len(nodes) + 6*len(spans) + len(contBeams) + len(areas)

designVec = [
    colTopo,
    colSize,
    colDirec,
    colEccL,
    colEccS,
    
    colSpanTopo,
    colSpanSize,
    colSpanEcc,
    
    beamTopo,
    beamSize,
    beamEcc,
    
    contBeamTopo,
    
    slabSize
]
```