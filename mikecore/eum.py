import os
import ctypes
from typing import Optional, Tuple
import numpy as np
from enum import IntEnum

# Predefined enums of EUM item types.
#
# Must be updated with every new release, or if the EUM.xml is updated
class eumItem(IntEnum):
    eumIItemUndefined = 999
    eumIWaterLevel = 100000
    eumIDischarge = 100001
    eumIWindVelocity = 100002
    eumIWindDirection = 100003
    eumIRainfall = 100004
    eumIEvaporation = 100005
    eumITemperature = 100006
    eumIConcentration = 100007
    eumIBacteriaConc = 100008
    eumIResistFactor = 100009
    eumISedimentTransport = 100010
    eumIBottomLevel = 100011
    eumIBottomLevelChange = 100012
    eumISedimentFraction = 100013
    eumISedimentFractionChange = 100014
    eumIGateLevel = 100015
    eumIFlowVelocity = 100016
    eumIDensity = 100017
    eumIDamBreachLevel = 100018
    eumIDamBreachWidth = 100019
    eumIDamBreachSlope = 100020
    eumISunShine = 100021
    eumISunRadiation = 100022
    eumIRelativeHumidity = 100023
    eumISalinity = 100024
    eumISurfaceSlope = 100025
    eumIFlowArea = 100026
    eumIFlowWidth = 100027
    eumIHydraulicRadius = 100028
    eumIResistanceRadius = 100029
    eumIManningsM = 100030
    eumIManningsn = 100031
    eumIChezyNo = 100032
    eumIConveyance = 100033
    eumIFroudeNo = 100034
    eumIWaterVolume = 100035
    eumIFloodedArea = 100036
    eumIWaterVolumeError = 100037
    eumIAccWaterVolumeError = 100038
    eumICompMass = 100039
    eumICompMassError = 100040
    eumIAccCompMassError = 100041
    eumIRelCompMassError = 100042
    eumIRelAccCompMassError = 100043
    eumICompDecay = 100044
    eumIAccCompDecay = 100045
    eumICompTransp = 100046
    eumIAccCompTransp = 100047
    eumICompDispTransp = 100048
    eumIAccCompDispTransp = 100049
    eumICompConvTransp = 100050
    eumIAccCompConvTransp = 100051
    eumIAccSedimentTransport = 100052
    eumIDuneLength = 100053
    eumIDuneHeight = 100054
    eumIBedSedimentLoad = 100055
    eumISuspSedimentLoad = 100056
    eumIIrrigation = 100057
    eumIRelMoistureCont = 100058
    eumIGroundWaterDepth = 100059
    eumISnowCover = 100060
    eumIInfiltration = 100061
    eumIRecharge = 100062
    eumIOF1_Flow = 100063
    eumIIF1_Flow = 100064
    eumICapillaryFlux = 100065
    eumISurfStorage_OF1 = 100066
    eumISurfStorage_OF0 = 100067
    eumISedimentLayer = 100068
    eumIBedLevel = 100069
    eumIRainfallIntensity = 100070
    eumIproductionRate = 100071
    eumIsedimentMass = 100072
    eumIprimaryProduction = 100073
    eumIprodPerVolume = 100074
    eumIsecchiDepth = 100075
    eumIAccSedimentMass = 100076
    eumISedimentMassPerM = 100077
    eumISurfaceElevation = 100078
    eumIBathymetry = 100079
    eumIFlowFlux = 100080
    eumIBedLoadPerM = 100081
    eumISuspLoadPerM = 100082
    eumISediTransportPerM = 100083
    eumIWaveHeight = 100084
    eumIWavePeriod = 100085
    eumIWaveFrequency = 100086
    eumIPotentialEvapRate = 100087
    eumIRainfallRate = 100088
    eumIWaterDemand = 100089
    eumIReturnFlowFraction = 100090
    eumILinearRoutingCoef = 100091
    eumISpecificRunoff = 100092
    eumIMachineEfficiency = 100093
    eumITargetPower = 100094
    eumIWaveDirection = 100095
    eumIAccSediTransportPerM = 100096
    eumISignificantWaveHeight = 100097
    eumIShieldsParameter = 100098
    eumIAngleBedVelocity = 100099
    eumIProfileNumber = 100100
    eumIClimateNumber = 100101
    eumISpectralDescription = 100102
    eumISpreadingFactor = 100103
    eumIRefPointNumber = 100104
    eumIWindFrictionFactor = 100105
    eumIWaveDisturbanceCoefficient = 100106
    eumITimeFirstWaveArrival = 100107
    eumISurfaceCurvature = 100108
    eumIRadiationStress = 100109
    eumISpectralDensity = 100120
    eumIFreqIntegSpectralDensity = 100121
    eumIDirecIntegSpectralDensity = 100122
    eumIViscosity = 100123
    eumIDSD = 100124
    eumIBeachPosition = 100125
    eumITrenchPosition = 100126
    eumIGrainDiameter = 100127
    eumIFallVelocity = 100128
    eumIGeoDeviation = 100129
    eumIBreakingWave = 100130
    eumIDunePosition = 100131
    eumIContourAngle = 100132
    eumIFlowDirection = 100133
    eumIBedSlope = 100134
    eumISurfaceArea = 100135
    eumICatchmentArea = 100136
    eumIRoughness = 100137
    eumIActiveDepth = 100138
    eumISedimentGradation = 100139
    eumIGroundwaterRecharge = 100140
    eumISoluteFlux = 100141
    eumIRiverStructGeo = 100142
    eumIRiverChainage = 100143
    eumINonDimFactor = 100144
    eumINonDimExp = 100145
    eumIStorageDepth = 100146
    eumIRiverWidth = 100147
    eumIFlowRoutingTimeCnst = 100148
    eumIFstOrderRateAD = 100149
    eumIFstOrderRateWQ = 100150
    eumIEroDepoCoef = 100151
    eumIShearStress = 100152
    eumIDispCoef = 100153
    eumIDispFact = 100154
    eumISedimentVolumePerLengthUnit = 100155
    eumILatLong = 100157
    eumISpecificGravity = 100158
    eumITransmissionCoefficient = 100159
    eumIReflectionCoefficient = 100160
    eumIFrictionFactor = 100161
    eumIRadiationIntensity = 100162
    eumIDuration = 100163
    eumIRespProdPerArea = 100164
    eumIRespProdPerVolume = 100165
    eumISedimentDepth = 100166
    eumIAngleOfRespose = 100167
    eumIHalfOrderRateWQ = 100168
    eumIRearationConstant = 100169
    eumIDepositionRate = 100170
    eumIBODAtRiverBed = 100171
    eumICropDemand = 100172
    eumIIrrigatedArea = 100173
    eumILiveStockDemand = 100174
    eumINumberOfLiveStock = 100175
    eumITotalGas = 100176
    eumIGroundWaterAbstraction = 100177
    eumIMeltingCoefficient = 100178
    eumIRainMeltingCoefficient = 100179
    eumIElevation = 100180
    eumICrossSectionXdata = 100181
    eumIVegetationHeight = 100182
    eumIGeographicalCoordinate = 100183
    eumIAngle = 100184
    eumIItemGeometry0D = 100185
    eumIItemGeometry1D = 100186
    eumIItemGeometry2D = 100187
    eumIItemGeometry3D = 100188
    eumITemperatureLapseRate = 100189
    eumICorrectionOfPrecipitation = 100190
    eumITemperatureCorrection = 100191
    eumIPrecipitationCorrection = 100192
    eumIMaxWater = 100193
    eumILowerBaseflow = 100194
    eumIMassFlux = 100195
    eumIPressureSI = 100196
    eumITurbulentKineticEnergy = 100197
    eumIDissipationTKE = 100198
    eumISaltFlux = 100199
    eumITemperatureFlux = 100200
    eumIConcentration1 = 100201
    eumILatentHeat = 100202
    eumIHeatFlux = 100203
    eumISpecificHeat = 100204
    eumIVisibility = 100205
    eumIIceThickness = 100206
    eumIStructureGeometryPerTime = 100207
    eumIDischargePerTime = 100208
    eumIFetchLength = 100209
    eumIRubbleMound = 100210
    eumIGridSpacing = 100211
    eumITimeStep = 100212
    eumILengthScale = 100213
    eumIErosionCoefficientFactor = 100214
    eumIFrictionCoeffient = 100215
    eumITransitionRate = 100216
    eumIDistance = 100217
    eumITimeCorrectionAtNoon = 100218
    eumICriticalVelocity = 100219
    eumILightExtinctionBackground = 100220
    eumIParticleProductionRate = 100221
    eumIFirstOrderGrazingRateDependance = 100222
    eumIResuspensionRate = 100223
    eumIAdsorptionCoefficient = 100224
    eumIDesorptionCoefficient = 100225
    eumISedimentationVelocity = 100226
    eumIBoundaryLayerThickness = 100227
    eumIDiffusionCoefficient = 100228
    eumIBioconcentrationFactor = 100229
    eumIFcoliConcentration = 100230
    eumISpecificDischarge = 100231
    eumIPrecipitation = 100232
    eumISpecificPrecipitation = 100233
    eumIPower = 100234
    eumIConveyanceLoss = 100235
    eumIInfiltrationFlux = 100236
    eumIEvaporationFlux = 100237
    eumIGroundWaterAbstractionFlux = 100238
    eumIFraction = 100239
    eumIYieldfactor = 100240
    eumISpecificSoluteFluxPerArea = 100241
    eumICurrentSpeed = 100242
    eumICurrentDirection = 100243
    eumICurrentMagnitude = 100244
    eumIPistonPosition = 100245
    eumISubPistonPosition = 100246
    eumISupPistonPosition = 100247
    eumIFlapPosition = 100248
    eumISubFlapPosition = 100249
    eumISupFlapPosition = 100250
    eumILengthZeroCrossing = 100251
    eumITimeZeroCrossing = 100252
    eumILengthLoggedData = 100253
    eumIForceLoggedData = 100254
    eumISpeedLoggedData = 100255
    eumIVolumeFlowLoggedData = 100256
    eumI2DSurfaceElevationSpectrum = 100257
    eumI3DSurfaceElevationSpectrum = 100258
    eumIDirectionalSpreadingFunction = 100259
    eumIAutoSpectrum = 100260
    eumICrossSpectrum = 100261
    eumICoherenceSpectrum = 100262
    eumICoherentSpectrum = 100263
    eumIFrequencyResponseSpectrum = 100264
    eumIPhaseSpectrum = 100265
    eumIFIRCoefficient = 100266
    eumIFourierACoefficient = 100267
    eumIFourierBCoefficient = 100268
    eumIuVelocity = 100269
    eumIvVelocity = 100270
    eumIwVelocity = 100271
    eumIBedThickness = 100272
    eumIDispersionVelocityFactor = 100273
    eumIWindSpeed = 100274
    eumIShoreCurrentZone = 100275
    eumIDepthofWind = 100276
    eumIEmulsificationConstantK1 = 100277
    eumIEmulsificationConstantK2 = 100278
    eumILightExtinction = 100279
    eumIWaterDepth = 100280
    eumIReferenceSettlingVelocity = 100281
    eumIPhaseError = 100282
    eumILevelAmplitudeError = 100283
    eumIDischargeAmplitudeError = 100284
    eumILevelCorrection = 100285
    eumIDischargeCorrection = 100286
    eumILevelSimulated = 100287
    eumIDischargeSimulated = 100288
    eumISummQCorrected = 100289
    eumITimeScale = 100290
    eumISpongeCoefficient = 100291
    eumIPorosityCoefficient = 100292
    eumIFilterCoefficient = 100293
    eumISkewness = 100294
    eumIAsymmetry = 100295
    eumIAtiltness = 100296
    eumIKurtosis = 100297
    eumIAuxiliaryVariableW = 100298
    eumIRollerThickness = 100299
    eumILineThickness = 100300
    eumIMarkerSize = 100301
    eumIRollerCelerity = 100302
    eumIEncroachmentOffset = 100303
    eumIEncroachmentPosition = 100304
    eumIEncroachmentWidth = 100305
    eumIConveyanceReduction = 100306
    eumIWaterLevelChange = 100307
    eumIEnergyLevelChange = 100308
    eumIParticleVelocityU = 100309
    eumIParticleVelocityV = 100310
    eumIAreaFraction = 100311
    eumICatchmentSlope = 100312
    eumIAverageLength = 100313
    eumIPersonEqui = 100314
    eumIInverseExpo = 100315
    eumITimeShift = 100316
    eumIAttenuation = 100317
    eumIPopulation = 100318
    eumIIndustrialOutput = 100319
    eumIAgriculturalArea = 100320
    eumIPopulationUsage = 100321
    eumIIndustrialUse = 100322
    eumIAgriculturalUsage = 100323
    eumILayerThickness = 100324
    eumISnowDepth = 100325
    eumISnowCoverPercentage = 100326
    eumIPressureHead = 100353
    eumIKC = 100354
    eumIAroot = 100355
    eumIC1 = 100356
    eumIC2 = 100357
    eumIC3 = 100358
    eumIIrrigationDemand = 100359
    eumIHydrTransmissivity = 100360
    eumIDarcyVelocity = 100361
    eumIHydrLeakageCoefficient = 100362
    eumIHydrConductance = 100363
    eumIHeightAboveGround = 100364
    eumIPumpingRate = 100365
    eumIDepthBelowGround = 100366
    eumICellHeight = 100367
    eumIHeadGradient = 100368
    eumIGroundWaterFlowVelocity = 100369
    eumIIntegerCode = 100370
    eumIDrainageTimeConstant = 100371
    eumIHeadElevation = 100372
    eumILengthError = 100373
    eumIElasticStorage = 100374
    eumISpecificYield = 100375
    eumIExchangeRate = 100376
    eumIVolumetricWaterContent = 100377
    eumIStorageChangeRate = 100378
    eumISeepage = 100379
    eumIRootDepth = 100380
    eumIRillDepth = 100381
    eumILogical = 100382
    eumILAI = 100383
    eumIIrrigationRate = 100384
    eumIIrrigationIndex = 100385
    eumIInterception = 100386
    eumIETRate = 100387
    eumIErosionSurfaceLoad = 100388
    eumIErosionConcentration = 100389
    eumIEpsilonUZ = 100390
    eumIDrainage = 100391
    eumIDeficit = 100392
    eumICropYield = 100393
    eumICropType = 100394
    eumICropStress = 100395
    eumICropStage = 100396
    eumICropLoss = 100397
    eumICropIndex = 100398
    eumIAge = 100399
    eumIHydrConductivity = 100400
    eumIPrintScaleEquivalence = 100401
    eumIConcentration_1 = 100402
    eumIConcentration_2 = 100403
    eumIConcentration_3 = 100404
    eumIConcentration_4 = 100405
    eumISedimentDiameter = 100406
    eumIMeanWaveDirection = 100407
    eumIFlowDirection_1 = 100408
    eumIAirPressure = 100409
    eumIDecayFactor = 100410
    eumISedimentBedDensity = 100411
    eumIDispersionCoefficient = 100412
    eumIFlowVelocityProfile = 100413
    eumIHabitatIndex = 100414
    eumIAngle2 = 100415
    eumIHydraulicLength = 100416
    eumISCSCatchSlope = 100417
    eumITurbidity_FTU = 100418
    eumITurbidity_MgPerL = 100419
    eumIBacteriaFlow = 100420
    eumIBedDistribution = 100421
    eumISurfaceElevationAtPaddle = 100422
    eumIUnitHydrographOrdinate = 100423
    eumITransferRate = 100424
    eumIReturnPeriod = 100425
    eumIConstFallVelocity = 100426
    eumIDepositionConcFlux = 100427
    eumISettlingVelocityCoef = 100428
    eumIErosionCoefficient = 100429
    eumIVolumeFlux = 100430
    eumIPrecipitationRate = 100431
    eumIEvaporationRate = 100432
    eumICoSpectrum = 100433
    eumIQuadSpectrum = 100434
    eumIPropagationDirection = 100435
    eumIDirectionalSpreading = 100436
    eumIMassPerUnitArea = 100437
    eumIIncidentSpectrum = 100438
    eumIReflectedSpectrum = 100439
    eumIReflectionFunction = 100440
    eumIBacteriaFlux = 100441
    eumIHeadDifference = 100442
    eumIenergy = 100443
    eumIDirStdDev = 100444
    eumIRainfallDepth = 100445
    eumIGroundWaterAbstractionDepth = 100446
    eumIEvaporationIntesity = 100447
    eumILongitudinalInfiltration = 100448
    eumIPollutantLoad = 100449
    eumIPressure = 100450
    eumICostPerTime = 100451
    eumIMass = 100452
    eumIMassPerTime = 100453
    eumIMassPerAreaPerTime = 100454
    eumIKd = 100455
    eumIPorosity = 100456
    eumIHalfLife = 100457
    eumIDispersivity = 100458
    eumIFrictionCoeffientcfw = 100459
    eumIWaveamplitude = 100460
    eumISedimentGrainDiameter = 100461
    eumISedimentSpill = 100463
    eumINumberOfParticles = 100464
    eumIEllipsoidalHeight = 100500
    eumICloudiness = 100501
    eumIProbability = 100502
    eumIDispersantActivity = 100503
    eumIDredgeRate = 100504
    eumIDredgeSpill = 100505
    eumIClearnessCoefficient = 100506
    eumIProfileOrientation = 100507
    eumIReductionFactor = 100508
    eumIActiveBeachHeight = 100509
    eumIUpdatePeriod = 100510
    eumIAccumulatedErosion = 100511
    eumIErosionRate = 100512
    eumINonDimTransport = 100513
    eumILocalCoordinate = 100514
    eumIRadiiOfGyration = 100515
    eumIPercentage = 100516
    eumILineCapacity = 100517
    eumIDiverteddischarge = 110001
    eumIDemandcarryoverfraction = 110002
    eumIGroundwaterdemand = 110003
    eumIDamcrestlevel = 110004
    eumISeepageflux = 110005
    eumISeepagefraction = 110006
    eumIEvaporationfraction = 110007
    eumIResidencetime = 110008
    eumIOwnedfractionofinflow = 110009
    eumIOwnedfractionofvolume = 110010
    eumIReductionlevel = 110011
    eumIReductionthreshold = 110012
    eumIReductionfraction = 110013
    eumITotalLosses = 110014
    eumICountsPerLiter = 110015
    eumIAssimilativeCapacity = 110016
    eumIStillWaterDepth = 110017
    eumITotalWaterDepth = 110018
    eumIMaxWaveHeight = 110019
    eumIIceConcentration = 110020
    eumIWindFrictionSpeed = 110021
    eumIRoughnessLength = 110022
    eumIWindDragCoefficient = 110023
    eumICharnockConstant = 110024
    eumIBreakingParameterGamma = 110025
    eumIThresholdPeriod = 110026
    eumICourantNumber = 110027
    eumITimeStepFactor = 110028
    eumIElementLength = 110029
    eumIElementArea = 110030
    eumIRollerAngle = 110031
    eumIRateBedLevelChange = 110032
    eumIBedLevelChange = 110033
    eumISedimentTransportDirection = 110034
    eumIWaveActionDensity = 110035
    eumIZeroMomentWaveAction = 110036
    eumIFirstMomentWaveAction = 110037
    eumIBedMass = 110038
    eumIEPANETWaterQuality = 110039
    eumIEPANETStatus = 110040
    eumIEPANETSetting = 110041
    eumIEPANETReactionRate = 110042
    eumIFRDischarge = 110043
    eumISRDischarge = 110044
    eumIAveSediTransportPerLengthUnit = 110045
    eumIValveSetting = 110046
    eumIWaveEnergyDensity = 110047
    eumIWaveEnergyDistribution = 110048
    eumIWaveEnergy = 110049
    eumIRadiationMeltingCoefficient = 110050
    eumIRainMeltingCoefficientPerDegree = 110051
    eumIEPANETFriction = 110052
    eumIWaveActionDensityRate = 110053
    eumIElementAreaLongLat = 110054
    eumIElectricCurrent = 110100
    eumIHeatFluxResistance = 110200
    eumIAbsoluteHumidity = 110210
    eumILength = 110220
    eumIArea = 110225
    eumIVolume = 110230
    eumIElementVolume = 110231
    eumIWavePower = 110232
    eumIMomentOfInertia = 110233
    eumITopography = 110234
    eumIScourDepth = 110235
    eumIScourWidth = 110236
    eumICostPerVolume = 110237
    eumICostPerEnergy = 110238
    eumICostPerMass = 110239
    eumIApplicationIntensity = 110240
    eumICost = 110241
    eumIVoltage = 110242
    eumINormalVelocity = 110243
    eumIGravity = 110244
    eumIVesselDisplacement = 110245
    eumIHydrostaticMatrix = 110246
    eumIWaveNumber = 110247
    eumIRadiationPotential = 110248
    eumIAddedMassTT = 110249
    eumIRadiationDamping = 110250
    eumIFrequency = 110251
    eumISoundExposureLevel = 110252
    eumITransmissionLoss = 110253
    eumIpH = 110254
    eumIAcousticAttenuation = 110255
    eumISoundSpeed = 110256
    eumILeakage = 110257
    eumIHeightAboveKeel = 110258
    eumISubmergedMass = 110259
    eumIDeflection = 110260
    eumILinearDampingCoefficient = 110261
    eumIQuadraticDampingCoefficient = 110262
    eumIDampingTT = 110263
    eumIRAOmotion = 110264
    eumIRAOrotation = 110265
    eumIAddedMassCoefficient = 110266
    eumIElectricConductivity = 110267
    eumIAddedMassTR = 110268
    eumIAddedMassRT = 110269
    eumIAddedMassRR = 110270
    eumIDampingTR = 110271
    eumIDampingRT = 110272
    eumIDampingRR = 110273
    eumIFenderForce = 110274
    eumIForce = 110275
    eumIMoment = 110276
    eumIReducedPollutantLoad = 110277
    eumISizeAndPosition = 110278
    eumIFrameRate = 110279
    eumIDynamicViscosity = 110280
    eumIGridRotation = 110281
    eumIAgentDensity = 110282
    eumIEmitterCoefficient = 110283
    eumIPipeDiameter = 110284
    eumISpeed = 110285
    eumIVelocity = 110286
    eumIDirection = 110287
    eumIDisplacement = 110288
    eumIPosition = 110289
    eumIRotation = 110290
    eumITorque = 110291
    eumIOvertopping = 110292
    eumIFlowRate = 110293
    eumIAcceleration = 110294
    eumIDimensionlessAcceleration = 110295
    eumITime = 110296
    eumIResistance = 110297
    eumIAmountOfSubstance = 110298
    eumIMolarConcentration = 110299
    eumIMolalConcentration = 110300
    eumISuspSedimentLoadPerArea = 110301
    eumIBollardForce = 110302
    eumIDischargePerPressure = 110303
    eumIRotationalSpeed = 110304
    eumIInfiltrationPerArea = 110305
    eumIMassPerLengthPerTime = 110306
    eumINearBedLoadPerLength = 110307
    eumISubstancePerUnitArea = 110308
    eumIAccNearBedLoadPerLength =     110309

# Predefined enums of EUM units.
#
# Must be updated with every new release, or if the EUM.xml is updated
class eumUnit(IntEnum):
    eumUUnitUndefined = 0
    eumUmeter = 1000
    eumUkilometer = 1001
    eumUmillimeter = 1002
    eumUfeet = 1003
    eumUinch = 1004
    eumUmile = 1005
    eumUyard = 1006
    eumUcentimeter = 1007
    eumUmicrometer = 1008
    eumUnauticalmile = 1009
    eumUmillifeet = 1010
    eumULiterPerM2 = 1011
    eumUMilliMeterD50 = 1012
    eumUinchUS = 1013
    eumUfeetUS = 1014
    eumUyardUS = 1015
    eumUmileUS = 1016
    eumUkilogram = 1200
    eumUgram = 1201
    eumUmilligram = 1202
    eumUmicrogram = 1203
    eumUton = 1204
    eumUkiloton = 1205
    eumUmegaton = 1206
    eumUPound = 1207
    eumUtonUS = 1208
    eumUounce = 1209
    eumUperKilogram = 1250
    eumUperGram = 1251
    eumUperMilligram = 1252
    eumUperMicrogram = 1253
    eumUperTon = 1254
    eumUperKiloton = 1255
    eumUperMegaton = 1256
    eumUperPound = 1257
    eumUperTonUS = 1258
    eumUperOunce = 1259
    eumUsec = 1400
    eumUminute = 1401
    eumUhour = 1402
    eumUday = 1403
    eumUyear = 1404
    eumUmonth = 1405
    eumUmillisec = 1406
    eumUm3 = 1600
    eumUliter = 1601
    eumUmilliliter = 1602
    eumUft3 = 1603
    eumUgal = 1604
    eumUmgal = 1605
    eumUkm3 = 1606
    eumUacft = 1607
    eumUMegaGal = 1608
    eumUMegaLiter = 1609
    eumUTenTo6m3 = 1610
    eumUm3PerCurrency = 1611
    eumUgalUK = 1612
    eumUMegagalUK = 1613
    eumUydUS3 = 1614
    eumUYard3 = 1615
    eumUm3PerSec = 1800
    eumUft3PerSec = 1801
    eumUMlPerDay = 1802
    eumUMgalPerDay = 1803
    eumUacftPerDay = 1804
    eumUm3PerYear = 1805
    eumUGalPerDayPerHead = 1806
    eumULiterPerDayPerHead = 1807
    eumUm3PerSecPerHead = 1808
    eumUliterPerPersonPerDay = 1809
    eumUm3PerDay = 1810
    eumUGalPerSec = 1811
    eumUGalPerDay = 1812
    eumUGalPerYear = 1813
    eumUft3PerDay = 1814
    eumUft3PerYear = 1815
    eumUm3PerMinute = 1816
    eumUft3PerMin = 1817
    eumUGalPerMin = 1818
    eumUliterPerSec = 1819
    eumUliterPerMin = 1820
    eumUm3PerHour = 1821
    eumUgalUKPerDay = 1822
    eumUMgalUKPerDay = 1823
    eumUft3PerDayPerHead = 1824
    eumUm3PerDayPerHead = 1825
    eumUGalUKPerSec = 1826
    eumUGalUKPerYear = 1827
    eumUGalUKPerDayPerHead = 1828
    eumUydUS3PerSec = 1829
    eumUyard3PerSec = 1830
    eumUftUS3PerSec = 1831
    eumUftUS3PerMin = 1832
    eumUftUS3PerDay = 1833
    eumUftUS3PerYear = 1834
    eumUyardUS3PerSec = 1835
    eumUliterPerDay = 1836
    eumUmeterPerSec = 2000
    eumUmillimeterPerHour = 2001
    eumUfeetPerSec = 2002
    eumUliterPerSecPerKm2 = 2003
    eumUmillimeterPerDay = 2004
    eumUacftPerSecPerAcre = 2005
    eumUmeterPerDay = 2006
    eumUft3PerSecPerMi2 = 2007
    eumUmeterPerHour = 2008
    eumUfeetPerDay = 2009
    eumUmillimeterPerMonth = 2010
    eumUinchPerSec = 2011
    eumUmeterPerMinute = 2012
    eumUfeetPerMinute = 2013
    eumUinchPerMinute = 2014
    eumUfeetPerHour = 2015
    eumUinchPerHour = 2016
    eumUmillimeterPerSecond = 2017
    eumUcmPerHour = 2018
    eumUknot = 2019
    eumUmilePerHour = 2020
    eumUkilometerPerHour = 2021
    eumUAcreFeetPerDayPerAcre = 2022
    eumUCentiMeterPerSecond = 2023
    eumUCubicFeetPerSecondPerAcre = 2024
    eumUCubicMeterPerDayPerHectar = 2025
    eumUCubicMeterPerHourPerHectar = 2026
    eumUCubicMeterPerSecondPerHectar = 2027
    eumUGallonPerMinutePerAcre = 2028
    eumULiterPerMinutePerHectar = 2029
    eumULiterPerSecondPerHectar = 2030
    eumUMicroMeterPerSecond = 2031
    eumUMillionGalPerDayPerAcre = 2032
    eumUMillionGalUKPerDayPerAcre = 2033
    eumUMillionLiterPerDayPerHectar = 2034
    eumUinchUSPerSecond = 2035
    eumUfeetUSPerSecond = 2036
    eumUfeetUSPerDay = 2037
    eumUinchUSPerHour = 2038
    eumUinchUSPerMinute = 2039
    eumUmillimeterPerYear = 2040
    eumUCubicFeetPerHourPerAcre = 2041
    eumUCubicFeetPerDayPerAcre = 2042
    eumULiterPerHourPerHectar = 2043
    eumULiterPerDayPerHectar = 2044
    eumUMeterPerSecondPerSecond = 2100
    eumUFeetPerSecondPerSecond = 2101
    eumUkiloGramPerM3 = 2200
    eumUmicroGramPerM3 = 2201
    eumUmilliGramPerM3 = 2202
    eumUgramPerM3 = 2203
    eumUmicroGramPerL = 2204
    eumUmilliGramPerL = 2205
    eumUgramPerL = 2206
    eumUPoundPerCubicFeet = 2207
    eumUtonPerM3 = 2208
    eumUPoundPerSquareFeet = 2209
    eumUtonPerM2 = 2210
    eumUmicroGramPerM2 = 2211
    eumUPoundPerydUS3 = 2212
    eumUPoundPeryard3 = 2213
    eumUPoundPerCubicFeetUS = 2214
    eumUPoundPerSquareFeetUS = 2215
    eumUouncePerCubicFeet = 2216
    eumUouncePerCubicFeetUS = 2217
    eumUouncePerYard3 = 2218
    eumUouncePerYardUS3 = 2219
    eumUouncePerSquareFeet = 2220
    eumUouncePerSquareFeetUS = 2221
    eumUKiloGramPerMeterPerSecond = 2300
    eumUPascalSecond = 2301
    eumUkilogramPerMeterPerDay = 2302
    eumUgramPerMeterPerDay = 2303
    eumUgramPerKmPerDay = 2304
    eumUpoundPerFeetPerDay = 2305
    eumUpoundPerFeetUSPerDay = 2306
    eumUouncePerFeetPerDay = 2307
    eumUouncePerFeetUSPerDay = 2308
    eumUkilogramPerYardPerSecond = 2309
    eumUkilogramPerFeetPerSecond = 2310
    eumUpoundPerYardPerSecond = 2311
    eumUpoundPerFeetPerSecond = 2312
    eumUradian = 2400
    eumUdegree = 2401
    eumUDegreeNorth50 = 2402
    eumUdegreesquared = 2403
    eumUdegreePerMeter = 2500
    eumUradianPerMeter = 2501
    eumUdegreePerSecond = 2510
    eumUradianPerSecond = 2511
    eumUperDay = 2600
    eumUpercentPerDay = 2601
    eumUhertz = 2602
    eumUperHour = 2603
    eumUcurrencyPerYear = 2604
    eumUperSec = 2605
    eumUbillionPerDay = 2606
    eumUtrillionPerYear = 2607
    eumUSquareMeterPerSecondPerHectar = 2608
    eumUSquareFeetPerSecondPerAcre = 2609
    eumURevolutionPerMinute = 2610
    eumUpercentPerHour = 2611
    eumUpercentPerMinute = 2612
    eumUpercentPerSecond = 2613
    eumURevolutionPerSecond = 2614
    eumURevolutionPerHour = 2615
    eumUdegreeCelsius = 2800
    eumUdegreeFahrenheit = 2801
    eumUdegreeKelvin = 2802
    eumUperDegreeCelsius = 2850
    eumUperDegreeFahrenheit = 2851
    eumUdeltaDegreeCelsius = 2900
    eumUdeltaDegreeFahrenheit = 2901
    eumUmillPer100ml = 3000
    eumUPer100ml = 3001
    eumUperLiter = 3002
    eumUperM3 = 3003
    eumUperMilliliter = 3004
    eumUperFt3 = 3005
    eumUperGallon = 3006
    eumUperMilligallon = 3007
    eumUperKm3 = 3008
    eumUperAcft = 3009
    eumUperMegagallon = 3010
    eumUperMegaliter = 3011
    eumUperGallonUK = 3012
    eumUperMegagallonUK = 3013
    eumUperYardUS3 = 3014
    eumUperYard3 = 3015
    eumUSecPerMeter = 3100
    eumUm2 = 3200
    eumUm3PerM = 3201
    eumUacre = 3202
    eumUft2 = 3203
    eumUha = 3204
    eumUkm2 = 3205
    eumUmi2 = 3206
    eumUft3PerFt = 3207
    eumUftUS2 = 3208
    eumUydUS2 = 3209
    eumUmiUS2 = 3210
    eumUacreUS = 3211
    eumUydUS3PeryardUS = 3212
    eumUYard3PerYard = 3213
    eumUftUS3PerftUS = 3214
    eumUliterPerMeter = 3215
    eumUEPerM2PerDay = 3400
    eumUThousandPerM2PerDay = 3401
    eumUPerM2PerSec = 3402
    eumUMeter2One3rdPerSec = 3600
    eumUFeet2One3rdPerSec = 3601
    eumUSecPerMeter2One3rd = 3800
    eumUSecPerFeet2One3rd = 3801
    eumUMeter2OneHalfPerSec = 4000
    eumUFeet2OneHalfPerSec = 4001
    eumUFeetUS2OneHalfPerSec = 4002
    eumUkilogramPerSec = 4200
    eumUmicrogramPerSec = 4201
    eumUmilligramPerSec = 4202
    eumUgramPerSec = 4203
    eumUkilogramPerHour = 4204
    eumUkilogramPerDay = 4205
    eumUgramPerDay = 4206
    eumUkilogramPerYear = 4207
    eumUGramPerMinute = 4208
    eumUKiloGramPerPersonPerDay = 4209
    eumUKilogramPerMinute = 4210
    eumUPoundPerDay = 4212
    eumUPoundPerHour = 4213
    eumUPoundPerMinute = 4214
    eumUPoundPerSecond = 4215
    eumUPoundPerPersonPerDay = 4216
    eumUPoundPerYear = 4217
    eumUTonPerYear = 4218
    eumUTonPerDay = 4219
    eumUTonPerSec = 4220
    eumUgramPerM2 = 4400
    eumUkilogramPerM = 4401
    eumUkilogramPerM2 = 4402
    eumUkilogramPerHa = 4403
    eumUmilligramPerM2 = 4404
    eumUPoundPerAcre = 4405
    eumUkilogramPerKm2 = 4406
    eumUtonPerKm2 = 4407
    eumUgramPerKm2 = 4408
    eumUtonPerHa = 4409
    eumUgramPerHa = 4410
    eumUPoundPerMi2 = 4411
    eumUkilogramPerAcre = 4412
    eumUkilogramPerSquareFeet = 4413
    eumUkilogramPerMi2 = 4414
    eumUtonPerAcre = 4415
    eumUtonPerSquareFeet = 4416
    eumUtonPerMi2 = 4417
    eumUgramPerAcre = 4418
    eumUgramPerSquareFeet = 4419
    eumUgramPerMi2 = 4420
    eumUPoundPerHa = 4421
    eumUPoundPerM2 = 4422
    eumUPoundPerKm2 = 4423
    eumUmilligramPerHa = 4424
    eumUmilligramPerKm2 = 4425
    eumUmilligramPerAcre = 4426
    eumUmilligramPerSquareFeet = 4427
    eumUmilligramPerMi2 = 4428
    eumUPoundPerMeter = 4429
    eumUtonPerMeter = 4430
    eumUpoundPerFeet = 4431
    eumUpoundPerYard = 4432
    eumUpoundPerFeetUS = 4433
    eumUpoundPerYardUS = 4434
    eumUouncePerFeet = 4435
    eumUouncePerYard = 4436
    eumUouncePerFeetUS = 4437
    eumUouncePerYardUS = 4438
    eumUkilogramPerYard = 4439
    eumUkilogramPerFeet = 4440
    eumUgramPerM2PerDay = 4500
    eumUgramPerM2PerSec = 4501
    eumUkilogramPerHaPerHour = 4502
    eumUkilogramPerM2PerSec = 4503
    eumUKiloGramPerHectarPerDay = 4504
    eumUPoundPerAcrePerDay = 4505
    eumUkilogramPerM2PerDay = 4506
    eumUPoundPerFt2PerSec = 4507
    eumUgramPerM3PerHour = 4600
    eumUgramPerM3PerDay = 4601
    eumUgramPerM3PerSec = 4602
    eumUMilliGramPerLiterPerDay = 4603
    eumUm3PerSecPerM = 4700
    eumUm3PerYearPerM = 4701
    eumUm2PerSec = 4702
    eumUft2PerSec = 4704
    eumUm3PerSecPer10mm = 4706
    eumUft3PerSecPerInch = 4707
    eumUm2PerHour = 4708
    eumUm2PerDay = 4709
    eumUft2PerHour = 4710
    eumUft2PerDay = 4711
    eumUGalUKPerDayPerFeet = 4712
    eumUGalPerDayPerFeet = 4713
    eumUGalPerMinutePerFeet = 4714
    eumULiterPerDayPerMeter = 4715
    eumULiterPerMinutePerMeter = 4716
    eumULiterPerSecondPerMeter = 4717
    eumUft3PerSecPerFt = 4718
    eumUft3PerHourPerFt = 4719
    eumUft2PerSec2 = 4720
    eumUcm3PerSecPerCm = 4721
    eumUmm3PerSecPerMm = 4722
    eumUftUS3PerSecPerFtUS = 4723
    eumUin3PerSecPerIn = 4724
    eumUinUS3PerSecPerInUS = 4725
    eumUydUS3PerSecPerydUS = 4726
    eumUyard3PerSecPeryard = 4727
    eumUyard3PerYearPeryard = 4728
    eumUydUS3PerYearPerydUS = 4729
    eumUm3PerHourPerM = 4730
    eumUm3PerDayPerM = 4731
    eumUft3PerDayPerFt = 4732
    eumUmmPerDay = 4801
    eumUinPerDay = 4802
    eumUm3PerKm2PerDay = 4803
    eumUwatt = 4900
    eumUkwatt = 4901
    eumUmwatt = 4902
    eumUgwatt = 4903
    eumUHorsePower = 4904
    eumUperMeter = 5000
    eumUpercentPer100meter = 5001
    eumUpercentPer100feet = 5002
    eumUperFeet = 5003
    eumUperInch = 5004
    eumUperFeetUS = 5005
    eumUperInchUS = 5006
    eumUm3PerS2 = 5100
    eumUm2SecPerRad = 5200
    eumUm2PerRad = 5201
    eumUm2Sec = 5202
    eumUm2PerDegree = 5203
    eumUm2Sec2PerRad = 5204
    eumUm2PerSecPerRad = 5205
    eumUm2SecPerDegree = 5206
    eumUm2Sec2PerDegree = 5207
    eumUm2PerSecPerDegree = 5208
    eumUft2PerSecPerRad = 5209
    eumUft2PerSecPerDegree = 5210
    eumUft2Sec2PerRad = 5211
    eumUft2Sec2PerDegree = 5212
    eumUft2SecPerRad = 5213
    eumUft2SecPerDegree = 5214
    eumUft2PerRad = 5215
    eumUft2PerDegree = 5216
    eumUft2Sec = 5217
    eumUmilliGramPerL2OneHalfPerDay = 5300
    eumUmilliGramPerL2OneHalfPerHour = 5301
    eumUNewtonPerSqrMeter = 5400
    eumUkiloNewtonPerSqrMeter = 5401
    eumUPoundPerFeetPerSec2 = 5402
    eumUNewtonPerM3 = 5500
    eumUkiloNewtonPerM3 = 5501
    eumUkilogramM2 = 5550
    eumUPoundSqrFeet = 5551
    eumUJoule = 5600
    eumUkiloJoule = 5601
    eumUmegaJoule = 5602
    eumUgigaJoule = 5603
    eumUteraJoule = 5604
    eumUKiloWattHour = 5605
    eumUWattSecond = 5606
    eumUpetaJoule = 5607
    eumUexaJoule = 5608
    eumUmegaWattHour = 5609
    eumUgigaWattHour = 5610
    eumUperJoule = 5650
    eumUperKiloJoule = 5651
    eumUperMegaJoule = 5652
    eumUperGigaJoule = 5653
    eumUperTeraJoule = 5654
    eumUperPetaJoule = 5655
    eumUperExaJoule = 5656
    eumUperKiloWattHour = 5657
    eumUperWattSecond = 5658
    eumUperMegaWattHour = 5659
    eumUperGigaWattHour = 5660
    eumUkiloJoulePerM2PerHour = 5700
    eumUkiloJoulePerM2PerDay = 5701
    eumUmegaJoulePerM2PerDay = 5702
    eumUJoulePerM2PerDay = 5703
    eumUm2mmPerKiloJoule = 5710
    eumUm2mmPerMegaJoule = 5711
    eumUMilliMeterPerDegreeCelsiusPerDay = 5800
    eumUMilliMeterPerDegreeCelsiusPerHour = 5801
    eumUInchPerDegreeFahrenheitPerDay = 5802
    eumUInchPerDegreeFahrenheitPerHour = 5803
    eumUPerDegreeCelsiusPerDay = 5900
    eumUPerDegreeCelsiusPerHour = 5901
    eumUPerDegreeFahrenheitPerDay = 5902
    eumUPerDegreeFahrenheitPerHour = 5903
    eumUDegreeCelsiusPer100meter = 6000
    eumUDegreeCelsiusPer100feet = 6001
    eumUDegreeFahrenheitPer100meter = 6002
    eumUDegreeFahrenheitPer100feet = 6003
    eumUPascal = 6100
    eumUhectoPascal = 6101
    eumUkiloPascal = 6102
    eumUpsi = 6103
    eumUMegaPascal = 6104
    eumUMetresOfWater = 6105
    eumUFeetOfWater = 6106
    eumUBar = 6107
    eumUmilliBar = 6108
    eumUmicroPascal = 6109
    eumUdeciBar = 6110
    eumUdB_re_1muPa2second = 6150
    eumUdBperLambda = 6160
    eumUPSU = 6200
    eumUPSUM3PerSec = 6300
    eumUDegreeCelsiusM3PerSec = 6301
    eumUConcNonDimM3PerSec = 6302
    eumUPSUft3PerSec = 6303
    eumUDegreeFahrenheitFt3PerSec = 6304
    eumUm2PerSec2 = 6400
    eumUm2PerSec3 = 6401
    eumUft2PerSec3 = 6402
    eumUm2PerSec3PerRad = 6403
    eumUft2PerSec3PerRad = 6404
    eumUJoulePerKilogram = 6500
    eumUWattPerM2 = 6600
    eumUJouleKilogramPerKelvin = 6700
    eumUm3PerSec2 = 6800
    eumUft3PerSec2 = 6801
    eumUAcreFeetPerDayPerSecond = 6802
    eumUMillionGalUKPerDayPerSecond = 6803
    eumUMillionGalPerDayPerSecond = 6804
    eumUGalPerMinutePerSecond = 6805
    eumUCubicMeterPerDayPerSecond = 6806
    eumUCubicMeterPerHourPerSecond = 6807
    eumUMillionLiterPerDayPerSecond = 6808
    eumULiterPerMinutePerSecond = 6809
    eumULiterPerSecondSquare = 6810
    eumUm3Pergram = 6900
    eumULiterPergram = 6901
    eumUm3PerMilligram = 6902
    eumUm3PerMicrogram = 6903
    eumUNewton = 7000
    eumUkiloNewton = 7001
    eumUmegaNewton = 7002
    eumUmilliNewton = 7003
    eumUkilogramMeter = 7050
    eumUkilogramMeter2 = 7060
    eumUkilogramMeterPerSecond = 7070
    eumUkilogramMeter2PerSecond = 7080
    eumUm2PerHertz = 7100
    eumUm2PerHertzPerDegree = 7101
    eumUm2PerHertzPerRadian = 7102
    eumUft2PerHertz = 7103
    eumUft2PerHertzPerDegree = 7104
    eumUft2PerHertzPerRadian = 7105
    eumUm2PerHertz2 = 7200
    eumUm2PerHertz2PerDegree = 7201
    eumUm2PerHertz2PerRadian = 7202
    eumUliterPerSecPerMeter = 7500
    eumUliterPerMinPerMeter = 7501
    eumUMegaLiterPerDayPerMeter = 7502
    eumUm3PerHourPerMeter = 7503
    eumUm3PerDayPerMeter = 7504
    eumUft3PerSecPerPsi = 7505
    eumUgallonPerMinPerPsi = 7506
    eumUMgalPerDayPerPsi = 7507
    eumUMgalUKPerDayPerPsi = 7508
    eumUacftPerDayPerPsi = 7509
    eumUm3PerHourPerBar = 7510
    eumUKilogramPerS2 = 8100
    eumUm2Perkilogram = 9100
    eumUPerMeterPerSecond = 9200
    eumUMeterPerSecondPerHectar = 9201
    eumUFeetPerSecondPerAcre = 9202
    eumUPerSquareMeter = 9300
    eumUPerAcre = 9301
    eumUPerHectar = 9302
    eumUperKm2 = 9303
    eumUPerCubicMeter = 9350
    eumUCurrencyPerCubicMeter = 9351
    eumUCurrencyPerCubicFeet = 9352
    eumUSquareMeterPerSecond = 9400
    eumUSquareFeetPerSecond = 9401
    eumUPerWatt = 9600
    eumUNewtonMeter = 9700
    eumUkiloNewtonMeter = 9701
    eumUmegaNewtonMeter = 9702
    eumUNewtonMillimeter = 9703
    eumUNewtonMeterSecond = 9800
    eumUNewtonPerMeterPerSecond = 9900
    eumUmole = 12000
    eumUmillimole = 12001
    eumUmicromole = 12002
    eumUnanomole = 12003
    eumUmolePerLiter = 12020
    eumUmillimolePerLiter = 12021
    eumUmicromolePerLiter = 12022
    eumUnanomolePerLiter = 12023
    eumUmolePerM3 = 12024
    eumUmillimolePerM3 = 12025
    eumUmicromolePerM3 = 12026
    eumUmolePerKilogram = 12040
    eumUmillimolePerKilogram = 12041
    eumUmicromolePerKilogram = 12042
    eumUnanomolePerKilogram = 12043
    eumUmolePerM2 = 12060
    eumUmillimolePerM2 = 12061
    eumUmicromolePerM2 = 12062
    eumUnanomolePerM2 = 12063
    eumUOnePerOne = 99000
    eumUPerCent = 99001
    eumUPerThousand = 99002
    eumUHoursPerDay = 99003
    eumUPerson = 99004
    eumUGramPerGram = 99005
    eumUGramPerKilogram = 99006
    eumUMilligramPerGram = 99007
    eumUMilligramPerKilogram = 99008
    eumUMicrogramPerGram = 99009
    eumUKilogramPerKilogram = 99010
    eumUM3PerM3 = 99011
    eumULiterPerM3 = 99012
    eumUintCode = 99013
    eumUMeterPerMeter = 99014
    eumUperminute = 99015
    eumUpermonth = 99016
    eumUperyear = 99017
    eumUMilliliterPerLiter = 99018
    eumUMicroliterPerLiter = 99019
    eumUPerMillion = 99020
    eumUgAcceleration = 99021
    eumUampere = 99100
    eumUMilliAmpere = 99101
    eumUmicroAmpere = 99102
    eumUkiloAmpere = 99103
    eumUmegaAmpere = 99104
    eumUvolt = 99150
    eumUmilliVolt = 99151
    eumUmicroVolt = 99152
    eumUkiloVolt = 99153
    eumUmegaVolt = 99154
    eumUohm = 99180
    eumUkiloOhm = 99181
    eumUmegaOhm = 99182
    eumUWattPerMeter = 99200
    eumUkiloWattPerMeter = 99201
    eumUmegaWattPerMeter = 99202
    eumUgigaWattPerMeter = 99203
    eumUkiloWattPerFeet = 99204
    eumUsiemens = 99250
    eumUmilliSiemens = 99251
    eumUmicroSiemens = 99252
    eumUsiemensPerMeter = 99260
    eumUmilliSiemensPerCentimeter = 99261
    eumUmicroSiemensPerCentimeter = 99262
    eumUkilogramPerSecPerM = 99263
    eumUCentipoise = 99264
    eumUPoundforceSecPerSqrFt = 99265
    eumUPoundFeetPerSec = 99266

  #/ <summary>
  #/ Dimension base enum, specifying the order of the dimension powers 
  #/ from the <see cref="eumUtil.Parameters"/> methods and the 
  #/ <see cref="EUMWrapper.eumUnitGetParameters"/> method.
  #/ </summary>
class eumDimensionBase(IntEnum):
    #/ <summary>
    #/ Length dimension; index 0
    #/ </summary>
    Length = 0;
    #/ <summary>
    #/ Mass dimension; index 1
    #/ </summary>
    Mass = 1;
    #/ <summary>
    #/ Time dimension; index 2
    #/ </summary>
    Time = 2;
    #/ <summary>
    #/ Temperature dimension; index 3
    #/ </summary>
    Temperature = 3;
    #/ <summary>
    #/ Electric current dimension; index 4
    #/ </summary>
    ElectricCurrent = 4;
    #/ <summary>
    #/ Amount of substance dimension; index 5
    #/ </summary>
    AmountOfSubstance = 5;
    #/ <summary>
    #/ Luminous intensity dimension; index 6
    #/ </summary>
    LuminousIntensity = 6


class eumQuantity:

    __undefined = None

    def __init__(self, item = eumItem.eumIItemUndefined, unit = eumUnit.eumUUnitUndefined):
        self.Item = item;
        self.ItemInt = item;
        self.Unit = unit;
        self.UnitInt = unit;

    def __repr__(self):
        return "{item}-{unit}".format(item=self.Item, unit=self.Unit)

    @staticmethod
    def Create(item, unit):
        return eumQuantity(item, unit)

    @staticmethod
    def UnDefined():
        if None == eumQuantity.__undefined:
            eumQuantity.__undefined = eumQuantity()
        return eumQuantity.__undefined


#/ <summary>
#/ Helper class for unit conversion without or without unit equivalent checking
#/ </summary>
class UnitConverter:
      #/ <summary>
      #/ Initilize the unit converter by checking the unit equivalent
      #/ </summary>
      #/ <param name="nUnitFrom"></param>
      #/ <param name="nUnitTo"></param>
      def __init__(self, unitFrom: eumUnit, unitTo: eumUnit, equivalentUnits: bool = True):
        self.dFactorFwd = 1;   # Forward conversion factor  - 1 by default
        self.dOffsetFwd = 0;   # Forward conversion offset  - 0 by default
        self.dFactorBck = 1;   # Backward conversion factor - 1 by default
        self.dOffsetBck = 0;   # Backward conversion offset - 0 by default
        if ((not equivalentUnits) or eumWrapper.eumUnitsEqv(unitFrom, unitTo)):
          dFactorFrom, dOffsetFrom = eumWrapper.eumUnitGetSIFactor(unitFrom);
          dFactorTo,   dOffsetTo   = eumWrapper.eumUnitGetSIFactor(unitTo);

          self.dFactorFwd = dFactorFrom/dFactorTo;
          self.dOffsetFwd = (dOffsetFrom - dOffsetTo)/dFactorTo;
          self.dFactorBck = dFactorTo/dFactorFrom;
          self.dOffsetBck = (dOffsetTo - dOffsetFrom)/dFactorFrom;
        else:
          raise Exception("Units are not equivalent")

      #/ <summary>
      #/ Convert from fromUnit to toUnit
      #/ </summary>
      #/ <param name="val"></param>
      #/ <returns></returns>
      def Convert(self, val: float) -> float:
          return self.dFactorFwd * val + self.dOffsetFwd;

      #/ <summary>
      #/ Convert data set from fromUnit to toUnit
      #/ </summary>
      #/ <param name="pData"></param>
      #/ <param name="dDeleteValue"></param>
      def ConvertArray(self, pData: np.ndarray, dDeleteValue: float = None):
          if (dDeleteValue is None):
              for i in range(pData.size):
                  pData[i] = self.Convert(pData[i]);
          else:
              for i in range(pData.size):
                  if (dDeleteValue != pData[i]):
                      pData[i] = self.Convert(pData[i]);

      #/ <summary>
      #/ Convert from toUnit to fromUnit
      #/ </summary>
      #/ <param name="val"></param>
      #/ <returns></returns>
      def InvConvert(self, val: float) -> float:
          return self.dFactorBck * val + self.dOffsetBck;

      #/ <summary>
      #/ Convert set data from toUnit to fromUnit
      #/ </summary>
      #/ <param name="pData"></param>
      #/ <param name="dDeleteValue"></param>
      def InvConvertArray(self, pData: np.ndarray, dDeleteValue: float = None):
          if (dDeleteValue is None):
              for i in range(pData.size):
                  pData[i] = self.InvConvert(pData[i]);
          else:
              for i in range(pData.size):
                  if (dDeleteValue != pData[i]):
                      pData[i] = self.InvConvert(pData[i]);






class eumDLL(object):
    """description of class"""

    # Static variables
    Wrapper = None
    # Leaving out extension should make it work for both Windows and Linux
    libfilename = "libeum.so"
    # libfilename = "eum";
    libfilepath = None

    #def __init__(self):
        # init()

    @staticmethod
    def Init(libfilepath=None, libfilename=None):

        if not libfilepath is None:
            eumDLL.libfilepath = libfilepath
        if not libfilename is None:
            eumDLL.libfilename = libfilename

        # eum lib should be loaded only once
        if eumDLL.Wrapper is None:
            # TODO: Is there a smarter way to have the eum library loaded (especially when xcopy-deployed)
            if os.name == "nt":
                eumDLL.Wrapper = ctypes.CDLL(os.path.join(eumDLL.libfilepath, "eum"))
            else:
                eumDLL.Wrapper = ctypes.CDLL(os.path.join(eumDLL.libfilepath, "libeum.so"))

                eumDLL.Wrapper.eumSetupLoadLinux.argtypes = [ctypes.c_char_p]
                # TODO: Should this not be simpler?
                eumFilePath = eumDLL.libfilepath + "/EUM.xml"
                eumFilePathP = ctypes.c_char_p(eumFilePath.encode("ascii"))
                res = eumDLL.Wrapper.eumSetupLoadLinux(eumFilePathP);

            eumDLL.Wrapper.eumUnitGetParameters.argtypes = [ctypes.c_int32, 
                                                            ctypes.POINTER(ctypes.c_double), 
                                                            ctypes.POINTER(ctypes.c_double), 
                                                            ctypes.c_void_p, ctypes.c_void_p]
            eumDLL.Wrapper.eumConvertItemArrayD.argtypes = [ctypes.c_int32, 
                                                            ctypes.c_int32, 
                                                            ctypes.c_void_p, 
                                                            ctypes.c_int32, 
                                                            ctypes.c_double]
            eumDLL.Wrapper.eumConvertItemArrayF.argtypes = [ctypes.c_int32, 
                                                            ctypes.c_int32, 
                                                            ctypes.c_void_p, 
                                                            ctypes.c_int32, 
                                                            ctypes.c_float]
            eumDLL.Wrapper.eumConvertItemArrayToUserUnitD.argtypes = [ctypes.c_int32, 
                                                                      ctypes.c_int32, 
                                                                      ctypes.c_void_p, 
                                                                      ctypes.c_int32, 
                                                                      ctypes.c_double]
            eumDLL.Wrapper.eumConvertItemArrayToUserUnitF.argtypes = [ctypes.c_int32, 
                                                                      ctypes.c_int32, 
                                                                      ctypes.c_void_p, 
                                                                      ctypes.c_int32, 
                                                                      ctypes.c_float]
            eumDLL.Wrapper.eumConvertItemArrayFromUserUnitD.argtypes = [ctypes.c_int32, 
                                                                        ctypes.c_int32, 
                                                                        ctypes.c_void_p, 
                                                                        ctypes.c_int32, 
                                                                        ctypes.c_double]
            eumDLL.Wrapper.eumConvertItemArrayFromUserUnitF.argtypes = [ctypes.c_int32, 
                                                                        ctypes.c_int32, 
                                                                        ctypes.c_void_p, 
                                                                        ctypes.c_int32, 
                                                                        ctypes.c_float]




  #/ <summary>
  #/ A static wrapper for making procedure calls in the EUM.dll. The methods here relate directly
  #/ to those in EUM.dll.
  #/ <para>
  #/ Whenever possible, please use the methods of the <see cref="eumQuantity"/>, or the
  #/ util/extension methods in <see cref="eumUtil"/> which works on the 
  #/ <see cref="eumQuantity"/>, <see cref="eumUnit"/> and <see cref="eumItem"/>.
  #/ </para>
  #/ </summary>
class eumWrapper:

    #region Additional Methods
    #/ <summary>
    #/ Returns a hashtable using the textual description of each item type as key, and
    #/ the numeric key as value. This allows for rapid lookup of item type keys using
    #/ the textual description if done repeatedly. Use "GetItemTag" for on-time lookups.
    #/ </summary>
    #/ <returns>A hashtable with item type text description, numeric key pairs.</returns>
    @staticmethod
    def CreateItemHashtable() -> dict:
      itemHash = dict();
      n = eumWrapper.eumGetItemTypeCount();
      for i in range(1,n):
        ok, key, desc = eumWrapper.eumGetItemTypeSeq(i);
        if (ok):
          itemHash[desc] = key;
      return itemHash;

    #/ <summary>
    #/ Returns a hashtable using the textual descriptions and abbreviations of units as
    #/ the key and the numeric EUM key as the value. This allows for rapic lookup of
    #/ unit keys using the textual description or abbreviation if done repeatedly.
    #/ Use "GetUnitTag" for one-time lookups. Note: there are duplicate units in the
    #/ EUM System (e.g. degrees Celcius), only the first found is added.
    #/ </summary>
    #/ <returns></returns>
    @staticmethod
    def CreateUnitHashTable(abbreviations: bool = False):
      unitHash = dict(); #current number of unique desc/abbrs.
      prevKey = eumUnit.eumUUnitUndefined;
      ok, unitKey, desc = eumWrapper.eumGetNextUnit(prevKey)
      while (ok):
        if (not abbreviations):
          # Add the full description to the unitHash
          if (not desc in unitHash):
            unitHash[desc] = unitKey;
        else:
          # Add the abbreviated describtion to the unitHash
          desc = eumWrapper.eumGetUnitAbbreviation(unitKey);
          if (not desc in unitHash):
            unitHash[desc] = unitKey;

        prevKey = unitKey;
        ok, unitKey, desc = eumWrapper.eumGetNextUnit(prevKey)
      return unitHash;

    #/ <summary>
    #/ Converts a textual description of the item type to the numeric key for the
    #/ item type if any item type with this text description exists. Returns first
    #/ match found.
    #/ </summary>
    #/ <param name="ItDesc">a textual description of a item type for which the
    #/ numeric key should be found</param>
    #/ <param name="ItKey">Returns the numeric unit key if the textual description
    #/ matches one of units in the system</param>
    #/ <returns>returns a boolean variable which is TRUE if an item type with a
    #/ matching textual description is found, and FALSE otherwise</returns>
    @staticmethod
    def GetItemTypeTag(itemDesc: str) -> eumItem:
      found = False;
      itemKey = None;
      for i in range(1, eumWrapper.eumGetItemTypeCount()):
        ok, key, desc = eumWrapper.eumGetItemTypeSeq(i);
        if (ok and desc == itemDesc):
          found = True
          itemKey = key;
          break;
      if (found):
        return itemKey;
      else:
        return None;

    #/ <summary>
    #/ returns array containing the EUM units that are allowed for an EUM data type
    #/ </summary>
    @staticmethod
    def GetItemAllowedUnits(eumItemType: eumItem):
      nUnits = eumWrapper.eumGetItemUnitCount(eumItemType);
      units = [];
      for i in range(nUnits):
        ok, iUnit, _ = eumWrapper.eumGetItemUnitSeq(eumItemType, i + 1)
        if (ok):
          units.append(iUnit);
      return units;


    #endregion

    #region EUM Procedure Declarations

    #See below for comments on parameters.

    #/ <summary>
    #/ Retrieves the number of different EUM items.
    #/ </summary>
    @staticmethod
    def eumGetItemTypeCount() -> int:
        return eumDLL.Wrapper.eumGetItemTypeCount();

    #/ <summary>
    #/ Retrieves a numeric item key and the corresponding textual description based on a sequence number SeqNo.
    #/ <para>
    #/ The <paramref name="seqNo"/> must be within 1 to <see cref="eumGetItemTypeCount"/>.
    #/ </para>
    #/ </summary>        
    #/ <param name="seqNo">Specifies a 1-based sequence number</param>
    #/ <param name="itemKey">Returns the numeric key of the item</param>
    #/ <param name="itemDesc">Returns the textual description of the item</param>
    #/ <returns>TRUE if an item is found and FALSE otherwise.</returns>
    @staticmethod
    def eumGetItemTypeSeq(seqNo: int) -> Tuple[bool, eumItem, str]:
      itemKey = ctypes.c_int32();
      lpItemDesc = ctypes.c_char_p();
      iok = eumDLL.Wrapper.eumGetItemTypeSeq(ctypes.c_int32(seqNo), ctypes.byref(itemKey), ctypes.byref(lpItemDesc))
      if (0 != iok):
        return True, eumItem(itemKey.value), lpItemDesc.value.decode("ascii");
      return False, eumItem.eumIItemUndefined, "";


    #/ <summary>
    #/ Retrieves the textual description of the item specified by <paramref name="itemKey"/>
    #/ </summary>
    @staticmethod
    def eumGetItemTypeKey(itemKey: eumItem) -> Optional[str]:
      lpItDesc = ctypes.c_char_p();
      if (0 != eumDLL.Wrapper.eumGetItemTypeKey(itemKey, ctypes.byref(lpItDesc))):
        return lpItDesc.value.decode("ascii");
      return None;

    #/ <summary>
    #/ retrieves the number of units attached to the item specified by <paramref name="itemKey"/>
    #/ </summary>
    @staticmethod
    def eumGetItemUnitCount(itemKey: eumItem) -> int:
        return eumDLL.Wrapper.eumGetItemUnitCount(ctypes.c_int32(itemKey));

    #/ <summary>
    #/ Gets the first unit defined in the eum-system for the item specified by itemKey.
    #/ </summary>
    @staticmethod
    def eumGetItemFirstEqvUnit(itemKey: eumItem) -> eumUnit:
      unitKey = ctypes.c_int32()
      lpUniDesc = ctypes.c_char_p();

      if (0 != eumDLL.Wrapper.eumGetItemUnitSeq(itemKey, ctypes.c_int32(1), ctypes.byref(unitKey), ctypes.byref(lpUniDesc))):
        return eumUnit(unitKey.value);
      raise Exception("Item not defined")


    #/ <summary>
    #/ Retrieves a numeric unit key and the corresponding textual description based on a 
    #/ sequence number <paramref name="UniSeq"/> for an item specified by <paramref name="itemKey"/>. 
    #/ <para>
    #/ The <paramref name="UniSeq"/> must be within range 1 to <see cref="eumGetItemUnitCount"/>
    #/ for the item.
    #/ </para>
    #/ </summary>    
    #/ <param name="itemKey">Specifies the numeric input key of the item</param>
    #/ <param name="UniSeq">Specifies a 1-based sequence number</param>
    #/ <param name="unitKey">Returns the numeric key of the found unit</param>
    #/ <param name="UniDesc">Returns the textual description of the unit, e.g. "hour" or "second"</param>
    @staticmethod
    def eumGetItemUnitSeq(itemKey: eumItem, UniSeq: int) -> Tuple[bool, eumUnit, str]:
      unitKey = ctypes.c_int32()
      lpUniDesc = ctypes.c_char_p()
      if (0 != eumDLL.Wrapper.eumGetItemUnitSeq(itemKey, UniSeq, ctypes.byref(unitKey), ctypes.byref(lpUniDesc))):
        return True, eumUnit(unitKey.value), lpUniDesc.value.decode("ascii");
      return False, eumUnit.eumUUnitUndefined, "";


    #/ <summary>
    #/ Sets the users unit of an item specified by <paramref name="itemKey"/>
    #/ </summary>
    #/ <remarks>
    #/ Automatic unit equivalence check between the item specified by <paramref name="itemKey"/> 
    #/ and the unit <paramref name="UserUnitKey"/> is performed. 
    #/ If this check fails the unit assignment to the item is ignored. 
    #/ </remarks>
    @staticmethod
    def eumSetItemUserUnit(itemKey: eumItem, UserunitKey: eumUnit) -> bool:
        return 0 != eumDLL.Wrapper.eumSetItemUserUnit(ctypes.c_int32(itemKey), ctypes.c_int32(UserunitKey))

    #/ <summary>
    #/ Gets the users unit of an item specified by <paramref name="itemKey"/>
    #/ </summary>
    @staticmethod
    def eumGetItemUserUnit(itemKey: eumItem) -> eumUnit:
        UserunitKey = ctypes.c_int32();
        if 0 != eumDLL.Wrapper.eumGetItemUserUnit(ctypes.c_int32(itemKey), ctypes.byref(UserunitKey)):
            return eumUnit(UserunitKey.value)
        raise Exception("Item not defined")

    #/ <summary>
    #/ Retrieves the textual description of the unit specified by the numeric input key <paramref name="unitKey"/>. 
    #/ </summary>    
    @staticmethod
    def eumGetUnitKey(unitKey: eumUnit) -> str:
      lpUniDesc = ctypes.c_char_p();
      if (0 != eumDLL.Wrapper.eumGetUnitKey(ctypes.c_int32(unitKey), ctypes.byref(lpUniDesc))):
        return lpUniDesc.value.decode("ascii");
      raise Exception("Unit not defined")

    #/ <summary>
    #/ retrieves the textual abbreviation of the unit specified by 
    #/ the numeric input key <paramref name="unitKey"/>. 
    #/ </summary>        
    @staticmethod
    def eumGetUnitAbbreviation(unitKey: eumUnit) -> str:
      lpUnitDesc = ctypes.c_char_p();
      if (1 == eumDLL.Wrapper.eumGetUnitAbbreviation(unitKey, ctypes.byref(lpUnitDesc))):
        return lpUnitDesc.value.decode("ascii");
      raise Exception("Unit not defined")

    #/ <summary>
    #/ Converts a textual description of the unit to the numeric 
    #/ key for the unit if any unit with this text description exists. 
    #/ </summary>
    #/ <remarks>
    #/ eumGetUnitTag accepts plural s' in UniDesc the textual description 
    #/ of the units though the built-in text for the unit general is without 
    #/ s-endings, e.g. "hour" and "hours". 
    #/ </remarks>
    @staticmethod
    def eumGetUnitTag(unitDesc: str) -> eumUnit:
        unitKey = ctypes.c_int32();
        if 0 != eumDLL.Wrapper.eumGetUnitTag(ctypes.c_char_p(unitDesc.encode("ascii")),
                                             ctypes.byref(unitKey)):
            return eumUnit(unitKey.value);
        return None;

    #/ <summary>
    #/ Converts a textual description of the unit to the numeric key for 
    #/ the unit if any unit attached to an item with this text description exists. 
    #/ </summary>
    @staticmethod
    def eumGetItemUnitTag(itemKey: eumItem, unitDesc: str) -> Tuple[bool,eumUnit]:
        unitKey = ctypes.c_int32();
        if 0 != eumDLL.Wrapper.eumGetItemUnitTag(ctypes.c_int32(itemKey), 
                                                 ctypes.c_char_p(unitDesc.encode("ascii")),
                                                 ctypes.byref(unitKey)):
            return eumUnit(unitKey.value);
        return None;

    #/ <summary>
    #/ Checks if two units specified are equivalent
    #/ </summary>
    @staticmethod
    def eumUnitsEqv(unitKey1: eumUnit, unitKey2: eumUnit) -> bool:
        return 0 != eumDLL.Wrapper.eumUnitsEqv(ctypes.c_int32(unitKey1), ctypes.c_int32(unitKey2))

    #/ <summary>
    #/ Checks if an item specified by <paramref name="itemKey"/> is 
    #/ equivalent with the unit specified by <paramref name="unitKey"/>.
    #/ </summary>
    @staticmethod
    def eumItemUnitEqv(itemKey: eumItem, unitKey: eumUnit) -> bool:
        return 0 != eumDLL.Wrapper.eumItemUnitEqv(ctypes.c_int32(itemKey), ctypes.c_int32(unitKey))


    #/ <summary>
    #/ Gets the base unit defined in the eum-system when given the tag for any unit.
    #/ </summary>        
    @staticmethod
    def eumGetBaseUnit(unitKey: eumUnit) -> eumUnit:
      baseunitKey = ctypes.c_int32();
      lpBaseUnitDesc = ctypes.c_char_p();
      if (0 != eumDLL.Wrapper.eumGetBaseUnit(ctypes.c_int32(unitKey), 
                                             ctypes.byref(baseunitKey), 
                                             ctypes.byref(lpBaseUnitDesc))):
        return eumUnit(baseunitKey.value);
      raise Exception("Unit not defined")

    #/ <summary>
    #/ Get the next unit defined in the eum-system when given the tag 
    #/ for the previous unit. 
    #/ <see cref="eumUnit.eumUUnitUndefined"/> gives the first unit in the system. 
    #/ </summary>        
    @staticmethod
    def eumGetNextUnit(prevUnitKey: eumUnit) -> Tuple[bool, eumUnit, str]:
      unitKey = ctypes.c_int32();
      lpUnitDesc = ctypes.c_char_p();
      if (0 != eumDLL.Wrapper.eumGetNextUnit(prevUnitKey, ctypes.byref(unitKey), ctypes.byref(lpUnitDesc))):
        return True, eumUnit(unitKey.value), lpUnitDesc.value.decode("ascii");
      return False, eumUnit.eumUUnitUndefined, "";

    #/ <summary>
    #/ Get the next unit defined in the eum-system which is equivalent 
    #/ with the unit specified by <paramref name="baseUnitKey"/> when given the tag for 
    #/ the previous unit. 
    #/ <see cref="eumUnit.eumUUnitUndefined"/> gives the first unit in the system. 
    #/ </summary>    
    #/ <param name="baseUnitKey">Specifies the numeric key of the unit which controls the equivalency</param>
    #/ <param name="PrevUnitKey">Specifies the numeric input key of the previous unit. <see cref="eumUnit.eumUUnitUndefined"/> gives the first unit</param>
    #/ <param name="unitKey">Returns the numeric key of the unit</param>
    #/ <param name="unitDesc">Returns the textual description of the unit</param>
    @staticmethod
    def eumGetNextEqvUnit(baseunitKey: eumUnit, PrevunitKey: eumUnit) -> Tuple[bool, eumUnit, str]:
      unitKey = ctypes.c_int32();
      lpUnitDesc = ctypes.c_char_p();
      rc = eumDLL.Wrapper.eumGetNextEqvUnit(baseunitKey, PrevunitKey, ctypes.byref(unitKey), ctypes.byref(lpUnitDesc))
      if rc != 0:
        return False, eumUnit.eumUUnitUndefined, "";
      return True, eumUnit(unitKey.value), lpUnitDesc.value.decode("ascii");

    #/ <summary>
    #/ Converts a floating point value from <paramref name="fromUnitKey"/>-units to 
    #/ <paramref name="toUnitKey"/> and automatically checks the equivalence of 
    #/ the two units. 
    #/ </summary>
    @staticmethod
    def eumConvertUnit(fromUnitKey: eumUnit, fromValue: float, toUnitKey: eumUnit) -> Tuple[bool, float]:
        toValue = ctypes.c_double();
        iok = eumDLL.Wrapper.eumConvertUnit(ctypes.c_int32(fromUnitKey), ctypes.c_double(fromValue), ctypes.c_int32(toUnitKey), ctypes.byref(toValue))
        return (iok != 0, toValue.value)

    #/ <summary>
    #/ Converts an entire double array from <paramref name="fromUnitKey"/>-units to <paramref name="toUnitKey"/> 
    #/ and automatically checks the equivalence of the two units. 
    #/ </summary>
    @staticmethod
    def eumConvertItemArrayD(fromUnitKey: eumUnit, toUnitKey: eumUnit, pData: np.ndarray, dDeleteValue: float = 0.0) -> bool:
        return 0 != eumDLL.Wrapper.eumConvertItemArrayD(ctypes.c_int32(fromUnitKey), 
                                                        ctypes.c_int32(toUnitKey), 
                                                        pData.ctypes.data, 
                                                        ctypes.c_int32(pData.size),
                                                        ctypes.c_double(dDeleteValue))

    #/ <summary>
    #/ Converts an entire float array from <paramref name="fromUnitKey"/>-units to <paramref name="toUnitKey"/> 
    #/ and automatically checks the equivalence of the two units. 
    #/ </summary>
    @staticmethod
    def eumConvertItemArrayF(fromUnitKey: eumUnit, toUnitKey: eumUnit, pData: np.ndarray, fDeleteValue: np.float32 = np.float32(0.0)) -> bool:
        return 0 != eumDLL.Wrapper.eumConvertItemArrayF(ctypes.c_int32(fromUnitKey), 
                                                        ctypes.c_int32(toUnitKey), 
                                                        pData.ctypes.data, 
                                                        ctypes.c_int32(pData.size),
                                                        ctypes.c_float(fDeleteValue))

    #/ <summary>
    #/ Converts a a floating point value from <paramref name="unitKey"/>-units to 
    #/ the equivalent base units. 
    #/ </summary>
    @staticmethod
    def eumConvertUnitToBase(unitKey: eumUnit, value: float) -> float:
        baseValue = ctypes.c_double();
        if 0 != eumDLL.Wrapper.eumConvertUnitToBase(ctypes.c_int32(unitKey), ctypes.c_double(value), ctypes.byref(baseValue)):
            return baseValue.value;
        raise Exception("Unit not found")

    #/ <summary>
    #/ Converts a a floating point value from the equivalent base units to <paramref name="unitKey"/>-units. 
    #/ </summary>
    @staticmethod
    def eumConvertUnitFromBase(unitKey: eumUnit, baseValue: float) -> float:
        value = ctypes.c_double();
        if 0 != eumDLL.Wrapper.eumConvertUnitFromBase(ctypes.c_int32(unitKey), ctypes.c_double(baseValue), ctypes.byref(value)):
            return value.value;
        raise Exception("Unit not found")


    #/ <summary>
    #/ Converts a floating point value from <paramref name="localUnitKey"/>-units to 
    #/ user unit and automatically checks the equivalence of the two units. 
    #/ </summary>
    #/ <param name="UBGitemKey">Specifies the Unit Base Group Item key</param>
    #/ <param name="localUnitKey">Specifies the unit of the variable <paramref name="fromValue"/>, to be convertes to user unit</param>
    #/ <param name="fromValue">Specifies the floating point value, in <paramref name="localUnitKey"/>-units, to be converted to user unit defined in the UBG Item</param>
    #/ <param name="toValue">Returns the value converted to User units</param>
    @staticmethod
    def eumConvertToUserUnit(UBGitemKey: eumItem, localunitKey: eumUnit, fromValue: float) -> float:
        toValue = ctypes.c_double();
        if 0 != eumDLL.Wrapper.eumConvertToUserUnit(ctypes.c_int32(UBGitemKey), 
                                                    ctypes.c_int32(localunitKey), 
                                                    ctypes.c_double(fromValue), 
                                                    ctypes.byref(toValue)):
            return toValue.value;
        raise Exception("Unit not found")

    #/ <summary>
    #/ Converts a floating point value to <paramref name="localUnitKey"/>-units from 
    #/ user unit and automatically checks the equivalence of the two units. 
    #/ </summary>
    #/ <param name="UBGitemKey">Specifies the Unit Base Group Item key</param>
    #/ <param name="localUnitKey">Specifies the unit of the variable <paramref name="fromValue"/>, to be convertes from user unit</param>
    #/ <param name="fromValue">Specifies the floating point value, in user units, to be converted</param>
    #/ <param name="toValue">Returns the value converted to <paramref name="localUnitKey"/></param>
    @staticmethod
    def eumConvertFromUserUnit(UBGitemKey: eumItem, localunitKey: eumUnit, fromValue: float) -> float:
        toValue = ctypes.c_double();
        if 0 != eumDLL.Wrapper.eumConvertFromUserUnit(ctypes.c_int32(UBGitemKey), 
                                                      ctypes.c_int32(localunitKey), 
                                                      ctypes.c_double(fromValue), 
                                                      ctypes.byref(toValue)):
            return toValue.value;
        raise Exception("Unit not found")

    #/ <summary>
    #/ converts a double array from <paramref name="localUnitKey"/>-units to user unit 
    #/ and automatically checks the equivalence of the two units. 
    #/ </summary>
    #/ <param name="UBGitemKey">Specifies the Unit Base Group Item key</param>
    #/ <param name="localUnitKey">Specifies the unit of the data, to be converted to user units</param>
    #/ <param name="pData">Specifies the double data to be converted user units</param>
    #/ <param name="nElements">Specifies the number of elements in the array</param>
    #/ <param name="dDeleteValue">Specifies the double precision delete value - these are not converted</param>
    @staticmethod
    def eumConvertItemArrayToUserUnitD(UBGitemKey: eumItem, localunitKey: eumUnit, pData: np.ndarray, dDeleteValue: float = 0.0) -> bool:
        return 0 != eumDLL.Wrapper.eumConvertItemArrayToUserUnitD(ctypes.c_int32(UBGitemKey),
                                                                  ctypes.c_int32(localunitKey),
                                                                  pData.ctypes.data,
                                                                  ctypes.c_int32(pData.size),
                                                                  ctypes.c_double(dDeleteValue))

    #/ <summary>
    #/ converts a float array from <paramref name="localUnitKey"/>-units to user unit 
    #/ and automatically checks the equivalence of the two units. 
    #/ </summary>
    #/ <param name="UBGitemKey">Specifies the Unit Base Group Item key</param>
    #/ <param name="localUnitKey">Specifies the unit of the data, to be converted to user units</param>
    #/ <param name="pData">Specifies the float data to be converted user units</param>
    #/ <param name="nElements">Specifies the number of elements in the array</param>
    #/ <param name="fDeleteValue">Specifies the single precision delete value - these are not converted</param>
    @staticmethod
    def eumConvertItemArrayToUserUnitF(UBGitemKey: eumItem, localunitKey: eumUnit, pData: float, fDeleteValue: np.float32 = np.float32(0.0)) -> bool:
        return 0 != eumDLL.Wrapper.eumConvertItemArrayToUserUnitF(ctypes.c_int32(UBGitemKey),
                                                                  ctypes.c_int32(localunitKey),
                                                                  pData.ctypes.data,
                                                                  ctypes.c_int32(pData.size),
                                                                  ctypes.c_float(fDeleteValue))

    #/ <summary>
    #/ Converts a double array to <paramref name="LocalUnitKey"/>-units from user 
    #/ unit and automatically checks the equivalence of the two units. 
    #/ </summary>
    #/ <param name="UBGitemKey">Specifies the Unit Base Group Item key</param>
    #/ <param name="LocalUnitKey">Specifies the unit of the data, to be converted from user units</param>
    #/ <param name="pData">Specifies the double data to be converted user units</param>
    #/ <param name="nElements">Specifies the number of elements in the array</param>
    #/ <param name="dDeleteValue">Specifies the double precision delete value</param>
    @staticmethod
    def eumConvertItemArrayFromUserUnitD(UBGitemKey: eumItem, localunitKey: eumUnit, pData: float, dDeleteValue: float = 0.0) -> bool:
        return 0 != eumDLL.Wrapper.eumConvertItemArrayFromUserUnitD(ctypes.c_int32(UBGitemKey),
                                                                    ctypes.c_int32(localunitKey),
                                                                    pData.ctypes.data,
                                                                    ctypes.c_int32(pData.size),
                                                                    ctypes.c_double(dDeleteValue))

    #/ <summary>
    #/ Converts a float array to <paramref name="LocalUnitKey"/>-units from user 
    #/ unit and automatically checks the equivalence of the two units. 
    #/ </summary>
    #/ <param name="UBGitemKey">Specifies the Unit Base Group Item key</param>
    #/ <param name="LocalUnitKey">Specifies the unit of the data, to be converted from user units</param>
    #/ <param name="pData">Specifies the float data to be converted user units</param>
    #/ <param name="nElements">Specifies the number of elements in the array</param>
    #/ <param name="fDeleteValue">Specifies the single precision delete value</param>
    @staticmethod
    def eumConvertItemArrayFromUserUnitF(UBGitemKey: eumItem, localunitKey: eumUnit, pData: float, fDeleteValue: np.float32 = np.float32(0.0)) -> bool:
        return 0 != eumDLL.Wrapper.eumConvertItemArrayFromUserUnitF(ctypes.c_int32(UBGitemKey),
                                                                    ctypes.c_int32(localunitKey),
                                                                    pData.ctypes.data,
                                                                    ctypes.c_int32(pData.size),
                                                                    ctypes.c_float(fDeleteValue))

#    #/ <summary>
#    #/ TODO: Pending
#    #/ </summary>
#    @staticmethod
#    def eumGetFilterCount(); -> int:
#
#    private static bool _eumGetFilterSeq(SeqNo: int, out FtKey: int, out IntPtr lpFtDesc);
#
#    #/ <summary>
#    #/ TODO: Pending
#    #/ </summary>        
#    @staticmethod
#    def eumGetFilterSeq(SeqNo: int, out FtKey: int, out FtDesc: str) -> bool:
#      IntPtr lpFtDesc;
#
#      if (not _eumGetFilterSeq(SeqNo, ctypes.byref(FtKey), ctypes.byref(lpFtDesc))):
#        FtDesc = string.Empty;
#        return False;
#
#      FtDesc = Marshal.PtrToStringAnsi(lpFtDesc);
#      return True;
#
#    private static bool _eumGetFilterKey(FtKey: int, out IntPtr lpFtDesc);
#
#    #/ <summary>
#    #/ TODO: Pending
#    #/ </summary>        
#    @staticmethod
#    def eumGetFilterKey(FtKey: int, out FtDesc: str) -> bool:
#      IntPtr lpFtDesc;
#
#      if (not _eumGetFilterKey(FtKey, ctypes.byref(lpFtDesc))):
#        FtDesc = string.Empty;
#        return False;
#
#      FtDesc = Marshal.PtrToStringAnsi(lpFtDesc);
#      return True;
#
#    #/ <summary>
#    #/ TODO: Pending
#    #/ </summary>
#    @staticmethod
#    def eumGetFilteredItemTypeCount(Filter: int); -> int:
#
#    private static bool _eumGetFilteredItemTypeSeq(Filter: int, SeqNo: int, out itemKey: eumItem, out IntPtr lpItDesc);
#
#    #/ <summary>
#    #/ TODO: Pending
#    #/ </summary>        
#    @staticmethod
#    def eumGetFilteredItemTypeSeq(Filter: int, SeqNo: int, out itemKey: eumItem, out ItDesc: str) -> bool:
#      IntPtr lpItDesc;
#
#      if (not _eumGetFilteredItemTypeSeq(Filter, SeqNo, ctypes.byref(itemKey), ctypes.byref(lpItDesc))):
#        ItDesc = string.Empty;
#        return False;
#
#      ItDesc = Marshal.PtrToStringAnsi(lpItDesc);
#      return True;
#
#    #/ <summary>
#    #/ TODO: Pending
#    #/ </summary>
#    @staticmethod
#    def eumItemFilterEqv(itemKey: eumItem, Filter: int); -> bool:
#
#    #/ <summary>
#    #/ TODO: Pending
#    #/ </summary>
#    @staticmethod
#    def eumSetProductFilter(Filter: int); -> void:
#
#    #/ <summary>
#    #/ TODO: Pending
#    #/ </summary>
#    @staticmethod
#    def eumGetProductFilter(); -> int:


    #/ <summary>
    #/ Returns factor and offset to SI base unit
    @staticmethod
    def eumUnitGetSIFactor(unitKey: eumUnit) -> Tuple[float,float]:
        factor = ctypes.c_double()
        offset = ctypes.c_double()
        powdim = np.zeros(7, dtype=np.double);
        facdim = np.zeros(7, dtype=np.double);
        if 0 != eumDLL.Wrapper.eumUnitGetParameters(ctypes.c_int32(unitKey),
                                                    ctypes.byref(factor),
                                                    ctypes.byref(offset),
                                                    powdim.ctypes.data,
                                                    facdim.ctypes.data):
            return factor.value, offset.value
        raise Exception("Unit no defined");

    #/ <summary>
    #/ Returns all 9 parameters, that describes a unit. First it's the two parameters (factor and offset) that defines 
    #/ how the unit is converted to the base (SI) unit. Secondly it's the power of the seven dimension 
    #/ <para>
    #/ The offset and factor are defined as:
    #/ <code>
    #/   baseValue = factor*unitValue + offset
    #/ </code>
    #/ </para>
    #/ See <see cref="eumDimensionBase"/> for the order of the dimensions
    #/ </summary>
    @staticmethod
    def eumUnitGetParameters(unitKey: eumUnit) -> Tuple[float,float,np.ndarray,np.ndarray]:
        factor = ctypes.c_double()
        offset = ctypes.c_double()
        powdim = np.zeros(7, dtype=np.double);
        facdim = np.zeros(7, dtype=np.double);
        if 0 != eumDLL.Wrapper.eumUnitGetParameters(ctypes.c_int32(unitKey),
                                                    ctypes.byref(factor),
                                                    ctypes.byref(offset),
                                                    powdim.ctypes.data,
                                                    facdim.ctypes.data):
            return factor.value, offset.value, powdim, facdim
        raise Exception("Unit no defined");


#    #/ <summary>
#    #/ TODO: Pending
#    #/ </summary>
#    @staticmethod
#    def eumGetFlybyFilter(); -> int:

#    #/ <summary>
#    #/ computes, if possible, the derivation factor <paramref name="Factor"/> to use 
#    #/ when derivating the unit <paramref name="unitKey"/> with the unit <paramref name="RefUnitKey"/>. 
#    #/ <paramref name="RefUnitKey"/> must be one dimensional. Also the numeric keys of the 
#    #/ resulting unit <paramref name="ResultUnitKey"/> and the remainder of the unit 
#    #/ <paramref name="RemainderUnitKey"/> is returned if they are present in the system, 
#    #/ if not their values are -1. 
#    #/ </summary>
#    #/ <example>
#    #/ deriving eumUft2PerDay (unitKey=4711) over eumUsec (RefUniKey=1400) gives a
#    #/ factor of (Factor=) 86400.0, a resulting unit of eumUUnitUndefined 
#    #/ (ResultUnitKey=0) since there is no eumUft2PerDay2 unit defined and a 
#    #/ remainding unit of eumUday (RemainderUnitKey=1403).
#    #/ </example>
#    @staticmethod
#    def eumUnitGetDerivationFactor(unitKey: eumUnit, RefunitKey: eumUnit, out ResultunitKey: eumUnit, out RemainderunitKey: eumUnit, out Factor: float); -> bool:

#    #/ <summary>
#    #/ Computes, if possible, the integration factor <paramref name="Factor"/> to use when integrating 
#    #/ the unit <paramref name="unitKey"/> over the unit <paramref name="RefUnitKey"/>. 
#    #/ <paramref name="RefUnitKey"/> must be one dimensional. 
#    #/ Also the numeric keys of the resulting unit <paramref name="ResultUnitKey"/> and the remainder of 
#    #/ the unit <paramref name="RemainderUnitKey"/> is returned if they are present in the system, 
#    #/ if not their values are -1. 
#    #/ </summary>
#    #/ <example>
#    #/ Integrating eumUft2PerDay (unitKey=4711) over eumUsec (RefUniKey=1400) gives a
#    #/ factor of (Factor=) 1.15740740740741E-05, a resulting unit of
#    #/ eumUft2 (ResultUnitKey=3203) and a remainding unit of eumUPerDay (RemainderUnitKey=2600).
#    #/ </example>
#    @staticmethod
#    def eumUnitGetIntegrationFactor(unitKey: eumUnit, RefunitKey: eumUnit, out ResultunitKey: eumUnit, out RemainderunitKey: eumUnit, out Factor: float); -> bool:


