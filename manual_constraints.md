### Kiriş

1. Kiriş uzunluğu izin verilen aralığın dışındadır. `L < L_min` veya `L > L_max`
2. Kirişler arasındaki mesafe izin verilen aralığın dışındadır. `d < d_min` veya `d > d_max`
3. Kiriş izin verilmeyen alanın içindedir.
4. ❌ Kiriş kaçıklık veya boyutları sebebiyle izin verilmeyen alana (mesela kat alanının dışına) taşmaktadır.
5. Kiriş belirli bir kıymet derecesi olan alanın içindedir.
6. ❌ Kiriş kaçıklık veya boyutları sebebiyle, belirli bir kıymet derecesi olan alanın içine taşmaktadır.
7. Kiriş başka bir kirişe saplanmıştır.
8. Başka bir kirişe saplanan kirişe de bir kiriş saplanmıştır (Saplamanın saplaması var).
9. Kirişin serbest ucu var.
10. Tam duvar altında kiriş yoktur.
11. Yarım duvar altında kiriş yoktur.
12. ❌ Kiriş bağlandığı kolonun kenarlarından taşmaktadır.

### Noktasal ve Çizgisel Kolon

13. Kolonlar arasındaki mesafe izin verilen aralığın dışındadır. `d < d_min` veya `d > d_max`
14. Kolon izin verilmeyen alanın içindedir (mesela oturma alanının dışında).
15. ❌ Kolon kaçıklık veya boyutları sebebiyle izin verilmeyen alana (mesela oturma alanının dışına) taşmaktadır.
16. Kolon belirli bir kıymet derecesi olan alanın içindedir.
17. ❌ Kolon kaçıklık veya boyutları sebebiyle, belirli bir kıymet derecesi olan alanın içine taşmaktadır.
18. ❌ Kolonlar kesişmektedir.
19. Kolona hiç kiriş bağlanmamaktadır.
20. Oturma alanı poligonunun köşelerinde kolon bulunmamaktadır.

### Noktasal Kolon

21. Kolonun uzun kenarı, üzerinde duvar bulunmayan (hacmin içine doğru) bir aks yönündedir.

### Çizgisel Kolon

22. Çizgisel kolon boyu izin verilen aralığın dışındadır. `h < h_min` veya `h > h_max`
23. Çizgisel kolon izin verilmeyen açıklığa (span) yerleştirilmiştir.
24. Çizgisel kolonun serbest ucu bulunmaktadır.
25. Çizgisel kolonun bulunduğu açıklıkta kiriş de bulunmaktadır.

### Çizgisel Kolonlar ile Oluşturulan Perdeler

26. ❌ Her iki yönde de perdelerin bulunduğu bir ortogonal eksen takımı bulunmamaktadır.
27. ❌ Perde sayısı izin verilen aralığın dışındadır. `n < n_min` veya `n > n_max`
28. ❌ Perdeler olabildiğince dış akslara yerleştirilmemiştir.
29. ❌ Perdelerin etki çizgileri bir noktada kesişmektedir.

### Sürekli Kiriş Hatları

30. Sistemde bulunan sürekli kiriş hatlarının, izin verilen alan içerisinde kalan en dış noktalarında kolon yoktur.
31. Sürekli kiriş hattındaki arasında kolon bulunmayan kirişlerin eksenleri çakışık değildir.
32. Sürekli kiriş hattında farklı kesitlerde kirişler bulunmaktadır.
33. Sürekli kiriş hattında süreksizlik yaratan kiriş eksiklikleri vardır.
34. Birbirinin yerine kullanılabilecek sürekli kiriş hatları sistemde aynı anda bulunmaktadır.
35. Yapının oturma alanını çevreleyen sürekli hatlar sistemde bulunmamaktadır.

### Taşıyıcı Sistem Planı
36. Planın kütle merkezi ile rijitlik merkezi arasındaki mesafe büyüktür (`dRG > max dRG`).
37. Yapıdaki kolonların toplam alanı belirtilen sınırlar arasında değildir (`A < A_min` veya `A > A_max`).
38. ❌ Yapının x ve y yönlerindeki eğilme atalet momentleri belirtilen sınırlar arasında değildir (`I < I_min` veya `I > I_max`).
39. Yapının kuvvetli ve zayıf yönlerindeki atalet momentleri farkı büyüktür (`I_strong / I_weak > rI_max`).
40. ❌ Yapının burulma atalet momenti belirtilen sınırlar arasında değildir (`It < It_min` veya `It > It_max`).