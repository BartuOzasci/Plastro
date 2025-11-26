### Vibe Code / Context Code

Problemin çözümü için aşağıdaki bilgiler kullanılacaktır.

1. axesDirection (numpy array) dizisinde aksların birbirlerine göre yönleri verilmiştir. Örneğin indeksi 2 ile 6 olan akslar için axesDirection[2][6] ile çağırılan değer 1 ise bu iki aks aynı yöndedir, -1 ise zıt yöndedir. 0 ise bu iki aks birbirine diktir.

2. axNod (list of numpy arrays) listesinde axNod = [ [0,2,4,7,8] , [1,3,5,12,13] , ... ] şeklinde hangi aks üzerinde hangi düğüm noktalarının olduğu bilgisi vardır. Her aks için verilen düğüm noktaları aksların başlangıç noktasından bitiş noktasına doğru sıralanmıştır.

3. nodMat (numpy array) dizisinde [ [-1,0,3,5,-1] , [6,-1,-1,1,-1] , ... ] şeklinde hangi düğüm ile hangi düğüm arasında kaç numaralı aks parçasının (span'in) tanımlı olduğunu tutan listedir. Örneğin 2 ile 5 numaralı düğümlerin arasındaki aks parçası numarası nodMat[2][5] şeklinde çağırılır. Eğer seçilen iki düğüm arasında bir span tanımlı değil ise -1 döner.

4. spanLen (numpy array) dizisinde [ 341 , 129 , ... ] şeklinde hangi span'in uzunluğunun ne kadar olduğu bilgisi vardır.

5. maxJumpDist (float) değişkeninde bir aks üzerindeki bir A düğümünden diğer bir aks üzerindeki bir B düğümüne atlayabilmek için BA mesafesinin en fazla kaç olabileceği tutulur.

6. maxJumpCount (int) değişkeninde kaç kez akslar arası geçiş yapılabileceği bilgisi tutulur.

Bir "sürekli hat" ifadesinden anlaşılacak şey; bir aksın başlangıç düğümünden başlayıp, hep aynı yönde ilerleyerek, aynı aksın veya diğer bir aksın ucundaki düğüme ulaşmaktır. Bir aksın ucundaki düğüme ulaşıldığında "sürekli hat" sonlanır. Örneğin, axNod listesindeki ilk (0 numaralı) aksın başlangıç düğümü olan 0 düğümünden başlayıp, sırasıyla aynı aks üzerindeki 2, 4, 7 ve 8 numaralı düğümlerden oluşan hat, sadece 0 numaralı aks üzerinde bulunan bir "sürekli hat"tır.

Bir "sürekli hat" birden fazla aks üzerinde de bulunabilir. Örneğin, yine 0 numaralı aksın başlangıç düğümü olan 0 düğümünden başlayarak 2 düğümünden geçerek 4 düğümüne ulaşan bir hat parçasından sonra,

a. Eğer bu düğüm ile başka bir aks üzerindeki başka bir düğüm arasında bir span var ise (nodMat matrisi ile kontrol edilebilir)
b. Bu düğümler arasındaki span'ın boyu en fazla maxJumpDist kadar ise (spanLen dizisi üzerinwden kontrol edilebilir)
c. Söz konusu "sürekli hat" oluşturulurken yapılan akslar arası atlama sayısı henüz maxJumpCount'a ulaşmadı ise

söz edilen diğer aksın ilgli düğümüne atlanarak da sürekli hat oluşturmaya devam edilebilir.

Örnek olarak, 0 numaralı aksta 4 numaralı düğümden 1 numaralı akstaki 5 numaralı düğüme atlanabilecek şartlar oluşmuş olsun (yukarıdaki a, b ve c şartları sağlanıyor olsun). Şimdi "sürekli hat", 1 numaralı aks üzerinde ilerleyerek tamamlanabilir. Ancak,

- aynı yönde ilerlenildiğinden emin olunmalıdır. Bunun için 0 numaralı ve 1 numaralı akslar aynı yönde mi kontrol edilmelidir. (Bu kontrol axesDirection listesi ile yapılabilir). Eğer 1 numaralı aks ters yönde ise düğüm sırası ters çevrilmelidir. Yani 1 numaralı aksın düğümlerinin sırası [1,3,5,12,13] yerine [13,12,5,3,1] şeklinde düşünülerek, 5 numaralı düğümden sonra 3 ve sonra 1 numaralı düğüme ulaşılarak sürekli hat oluşturulmalıdır.

- "Sürekli hat" oluşturmak için düğümler arası hareketleri belirlerken ilk ve son hareket "akslar arası atlama" olmamalıdır. İlk hareket bir aksın başlangıç noktasından aynı aksın ardışık düğümüne geçiş, son hareket ise üzerinde bulunulan aksın uç düğümüne geçiş olmalıdır.

Fonksiyon, yukarıda madde 1'den 6'ya kadar verilen girdiyi alarak aşağıdaki listeleri üretmelidir.

I. axNod listesinde üzerindeki düğümler sıralı bir şekilde verilen akslar kullanılarak oluşturulabilecek tüm "sürekli hat"ların [ [[0,2,4],[4,5],[5,3,1]], ... ] şeklinde listesi. Örnek listede bir "sürekli hat" verilmiştir. Aynı akstaki 0, 2 ve 4 düğümlerinden sonra 4 ve 5 düğümleri kullanılarak diğer aksa atlanmıştır. Bu diğer aksta da 5, 3 ve 1 düğümlerine ulaşılarak "sürekli hat" tamamlanmıştır.

II. "Sürekli hat"lar oluşturulurken hangi aksların kullanıldığının [ [0,1] , ...] şeklinde listesi. Örnek listede ilk sürekli hat oluşturulurken 0 ve 1 numaralı aksların kullanıldığı belirtilmiştir.


***


### Ne Oldu?

Vibe Code ile bu modülü oluşturamadım. Yapılacak işi küçük alt görevlere bölüp öyle halledebildim.


***


### Algoritma

1. Tüm aks çiftleri için akslar arasında geçiş yapmak için kullanılabilecek [i,j] şeklinde düğüm çiftlerini belirle
2. Akslar arası geçiş yapılabilecek düğüm çiftleri bulunan akslar için, aynı aks üzerinde ve ilerleme yönünde olan düğüm çiftlerini belirle
3. İlk iki madde ile bulunan düğüm çiftleri, söz konusu iki aks üzerinde "sürekli hat"lar oluşturmak için kullanılabilecek geçişleri oluşturur.
4. Aks çiftleri üzerinde oluşturulabilecek "sürekli hat"ları Depth-First Search (DFS) algoritması ile belirle
5. m ve n aksları için bulunan "sürekli hat"ların detaylarını bir matrisin m. Satır ve n. Sütununa kaydet.


***


```
1. find_jumps(axNod, axesDirection, nodMat, spanLen, maxJumpLength=np.inf)

2. find_transitions(axNod, axesDirection, jumps)

3. dfs_all_paths(transitions, start_node, end_nodes)

4. build_path_details(axNod, nodMat, all_transitions, all_start_nodes, all_end_nodes, jumps, maxJumpCount=2)
    3. dfs_all_paths(transitions, start_node, end_nodes)

5. build_data_cont_lines(axNod, axesDirection, nodMat, spanLen, maxJumpLength=np.inf, maxJumpCount=2)
    1. find_jumps(axNod, axesDirection, nodMat, spanLen, maxJumpLength=np.inf)
    2. find_transitions(axNod, axesDirection, jumps)
    4. build_path_details(axNod, nodMat, all_transitions, all_start_nodes, all_end_nodes, jumps, maxJumpCount=2)
```