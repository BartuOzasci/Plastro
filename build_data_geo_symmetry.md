```
1. find_symmetry_points(points, symmetry_line)
2. find_symmetry_indices(points, symmetry_line, tol = 1e-6)
3. find_axesToTestForSymmetry(polygon_nodes, points)
4. build_axesAndNodeSymmetry(polygon_nodes, points, axesToTestForSymmetry)
5. build_axesSymmetry(axNod, nodeSymmetry)
6. build_spanSymmetry(spans, nodeSymmetry)
7. build_areaSymmetry(areas, nodeSymmetry)
8. build_nodeSymMove(symAxesAngle)
9. build_spanSymMove(nodes, spans, spanSymmetry, symAxesAngle)
10. combine_symmetry_lists(sym_list)
11. build_data_geo_symmetry(polygon_nodes, nodes, spans, areas)
```

```
1. find_symmetry_points(points, symmetry_line)
```

```
2. find_symmetry_indices(points, symmetry_line, tol = 1e-6)
    1. find_symmetry_points(points, symmetry_line)
```

```
3. find_axesToTestForSymmetry(polygon_nodes, points)
```

```
4. build_axesAndNodeSymmetry(polygon_nodes, points, axesToTestForSymmetry)
    2. find_symmetry_indices(points, symmetry_line, tol = 1e-6)
```

```
5. build_axesSymmetry(axNod, nodeSymmetry)
```

```
6. build_spanSymmetry(spans, nodeSymmetry)
```

```
7. build_areaSymmetry(areas, nodeSymmetry)
```

```
8. build_nodeSymMove(symAxesAngle)
```

```
9. build_spanSymMove(nodes, spans, spanSymmetry, symAxesAngle)
```

```
10. combine_symmetry_lists(sym_list)
```

```
11. build_data_geo_symmetry(polygon_nodes, nodes, spans, areas)
    3. find_axesToTestForSymmetry(polygon_nodes, points)
    4. build_axesAndNodeSymmetry(polygon_nodes, points, axesToTestForSymmetry)
    5. build_axesSymmetry(axNod, nodeSymmetry)
    6. build_spanSymmetry(spans, nodeSymmetry)
    7. build_areaSymmetry(areas, nodeSymmetry)
    8. build_nodeSymMove(symAxesAngle)
    9. build_spanSymMove(nodes, spans, spanSymmetry, symAxesAngle)
    10. combine_symmetry_lists(sym_list) # vazgeçtim; gereksiz
```