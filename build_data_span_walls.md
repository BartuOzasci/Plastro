### Algoritma

1. span'e cos_tol toleransı ile paralel sayılabilecek ve span eksenine dik (ortalama) uzaklığı dProbe'dan büyük olmayan duvar çizgilerini al
2. Bu duvar çizgilerinin span üzerindeki izdüşümlerini (projeksiyonlarını) bul
3. Duvar çizgisi izdüşümlerinin başlangıç ve bitiş noktalarından faydalanarak span üzerinde aralıklar oluştur ve bu aralıklara denk gelen (varsa) en büyük duvar kalınlıklarını ve ortalama duvar ekseni mesafelerini bul
4. En az iki adet duvar çizgisi bulunmadığı için üzerinde duvar oluşmayan aralıkları "duvar yok" olarak işaretle
5. Ardışık duvar hatları oluşturan aralıkları (duvar mesafeleri ve kalınlıkları aynı olmasa da) birleştir
6. Her span için aşağıdaki bilgilerden oluşan bir özet döndür
    - span başlangıcından itibaren (kesintisiz) duvar bağıl uzunluğu
    - span bitişinden itibaren (kesintisiz) duvar bağıl uzunluğu
    - span eksenine dik ortalama duvar mesafesi
    - ortalama duvar kalınlığı

***

### Eksikler

1. Duvar çizerken, duvar birleşim yerlerinde duvarların birbirleri içine geçen kısımları budanır. Bu durum, duvar çizgi(ler)inin budanmış kısımları sebebiyle, ilgili duvar(ların) tespitini engeller. Örneğin aşağıdaki durumda span'in yalnızca * ile gösterilen kısmında duvar bulunduğu tespit edilir. Bu sebeple hem span başlangıcından, hem de span bitişinden itibaren kesintisiz duvar uzunluğu bulunamaz.

```
 |  |          |  |
 |  |          |  |
 |  ------------  |
 | -************- |
 |----------------|
```

***

### Fonksiyonlar

```
1. is_line_parallel_to_span(line, span_unit, cos_tol)

2. is_line_within_distance(line, span_start, span_unit, dProbe)

3. project_line_onto_span(line, span_start, span_unit, span_len)

4. find_wall_projections(spans, nodes, wallLines, dProbe=30, tol_deg=1)
    1. is_line_parallel_to_span(line, span_unit, cos_tol)
    2. is_line_within_distance(line, span_start, span_unit, dProbe)
    3. project_line_onto_span(line, span_start, span_unit, span_len)

5. arrange_wall_projections(matched_lines_list, signed_distances_list, tRound=3)

6. refine_wall_projections(arranged_walls_list, arranged_distances_list, wall_widths_list)

7. merge_wall_lines(refined_walls_list, tol=1e-3)

8. build_data_span_walls(spans, nodes, wallLines, dProbe=30)
    4. find_wall_projections(spans, nodes, wallLines, dProbe=30, tol_deg=1)
    5. arrange_wall_projections(matched_lines_list, signed_distances_list, tRound=3)
    6. refine_wall_projections(arranged_walls_list, arranged_distances_list, wall_widths_list)
    7. merge_wall_lines(refined_walls_list, tol=1e-3)
```