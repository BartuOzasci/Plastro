### Uyarı


- Eğer sistemde *izin verilen en büyük kiriş uzunluğu* veya *iki kolon arası izin verilen en büyük mesafe* değerlerinden daha uzun aks parçası varsa kullanıcı uyarılarak bu aks parçasını bölmesi istenir (**1, 13**).


***


### Onarım


- Sürekli Kiriş Hatları (Önce bir madde tüm sürekli kiriş hatları için kontrol edilir; daha sonra diğer maddeye geçilir).
    
    1. ***MASK*** ✅ : Sürekli kiriş hattı izin verilmeyen alanın içinde kiriş bulunmasını gerektiriyorsa sistemden çıkarılır (**3, 33**).
    2. ***MASK*** ✅ :Sürekli kiriş hattının alternatif(ler)i, yani aynı aks(lar) üzerindeki başka hat(lar), sistemde bulunuyorsa alternatif(ler) sistemden çıkarılır (**34**).
    3. ***MASK*** ✅ :Sürekli kiriş hattı yapının oturma alanını çevreleyen hatlardan biriyse ve alternatifi sistemde bulunmuyorsa, ilgili sürekli kiriş sisteme eklenir (**35**).
    4. ***MASK*** ✅ :Sürekli kiriş hattı sistemdeki başka sürekli kiriş hatlarına izin verilenden fazla yakınsa söz edilen yakın hatlar sistemden çıkarılır. Ancak, eğer yakın hatlardan biri oturma alanını çevreliyorsa yakın hat sistemde kalır; geri kalan diğer hatlar (göz önünde bulundurulan sürekli hat dahil) sistemden çıkarılır (**2**).
    5. ***MASK*** ✅ : Sürekli kiriş hattının (izin verilen alan içinde kalan) uç düğümlerinde noktasal kolon yoksa ilgili noktasal kolonlar sisteme eklenir (**30**).
    6. ❌ Sürekli kiriş hattında başlangıç düğümünden başlanarak i. ve i+1. kolonlar incelenir. Bu kolonların her ikisinin de varlığı *izin verilen en kısa kiriş boyu* veya *iki kolon arası izin verilen en küçük mesafe* kısıtlarından birinin ihlaline sebep oluyorsa, i+1. kolon kaldırılır; inceleme i. kolondan tekrar başlar. Ancak i. veya i+1. kolonlardan biri uç kolon ise uç kolon korunur; diğer kolon kaldırılır (**1, 13**).
    7. ❌ Sürekli kiriş hattında farklı kiriş kesitleri var ise, tüm kiriş kesitleri ilk kirişin kesiti olarak belirlenir (**32**).
    8. ❌ Sürekli kiriş hattında, ilk açıklıktan başlanarak, aralarında kolon bulunmayan komşu açıklıkların kaçıklıkları, bir önceki açıklık referans alınarak eşitlenir (**31**).


- Kirişler (Eğer `contBeam mode = 0 veya 1` ile kiriş varlığına, bir sürekli hattın parçası olmaksızın, izin veriliyorsa)

    9. ***MASK*** ✅ : İzin verilmeyen alanların içindeki tüm kirişler kaldırılır (**3**).
    10. ***MASK*** ✅ : Kullanıcı seçimine göre tüm tam duvarlar altına kiriş konur (**10**).
    11. ***MASK*** ✅ : Kullanıcı seçimine göre tüm yarım duvarlar altına kiriş konur (**11**).
    12. ***ONDEMAND*** ✅ : İki ucu da serbest olan kirişler kaldırılır (**9**).
    13. ❌ Aralarında kolon bulunmayan komşu açıklıkların *kesitleri*, bir önceki açıklık referans alınarak eşitlenir (**32**).
    14. ❌ Aralarında kolon bulunmayan komşu açıklıkların *kaçıklıkları*, bir önceki açıklık referans alınarak eşitlenir (**31**).


- Çizgisel Kolonlar

    15. ***MASK*** ✅ : Oturma alanının dışına yerleştirilen çizgisel kolonlar kaldırılır (**14**).
    16. ***MASK*** ✅ : İzin verilmeyen alanların içindeki çizgisel kolonlar kaldırılr (**14**).
    17. ***MASK*** ✅ : İzin verilmeyen açıklığa yerleştirilen çizgisel kolonlar kaldırılır (**23**).
    18. ***MASK*** ✅ : İzin verilen uzunluktan küçük veya büyük açıklıklara yerleştirilmiş çizgisel kolonlar sistemden kaldırılır (**22**).
    19. ❌ Serbest ucu bulunan çizgisel kolonlar, noktasal kolonlara çevrilir (**24**).
    20. ***ONDEMAND*** ✅ : Bir açıklıkta hem çizgisel kolon hem de kiriş varsa ilgili kiriş kaldırılır (**25**).


- Noktasal Kolonlar

    21. ***MASK*** ✅ : Oturma alanının dışına yerleştirilen noktasal kolonlar kaldırılır (**14**).
    22. ***MASK*** ✅ : İzin verilmeyen alanların içindeki kolonlar kaldırılır (**14**).
    23. ***MASK*** ✅ : İzin verilmeyen düğümlere yerleştirilen noktasal kolonlar kaldırılır (**14**).
    24. ***ONDEMAND*** ✅ : Hiç kiriş bağlı olmayan kolonlar kaldırılır (**19**).
    25. ***ONDEMAND*** ✅ : Noktasal kolon bulunan bir düğüm, bir çizgisel kolonun da uç düğümü ise noktasal kolon sistemden kaldırılır (**18**).
    26. ***MASK*** ✅ : Oturma alanının köşelerine denk gelen kolonlar sisteme eklenir (**20**).
    27. ❌ Üzerinde duvar bulunmayan açıklıklar doğrultusunda olan kolonların yönü, üzerinde duvar bulunan yönlerden biri seçilerek düzeltilir (**21**).


***


### Ceza


- Kirişler

    1. ***ONDEMAND*** ✅ : Kiriş uzunluğu izin verilen aralığın dışındadır. `L < L_min` veya `L > L_max`
    2. ***ONDEMAND*** ✅ : Kirişler arasındaki mesafe izin verilen aralığın dışındadır. `d < d_min` veya `d > d_max`
    8. ❌ Başka bir kirişe saplanan kirişe de bir kiriş saplanmıştır (Saplamanın saplaması var).
    9. ***ONDEMAND*** ✅ : Kirişin serbest ucu var.


- Noktasal ve Çizgisel Kolonlar

    13. ***ONDEMAND*** ✅ : Kolonlar arasındaki mesafe izin verilen aralığın dışındadır. `d < d_min` veya `d > d_max`


- Taşıyıcı Sistem Planı

    36. Planın kütle merkezi ile rijitlik merkezi arasındaki mesafe büyüktür (`dRG > max dRG`).
    37. Yapıdaki kolonların toplam alanı belirtilen sınırlar arasında değildir (`A < A_min` veya `A > A_max`).
    39. Yapının kuvvetli ve zayıf yönlerindeki atalet momentleri farkı büyüktür (`I_strong / I_weak > rI_max`).


***


### Amaç


- Kirişler

    5. ***PRECALC*** ✅ : Kiriş belirli bir kıymet derecesi olan alanın içindedir.
    7. ***ONDEMAND*** ✅ : Kiriş başka bir kirişe saplanmıştır.
    41. ***ONDEMAND*** ✅ : Kiriş sistemde bulunan bir sürekli kiriş hattının parçası değildir.


- Noktasal ve Çizgisel Kolonlar

    16. ***PRECALC*** ✅ : Kolon belirli bir kıymet derecesi olan alanın içindedir.