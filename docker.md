## Run mikecore using Docker


1. `git clone https://github.com/DHI/mikecore-python`
2. `cd mikecore-python`
2. `docker build . -t mikecore:latest`
3. `docker run mikecore:latest`

Then you should get output like this:
```
============================= test session starts ==============================
platform linux -- Python 3.9.4, pytest-6.2.4, py-1.10.0, pluggy-0.13.1
rootdir: /app
collected 68 items

tests/test_dfs0.py ........                                              [ 11%]
tests/test_dfs2.py ..........                                            [ 26%]
tests/test_dfs_basic.py .....                                            [ 33%]
tests/test_dfs_custom_block.py ..                                        [ 36%]
tests/test_dfs_static_item.py .                                          [ 38%]
tests/test_dfsbuilder.py ......                                          [ 47%]
tests/test_dfsu2D.py ..........                                          [ 61%]
tests/test_dfsu_file.py ..........                                       [ 76%]
tests/test_eum.py ..                                                     [ 79%]
tests/test_mesh.py ...                                                   [ 83%]
tests/test_miketools.py .                                                [ 85%]
tests/test_projections.py ..........                                     [100%]

============================= 68 passed in 31.46s ==============================