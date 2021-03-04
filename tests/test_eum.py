import unittest
from tests.test_util import *
from mikecore.eum import *


class TestEUM(unittest.TestCase):
    def test_wrapper(self):
        itemTable = eumWrapper.CreateItemHashtable();
        Assert.AreEqual(eumItem.eumIDischarge, itemTable["Discharge"])
        unitTable = eumWrapper.CreateUnitHashTable();
        Assert.AreEqual(eumUnit.eumUmeter, unitTable["meter"])
        unitabTable = eumWrapper.CreateUnitHashTable(abbreviations = True);
        Assert.AreEqual(eumUnit.eumUmeter, unitabTable["m"])

        Assert.AreEqual(eumItem.eumIDischarge, eumWrapper.GetItemTypeTag("Discharge"))
        Assert.AreEqual(eumUnit.eumUm3PerSec, eumWrapper.eumGetItemUnitTag(eumItem.eumIDischarge, "meter^3/sec"))
        Assert.AreEqual(eumUnit.eumUmeter, eumWrapper.eumGetUnitTag("meter"))

        disUnits = eumWrapper.GetItemAllowedUnits(eumItem.eumIDischarge);
        Assert.IsTrue(eumUnit.eumUm3PerSec in disUnits)

        Assert.AreEqual("Discharge", eumWrapper.eumGetItemTypeKey(eumItem.eumIDischarge))
        Assert.AreEqual("meter", eumWrapper.eumGetUnitKey(eumUnit.eumUmeter));
        Assert.AreEqual("m", eumWrapper.eumGetUnitAbbreviation(eumUnit.eumUmeter));

        Assert.AreEqual(eumUnit.eumUm3PerSec, eumWrapper.eumGetItemFirstEqvUnit(eumItem.eumIDischarge));
        Assert.IsTrue(eumWrapper.eumUnitsEqv(eumUnit.eumUmeter, eumUnit.eumUfeet))
        Assert.IsFalse(eumWrapper.eumUnitsEqv(eumUnit.eumUmeter, eumUnit.eumUacre))
        Assert.IsTrue(eumWrapper.eumItemUnitEqv(eumItem.eumIWaterDepth, eumUnit.eumUfeet))
        Assert.IsFalse(eumWrapper.eumItemUnitEqv(eumItem.eumIWaterDepth, eumUnit.eumUacre));

        Assert.AreEqual(eumUnit.eumUmeter, eumWrapper.eumGetBaseUnit(eumUnit.eumUfeet));

        Assert.AreEqual(0.3048, eumWrapper.eumConvertUnit(eumUnit.eumUfeet, 1, eumUnit.eumUmeter)[1], 1e-10);
        Assert.AreEqual(0.3048, eumWrapper.eumConvertUnit(1003, 1, 1000)[1], 1e-10);

        array = np.array([0.5, 1, 2, 3.280839895])
        Assert.IsTrue(eumWrapper.eumConvertItemArrayD(eumUnit.eumUfeet, eumUnit.eumUmeter, array));
        Assert.AreEqual(np.array([0.1524, 0.3048, 0.6096, 1]), array, 1e-10)

        array = np.array([0.5, 1, 2, 3.280839895], dtype=np.float32)
        Assert.IsTrue(eumWrapper.eumConvertItemArrayF(eumUnit.eumUfeet, eumUnit.eumUmeter, array));
        Assert.AreEqual(np.array([0.1524, 0.3048, 0.6096, 1], dtype=np.float32), array, 1e-6)

        Assert.AreEqual(0.3048, eumWrapper.eumConvertUnitToBase(eumUnit.eumUfeet, 1), 1e-10);
        Assert.AreEqual(1/0.3048, eumWrapper.eumConvertUnitFromBase(eumUnit.eumUfeet, 1), 1e-10);

        Assert.AreEqual(0.3048, eumWrapper.eumConvertToUserUnit(eumItem.eumIWaterLevel, eumUnit.eumUfeet, 1), 1e-10);
        Assert.AreEqual(1/0.3048, eumWrapper.eumConvertFromUserUnit(eumItem.eumIWaterLevel, eumUnit.eumUfeet, 1), 1e-10);

        array = np.array([0.5, 1, 2, 3.280839895])
        Assert.IsTrue(eumWrapper.eumConvertItemArrayToUserUnitD(eumItem.eumIWaterLevel, eumUnit.eumUfeet, array));
        Assert.AreEqual(np.array([0.1524, 0.3048, 0.6096, 1]), array, 1e-10)

        array = np.array([0.5, 1, 2, 3.280839895], dtype=np.float32)
        Assert.IsTrue(eumWrapper.eumConvertItemArrayToUserUnitF(eumItem.eumIWaterLevel, eumUnit.eumUfeet, array));
        Assert.AreEqual(np.array([0.1524, 0.3048, 0.6096, 1], dtype=np.float32), array, 1e-6)

        array = np.array([0.1524, 0.3048, 0.6096, 1])
        Assert.IsTrue(eumWrapper.eumConvertItemArrayFromUserUnitD(eumItem.eumIWaterLevel, eumUnit.eumUfeet, array));
        Assert.AreEqual(np.array([0.5, 1, 2, 3.280839895]), array, 1e-6)

        array = np.array([0.1524, 0.3048, 0.6096, 1], dtype=np.float32)
        Assert.IsTrue(eumWrapper.eumConvertItemArrayFromUserUnitF(eumItem.eumIWaterLevel, eumUnit.eumUfeet, array));
        Assert.AreEqual(np.array([0.5, 1, 2, 3.280839895], dtype=np.float32), array, 1e-6)

        Assert.AreEqual((1/1.8, -32/1.8), eumWrapper.eumUnitGetSIFactor(eumUnit.eumUdegreeFahrenheit))
        scale, offset, powdim, facdim = eumWrapper.eumUnitGetParameters(eumUnit.eumUft3PerDay);
        Assert.AreEqual((0.3048**3)/86400, scale, 1e-10)
        Assert.AreEqual(0, offset)
        Assert.AreEqual(np.array([      3.0, 0,    -1.0, 0, 0, 0, 0]),powdim)
        Assert.AreEqual(np.array([0.3048**3, 1, 1/86400, 1, 1, 1, 1]),facdim, 1e-10)




    def test_converter(self):
        uc = UnitConverter(eumUnit.eumUfeet, eumUnit.eumUmeter);
        Assert.AreEqual(0.3048, uc.Convert(1), 1e-10)
        Assert.AreEqual(1/0.3048, uc.InvConvert(1), 1e-10)
        array = np.array([0.5, 1, 2, 3.280839895])
        uc.ConvertArray(array);
        Assert.AreEqual(np.array([0.1524, 0.3048, 0.6096, 1]), array, 1e-10)

        array = np.array([0.1524, 0.3048, 0.6096, 1])
        uc.InvConvertArray(array);
        Assert.AreEqual(np.array([0.5, 1, 2, 3.280839895]), array, 1e-6)


