```
1. build_fitness_span_in_area(spanLen, spanInArea, areaImportance)

2. build_fitness_node_in_area(nodInArea, areaImportance)

3. build_fitness_standalone_beams(beamTopo, contBeamTopo, contBeam, spanLen)

4. build_fitness_crossing_beams(colTopo, colSpanTopo, beamTopo, spans, nodSpan, spanAx, spanLen)

5. build_data_fitness(cand, geoData, contBeam, fitness_span_in_area, fitness_node_in_area)
    3. build_fitness_standalone_beams(beamTopo, contBeamTopo, contBeam, spanLen)
    4. build_fitness_crossing_beams(colTopo, colSpanTopo, beamTopo, spans, nodSpan, spanAx, spanLen)
```