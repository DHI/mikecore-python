import unittest
from mikecore.DfsFileFactory import DfsFileFactory
from mikecore.DfsFile import *
from numpy.testing import *

class Test_dfs_static_item(unittest.TestCase):

    def test_static_item(self):
        dfsFile = DfsFileFactory.DfsGenericOpen("testdata/OresundHD.dfsu")

        staticItems = []
        staticItemNumber = 1;
        while (True):
            varstaticItem = dfsFile.ReadStaticItem(staticItemNumber);
            if (varstaticItem == None):
                break;
            staticItems.append(varstaticItem);
            staticItemNumber += 1

        assert staticItems != None
        assert 9 == len(staticItems)

        # Check x-coord static item
        staticItem = staticItems[1];
        assert 2 ==  staticItem.ItemNumber
        assert 2057 == staticItem.ElementCount
        #assert 2057 == staticItem.UsedElementCount
        assert "X-coord" == staticItem.Name

        if (eumItem.eumIItemUndefined == staticItem.Quantity.Item):
            assert eumUnit.eumUUnitUndefined == staticItem.Quantity.Unit
        elif (eumItem.eumIGeographicalCoordinate == staticItem.Quantity.Item):
            assert eumUnit.eumUmeter == staticItem.Quantity.Unit
        else:
            assert "X coordinate axis item type mismatch" == ""

        if (staticItem.DataType != DfsSimpleType.Double and staticItem.DataType != DfsSimpleType.Float):
            assert "DataType of X static item mismatch" == ""

        #assert deleteValueFloat == staticItem.ReferenceCoordinateX
        #assert deleteValueFloat == staticItem.ReferenceCoordinateY
        #assert deleteValueFloat == staticItem.ReferenceCoordinateZ
        #assert deleteValueFloat == staticItem.OrientationAlpha
        #assert deleteValueFloat == staticItem.OrientationPhi
        #assert deleteValueFloat == staticItem.OrientationTheta

        # Check dummy spatial axis
        axis = staticItem.SpatialAxis
        assert SpaceAxisType.EqD1 == axis.AxisType
        assert    1 == axis.Dimension
        assert 2057 == axis.XCount
        assert    0 == axis.X0
        assert    1 == axis.Dx

        # Check data - first and last coordinate
        assert_allclose(359978.8, staticItem.Data[0])
        assert_allclose(338109.5, staticItem.Data[2056])

        #--------------------------------------
        # Check element type static item
        staticItem = staticItems[6];
        assert 7    == staticItem.ItemNumber;
        assert 3636 == staticItem.ElementCount
        #assert 3636 == staticItem.UsedElementCount

        if   (eumItem.eumIItemUndefined == staticItem.Quantity.Item):
            assert eumUnit.eumUUnitUndefined == staticItem.Quantity.Unit
        elif (eumItem.eumIIntegerCode == staticItem.Quantity.Item):
            assert eumUnit.eumUintCode == staticItem.Quantity.Unit
        else:
            raise Exception("Element Type coordinate axis item type mismatch")

        assert DfsSimpleType.Int == staticItem.DataType
        assert "Element type" == staticItem.Name

        # Check dummy spatial axis
        axis = staticItem.SpatialAxis
        assert SpaceAxisType.EqD1 == axis.AxisType
        assert 3636, axis.XCount

        # Check data - first and last elements
        assert 21 == staticItem.Data[0]
        assert 21 == staticItem.Data[3635]

        #--------------------------------------
        # Check connectivity static item
        staticItem = staticItems[8];
        assert 9 == staticItem.ItemNumber
        assert 3 * 3636 == staticItem.ElementCount
        #assert 3 * 3636 == staticItem.UsedElementCount

        if (eumItem.eumIItemUndefined == staticItem.Quantity.Item):
            assert eumUnit.eumUUnitUndefined == staticItem.Quantity.Unit
        elif (eumItem.eumIIntegerCode == staticItem.Quantity.Item):
            assert eumUnit.eumUintCode == staticItem.Quantity.Unit
        else:
            raise Exception("Connectivity coordinate axis item type mismatch")

        assert DfsSimpleType.Int == staticItem.DataType
        assert "Connectivity" == staticItem.Name

        #assert deleteValueFloat == staticItem.ReferenceCoordinateX
        #assert deleteValueFloat == staticItem.ReferenceCoordinateY
        #assert deleteValueFloat == staticItem.ReferenceCoordinateZ
        #assert deleteValueFloat == staticItem.OrientationAlpha
        #assert deleteValueFloat == staticItem.OrientationPhi
        #assert deleteValueFloat == staticItem.OrientationTheta

        # Check dummy spatial axis
        axis = staticItem.SpatialAxis;
        assert SpaceAxisType.EqD1 == axis.AxisType
        assert 1 == axis.Dimension
        # TODO: Assert.AreEqual(eumUnit.eumUmeter, axis.AxisUnit
        assert 3 * 3636 == axis.XCount
        assert 0 == axis.X0
        assert 1 == axis.Dx

        # Check data - first and last element
        assert 1 == staticItem.Data[0]
        assert 2 == staticItem.Data[1]
        assert 3 == staticItem.Data[2]
        assert 1698 == staticItem.Data[10905]
        assert 1697 == staticItem.Data[10906]
        assert 2056 == staticItem.Data[10907]




if __name__ == '__main__':
    unittest.main()
