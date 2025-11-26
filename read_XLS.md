1. **planSettings** sayfasında ön taşıyıcı sistem planı ile ilgili ayarlar vardır.
    - `force symmetry` : Eğer simetri eksenleri varsa elemanları simetrik olmaya zorla
    - `force beams full` : *Tam* duvarlar altında kiriş bulunması durumunu zorla
    - `force beams half` : *Yarım* duvarlar altında kiriş bulunması durumunu zorla
    - `contBeam mode` : Bu ayar yukarıda *force...* ile başlayan üç ayarı da baskılar. 0 ise tasarım vektöründeki *contBeamTopo* kısmının bir önemi yoktur. 1 ise *contBeamTopo* kısmındaki -1 değerlerine denk gelen sürekli kiriş elemanları için bir işlem yapılmaz. 2 ise *contBeamTopo* kısmında -1 değerine izin verilmez.
    - `max dRG` : Kütle merkezi ile rijitlik merkezi arasındaki (hem x hem de y yönündeki) mesafelerin ilgili yöndeki plan boyutuna oranı için izin verilen en büyük değer
    - `min A` : Sistemdeki toplam kolon / perde alanının izin verilen en *küçük* değeri (dm2)
    - `max A` : Sistemdeki toplam kolon / perde alanının izin verilen en *büyük* değeri (dm2)
    - `min I` : Her iki yöndeki toplam kolon / perde atalet momentlerinin izin verilen en *küçük* değeri (dm4)
    - `max I` : Her iki yöndeki toplam kolon / perde atalet momentlerinin izin verilen en *büyük* değeri (dm4)
    - `max rI` : Kuvvetli yöndeki toplam atalet momenti / zayıf yöndeki toplam atalet momenti oranının izin verilen en büyük değeri
    - `min It` : Sistemdeki bileşke burulma atalet momentinin izin verilen en *küçük* değeri (dm4)
    - `max It` : Sistemdeki bileşke burulma atalet momentinin izin verilen en *büyük* değeri (dm4)

2. **floorHeight** sayfasında kat yükseklikleri vardır.
    - `floor` : kat ismi
    - `height` : kat yüksekliği (cm)

3. **areaProp** sayfasında, hangi sınıftaki alanlar içinde hangi elemanların bulunmasına izin verildiği ve hangi sınıftaki alanların önem faktörünün ne olduğu vardır.
    - `class` : Alan sınıfı
    - `no columns` (0 veya 1): İlgili alan sınıfında olan alanların içinde *kolon* olabilir (0) veya olamaz (1)
    - `no beams` (0 veya 1): İlgili alan sınıfında olan alanların içinde *kiriş* olabilir (0) veya olamaz (1)
    - `no slab` (0 veya 1): İlgili alan sınıfında olan alanlarda *döşeme* olabilir (0) veya olamaz (1)
    - `importance` (0 veya daha büyük): İlgili alan sınıfında olan alanların önem faktörü

4. **colSec** sayfasında *noktasal* kolon kesitlerinin uzun (`dL`) ve kısa (`dS`) kenar bilgisi cm cinsinden verilmiştir. Eğer sadece `dL` bilgisi varsa kolon dairesel kolondur.

5. **colSpanLenLim** sayfasında *çizgisel* kolonların uzunluklarının (cm) izin verilen en az (`min`) ve en çok (`max`) değerleri vardır.

6. **colSpanSec** sayfasında *çizgisel* kolonların izin verilen cm cinsinden genişlik (`width`) değerleri vardır.

7. **colDist** sayfasında kolonlar arasında izin verilen en küçük (`min`) ve en büyük (`max`) mesafe değerleri (cm) vardır.

8. **RCWsettings** sayfasında perdeler ile ilgili ayarlar vardır.
    - `min` : en az betonarme perde sayısı
    - `max` : en fazla betonarme perde sayısı
    - `min R` : betonarme perdeler için en küçük kesit uzunluğu / genişliği oranı

9. **beamLenLim** sayfasında kirişlerin izin verilen en az (`min`) ve en çok (`max`) uzunluk değerleri (cm) vardır.

10. **beamSec** sayfasında izin verilen kiriş kesitlerinin genişlik (`b`) ve derinlik (`h`) değerleri cm cinsinden verilmiştir.

11. **beamDist** sayfasında kirişler arasında izin verilen en küçük (`min`) ve en büyük (`max`) mesafe değerleri (cm) vardır.

12. **slabSec** sayfasında döşemeler için izin verilen plak yükseklikleri (`h`) cm cinsinden bulunmaktadır.

13. **eccIntervals** sayfasında noktasal kolonların (`col`), çizgisel kolonların (`colSpan`) ve kirişlerin (`beam`) kaçıklıklarını hesaplarken kaç aralık kullanılacağının bilgisi bulunmaktadır.
    - 0 : aralık yoktur; kaçıklıklar sadece 0 değerini alabilir.
    - 1 : kaçıklıklar -0.5, 0, 0.5 değerlerini alabilir.
    - 2 : kaçıklıklar -0.5, -0.25, 0, 0.25, 0.5 değerlerini alabilir.
    - 3 : ...