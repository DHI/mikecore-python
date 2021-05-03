from mikecore.DfsuFile import DfsuFile

class MeshBuilder:
    Projection = None
    EumQuantity = None
    
    __isSetProjection = False  # None? 
    __isSetNodes = None
    __isSetConnectivity = None

    NodeIds = None
    X = None
    Y = None
    Z = None
    Code = None

    ElementIds = None
    __connectivity = None

    def SetProjection(self, projection):
        #if self.Projection is None:
        #throw new ArgumentNullException("projection");
        if isinstance(projection,str):
            self.Projection = projection
        else:
            self.Projection = projection.WKTString
        self.__isSetProjection = True    

    # public void SetEumQuantity(eumQuantity eumQuantity)
    # {
    #   _eumQuantity = eumQuantity;
    # }

    def SetNodes(self, x, y, z, code):
        self.X = x
        self.Y = y
        self.Z = z
        self.Code = code
        self.__isSetNodes = True

    def SetElements(self, connectivity):
        if connectivity == None:
            raise TypeError("connectivity")
        if len(connectivity) == 0:
            raise ValueError("Element table has no rows. There must be at least one row")

        ## Check number of elements
        for i in range(len(connectivity)):
            elmnt = connectivity[i]
            if (3 > len(elmnt)) or (len(elmnt) > 4):
                raise ValueError("All elements must have 3 or 4 nodes. Element number {0} has {1} nodes".format(i + 1, len(elmnt)))
        
        self.__connectivity = connectivity
        self.__isSetConnectivity = True


    ## <summary>
    ## Set the element id's. Optional. If not set, default values are used (1,2,3,...)
    ## </summary>
    # public void SetElementIds(int[] elementIds)
    # {
    #   if (_connectivity != null && _connectivity.Length != elementIds.Length)
    #   {
    #     throw new ArgumentException("Number of element id's does not match number of elements", "elementIds");
    #   }

    # }

    ## <summary>
    ## Validate will return a string of issues from the item builder.
    ## When this returns an empty list, the item has been properly build.
    ## </summary>
    # public string[] Validate()
    # {
    #   return (Validate(false));
    # }

    # private string[] Validate(bool dieOnError)
    # {
    #   List<string> errors = new List<string>();

    #   if (!_isSetProjection)
    #     errors.Add("Projection has not been set");
    #   if (!_isSetNodes)
    #     errors.Add("Nodes have not been set");
    #   if (!_isSetConnectivity)
    #     errors.Add("Elements have not been set");

    #   // Check that all nodenumbers are within the range of
    #   // number of nodes.
    #   if (_isSetNodes && _isSetConnectivity)
    #   {
    #     bool check = true;
    #     foreach (int[] elmt in _connectivity)
    #     {
    #       foreach (int nodeNumber in elmt)
    #       {
    #         if (0 >= nodeNumber || nodeNumber > _x.Length)
    #         {
    #           check = false;
    #           break;
    #         }
    #       }
    #       if (!check)
    #         break;
    #     }
    #     if (!check)
    #       errors.Add("At least one element has an invalid node number. Node numbers must be within [1,numberOfNodes]");
    #   }

    #   if (dieOnError && errors.Count > 0)
    #   {
    #     string msgs = DfsBuilder.ErrorMessage(errors);
    #     throw new DfsException(msgs);
    #   }

    #   return (errors.ToArray());
    # }

    # ## <summary>
    # ## Create and return a new <see cref="MeshFile"/> object
    # ## </summary>
    # public MeshFile CreateMesh()
    # {

    #   Validate(true);

    #   // Creating default eumQuantity in meters
    #   if (_eumQuantity == null)
    #     _eumQuantity = new eumQuantity(eumItem.eumIBathymetry, eumUnit.eumUmeter);

    #   // Creating default node id's, if empty
    #   if (_nodeIds == null)
    #   {
    #     // Setting node ids 1,2,3,...
    #     _nodeIds = new int[_x.Length];
    #     for (int i = 0; i < _x.Length; i++)
    #     {
    #       _nodeIds[i] = i + 1;
    #     }
    #   }
    #   // Creating default element id's, if empty
    #   if (_elementIds == null)
    #   {
    #     // Setting element ids 1,2,3,...
    #     _elementIds = new int[_connectivity.Length];
    #     for (int i = 0; i < _connectivity.Length; i++)
    #     {
    #       _elementIds[i] = i + 1;
    #     }
    #   }

    #   // Creating additional element information
    #   int[] elementType = new int[_connectivity.Length];
    #   int[] nodesPerElmt = new int[_connectivity.Length];
    #   int nodeElmtCount = 0;  // total number of nodes listed in the connectivity table
    #   for (int i = 0; i < elementType.Length; i++)
    #   {
    #     int elmtTypeNumber;
    #     int[] elmt = _connectivity[i];
    #     switch (elmt.Length)
    #     {
    #       case 3:
    #         elmtTypeNumber = 21;
    #         break;
    #       case 4:
    #         elmtTypeNumber = 25;
    #         break;
    #       case 6:
    #         elmtTypeNumber = 32;
    #         break;
    #       case 8:
    #         elmtTypeNumber = 33;
    #         break;
    #       default:
    #         // this should have been caught in the validate phase, but just in case:
    #         throw new DfsException("Element with invalid number of nodes encountered");
    #     }
    #     elementType[i] = elmtTypeNumber;
    #     nodesPerElmt[i] = elmt.Length;
    #     nodeElmtCount += elmt.Length;
    #   }

    #   int[] connectivityArray = new int[nodeElmtCount];
    #   int k = 0;
    #   for (int i = 0; i < elementType.Length; i++)
    #   {
    #     int[] elmt = _connectivity[i];
    #     for (int j = 0; j < elmt.Length; j++)
    #     {
    #       connectivityArray[k++] = elmt[j];
    #     }
    #   }

    #   MeshFile res = MeshFile.Create(_eumQuantity, _projection, _nodeIds, _x, _y, _z, _code, _elementIds, elementType, _connectivity);

    #   return (res);
    # }


    # TODO: do we need this? 
    @staticmethod
    def Convert(arr) -> List[float]:    # float[] 
        res = [] #new double[arr.Length];
        for i in range(len(arr)):        
            res[i] = arr[i]
        return res    

    # internal static float[] Convert(double[] arr)
    # {
    #   float[] res = new float[arr.Length];
    #   for (int i = 0; i < arr.Length; i++)
    #   {
    #     res[i] = (float)arr[i];
    #   }
    #   return (res);
    # }

    ## <summary>
    ## Create a mesh file from the provided dfsu file.
    ## <para>
    ## The dfsu file must be a 2D dfsu file.
    ## </para>
    ## </summary>
    # @staticmethod
    # def Create(dfsuFile: DfsuFile) -> MeshFile:
    
    #   eumQuantity bathyQuantity;
    #   if (dfsuFile.ZUnit != eumUnit.eumUUnitUndefined)
    #     bathyQuantity = new eumQuantity(eumItem.eumIBathymetry, dfsuFile.ZUnit);
    #   else
    #     bathyQuantity = new eumQuantity(eumItem.eumIBathymetry, eumUnit.eumUmeter);
      
    #   res = MeshFile.Create(bathyQuantity, dfsuFile.Projection.WKTString, 
    #     dfsuFile.NodeIds, 
    #     dfsuFile.X, 
    #     dfsuFile.Y, 
    #     Convert(dfsuFile.Z), 
    #     dfsuFile.Code, 
    #     dfsuFile.ElementIds, 
    #     dfsuFile.ElementType, 
    #     dfsuFile.ElementTable);
    #   return res
    