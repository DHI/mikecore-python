import unittest

from miketools.Dfs0ToAscii import *

class Test_miketools(unittest.TestCase):

    def test_Dfs0ToAscii(self):
        Dfs0ToAscii("testdata/Rain_accumulated.dfs0"    ,"testdata/testtmp/Rain_accumulated.txt"    )
        Dfs0ToAscii("testdata/Rain_backwardStep.dfs0"   ,"testdata/testtmp/Rain_backwardStep.txt"   )
        Dfs0ToAscii("testdata/Rain_forwardStep.dfs0"    ,"testdata/testtmp/Rain_forwardStep.txt"    )
        Dfs0ToAscii("testdata/Rain_instantaneous.dfs0"  ,"testdata/testtmp/Rain_instantaneous.txt"  )
        Dfs0ToAscii("testdata/Rain_stepaccumulated.dfs0","testdata/testtmp/Rain_stepaccumulated.txt")
        Dfs0ToAscii("testdata/TemporalEqCal.dfs0"       ,"testdata/testtmp/TemporalEqCal.txt"       )
        Dfs0ToAscii("testdata/TemporalEqTime.dfs0"      ,"testdata/testtmp/TemporalEqTime.txt"      )
        Dfs0ToAscii("testdata/TemporalNeqCal.dfs0"      ,"testdata/testtmp/TemporalNeqCal.txt"      )
        Dfs0ToAscii("testdata/TemporalNeqTime.dfs0"     ,"testdata/testtmp/TemporalNeqTime.txt"     )
